"""
ThumbnailController - Handles thumbnail management for the image viewer.

This controller manages thumbnail loading, display, scrolling, and interaction
functionality with deferred loading for performance.
"""

import math
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from core.controllers.viewer.thumbnails.ThumbnailLoader import ThumbnailLoader
from core.services.LoggerService import LoggerService


class ThumbnailController:
    """
    Controller for managing thumbnail functionality.
    
    Handles thumbnail creation, loading, scrolling, and interaction
    with deferred loading for better performance with large datasets.
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
        self.loaded_thumbnails = []
        self.visible_thumbnails_range = (0, 0)
        self.active_thumbnail = None
        
        # Thumbnail configuration
        self.thumbnail_limit = 30
        self.thumbnail_size = (122, 78)
        self.thumbnail_loader = None
        
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
        """Initialize only visible thumbnails first, defer the rest."""
        if not self.thumbnailLayout:
            return
            
        self.thumbnailLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.thumbnailLayout.setSpacing(5)

        # Only create widgets for the first batch of thumbnails
        initial_count = min(self.thumbnail_limit, len(self.parent.images))

        for index in range(initial_count):
            image = self.parent.images[index]
            frame = QFrame()
            button = QPushButton()
            button.setFixedSize(QSize(100, 56))
            button.setProperty('imageIndex', index)
            button.setProperty('frame', frame)
            button.clicked.connect(lambda: self.on_thumbnail_clicked(button))
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

        # Start loading thumbnail images for the initial batch
        self.load_thumbnails_in_range(0, initial_count)

        # Create remaining thumbnail widgets in smaller batches to avoid blocking
        if len(self.parent.images) > initial_count:
            self.create_remaining_thumbnails(initial_count)
    
    def create_remaining_thumbnails(self, start_index):
        """Create remaining thumbnail widgets."""
        # Check if viewer is still valid
        if not hasattr(self.parent, 'main_image') or self.parent.main_image is None:
            return

        for index in range(start_index, len(self.parent.images)):
            image = self.parent.images[index]
            # Skip if thumbnail already exists
            if 'thumbnail' in image:
                continue

            frame = QFrame()
            button = QPushButton()
            button.setFixedSize(QSize(100, 56))
            button.setProperty('imageIndex', index)
            button.setProperty('frame', frame)
            button.clicked.connect(lambda: self.on_thumbnail_clicked(button))
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

        # Load thumbnails for all remaining images
        self.load_thumbnails_in_range(start_index, len(self.parent.images))
    
    def load_thumbnails_in_range(self, start_index, end_index):
        """Loads thumbnails in the specified range asynchronously.

        Args:
            start_index (int): The starting index of thumbnails to load.
            end_index (int): The ending index of thumbnails to load.
        """
        self.thumbnail_loader = ThumbnailLoader(self.parent.images, start_index, end_index, self.loaded_thumbnails)
        from PySide6.QtCore import QThread
        thread = QThread()
        self.parent._threads.append((thread, self.thumbnail_loader))
        self.thumbnail_loader.moveToThread(thread)
        self.thumbnail_loader.thumbnail_loaded.connect(self.on_thumbnail_loaded)
        self.thumbnail_loader.finished.connect(self.on_thumbnail_load_finished)
        thread.started.connect(self.thumbnail_loader.run)
        thread.start()
    
    def on_thumbnail_loaded(self, index, icon):
        """Updates the thumbnail icon and overlay for the loaded thumbnail.

        Args:
            index (int): The index of the loaded thumbnail.
            icon (QIcon): The icon to display for the thumbnail.
        """
        # Safety checks: ensure index is valid and thumbnail button exists
        if index >= len(self.parent.images) or 'thumbnail' not in self.parent.images[index]:
            return
            
        button = self.parent.images[index]['thumbnail']
        button.setIcon(icon)
        button.setIconSize(QSize(100, 56))
        if self.parent.images[index].get('hidden'):
            overlay = button.property('overlay')
            overlay.setStyleSheet("background-color: rgba(128, 128, 128, 150);")

        self.loaded_thumbnails.append(index)
    
    def on_thumbnail_load_finished(self):
        """Stops and quits all thumbnail threads after loading is complete."""
        for thread, analyze in self.parent._threads:
            thread.quit()
    
    def on_thumbnail_scroll(self):
        """Loads thumbnails in the visible range when the user scrolls."""
        if not self.thumbnailScrollArea:
            return
            
        scrollbar = self.thumbnailScrollArea.horizontalScrollBar()
        max_scroll_value = scrollbar.maximum()
        current_scroll_value = scrollbar.value()
        total_images = len(self.parent.images)
        visible_thumbnails = math.ceil(self.parent.width()/self.thumbnail_size[0])
        if max_scroll_value == 0:
            current_index = 0
        else:
            current_index = math.ceil((current_scroll_value / max_scroll_value) * total_images)
        visible_start_index = max(0, current_index - int(self.thumbnail_limit))
        visible_end_index = min(current_index + visible_thumbnails + 4, total_images)
        if (int(visible_start_index), int(visible_end_index)) != self.visible_thumbnails_range:
            self.load_thumbnails_in_range(visible_start_index, visible_end_index)
            self.visible_thumbnails_range = (int(visible_start_index), int(visible_end_index))
    
    def on_thumbnail_clicked(self, button):
        """Loads the image associated with the clicked thumbnail."""
        self.parent.current_image = button.property('imageIndex')
        self.parent._load_image()
    
    def scroll_thumbnail_into_view(self):
        """Ensures the active thumbnail is visible in the scroll area."""
        if self.active_thumbnail and self.thumbnailScrollArea:
            self.thumbnailScrollArea.ensureWidgetVisible(self.active_thumbnail)
            self.on_thumbnail_scroll()
    
    def set_active_thumbnail(self, button):
        """Sets the specified thumbnail as active.

        Args:
            button (QPushButton): The thumbnail button to set as active.
        """
        frame = button.property('frame')
        if self.active_thumbnail:
            self.active_thumbnail.setStyleSheet("border: 1px solid grey;")

        frame.setStyleSheet("QFrame { border: 1px solid blue; }")
        self.active_thumbnail = frame
    
    def update_thumbnail_overlay(self, image_index, is_hidden):
        """Update the overlay style for a thumbnail based on hidden state.
        
        Args:
            image_index (int): Index of the image
            is_hidden (bool): Whether the image is hidden
        """
        if image_index < len(self.parent.images):
            image = self.parent.images[image_index]
            if 'thumbnail' in image:
                button = image['thumbnail']
                overlay = button.property('overlay')
                if overlay:
                    if is_hidden:
                        overlay.setStyleSheet("background-color: rgba(128, 128, 128, 150);")
                    else:
                        overlay.setStyleSheet("background-color: none;")
    
    def cleanup(self):
        """Clean up thumbnail resources."""
        # Stop any running thumbnail threads
        for thread, loader in self.parent._threads:
            if thread.isRunning():
                thread.requestInterruption()
                thread.quit()
                thread.wait()
        
        # Clear references
        self.loaded_thumbnails.clear()
        self.active_thumbnail = None
