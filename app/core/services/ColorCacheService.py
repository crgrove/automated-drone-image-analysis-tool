"""
ColorCacheService - Manages persistent caching of AOI color information.

This service provides:
- Per-dataset JSON storage of color information (hue, hex, RGB)
- Fast lookup during gallery rendering
- Fallback to on-demand calculation for backwards compatibility
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
from core.services.LoggerService import LoggerService


class ColorCacheService:
    """
    Service for caching AOI color information to disk.

    Color info includes:
    - rgb: [r, g, b] values (0-255)
    - hex: "#RRGGBB" hex color string
    - hue_degrees: 0-360 degree hue value
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the color cache service.

        Args:
            cache_dir: Directory for color cache (default: per-dataset .color_cache/)
        """
        self.logger = LoggerService()
        self.cache_dir = Path(cache_dir) if cache_dir else None

        # In-memory cache: {cache_key: color_info_dict}
        self.memory_cache: Dict[str, Optional[Dict[str, Any]]] = {}

        # Flag to track if cache file has been loaded
        self._cache_loaded = False

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Color cache initialized at {self.cache_dir}")

    def get_cache_key(self, image_path: str, aoi_data: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for an AOI.

        Uses only the filename and AOI coordinates to make caches fully portable
        across machines and time. Modification time is NOT included so cached
        colors remain valid when files are copied/moved.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary with center and radius

        Returns:
            MD5 hash cache key
        """
        try:
            import os

            # Use only the filename to make cache portable across machines
            # Drone images have unique filenames, so this is safe
            filename = os.path.basename(image_path)

            # Create unique identifier from filename, center, radius
            # NOTE: mtime is intentionally NOT included to allow caches to work
            # when files are copied between machines (which changes mtime)
            center = aoi_data.get('center', (0, 0))
            radius = aoi_data.get('radius', 0)

            identifier = f"{filename}_{center[0]}_{center[1]}_{radius}"

            # Generate hash
            return hashlib.md5(identifier.encode()).hexdigest()

        except Exception as e:
            self.logger.error(f"Error generating cache key: {e}")
            # Fallback to simple hash
            return hashlib.md5(str(aoi_data).encode()).hexdigest()

    def get_legacy_cache_key(self, image_path: str, aoi_data: Dict[str, Any], xml_path: Optional[str] = None) -> str:
        """
        Generate cache key using the OLD formula (for backward compatibility).

        This is used to find caches generated before the portable key update.
        Uses the original XML path if provided (for relocated files).

        Args:
            image_path: Path to the source image (current location)
            aoi_data: AOI dictionary with center and radius
            xml_path: Original path from XML (for relocated files)

        Returns:
            MD5 hash cache key using old formula
        """
        try:
            import os

            # Use XML path if provided (for relocated files), otherwise use absolute path
            # The XML path is the original path from when cache was generated
            if xml_path:
                # Convert forward slashes to platform separator
                cache_path = xml_path.replace('/', os.sep)
                # Make absolute if it was stored as relative
                if not os.path.isabs(cache_path):
                    cache_path = os.path.abspath(cache_path)
            else:
                cache_path = os.path.abspath(image_path)

            mtime = Path(image_path).stat().st_mtime

            center = aoi_data.get('center', (0, 0))
            radius = aoi_data.get('radius', 0)

            # OLD identifier format
            identifier = f"{cache_path}_{mtime}_{center[0]}_{center[1]}_{radius}"

            return hashlib.md5(identifier.encode()).hexdigest()

        except Exception as e:
            # Fallback to simple hash
            return hashlib.md5(str(aoi_data).encode()).hexdigest()

    def get_cache_file_path(self) -> Optional[Path]:
        """Get the path to the cache JSON file."""
        if not self.cache_dir:
            return None
        return self.cache_dir / "colors.json"

    def get_lock_file_path(self) -> Optional[Path]:
        """Get the path to the lock file."""
        if not self.cache_dir:
            return None
        return self.cache_dir / "colors.json.lock"

    def _acquire_lock(self, timeout: float = 10.0) -> bool:
        """
        Acquire a file lock for thread-safe cache access.

        Args:
            timeout: Maximum time to wait for lock in seconds

        Returns:
            True if lock acquired, False if timeout
        """
        lock_file = self.get_lock_file_path()
        if not lock_file:
            return True  # No locking if no cache dir

        start_time = time.time()
        while True:
            try:
                # Try to create lock file exclusively
                lock_file.touch(exist_ok=False)
                return True
            except FileExistsError:
                # Lock file exists, wait and retry
                if time.time() - start_time > timeout:
                    self.logger.warning("Lock acquisition timeout")
                    return False
                time.sleep(0.1)  # Wait 100ms before retry

    def _release_lock(self):
        """Release the file lock."""
        lock_file = self.get_lock_file_path()
        if lock_file and lock_file.exists():
            try:
                lock_file.unlink()
            except Exception as e:
                self.logger.error(f"Error releasing lock: {e}")

    def load_cache_file(self) -> bool:
        """
        Load all cached color information from disk into memory.

        Returns:
            True if loaded successfully, False otherwise
        """
        cache_file = self.get_cache_file_path()

        if not cache_file or not cache_file.exists():
            return False

        # Acquire lock for thread-safe reading
        if not self._acquire_lock():
            self.logger.warning("Could not acquire lock for loading cache")
            return False

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                self.memory_cache = data
                self._cache_loaded = True
                self.logger.info(f"Loaded {len(self.memory_cache)} cached colors from disk")
                return True

        except Exception as e:
            self.logger.error(f"Error loading color cache file: {e}")
            return False
        finally:
            self._release_lock()

    def save_cache_file(self) -> bool:
        """
        Save all cached color information from memory to disk.

        Returns:
            True if saved successfully, False otherwise
        """
        cache_file = self.get_cache_file_path()

        if not cache_file:
            self.logger.warning("No cache directory configured, cannot save")
            return False

        # Acquire lock for thread-safe writing
        if not self._acquire_lock():
            self.logger.warning("Could not acquire lock for saving cache")
            return False

        try:
            # Re-load from disk to merge with any updates from other processes
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        existing_data = json.load(f)
                        # Merge existing data with our new data (our data takes precedence)
                        existing_data.update(self.memory_cache)
                        self.memory_cache = existing_data
                except Exception as e:
                    self.logger.warning(f"Could not load existing cache for merging: {e}")

            # Save merged data
            with open(cache_file, 'w') as f:
                json.dump(self.memory_cache, f, indent=2)

            self.logger.info(f"Saved {len(self.memory_cache)} colors to cache file")
            return True

        except Exception as e:
            self.logger.error(f"Error saving color cache file: {e}")
            return False
        finally:
            self._release_lock()

    def get_color_info(self, image_path: str, aoi_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached color information for an AOI.

        Checks both new (portable) and legacy cache keys for backward compatibility.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary

        Returns:
            Dict with 'rgb', 'hex', 'hue_degrees' keys, or None if not cached
        """
        # Load cache file on first access
        if not self._cache_loaded and self.cache_dir:
            self.load_cache_file()

        # Try new (portable) cache key first
        cache_key = self.get_cache_key(image_path, aoi_data)
        color_info = self.memory_cache.get(cache_key)

        # If not found, try legacy key (for backward compatibility with old caches)
        if color_info is None:
            xml_path = aoi_data.get('_xml_path')  # Extract original XML path if provided
            legacy_key = self.get_legacy_cache_key(image_path, aoi_data, xml_path)
            if legacy_key != cache_key:  # Only try if different
                color_info = self.memory_cache.get(legacy_key)

        return color_info

    def save_color_info(self, image_path: str, aoi_data: Dict[str, Any],
                       color_info: Dict[str, Any]) -> bool:
        """
        Save color information for an AOI to cache.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary
            color_info: Dict with 'rgb', 'hex', 'hue_degrees' keys

        Returns:
            True if saved successfully
        """
        try:
            cache_key = self.get_cache_key(image_path, aoi_data)

            # Validate color info structure
            required_keys = ['rgb', 'hex', 'hue_degrees']
            if not all(key in color_info for key in required_keys):
                self.logger.warning(f"Invalid color info structure, missing required keys")
                return False

            # Add to memory cache
            self.memory_cache[cache_key] = color_info

            return True

        except Exception as e:
            self.logger.error(f"Error saving color info to cache: {e}")
            return False

    def bulk_save_colors(self, colors: Dict[str, Dict[str, Any]]) -> bool:
        """
        Bulk save multiple color entries (for batch processing).

        Args:
            colors: Dict of {cache_key: color_info}

        Returns:
            True if saved successfully
        """
        try:
            self.memory_cache.update(colors)
            self.logger.info(f"Added {len(colors)} colors to cache")
            return True

        except Exception as e:
            self.logger.error(f"Error in bulk save: {e}")
            return False

    def clear_cache(self):
        """Clear the in-memory cache."""
        self.memory_cache.clear()
        self._cache_loaded = False
        self.logger.info("Color cache cleared from memory")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        cache_file = self.get_cache_file_path()

        stats = {
            'memory_count': len(self.memory_cache),
            'cache_dir': str(self.cache_dir) if self.cache_dir else None,
            'file_exists': cache_file.exists() if cache_file else False,
            'loaded': self._cache_loaded
        }

        if cache_file and cache_file.exists():
            stats['file_size_bytes'] = cache_file.stat().st_size
            stats['file_size_kb'] = round(cache_file.stat().st_size / 1024, 2)

        return stats
