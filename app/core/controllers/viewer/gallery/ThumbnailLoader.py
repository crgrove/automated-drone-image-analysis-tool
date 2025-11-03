"""
ThumbnailLoader - Background thumbnail loading for gallery view.

This module handles asynchronous thumbnail generation using a thread pool
to keep the UI responsive while loading thousands of thumbnails.
"""

from typing import Dict, List, Set, Tuple, Optional
from PySide6.QtCore import QObject, Signal, QThreadPool, QTimer
from PySide6.QtGui import QIcon

from core.services.ThumbnailCacheService import ThumbnailCacheService, ThumbnailWorker
from core.services.LoggerService import LoggerService


class ThumbnailLoader(QObject):
    """
    Manages background thumbnail loading using thread pool.

    Emits signals when thumbnails are ready for UI updates.
    """

    # Signal emitted when a thumbnail is ready
    thumbnail_ready = Signal(int, int, QIcon)  # image_idx, aoi_idx, icon

    # Signal emitted when a batch is complete
    batch_complete = Signal(int)  # number of thumbnails loaded

    def __init__(self, parent=None, max_workers: int = 4, dataset_cache_dir: Optional[str] = None):
        """
        Initialize the thumbnail loader.

        Args:
            parent: Parent QObject
            max_workers: Maximum number of worker threads
            dataset_cache_dir: Per-dataset cache directory (optional)
        """
        super().__init__(parent)
        self.logger = LoggerService()

        # Thread pool for background loading
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_workers)

        # Cache service with per-dataset cache support
        self.cache_service = ThumbnailCacheService(dataset_cache_dir=dataset_cache_dir)

        # Track pending loads
        self.pending_loads: List[Tuple[int, int, str, Dict]] = []
        self.loading_set: Set[Tuple[int, int]] = set()

        # Priority queue for visible items
        self.high_priority_queue: List[Tuple[int, int, str, Dict]] = []

        # Batch processing timer
        self.batch_timer = QTimer()
        self.batch_timer.timeout.connect(self._process_batch)
        self.batch_timer.setInterval(20)  # Process batch every 20ms

        # Statistics
        self.total_loaded = 0
        self.total_pending = 0

    def queue_thumbnail(self, image_idx: int, aoi_idx: int,
                       image_path: str, aoi_data: Dict,
                       xml_path: str = None,
                       high_priority: bool = False):
        """
        Queue a thumbnail for background loading, or load immediately if cached.

        Args:
            image_idx: Index of the image
            aoi_idx: Index of the AOI within the image
            image_path: Path to the source image (current location)
            aoi_data: AOI dictionary
            xml_path: Original path from XML (for legacy cache lookups)
            high_priority: Whether this is high priority (visible)
        """
        key = (image_idx, aoi_idx)

        # Store xml_path in aoi_data temporarily for cache lookups
        aoi_data_with_xml = aoi_data.copy()
        if xml_path:
            aoi_data_with_xml['_xml_path'] = xml_path

        # Skip if already loading (being processed by a worker thread)
        if key in self.loading_set:
            return

        # Check if already in queue
        in_queue = any(item[0] == image_idx and item[1] == aoi_idx 
                      for item in self.high_priority_queue + self.pending_loads)
        if in_queue:
            # If already in queue and this is high priority, promote it to high priority queue
            if high_priority:
                # Remove from normal queue if present
                self.pending_loads = [item for item in self.pending_loads 
                                     if not (item[0] == image_idx and item[1] == aoi_idx)]
                # Add to high priority if not already there
                if not any(item[0] == image_idx and item[1] == aoi_idx 
                          for item in self.high_priority_queue):
                    item = (image_idx, aoi_idx, image_path, aoi_data_with_xml)
                    self.high_priority_queue.append(item)
            return

        # Check if thumbnail is already cached - if so, load it immediately
        if self.cache_service.is_cached(image_path, aoi_data_with_xml):
            try:
                # Load from cache synchronously (fast - just reads from disk)
                icon = self.cache_service.get_thumbnail(image_path, aoi_data_with_xml)
                if icon:
                    # Emit signal immediately
                    self.thumbnail_ready.emit(image_idx, aoi_idx, icon)
                    self.total_loaded += 1
                    return  # Don't queue it
            except Exception as e:
                # If loading from cache failed, fall through to queue for generation
                self.logger.error(f"Error loading cached thumbnail: {e}")

        # Not cached - add to background generation queue
        self.loading_set.add(key)

        # Add to appropriate queue (store aoi_data with xml_path)
        item = (image_idx, aoi_idx, image_path, aoi_data_with_xml)

        if high_priority:
            self.high_priority_queue.append(item)
        else:
            self.pending_loads.append(item)

        self.total_pending += 1

        # Start batch timer if not running
        if not self.batch_timer.isActive():
            self.batch_timer.start()

    def _process_batch(self):
        """Process a batch of thumbnail loads."""
        batch_size = 10  # Process 10 thumbnails per batch
        processed = 0

        # Process high priority first
        while self.high_priority_queue and processed < batch_size:
            item = self.high_priority_queue.pop(0)
            self._start_load(*item)
            processed += 1

        # Then process normal priority
        while self.pending_loads and processed < batch_size:
            item = self.pending_loads.pop(0)
            self._start_load(*item)
            processed += 1

        # Stop timer if no more pending
        if not self.high_priority_queue and not self.pending_loads:
            self.batch_timer.stop()

    def _start_load(self, image_idx: int, aoi_idx: int,
                   image_path: str, aoi_data: Dict):
        """Start loading a single thumbnail."""
        try:
            # Create worker with callback
            def on_complete(cache_key: str, icon: Optional[QIcon]):
                if icon:
                    self.thumbnail_ready.emit(image_idx, aoi_idx, icon)
                    self.total_loaded += 1

                    # Emit batch complete every 20 thumbnails
                    if self.total_loaded % 20 == 0:
                        self.batch_complete.emit(self.total_loaded)

                # Remove from loading set
                self.loading_set.discard((image_idx, aoi_idx))

            worker = ThumbnailWorker(
                self.cache_service,
                image_path,
                aoi_data,
                callback=on_complete
            )

            # Start worker
            self.thread_pool.start(worker)

        except Exception as e:
            self.logger.error(f"Error starting thumbnail load: {e}")
            self.loading_set.discard((image_idx, aoi_idx))

    def set_dataset_cache_dir(self, dataset_cache_dir: Optional[str]):
        """
        Update the dataset cache directory.

        Args:
            dataset_cache_dir: Per-dataset cache directory path
        """
        # Recreate cache service with new dataset cache directory
        self.cache_service = ThumbnailCacheService(dataset_cache_dir=dataset_cache_dir)
        self.logger.info(f"Updated thumbnail cache to use dataset directory: {dataset_cache_dir}")

    def clear_queue(self):
        """Clear all pending loads."""
        self.pending_loads.clear()
        self.high_priority_queue.clear()
        self.loading_set.clear()  # Also clear loading set so items can be re-queued
        self.batch_timer.stop()

    def reprioritize_visible(self, visible_items: List[Tuple[int, int, str, Dict]]):
        """
        Reprioritize loading for visible items.

        Args:
            visible_items: List of (image_idx, aoi_idx, image_path, aoi_data) tuples
        """
        # Move visible items to high priority queue
        for item in visible_items:
            image_idx, aoi_idx = item[0], item[1]
            key = (image_idx, aoi_idx)

            # Skip if already loading
            if key in self.loading_set:
                continue

            # Remove from normal queue if present
            if item in self.pending_loads:
                self.pending_loads.remove(item)

            # Add to high priority
            if item not in self.high_priority_queue:
                self.high_priority_queue.append(item)

    def get_stats(self) -> Dict:
        """Get loader statistics."""
        return {
            'total_loaded': self.total_loaded,
            'pending': len(self.pending_loads) + len(self.high_priority_queue),
            'loading': len(self.loading_set),
            'cache_stats': self.cache_service.get_cache_stats()
        }

    def shutdown(self):
        """Shutdown the loader and wait for threads."""
        self.clear_queue()
        self.thread_pool.waitForDone(1000)  # Wait max 1 second