"""
ThumbnailController - Handles thumbnail management for the image viewer.

This controller manages thumbnail loading, display, scrolling, and interaction
functionality with non-blocking lazy loading.
"""

import math
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize, QThread, QTimer, Signal
from PySide6.QtGui import QIcon

from core.controllers.viewer.thumbnails.ThumbnailLoader import ThumbnailLoader
from core.services.LoggerService import LoggerService


class ThumbnailController:
    """
    Controller for managing thumbnail functionality.
    
    Handles thumbnail creation, loading, scrolling, and interaction
    with non-blocking lazy loading for better performance.
    """
    
    def __init__(self, parent_viewer, logger=None):
        """
        Initialize the thumbnail controller.
        
        Args:
            parent_viewer: The main Viewer instance
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_viewer
        self.logger = logger or LoggerService()
        
        # Thumbnail state
        self.active_thumbnail = None
        self.active_index = None
        
        # Thumbnail configuration
        self.thumbnail_size = (122, 78)
        
        # Background loading
        self.loader_thread = None
        self.loader = None
        
        # Loading queue management
        self.pending_indices = set()
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self._process_next_thumbnail)
        self.load_timer.setSingleShot(True)
        
        # UI elements (will be set by parent)
        self.thumbnailLayout = None
        self.thumbnailScrollArea = None
    
    def set_ui_elements(self, thumbnail_layout, thumbnail_scroll_area):
        """Set references to UI elements.
        
        Args:
            thumbnail_layout: The QLayout for thumbnail widgets
            thumbnail_scroll_area: The QScrollArea containing thumbnails
        """
        self.thumbnailLayout = thumbnail_layout
        self.thumbnailScrollArea = thumbnail_scroll_area
    
    def initialize_thumbnails_deferred(self):
        """Initialize thumbnail widgets immediately, load images in background."""
        if not self.thumbnailLayout:
            return
            
        self.thumbnailLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.thumbnailLayout.setSpacing(5)

        # Create all thumbnail widgets immediately (no images yet)
        for index in range(len(self.parent.images)):
            self._create_thumbnail_widget(index)
        
        # Start background loader
        self._start_background_loader()
        
        # Load initial visible thumbnails
        self._request_visible_thumbnails()
    
    def _create_thumbnail_widget(self, index):
        """Create a thumbnail widget for the given index."""
        image = self.parent.images[index]
        
        frame = QFrame()
        button = QPushButton()
        button.setFixedSize(QSize(100, 56))
        button.setProperty('imageIndex', index)
        button.setProperty('frame', frame)
        
        # Connect click handler
        from functools import partial
        button.clicked.connect(partial(self.on_thumbnail_clicked, button))
        
        layout = QVBoxLayout(frame)
        layout.addWidget(button)
        layout.setAlignment(Qt.AlignCenter)
        frame.setLayout(layout)
        frame.setFixedSize(QSize(*self.thumbnail_size))
        frame.setStyleSheet("border: 1px solid grey; border-radius: 3px;")
        
        overlay = QLabel(frame)
        overlay.setFixedSize(frame.width(), frame.height())
        overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        overlay.move(0, 0)
        overlay.show()
        button.setProperty('overlay', overlay)
        
        self.thumbnailLayout.addWidget(frame)
        image['thumbnail'] = button
    
    def _start_background_loader(self):
        """Start the background thumbnail loader."""
        if self.loader_thread is not None:
            return
            
        self.loader_thread = QThread()
        self.loader = ThumbnailLoader(self.parent.images)
        self.loader.moveToThread(self.loader_thread)
        
        # Connect signals
        self.loader.thumbnail_loaded.connect(self.on_thumbnail_loaded)
        
        self.loader_thread.start()
    
    def _request_visible_thumbnails(self):
        """Request thumbnails for currently visible range."""
        if not self.thumbnailScrollArea or not self.loader:
            return
            
        # Calculate visible range
        area = self.thumbnailScrollArea
        bar = area.horizontalScrollBar()
        
        spacing = self.thumbnailLayout.spacing() if self.thumbnailLayout else 0
        slot_width = max(1, self.thumbnail_size[0] + spacing)
        viewport_width = area.viewport().width() if area.viewport() else 0
        
        start_index = max(0, int(bar.value() // slot_width))
        visible_count = max(1, math.ceil(viewport_width / slot_width) + 10)  # Buffer
        end_index = min(len(self.parent.images), start_index + visible_count)
        
        # Queue range for loading
        for i in range(start_index, end_index):
            self._request_thumbnail(i)
    
    def on_thumbnail_loaded(self, index, icon):
        """Handle thumbnail loaded from background thread."""
        if index >= len(self.parent.images):
            return
            
        image = self.parent.images[index]
        if 'thumbnail' not in image:
            return
            
        try:
            button = image['thumbnail']
            button.setIcon(icon)
            button.setIconSize(QSize(100, 56))
            
            # Apply overlay if hidden
            if image.get('hidden', False):
                overlay = button.property('overlay')
                if overlay:
                    try:
                        overlay.setStyleSheet("background-color: rgba(128, 128, 128, 150);")
                    except RuntimeError:
                        pass  # Widget was deleted
            
            # Apply active style if this is the active thumbnail
            if self.active_index == index:
                self.set_active_thumbnail(button)
        except RuntimeError:
            # Widget was deleted, skip
            pass
    
    def on_thumbnail_scroll(self):
        """Load thumbnails when user scrolls."""
        self._request_visible_thumbnails()
    
    def on_thumbnail_clicked(self, button, checked=False):
        """Handle thumbnail click."""
        index = button.property('imageIndex')
        self.parent.current_image = index
        self.active_index = index
        self.parent._load_image()
    
    def scroll_thumbnail_into_view(self):
        """Ensure active thumbnail is visible."""
        if not self.active_thumbnail or not self.thumbnailScrollArea:
            return
            
        area = self.thumbnailScrollArea
        # Center the active thumbnail
        x_margin = max(0, area.viewport().width() // 2)
        area.ensureWidgetVisible(self.active_thumbnail, x_margin, 0)
        
        # Request thumbnails for new visible area
        self._request_visible_thumbnails()
    
    def set_active_thumbnail(self, button):
        """Set the active thumbnail and update styling."""
        if not button:
            return
            
        try:
            frame = button.property('frame')
            if not frame:
                return
                
            # Clear previous active style safely
            if self.active_thumbnail:
                try:
                    self.active_thumbnail.setStyleSheet("border: 1px solid grey; border-radius: 3px;")
                except RuntimeError:
                    pass  # Widget was deleted
            
            # Set new active style safely
            try:
                frame.setStyleSheet("QFrame { border: 2px solid blue; border-radius: 3px; }")
                self.active_thumbnail = frame
            except RuntimeError:
                return  # Widget was deleted
            
            # Update active index
            try:
                self.active_index = int(button.property('imageIndex'))
            except (TypeError, ValueError):
                self.active_index = None
            
            # Ensure it's visible
            self.scroll_thumbnail_into_view()
        except Exception:
            # Catch any other UI access errors
            pass
    
    def set_active_index(self, index):
        """Set active thumbnail by index."""
        try:
            index = int(index)
            self.active_index = index
        except (TypeError, ValueError):
            return
            
        if 0 <= index < len(self.parent.images):
            image = self.parent.images[index]
            if 'thumbnail' in image:
                self.set_active_thumbnail(image['thumbnail'])
                return
        
        # If thumbnail widget doesn't exist yet, just store index
        self.active_thumbnail = None
        # Request this thumbnail to be loaded
        self._request_thumbnail(index)
    
    def update_thumbnail_overlay(self, image_index, is_hidden):
        """Update overlay for hidden state."""
        if image_index >= len(self.parent.images):
            return
            
        image = self.parent.images[image_index]
        if 'thumbnail' not in image:
            return
            
        button = image['thumbnail']
        overlay = button.property('overlay')
        if not overlay:
            return
            
        if is_hidden:
            overlay.setStyleSheet("background-color: rgba(128, 128, 128, 150);")
        else:
            overlay.setStyleSheet("background-color: none;")
    
    def cleanup(self):
        """Clean up resources."""
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait()
        
        self.active_thumbnail = None
        self.active_index = None
    
    def _request_thumbnail(self, index):
        """Request a thumbnail to be loaded."""
        if not self.loader or index in self.pending_indices or index in self.loader.loaded_indices:
            return
        if index < 0 or index >= len(self.parent.images):
            return
            
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
        
        # Request loader to process this thumbnail
        self.loader.load_thumbnail(index)
        
        # Continue with next if more pending
        if self.pending_indices:
            self.load_timer.start(10)  # Small delay between thumbnails