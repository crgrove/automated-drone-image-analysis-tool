"""
ThumbnailUIComponent - Handles UI manipulation for thumbnail display.

This component manages all UI operations for thumbnails while ThumbnailController
manages business logic and state.
"""

import math
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from core.services.LoggerService import LoggerService


class ThumbnailUIComponent:
    """
    UI component for managing thumbnail display and interaction.
    
    This component handles all UI operations while ThumbnailController manages business logic.
    """
    
    def __init__(self, thumbnail_controller):
        """
        Initialize the thumbnail UI component.
        
        Args:
            thumbnail_controller: Reference to the ThumbnailController for business logic
        """
        self.thumbnail_controller = thumbnail_controller
        self.logger = LoggerService()  # Create our own logger
        
        # UI state
        self.active_thumbnail = None
        self.active_index = None
        
        # Thumbnail configuration
        self.thumbnail_size = (122, 78)
    
    def initialize_thumbnails(self):
        """Initialize thumbnail widgets immediately."""
        thumbnail_layout = self.thumbnail_controller.parent.thumbnailLayout
        if not thumbnail_layout:
            return
            
        thumbnail_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        thumbnail_layout.setSpacing(5)
        
        # Create all thumbnail widgets immediately (no images yet)
        for index in range(len(self.thumbnail_controller.parent.images)):
            self._create_thumbnail_widget(index)
    
    def _create_thumbnail_widget(self, index):
        """Create a thumbnail widget for the given index."""
        image = self.thumbnail_controller.parent.images[index]
        
        frame = QFrame()
        button = QPushButton()
        button.setFixedSize(QSize(100, 56))
        button.setProperty('imageIndex', index)
        button.setProperty('frame', frame)
        
        # Connect click handler
        from functools import partial
        button.clicked.connect(partial(self.thumbnail_controller.on_thumbnail_clicked, button))
        
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
        
        thumbnail_layout = self.thumbnail_controller.parent.thumbnailLayout
        thumbnail_layout.addWidget(frame)
        image['thumbnail'] = button
    
    def on_thumbnail_loaded(self, index, icon):
        """Handle thumbnail loaded from background thread."""
        if index >= len(self.thumbnail_controller.parent.images):
            return
            
        image = self.thumbnail_controller.parent.images[index]
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
            
        if 0 <= index < len(self.thumbnail_controller.parent.images):
            image = self.thumbnail_controller.parent.images[index]
            if 'thumbnail' in image:
                self.set_active_thumbnail(image['thumbnail'])
                return
                
        # If thumbnail widget doesn't exist yet, just store index
        self.active_thumbnail = None
    
    def update_thumbnail_overlay(self, image_index, is_hidden):
        """Update overlay for hidden state."""
        if image_index >= len(self.thumbnail_controller.parent.images):
            return
            
        image = self.thumbnail_controller.parent.images[image_index]
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
    
    def scroll_thumbnail_into_view(self):
        """Ensure active thumbnail is visible."""
        if not self.active_thumbnail:
            return
            
        thumbnail_scroll_area = self.thumbnail_controller.parent.thumbnailScrollArea
        if not thumbnail_scroll_area:
            return
            
        area = thumbnail_scroll_area
        # Center the active thumbnail
        x_margin = max(0, area.viewport().width() // 2)
        area.ensureWidgetVisible(self.active_thumbnail, x_margin, 0)
    
    def get_visible_thumbnail_range(self):
        """Calculate visible thumbnail range for loading optimization."""
        thumbnail_scroll_area = self.thumbnail_controller.parent.thumbnailScrollArea
        thumbnail_layout = self.thumbnail_controller.parent.thumbnailLayout
        
        if not thumbnail_scroll_area or not thumbnail_layout:
            self.logger.warning("Thumbnail UI elements not available for range calculation")
            return 0, 0
            
        # Calculate visible range
        area = thumbnail_scroll_area
        bar = area.horizontalScrollBar()
        
        spacing = thumbnail_layout.spacing() if thumbnail_layout else 0
        slot_width = max(1, self.thumbnail_size[0] + spacing)
        
        # Try multiple methods to get viewport width
        viewport_width = 0
        if area.viewport():
            viewport_width = area.viewport().width()
        
        # If viewport width is too small, try the scroll area width
        if viewport_width <= 100:
            viewport_width = area.width()
            
        # If still too small, try the parent widget width
        if viewport_width <= 100 and area.parent():
            viewport_width = area.parent().width()
        
        # If viewport isn't ready yet or too small, load a reasonable number of thumbnails
        if viewport_width <= 200:  # Increased threshold - 100px is definitely too small
            # Load first 50 thumbnails as fallback to ensure screen is filled
            fallback_count = min(50, len(self.thumbnail_controller.parent.images))
            return 0, fallback_count
        
        start_index = max(0, int(bar.value() // slot_width))
        visible_count = max(1, math.ceil(viewport_width / slot_width) + 20)  # Increased buffer
        end_index = min(len(self.thumbnail_controller.parent.images), start_index + visible_count)
        
        return start_index, end_index
    
    def cleanup(self):
        """Clean up UI resources."""
        self.active_thumbnail = None
        self.active_index = None

