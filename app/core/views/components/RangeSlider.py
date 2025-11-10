"""
Custom Range Slider Widget

A horizontal range slider with two handles, tick marks, and a highlighted range segment.
Uses 7 discrete snap-to points with descriptive labels.
"""

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtWidgets import QWidget, QApplication, QSlider, QStyle, QStyleOptionSlider
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPalette, QFont, QTextOption


class RangeSlider(QWidget):
    """Custom range slider widget with two handles and 7 snap-to points."""
    
    # Signal emitted when the range values change
    rangeChanged = Signal(int, int)  # min_value, max_value
    
    # Define the 7 snap-to points with their labels
    SNAP_POINTS = [
        (1, "Small\nArticle\n(1 sqft)"),
        (3, "Small\nDog\n(3 sqft)"),
        (6, "Person\nStanding\n(6 sqft)"),
        (12, "Person\nRecumbent\n(12 sqft)"),
        (50, "ATV\n(50 sqft)"),
        (200, "Car\n(200 sqft)"),
        (1000, "Medium\nBuilding\n(1000 sqft)")
    ]
    
    def __init__(self, parent=None, minimum=1, maximum=1000, min_value=3, max_value=100):
        super().__init__(parent)
        
        # Find closest snap points for initial values
        self._min_value = self._snap_to_point(min_value)
        self._max_value = self._snap_to_point(max_value)
        
        # Ensure min < max
        if self._min_value >= self._max_value:
            min_idx = self._get_snap_index(self._min_value)
            if min_idx < len(self.SNAP_POINTS) - 1:
                self._max_value = self.SNAP_POINTS[min_idx + 1][0]
            else:
                self._min_value = self.SNAP_POINTS[min_idx - 1][0]
        
        # Track which handle is being dragged
        self._dragging_handle = None  # 'min', 'max', or None
        self._drag_start_pos = None
        
        # Visual properties
        self._handle_radius = 8
        self._track_height = 4
        self._tick_height = 8
        self._track_margin = 60  # Space on left and right for handles (increased for wider labels)
        self._label_height = 80  # Space above track for labels (increased for multi-line labels)
        
        # Colors will be set from palette in paintEvent
        self._track_color = None
        self._range_color = None
        self._handle_color = None
        self._tick_color = None
        self._label_color = None
        
        # Ensure minimum size (increased to accommodate multi-line labels and wider text)
        self.setMinimumHeight(120)
        self.setMinimumWidth(800)  # Increased to accommodate all labels without side cutoff
        
        # Create a temporary QSlider to extract its actual theme color
        self._temp_slider = QSlider()
        self._temp_slider.setStyleSheet("")  # Ensure it gets the theme stylesheet
    
    def _snap_to_point(self, value):
        """Snap a value to the nearest snap point."""
        closest_value = self.SNAP_POINTS[0][0]
        min_distance = abs(value - closest_value)
        
        for snap_value, _ in self.SNAP_POINTS:
            distance = abs(value - snap_value)
            if distance < min_distance:
                min_distance = distance
                closest_value = snap_value
        
        return closest_value
    
    def _get_snap_index(self, value):
        """Get the index of a snap point value."""
        for i, (snap_value, _) in enumerate(self.SNAP_POINTS):
            if snap_value == value:
                return i
        return 0
    
    def minValue(self):
        """Get the current minimum value."""
        return self._min_value
    
    def maxValue(self):
        """Get the current maximum value."""
        return self._max_value
    
    def setMinValue(self, value):
        """Set the minimum value, snapping to nearest point."""
        snapped = self._snap_to_point(value)
        # Ensure it doesn't exceed max
        if snapped < self._max_value:
            if snapped != self._min_value:
                self._min_value = snapped
                self.update()
                self.rangeChanged.emit(self._min_value, self._max_value)
    
    def setMaxValue(self, value):
        """Set the maximum value, snapping to nearest point."""
        snapped = self._snap_to_point(value)
        # Ensure it doesn't go below min
        if snapped > self._min_value:
            if snapped != self._max_value:
                self._max_value = snapped
                self.update()
                self.rangeChanged.emit(self._min_value, self._max_value)
    
    def setRange(self, min_val, max_val):
        """Set both min and max values at once, snapping to points."""
        min_snapped = self._snap_to_point(min_val)
        max_snapped = self._snap_to_point(max_val)
        
        # Ensure min < max
        if min_snapped >= max_snapped:
            min_idx = self._get_snap_index(min_snapped)
            if min_idx < len(self.SNAP_POINTS) - 1:
                max_snapped = self.SNAP_POINTS[min_idx + 1][0]
            else:
                min_snapped = self.SNAP_POINTS[min_idx - 1][0]
        
        changed = False
        if min_snapped != self._min_value:
            self._min_value = min_snapped
            changed = True
        if max_snapped != self._max_value:
            self._max_value = max_snapped
            changed = True
        
        if changed:
            self.update()
            self.rangeChanged.emit(self._min_value, self._max_value)
    
    def _value_to_position(self, value):
        """Convert a snap point value to a pixel position on the track."""
        width = self.width() - 2 * self._track_margin
        snap_index = self._get_snap_index(value)
        # Distribute evenly across the track
        ratio = snap_index / (len(self.SNAP_POINTS) - 1)
        return self._track_margin + ratio * width
    
    def _position_to_snap_value(self, position):
        """Convert a pixel position to the nearest snap point value."""
        width = self.width() - 2 * self._track_margin
        if width <= 0:
            return self.SNAP_POINTS[0][0]
        
        # Clamp position to track bounds
        position = max(self._track_margin, min(position, self.width() - self._track_margin))
        
        ratio = (position - self._track_margin) / width
        snap_index = round(ratio * (len(self.SNAP_POINTS) - 1))
        snap_index = max(0, min(snap_index, len(self.SNAP_POINTS) - 1))
        
        return self.SNAP_POINTS[snap_index][0]
    
    def _get_handle_rect(self, position):
        """Get the bounding rectangle for a handle at the given position."""
        # Calculate the same center_y as in paintEvent
        from PySide6.QtGui import QFontMetrics, QFont
        font = QFont()
        font.setPointSize(11)
        fm = QFontMetrics(font)
        max_lines = max(len(label_text.split('\n')) for _, label_text in self.SNAP_POINTS)
        line_height = fm.height() + 2
        # Account for font ascent at top
        actual_label_height = max_lines * line_height + fm.ascent() + 5
        center_y = actual_label_height + 15
        
        return QRectF(
            position - self._handle_radius,
            center_y - self._handle_radius,
            2 * self._handle_radius,
            2 * self._handle_radius
        )
    
    def _handle_at_position(self, pos):
        """Check if a handle is at the given mouse position. Returns 'min', 'max', or None."""
        min_pos = self._value_to_position(self._min_value)
        max_pos = self._value_to_position(self._max_value)
        
        min_rect = self._get_handle_rect(min_pos)
        max_rect = self._get_handle_rect(max_pos)
        
        # Convert QPoint to QPointF for contains check
        pos_f = QPointF(pos)
        
        # Check max handle first (it's usually on the right)
        if max_rect.contains(pos_f):
            return 'max'
        elif min_rect.contains(pos_f):
            return 'min'
        return None
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self._dragging_handle = self._handle_at_position(event.pos())
            if self._dragging_handle:
                self._drag_start_pos = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
            else:
                # Check if clicking near a snap point - snap to it
                clicked_value = self._position_to_snap_value(event.pos().x())
                min_pos = self._value_to_position(self._min_value)
                max_pos = self._value_to_position(self._max_value)
                clicked_pos = self._value_to_position(clicked_value)
                
                # Determine which handle to move (closest one)
                dist_to_min = abs(clicked_pos - min_pos)
                dist_to_max = abs(clicked_pos - max_pos)
                
                if dist_to_min < dist_to_max and clicked_value < self._max_value:
                    self._dragging_handle = 'min'
                    self.setMinValue(clicked_value)
                elif clicked_value > self._min_value:
                    self._dragging_handle = 'max'
                    self.setMaxValue(clicked_value)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self._dragging_handle:
            new_value = self._position_to_snap_value(event.pos().x())
            
            if self._dragging_handle == 'min':
                self.setMinValue(new_value)
            elif self._dragging_handle == 'max':
                self.setMaxValue(new_value)
        else:
            # Check if hovering over a handle
            handle = self._handle_at_position(event.pos())
            if handle:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self._dragging_handle = None
            self._drag_start_pos = None
            self.setCursor(Qt.ArrowCursor)
    
    def _get_theme_colors(self):
        """Get colors from the application palette and QSlider widget."""
        palette = QApplication.palette()
        
        # Try to get the actual slider color from qdarktheme
        # qdarktheme applies stylesheets, so we need to check the actual rendered color
        # First, try to get it from the slider's style
        slider_palette = self._temp_slider.palette()
        self._range_color = slider_palette.color(QPalette.ColorRole.Highlight)
        self._handle_color = slider_palette.color(QPalette.ColorRole.Highlight)
        
        # If that doesn't work, try application palette
        if not self._range_color.isValid() or self._range_color.alpha() == 0:
            self._range_color = palette.color(QPalette.ColorRole.Highlight)
            self._handle_color = palette.color(QPalette.ColorRole.Highlight)
        
        # Try to extract color from stylesheet if qdarktheme is being used
        # qdarktheme typically uses a purple/violet color for sliders in dark mode
        app = QApplication.instance()
        if app:
            # Check if there's a global stylesheet
            stylesheet = app.styleSheet()
            if stylesheet and 'QSlider' in stylesheet:
                # Try to find color in stylesheet (this is a fallback)
                # qdarktheme uses colors like #9C27B0, #BA68C8, or similar purples
                pass  # Stylesheet parsing is complex, skip for now
        
        # If still invalid, try accent color
        if not self._range_color.isValid():
            self._range_color = palette.color(QPalette.ColorRole.Accent)
            self._handle_color = palette.color(QPalette.ColorRole.Accent)
        
        # Final fallback - use theme-appropriate defaults
        # For qdarktheme dark mode, the slider color is typically a purple/violet
        if not self._range_color.isValid():
            window_color = palette.color(QPalette.ColorRole.Window)
            if window_color.lightness() > 128:
                # Light theme - use blue
                self._range_color = QColor(74, 144, 226)  # #4A90E2
                self._handle_color = QColor(74, 144, 226)
            else:
                # Dark theme - qdarktheme typically uses purple/lavender for sliders
                # Common colors: #9C27B0 (purple-500), #BA68C8 (purple-300), or #AB47BC
                # Try a purple that matches qdarktheme's typical slider color
                self._range_color = QColor(156, 39, 176)  # #9C27B0 - purple-500
                self._handle_color = QColor(156, 39, 176)
        
        # Ensure colors are fully opaque (alpha = 255, transparency = 0%)
        self._range_color.setAlpha(255)
        self._handle_color.setAlpha(255)
        
        # Get text color for labels
        self._label_color = palette.color(QPalette.ColorRole.WindowText)
        
        # Get track and tick colors based on theme
        window_color = palette.color(QPalette.ColorRole.Window)
        if window_color.lightness() > 128:
            # Light theme - use darker gray for track
            self._track_color = QColor(200, 200, 200)
            self._tick_color = QColor(200, 200, 200)
        else:
            # Dark theme - use lighter gray for track
            self._track_color = QColor(100, 100, 100)
            self._tick_color = QColor(100, 100, 100)
    
    def paintEvent(self, event):
        """Paint the range slider."""
        # Update colors from palette
        self._get_theme_colors()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Set up font for labels first to get accurate metrics
        font = QFont()
        font.setPointSize(11)
        painter.setFont(font)
        fm = painter.fontMetrics()
        
        # Calculate the actual height needed for labels
        max_lines = max(len(label_text.split('\n')) for _, label_text in self.SNAP_POINTS)
        line_height = fm.height() + 2
        # Account for font ascent at top and descent at bottom
        actual_label_height = max_lines * line_height + fm.ascent() + 5  # Top padding + ascent
        
        # Position track at a fixed distance below labels (not relative to widget height)
        center_y = actual_label_height + 15  # 15px gap between labels and track
        
        # Calculate track positions
        track_start = self._track_margin
        track_end = width - self._track_margin
        track_width = track_end - track_start
        
        min_pos = self._value_to_position(self._min_value)
        max_pos = self._value_to_position(self._max_value)
        
        # Draw track background (full track)
        track_rect = QRectF(
            track_start,
            center_y - self._track_height // 2,
            track_width,
            self._track_height
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._track_color))
        painter.drawRoundedRect(track_rect, self._track_height // 2, self._track_height // 2)
        
        # Draw selected range segment
        if max_pos > min_pos:
            range_rect = QRectF(
                min_pos,
                center_y - self._track_height // 2,
                max_pos - min_pos,
                self._track_height
            )
            painter.setBrush(QBrush(self._range_color))
            painter.drawRoundedRect(range_rect, self._track_height // 2, self._track_height // 2)
        
        # Draw tick marks and labels for all 7 snap points
        painter.setPen(QPen(self._tick_color, 1))
        
        # Calculate maximum label width (to allow wrapping)
        # Space between tick points minus some padding
        tick_spacing = track_width / (len(self.SNAP_POINTS) - 1)
        max_label_width = int(tick_spacing * 0.9)  # 90% of spacing to prevent overlap
        
        for snap_value, label_text in self.SNAP_POINTS:
            tick_pos = self._value_to_position(snap_value)
            
            # Draw tick mark
            painter.setPen(QPen(self._tick_color, 1))
            painter.drawLine(
                int(tick_pos),
                center_y - self._tick_height // 2,
                int(tick_pos),
                center_y + self._tick_height // 2
            )
            
            # Check if this snap point is within the selected range
            is_in_range = self._min_value <= snap_value <= self._max_value
            
            # Set font and color based on whether it's in range
            if is_in_range:
                label_font = QFont()
                label_font.setPointSize(11)
                label_font.setBold(True)
                painter.setFont(label_font)
                label_color = QColor(138, 180, 247)
            else:
                label_font = QFont()
                label_font.setPointSize(11)
                painter.setFont(label_font)
                label_color = self._label_color
            
            # Recalculate font metrics for the current font
            fm_label = painter.fontMetrics()
            
            # Draw label above tick, respecting manual line breaks (\n)
            # Start from top with proper padding to account for font ascent
            label_start_y = fm_label.ascent() + 5  # Top padding + font ascent (so text isn't cut off)
            line_height = fm_label.height() + 2  # Add small spacing between lines
            
            # Split text by \n to get lines (manual breaks)
            lines = label_text.split('\n')
            
            painter.setPen(QPen(label_color))
            current_y = label_start_y
            
            for line in lines:
                # Center each line horizontally
                line_width = fm_label.horizontalAdvance(line)
                line_x = tick_pos - line_width // 2
                
                # Draw the line (y coordinate is baseline)
                painter.drawText(int(line_x), int(current_y), line)
                current_y += line_height
        
        # Draw handles
        painter.setPen(QPen(self._handle_color, 2))
        painter.setBrush(QBrush(self._handle_color))
        
        # Min handle
        min_handle_center = QPointF(min_pos, center_y)
        painter.drawEllipse(min_handle_center, self._handle_radius, self._handle_radius)
        
        # Max handle
        max_handle_center = QPointF(max_pos, center_y)
        painter.drawEllipse(max_handle_center, self._handle_radius, self._handle_radius)
