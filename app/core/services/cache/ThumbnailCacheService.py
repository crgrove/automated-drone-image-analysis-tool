"""
ThumbnailCacheService - Manages persistent caching of AOI thumbnails for performance.

This service handles:
- Persistent disk caching of thumbnails
- In-memory LRU cache for fast access
- Background thumbnail generation
- Smart extraction without loading full images
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image
import io
import shutil

from PySide6.QtCore import QThread, Signal, QObject, QMutex, QMutexLocker, QThreadPool, QRunnable
from PySide6.QtGui import QPixmap, QIcon, QImage
import qimage2ndarray

from core.services.LoggerService import LoggerService


class ThumbnailCacheService:
    """
    Service for managing thumbnail caching with persistent storage.

    Features:
    - Persistent disk cache in user's home directory
    - LRU memory cache for fast access
    - Smart region extraction without loading full images
    - Thread-safe operations
    """

    def __init__(self, cache_dir: Optional[str] = None, max_memory_cache: int = 4000, dataset_cache_dir: Optional[str] = None):
        """
        Initialize the thumbnail cache service.

        Args:
            cache_dir: Optional global cache directory (if None, only per-dataset cache is used)
            max_memory_cache: Maximum items in memory cache
            dataset_cache_dir: Per-dataset cache directory (optional, checked first)
        """
        self.logger = LoggerService()

        # Set up global cache directory (only if explicitly provided)
        # If not provided, we only use per-dataset cache
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Thumbnail cache initialized at {self.cache_dir}")

        # Set up per-dataset cache directory (optional)
        self.dataset_cache_dir = Path(dataset_cache_dir) if dataset_cache_dir else None
        if self.dataset_cache_dir:
            self.dataset_cache_dir.mkdir(parents=True, exist_ok=True)

        # Thread safety
        self.mutex = QMutex()

        # Memory cache size
        self.max_memory_cache = max_memory_cache

        # Clear the LRU cache to set max size
        self.get_thumbnail_from_memory.cache_clear()

    def get_cache_key(self, image_path: str, aoi_data: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for a thumbnail.

        Uses only the filename and AOI coordinates to make caches fully portable
        across machines and time. Modification time is NOT included so cached
        thumbnails remain valid when files are copied/moved.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary with center and radius

        Returns:
            Unique hash key for this thumbnail
        """
        # Use only the filename to make cache portable across machines
        # Drone images have unique filenames, so this is safe
        filename = os.path.basename(image_path)

        center = aoi_data.get('center', (0, 0))
        radius = aoi_data.get('radius', 50)

        # Create unique identifier using filename and AOI coordinates only
        # NOTE: mtime is intentionally NOT included to allow caches to work
        # when files are copied between machines (which changes mtime)
        identifier = f"{filename}:{center[0]}:{center[1]}:{radius}"

        # Generate hash
        return hashlib.md5(identifier.encode()).hexdigest()

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
            Unique hash key using old formula
        """

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

        try:
            mtime = os.path.getmtime(image_path)
        except Exception:
            mtime = 0

        center = aoi_data.get('center', (0, 0))
        radius = aoi_data.get('radius', 50)

        # OLD identifier format
        identifier = f"{cache_path}:{mtime}:{center[0]}:{center[1]}:{radius}"

        return hashlib.md5(identifier.encode()).hexdigest()

    def get_cache_path(self, cache_key: str, cache_dir: Optional[Path] = None) -> Path:
        """
        Get the disk cache path for a cache key.

        Args:
            cache_key: Cache key hash
            cache_dir: Optional override cache directory (defaults to self.cache_dir)

        Returns:
            Path to cache file
        """
        # Use specified directory or dataset cache (no global cache fallback)
        if cache_dir:
            base_dir = cache_dir
        elif self.dataset_cache_dir:
            base_dir = self.dataset_cache_dir
        elif self.cache_dir:
            base_dir = self.cache_dir
        else:
            raise ValueError("No cache directory available")

        # Use flat directory structure for all thumbnails (main images and AOIs)
        # No subdirectories needed - modern file systems handle thousands of files efficiently
        base_dir.mkdir(exist_ok=True, parents=True)
        return base_dir / f"{cache_key}.jpg"

    def extract_aoi_region_fast(self, image_path: str, aoi_data: Dict[str, Any],
                                target_size: Tuple[int, int] = (180, 180)) -> Optional[np.ndarray]:
        """
        Extract AOI region from image WITHOUT loading the entire image into memory.

        This uses PIL's lazy loading to only read the required region.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary with center and radius
            target_size: Target thumbnail size

        Returns:
            Numpy array of the thumbnail or None
        """
        try:
            center = aoi_data.get('center')
            radius = aoi_data.get('radius', 50)

            if not center:
                return None

            cx, cy = center
            crop_radius = radius + 10  # Add padding

            # Calculate crop bounds
            x1 = int(cx - crop_radius)
            y1 = int(cy - crop_radius)
            x2 = int(cx + crop_radius)
            y2 = int(cy + crop_radius)

            # Use PIL for efficient region extraction
            with Image.open(image_path) as img:
                # PIL doesn't load the entire image until needed
                width, height = img.size

                # Clamp to image bounds
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)

                # Crop the region (PIL only loads this portion)
                cropped = img.crop((x1, y1, x2, y2))

                # Convert to RGB if needed
                if cropped.mode != 'RGB':
                    cropped = cropped.convert('RGB')

                # Resize to target size
                cropped = cropped.resize(target_size, Image.Resampling.LANCZOS)

                # Convert to numpy array
                return np.array(cropped)

        except Exception as e:
            self.logger.error(f"Error extracting AOI region: {e}")
            return None

    @lru_cache(maxsize=4000)
    def get_thumbnail_from_memory(self, cache_key: str) -> Optional[QIcon]:
        """
        Get thumbnail from memory cache.

        This is an LRU cache that automatically evicts least recently used items.

        Args:
            cache_key: Unique cache key

        Returns:
            QIcon or None
        """
        # This method is just for the LRU decorator
        # Actual loading happens in get_thumbnail
        return None

    def save_thumbnail_to_disk(self, cache_key: str, thumbnail_array: np.ndarray, cache_dir: Optional[Path] = None) -> bool:
        """
        Save thumbnail to disk cache.

        Args:
            cache_key: Unique cache key
            thumbnail_array: Numpy array of thumbnail (RGB format)
            cache_dir: Optional override cache directory

        Returns:
            True if saved successfully
        """
        try:
            cache_path = self.get_cache_path(cache_key, cache_dir)

            # Convert RGB to BGR for cv2.imwrite (cv2 expects BGR format)
            if len(thumbnail_array.shape) == 3 and thumbnail_array.shape[2] == 3:
                thumbnail_bgr = cv2.cvtColor(thumbnail_array, cv2.COLOR_RGB2BGR)
            else:
                thumbnail_bgr = thumbnail_array

            # Save as JPEG with balanced quality (80 = good balance of quality and speed)
            # Reduced from 90 for faster writes with minimal visual difference for thumbnails
            cv2.imwrite(str(cache_path), thumbnail_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])

            return True

        except Exception as e:
            self.logger.error(f"Error saving thumbnail to disk: {e}")
            return False

    def save_thumbnail_from_array(self, image_path: str, aoi_data: Dict[str, Any],
                                  thumbnail_array: np.ndarray, cache_dir: Optional[Path] = None) -> bool:
        """
        Save a pre-generated thumbnail array to disk cache.

        This is used during detection to save thumbnails that have already been extracted.

        Args:
            image_path: Path to source image
            aoi_data: AOI dictionary
            thumbnail_array: Pre-generated thumbnail as numpy array
            cache_dir: Optional cache directory (defaults to dataset_cache_dir if set)

        Returns:
            True if saved successfully
        """
        try:
            cache_key = self.get_cache_key(image_path, aoi_data)

            # Use dataset cache if available and no override specified
            target_dir = cache_dir if cache_dir else self.dataset_cache_dir

            return self.save_thumbnail_to_disk(cache_key, thumbnail_array, target_dir)

        except Exception as e:
            self.logger.error(f"Error saving thumbnail from array: {e}")
            return False

    def load_thumbnail_from_disk(self, cache_key: str) -> Optional[np.ndarray]:
        """
        Load thumbnail from disk cache.

        Checks in order:
        1. Per-dataset cache (if configured)
        2. Global cache

        Args:
            cache_key: Unique cache key

        Returns:
            Numpy array or None
        """
        try:
            # Try dataset cache first if available
            if self.dataset_cache_dir:
                dataset_cache_path = self.get_cache_path(cache_key, self.dataset_cache_dir)
                if dataset_cache_path.exists():
                    img = Image.open(dataset_cache_path)
                    return np.array(img)

            # Fall back to global cache (if available)
            if self.cache_dir:
                cache_path = self.get_cache_path(cache_key)
                if cache_path.exists():
                    with Image.open(cache_path) as img:
                        return np.array(img.convert('RGB'))

            return None

        except Exception as e:
            self.logger.error(f"Error loading thumbnail from disk: {e}")
            return None

    def is_cached(self, image_path: str, aoi_data: Dict[str, Any]) -> bool:
        """
        Check if a thumbnail is already cached (memory or disk) without loading it.

        Checks both new (portable) and legacy cache keys for backward compatibility.

        Args:
            image_path: Path to source image
            aoi_data: AOI dictionary

        Returns:
            True if cached, False otherwise
        """
        # Try new (portable) cache key first
        cache_key = self.get_cache_key(image_path, aoi_data)

        # Check memory cache
        cached_icon = self.get_thumbnail_from_memory(cache_key)
        if cached_icon is not None:
            return True

        # Check per-dataset cache
        if self.dataset_cache_dir:
            dataset_cache_path = Path(self.dataset_cache_dir) / f"{cache_key}.jpg"
            if dataset_cache_path.exists():
                return True

        # Check global cache (if available)
        if self.cache_dir:
            cache_path = self.get_cache_path(cache_key)
            if cache_path.exists():
                return True

        # Fallback: Try legacy cache key (for backward compatibility with old caches)
        xml_path = aoi_data.get('_xml_path')  # Extract original XML path if provided
        legacy_key = self.get_legacy_cache_key(image_path, aoi_data, xml_path)
        if legacy_key != cache_key:  # Only try if different
            # Check per-dataset cache with legacy key
            if self.dataset_cache_dir:
                legacy_dataset_path = Path(self.dataset_cache_dir) / f"{legacy_key}.jpg"
                if legacy_dataset_path.exists():
                    return True

            # Check global cache with legacy key (if available)
            if self.cache_dir:
                legacy_cache_path = self.get_cache_path(legacy_key)
                if legacy_cache_path.exists():
                    return True

        return False

    def get_thumbnail(self, image_path: str, aoi_data: Dict[str, Any],
                      target_size: Tuple[int, int] = (180, 180)) -> Optional[QIcon]:
        """
        Get thumbnail with multi-level caching.

        Checks in order:
        1. Memory cache (fastest)
        2. Disk cache with new key (fast)
        3. Disk cache with legacy key (backward compatibility)
        4. Generate new (slower)

        Args:
            image_path: Path to source image
            aoi_data: AOI dictionary
            target_size: Target thumbnail size

        Returns:
            QIcon or None
        """
        with QMutexLocker(self.mutex):
            cache_key = self.get_cache_key(image_path, aoi_data)

            # Check memory cache first
            cached_icon = self.get_thumbnail_from_memory(cache_key)
            if cached_icon is not None:
                return cached_icon

            # Check disk cache with new (portable) key
            thumbnail_array = self.load_thumbnail_from_disk(cache_key)

            # If not found, try legacy key (for backward compatibility with old caches)
            if thumbnail_array is None:
                xml_path = aoi_data.get('_xml_path')  # Extract original XML path if provided
                legacy_key = self.get_legacy_cache_key(image_path, aoi_data, xml_path)
                if legacy_key != cache_key:  # Only try if different
                    thumbnail_array = self.load_thumbnail_from_disk(legacy_key)

            if thumbnail_array is None:
                # Generate new thumbnail
                thumbnail_array = self.extract_aoi_region_fast(image_path, aoi_data, target_size)

                if thumbnail_array is None:
                    return None

                # Save to disk cache with new key (prefer dataset cache)
                target_cache_dir = self.dataset_cache_dir if self.dataset_cache_dir else self.cache_dir
                if target_cache_dir:
                    self.save_thumbnail_to_disk(cache_key, thumbnail_array, target_cache_dir)

            # Convert to QIcon
            qimage = qimage2ndarray.array2qimage(thumbnail_array, normalize=False)
            pixmap = QPixmap.fromImage(qimage)
            icon = QIcon(pixmap)

            # Update memory cache (replace the None placeholder)
            # We need to clear the specific cache entry and re-add it
            self.get_thumbnail_from_memory.cache_clear()
            self.get_thumbnail_from_memory.__wrapped__(self, cache_key)  # Call uncached version
            self.get_thumbnail_from_memory.cache_info()  # Refresh cache

            return icon

    def clear_disk_cache(self):
        """Clear all thumbnails from disk cache."""
        try:
            if self.cache_dir:
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            if self.dataset_cache_dir:
                shutil.rmtree(self.dataset_cache_dir)
                self.dataset_cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Disk cache cleared")
        except Exception as e:
            self.logger.error(f"Error clearing disk cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        # Count disk cache files
        disk_count = 0
        disk_size = 0
        if self.cache_dir:
            disk_count += sum(1 for _ in self.cache_dir.rglob("*.jpg"))
            disk_size += sum(f.stat().st_size for f in self.cache_dir.rglob("*.jpg"))
        if self.dataset_cache_dir:
            disk_count += sum(1 for _ in self.dataset_cache_dir.rglob("*.jpg"))
            disk_size += sum(f.stat().st_size for f in self.dataset_cache_dir.rglob("*.jpg"))

        # Get memory cache stats
        cache_info = self.get_thumbnail_from_memory.cache_info()

        return {
            'disk_count': disk_count,
            'disk_size_mb': disk_size / (1024 * 1024),
            'memory_hits': cache_info.hits,
            'memory_misses': cache_info.misses,
            'memory_current_size': cache_info.currsize,
            'memory_max_size': cache_info.maxsize
        }


class ThumbnailWorker(QRunnable):
    """
    Worker for generating thumbnails in background.
    """

    def __init__(self, cache_service: ThumbnailCacheService,
                 image_path: str, aoi_data: Dict[str, Any],
                 callback: callable = None):
        """
        Initialize thumbnail worker.

        Args:
            cache_service: The thumbnail cache service
            image_path: Path to source image
            aoi_data: AOI dictionary
            callback: Optional callback function(cache_key, icon)
        """
        super().__init__()
        self.cache_service = cache_service
        self.image_path = image_path
        self.aoi_data = aoi_data
        self.callback = callback

    def run(self):
        """Generate thumbnail in background."""
        try:
            icon = self.cache_service.get_thumbnail(
                self.image_path,
                self.aoi_data,
                target_size=(180, 180)
            )

            if self.callback:
                cache_key = self.cache_service.get_cache_key(self.image_path, self.aoi_data)
                self.callback(cache_key, icon)

        except Exception:
            # Don't crash the thread pool
            pass
