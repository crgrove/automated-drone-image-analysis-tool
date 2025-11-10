"""
ThumbnailController - Handles thumbnail management for the image viewer.

This controller manages thumbnail loading, display, scrolling, and interaction
functionality with non-blocking lazy loading.
"""

import math
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QIcon

from core.controllers.images.viewer.thumbnails.ThumbnailLoader import ThumbnailLoader
from core.services.LoggerService import LoggerService


class ThumbnailController(QObject):
    """
    Controller for managing thumbnail functionality.

    Handles thumbnail creation, loading, scrolling, and interaction
    with non-blocking lazy loading for better performance.
    """

    # Signal to request thumbnail loading
    load_thumbnail_signal = Signal(int)

    def __init__(self, parent_viewer):
        """
        Initialize the thumbnail controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        super().__init__()
        self.parent = parent_viewer
        self.logger = LoggerService()  # Create our own logger

        # Create UI component internally
        from core.controllers.images.viewer.thumbnails.ThumbnailUIComponent import ThumbnailUIComponent
        self.ui_component = ThumbnailUIComponent(self)

        # Background loading
        self.loader_thread = None
        self.loader = None

        # Alternative cache directory (set by viewer if user provides one)
        self.alternative_cache_dir = None

        # Loading queue management
        self.pending_indices = set()
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self._process_next_thumbnail)
        self.load_timer.setSingleShot(True)


    def initialize_thumbnails_deferred(self):
        """Initialize thumbnail widgets immediately, load images in background."""
        # Delegate UI initialization to UI component
        if self.ui_component:
            self.ui_component.initialize_thumbnails()

        # Start background loader
        self._start_background_loader()

        # Load initial visible thumbnails
        self._request_visible_thumbnails()


    def _start_background_loader(self):
        """Start the background thumbnail loader."""
        if self.loader_thread is not None:
            return

        # Get results directory - prefer alternative cache dir if provided
        results_dir = None
        if self.alternative_cache_dir:
            results_dir = self.alternative_cache_dir
        elif hasattr(self.parent, 'xml_path') and self.parent.xml_path:
            import os
            results_dir = os.path.dirname(self.parent.xml_path)

        # Determine input root (for relative-path hashing)
        input_root = None
        try:
            if hasattr(self.parent, 'settings') and isinstance(self.parent.settings, dict):
                input_root = self.parent.settings.get('input_dir')
            if not input_root and hasattr(self.parent, 'xml_service') and self.parent.xml_service:
                settings, _ = self.parent.xml_service.get_settings()
                input_root = settings.get('input_dir') if isinstance(settings, dict) else None
        except Exception:
            input_root = None

        self.loader_thread = QThread()
        self.loader = ThumbnailLoader(self.parent.images, results_dir=results_dir, input_root=input_root)
        self.loader.moveToThread(self.loader_thread)

        # Connect signals with queued connection to ensure UI updates on main thread
        self.loader.thumbnail_loaded.connect(self.on_thumbnail_loaded, Qt.QueuedConnection)
        self.load_thumbnail_signal.connect(self.loader.load_thumbnail, Qt.QueuedConnection)

        self.loader_thread.start()

    def _request_visible_thumbnails(self):
        """Request thumbnails for currently visible range."""
        if not self.loader or not self.ui_component:
            return

        # Get visible range from UI component
        start_index, end_index = self.ui_component.get_visible_thumbnail_range()

        # Queue range for loading
        for i in range(start_index, end_index):
            self._request_thumbnail(i)

    def on_thumbnail_loaded(self, index, icon):
        """Handle thumbnail loaded from background thread."""
        if self.ui_component:
            self.ui_component.on_thumbnail_loaded(index, icon)

    def on_thumbnail_scroll(self):
        """Load thumbnails when user scrolls."""
        self._request_visible_thumbnails()

    def on_thumbnail_clicked(self, button, checked=False):
        """Handle thumbnail click."""
        index = button.property('imageIndex')
        self.parent.current_image = index
        
        # Delegate UI updates to UI component
        if self.ui_component:
            self.ui_component.set_active_index(index)
            
        self.parent._load_image()



    def set_active_index(self, index):
        """Set active thumbnail by index."""
        try:
            index = int(index)
        except (TypeError, ValueError):
            return

        # Delegate UI updates to UI component
        if self.ui_component:
            self.ui_component.set_active_index(index)
            
        # Request this thumbnail to be loaded
        self._request_thumbnail(index)

    def update_thumbnail_overlay(self, image_index, is_hidden):
        """Update overlay for hidden state."""
        if self.ui_component:
            self.ui_component.update_thumbnail_overlay(image_index, is_hidden)

    def cleanup(self):
        """Clean up resources."""
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait()

        # Delegate UI cleanup to UI component
        if self.ui_component:
            self.ui_component.cleanup()

    def _request_thumbnail(self, index):
        """Request a thumbnail to be loaded, or load immediately if cached."""
        if not self.loader or index in self.pending_indices or index in self.loader.loaded_indices:
            return
        if index < 0 or index >= len(self.parent.images):
            return

        # Check if thumbnail is cached - if so, load it immediately (fast)
        image_path = self.parent.images[index].get('path', '')
        if image_path and self.loader.is_cached(image_path):
            try:
                # Load from cache on main thread (safe - just reading a cached file)
                cached_pixmap = self.loader._load_cached_thumbnail(image_path)
                if cached_pixmap:
                    icon = QIcon(cached_pixmap)
                    self.loader.loaded_indices.add(index)
                    # Notify UI component directly
                    if self.ui_component:
                        self.ui_component.on_thumbnail_loaded(index, icon)
                    return  # Don't queue it
            except Exception as e:
                # If loading from cache failed, fall through to background loading
                self.logger.error(f"Error loading cached thumbnail: {e}")

        # Not cached - queue for background loading
        self.pending_indices.add(index)
        if not self.load_timer.isActive():
            self.load_timer.start(1)  # Start processing immediately

    def _process_next_thumbnail(self):
        """Process next thumbnail in queue."""
        if not self.pending_indices or not self.loader:
            return

        # Get next index and remove from pending
        index = min(self.pending_indices)
        self.pending_indices.remove(index)

        # Request loader to process this thumbnail using signal
        self.load_thumbnail_signal.emit(index)

        # Continue with next if more pending
        if self.pending_indices:
            self.load_timer.start(10)  # Small delay between thumbnails
