"""
HueRingSelector - Shared circular hue selector.

A colour-wheel hue picker with a centre hue and adjustable lower/upper range
handles. Shared by the HSV Color Range picker and the viewer's colour
histogram dialog so the hue-selection UI is identical across the app.

Model: a centre hue ``h`` with lower/upper offsets ``h_minus`` / ``h_plus``,
all normalized to 0-1 (fractions of 360 degrees). ``valueChanged`` is emitted
continuously while dragging.

The static colour ring is cached to a QPixmap and only rebuilt when the widget
is resized; the range indicators, centre line, and handles are painted on top
each frame. This avoids rebuilding 360 colour arcs on every mouse-move repaint.
"""

import math

from PySide6.QtCore import Qt, QPoint, QRect, QRectF, QSize, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QPixmap
from PySide6.QtWidgets import QWidget


class HueRingSelector(QWidget):
    """Hue ring selector with range visualization."""

    valueChanged = Signal(float, float, float)  # h, h_minus, h_plus

    # Default square footprint so the ring stays visible/usable when a caller
    # drops it into a layout without sizing it. Sized generously so the ring
    # and its drag handles are easy to grab. Callers that need a specific size
    # (e.g. the HSV picker) still override via setFixedSize().
    PREFERRED_SIZE = 300
    MINIMUM_SIZE = 240

    # Ring geometry as fractions of the widget's min dimension. Tuned so the
    # ring fills most of its footprint -- a larger band and more widely spaced,
    # easier-to-grab handles -- while leaving room for the range-indicator arcs
    # drawn just outside the ring. Used by both painting and hit-testing so the
    # two never diverge.
    RING_MARGIN = 20
    OUTER_RADIUS_RATIO = 0.47
    INNER_RADIUS_RATIO = 0.31
    HANDLE_RADIUS_RATIO = 0.39

    def __init__(self, parent=None):
        super().__init__(parent)
        self.h = 0.0
        self.h_minus = 20 / 360
        self.h_plus = 20 / 360

        self.dragging_hue = False
        self.dragging_left = False
        self.dragging_right = False

        # Cached static colour ring; rebuilt only on resize.
        self._ring_pixmap = None

        self.setMouseTracking(True)

    def sizeHint(self):
        """Preferred square size so the ring renders sensibly by default."""
        return QSize(self.PREFERRED_SIZE, self.PREFERRED_SIZE)

    def minimumSizeHint(self):
        """Keep the ring from collapsing to zero in a hint-driven layout."""
        return QSize(self.MINIMUM_SIZE, self.MINIMUM_SIZE)

    def set_values(self, h, h_minus, h_plus):
        """Update values and repaint (does not emit a signal)."""
        self.h = h
        self.h_minus = h_minus
        self.h_plus = h_plus
        self.update()

    def values(self):
        """Return the current ``(h, h_minus, h_plus)`` (all 0-1)."""
        return self.h, self.h_minus, self.h_plus

    def _metrics(self):
        """Return (center, outer_radius, inner_radius, handle_radius)."""
        center = self.rect().center()
        size = min(self.width(), self.height()) - self.RING_MARGIN
        outer_radius = size * self.OUTER_RADIUS_RATIO
        inner_radius = size * self.INNER_RADIUS_RATIO
        handle_radius = size * self.HANDLE_RADIUS_RATIO
        return center, outer_radius, inner_radius, handle_radius

    def resizeEvent(self, event):
        """Invalidate the cached ring so it is rebuilt at the new size."""
        self._ring_pixmap = None
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Paint the hue ring with range indicators."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center, outer_radius, inner_radius, handle_radius = self._metrics()

        # Static colour ring (cached) + dynamic overlays.
        self._draw_cached_ring(painter)
        self.draw_range_indicators(painter, center, outer_radius, inner_radius)
        self.draw_handles(painter, center, outer_radius, inner_radius, handle_radius)

    def _draw_cached_ring(self, painter):
        """Blit the static hue ring, rebuilding the pixmap only when needed."""
        if self._ring_pixmap is None or self._ring_pixmap.size() != self.size():
            self._ring_pixmap = self._build_ring_pixmap()
        if self._ring_pixmap is not None:
            painter.drawPixmap(0, 0, self._ring_pixmap)

    def _build_ring_pixmap(self):
        """Render the colourful hue ring once into an off-screen pixmap."""
        if self.width() <= 0 or self.height() <= 0:
            return None
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        center, outer_radius, inner_radius, _ = self._metrics()
        self.draw_hue_ring(p, center, outer_radius, inner_radius)
        p.end()
        return pixmap

    def draw_hue_ring(self, painter, center, outer_radius, inner_radius):
        """Draw the colorful hue ring."""
        # Convert to integers for QRect
        outer_radius = int(outer_radius)
        inner_radius = int(inner_radius)

        for degree in range(360):
            # Original working code - hue colors will be upside down but handles work
            color = QColor.fromHsv(degree, 255, 255)

            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))

            # Create arc path using QRectF for floating point precision
            outer_rect = QRectF(center.x() - outer_radius, center.y() - outer_radius,
                                outer_radius * 2, outer_radius * 2)
            inner_rect = QRectF(center.x() - inner_radius, center.y() - inner_radius,
                                inner_radius * 2, inner_radius * 2)

            path = QPainterPath()
            path.arcMoveTo(outer_rect, degree - 90)
            path.arcTo(outer_rect, degree - 90, 1)
            path.arcTo(inner_rect, degree - 89, -1)
            path.closeSubpath()

            painter.fillPath(path, color)

    def draw_range_indicators(self, painter, center, outer_radius, inner_radius):
        """Draw the range selection indicators."""
        # Convert to integers
        outer_radius = int(outer_radius)
        inner_radius = int(inner_radius)

        # Original working coordinate system
        start_angle = (self.h - self.h_minus) * 360 - 90
        end_angle = (self.h + self.h_plus) * 360 - 90

        painter.setPen(QPen(QColor(204, 204, 204), 4))

        # Draw outer arc
        outer_rect = QRect(center.x() - outer_radius - 4, center.y() - outer_radius - 4,
                           (outer_radius + 4) * 2, (outer_radius + 4) * 2)
        painter.drawArc(outer_rect, int(start_angle * 16), int((end_angle - start_angle) * 16))

        # Draw inner arc
        inner_rect = QRect(center.x() - inner_radius + 4, center.y() - inner_radius + 4,
                           (inner_radius - 4) * 2, (inner_radius - 4) * 2)
        painter.drawArc(inner_rect, int(start_angle * 16), int((end_angle - start_angle) * 16))

        # Draw radial lines
        for angle in [start_angle, end_angle]:
            rad = math.radians(angle)
            start_point = QPoint(int(center.x() + (inner_radius - 4) * math.cos(rad)),
                                 int(center.y() - (inner_radius - 4) * math.sin(rad)))  # Negative sin for Qt coordinate system
            end_point = QPoint(int(center.x() + (outer_radius + 4) * math.cos(rad)),
                               int(center.y() - (outer_radius + 4) * math.sin(rad)))    # Negative sin for Qt coordinate system
            painter.drawLine(start_point, end_point)

    def draw_handles(self, painter, center, outer_radius, inner_radius, handle_radius):
        """Draw center line and range handles."""
        # Convert to integers
        outer_radius = int(outer_radius)
        inner_radius = int(inner_radius)
        handle_radius = int(handle_radius)

        # Center line - original working coordinate system
        line_angle = self.h * 360 - 90
        line_rad = math.radians(line_angle)

        start_point = QPoint(int(center.x() + inner_radius * math.cos(line_rad)),
                             int(center.y() - inner_radius * math.sin(line_rad)))  # Negative sin for Qt coords
        end_point = QPoint(int(center.x() + outer_radius * math.cos(line_rad)),
                           int(center.y() - outer_radius * math.sin(line_rad)))   # Negative sin for Qt coords

        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawLine(start_point, end_point)

        # Range handles - original working coordinate system
        left_angle = (self.h - self.h_minus) * 360 - 90
        right_angle = (self.h + self.h_plus) * 360 - 90

        for angle in [left_angle, right_angle]:
            rad = math.radians(angle)
            handle_center = QPoint(int(center.x() + handle_radius * math.cos(rad)),
                                   int(center.y() - handle_radius * math.sin(rad)))  # Negative sin for Qt coords

            painter.setPen(QPen(QColor(51, 51, 51), 2))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(handle_center, 10, 10)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            # Use the same metrics as painting so hit-testing matches what is drawn.
            center, outer_radius, inner_radius, handle_radius = self._metrics()

            # Check which element was clicked
            dx = pos.x() - center.x()
            dy = pos.y() - center.y()
            distance = math.sqrt(dx * dx + dy * dy)

            # Check handle clicks - original working coordinate system
            left_angle = math.radians((self.h - self.h_minus) * 360 - 90)
            right_angle = math.radians((self.h + self.h_plus) * 360 - 90)

            left_handle = QPoint(int(center.x() + handle_radius * math.cos(left_angle)),
                                 int(center.y() - handle_radius * math.sin(left_angle)))   # Negative sin for Qt coords
            right_handle = QPoint(int(center.x() + handle_radius * math.cos(right_angle)),
                                  int(center.y() - handle_radius * math.sin(right_angle)))  # Negative sin for Qt coords

            if (pos - left_handle).manhattanLength() < 15:
                self.dragging_left = True
            elif (pos - right_handle).manhattanLength() < 15:
                self.dragging_right = True
            elif inner_radius < distance < outer_radius:
                self.dragging_hue = True
                self.update_hue_from_pos(pos)

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.dragging_hue or self.dragging_left or self.dragging_right:
            self.update_hue_from_pos(event.pos())

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        self.dragging_hue = False
        self.dragging_left = False
        self.dragging_right = False

    def update_hue_from_pos(self, pos):
        """Update hue value from mouse position."""
        center = self.rect().center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()

        # Calculate angle from mouse position.
        # Drawing uses: qt_angle = (-hue_degrees + 90) % 360, so reverse it:
        # hue_degrees = (90 - qt_angle) % 360
        qt_angle = math.atan2(dy, dx)  # Qt coordinate system
        qt_angle_degrees = math.degrees(qt_angle)
        hue_degrees = (90 - qt_angle_degrees) % 360
        normalized_angle = hue_degrees / 360.0

        EPS = 1e-3

        if self.dragging_hue:
            self.h = normalized_angle
        elif self.dragging_left:
            clockwise_gap = (self.h - normalized_angle + 1) % 1
            clockwise_gap = min(clockwise_gap, 1 - EPS)
            self.h_minus = min(1 - self.h_plus - EPS, clockwise_gap)
        elif self.dragging_right:
            counter_clockwise_gap = (normalized_angle - self.h + 1) % 1
            counter_clockwise_gap = min(counter_clockwise_gap, 1 - EPS)
            self.h_plus = min(1 - self.h_minus - EPS, counter_clockwise_gap)

        self.update()
        self.valueChanged.emit(self.h, self.h_minus, self.h_plus)
