"""
TemperatureCacheService - Manages persistent caching of AOI temperature information.

This service provides:
- Per-dataset JSON storage of temperature information (in Celsius)
- Fast lookup during gallery rendering and filtering
- Fallback to XML data for backwards compatibility
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Any
from core.services.LoggerService import LoggerService


class TemperatureCacheService:
    """
    Service for caching AOI temperature information to disk.

    Temperature is stored in Celsius for consistency.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the temperature cache service.

        Args:
            cache_dir: Directory for temperature cache (default: per-dataset .temperature_cache/)
        """
        self.logger = LoggerService()
        self.cache_dir = Path(cache_dir) if cache_dir else None

        # In-memory cache: {cache_key: temperature_celsius}
        self.memory_cache: Dict[str, Optional[float]] = {}

        # Flag to track if cache file has been loaded
        self._cache_loaded = False

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Temperature cache initialized at {self.cache_dir}")

    def get_cache_key(self, image_path: str, aoi_data: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for an AOI.

        Uses only the filename and AOI coordinates to make caches fully portable
        across machines and time.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary with center and radius

        Returns:
            MD5 hash cache key
        """
        try:
            import os

            # Use only the filename to make cache portable across machines
            filename = os.path.basename(image_path)

            # Create unique identifier from filename, center, radius
            center = aoi_data.get('center', (0, 0))
            radius = aoi_data.get('radius', 0)

            identifier = f"{filename}_{center[0]}_{center[1]}_{radius}"

            # Generate hash
            return hashlib.md5(identifier.encode()).hexdigest()

        except Exception as e:
            self.logger.error(f"Error generating cache key: {e}")
            # Fallback to simple hash
            return hashlib.md5(str(aoi_data).encode()).hexdigest()

    def get_cache_file_path(self) -> Optional[Path]:
        """Get the path to the cache JSON file."""
        if not self.cache_dir:
            return None
        return self.cache_dir / "temperatures.json"

    def get_lock_file_path(self) -> Optional[Path]:
        """Get the path to the lock file."""
        if not self.cache_dir:
            return None
        return self.cache_dir / "temperatures.json.lock"

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
        Load all cached temperature information from disk into memory.

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
                self.logger.info(f"Loaded {len(self.memory_cache)} cached temperatures from disk")
                return True

        except Exception as e:
            self.logger.error(f"Error loading temperature cache file: {e}")
            return False
        finally:
            self._release_lock()

    def save_cache_file(self) -> bool:
        """
        Save all cached temperature information from memory to disk.

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

            self.logger.info(f"Saved {len(self.memory_cache)} temperatures to cache file")
            return True

        except Exception as e:
            self.logger.error(f"Error saving temperature cache file: {e}")
            return False
        finally:
            self._release_lock()

    def get_temperature(self, image_path: str, aoi_data: Dict[str, Any]) -> Optional[float]:
        """
        Get cached temperature for an AOI (in Celsius).

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary

        Returns:
            Temperature in Celsius, or None if not cached
        """
        # Load cache file on first access
        if not self._cache_loaded and self.cache_dir:
            self.load_cache_file()

        cache_key = self.get_cache_key(image_path, aoi_data)
        return self.memory_cache.get(cache_key)

    def save_temperature(self, image_path: str, aoi_data: Dict[str, Any],
                         temperature: float) -> bool:
        """
        Save temperature for an AOI to cache (in Celsius).

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary
            temperature: Temperature in Celsius

        Returns:
            True if saved successfully
        """
        try:
            cache_key = self.get_cache_key(image_path, aoi_data)

            # Add to memory cache
            self.memory_cache[cache_key] = float(temperature)

            return True

        except Exception as e:
            self.logger.error(f"Error saving temperature to cache: {e}")
            return False

    def bulk_save_temperatures(self, temperatures: Dict[str, float]) -> bool:
        """
        Bulk save multiple temperature entries (for batch processing).

        Args:
            temperatures: Dict of {cache_key: temperature_celsius}

        Returns:
            True if saved successfully
        """
        try:
            self.memory_cache.update(temperatures)
            self.logger.info(f"Added {len(temperatures)} temperatures to cache")
            return True

        except Exception as e:
            self.logger.error(f"Error in bulk save: {e}")
            return False

    def clear_cache(self):
        """Clear the in-memory cache."""
        self.memory_cache.clear()
        self._cache_loaded = False
        self.logger.info("Temperature cache cleared from memory")

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
