"""
AOISelectionOverlay - On-image decoration for the currently selected AOI.

Draws, on top of the main image, the run-wide AOI number next to the
selected AOI's circle and a horizontal real-world ruler beneath it. The
ruler is calibrated in feet or metres (per the distance-unit preference)
with a major tick every whole unit, a medium tick every half unit and a
minor tick every quarter unit.

The ruler can be swung around the AOI centre with a grab handle so it
aligns with the object being measured; the rotation is clamped to 90
degrees each way from horizontal and is not persisted.

The geometry that drives the ruler is produced by the pure helpers in
this module (build_ruler_model / compute_ruler_ticks / ruler_angle_from_drag)
so it can be unit tested without a running Qt scene.
"""

import math

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QPen, QPainter
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem


# Screen-constant decoration sizes, in device pixels. They are divided by
# the current zoom in paint() so the decoration keeps a stable on-screen
# size while the ruler's length still tracks the AOI circle.
_RULER_GAP = 7            # gap between the circle bottom and the ruler baseline
_RULER_STRIP_HEIGHT = 47  # height of the dark contrast strip behind the ruler
_TICK_MAJOR = 11          # major tick length (every whole unit)
_TICK_MEDIUM = 7          # medium tick length (every half unit)
_TICK_MINOR = 4           # minor tick length (every quarter unit)
_NUMBER_FONT_PT = 10
_TICK_LABEL_FONT_PT = 7
_READOUT_FONT_PT = 8
_HANDLE_RADIUS = 6        # grab-handle dot radius

# The ruler may be swung this many degrees each way from horizontal.
_MAX_RULER_ANGLE = 90.0

# Feet are the only sub-metre unit ADIAT exposes; everything else is metres.
_FEET_ALIASES = ('feet', 'ft', 'foot', 'imperial')
_FOOT_IN_METERS = 0.3048


def _is_feet(distance_unit):
    """Return True when the distance-unit preference selects feet."""
    return str(distance_unit or '').strip().lower() in _FEET_ALIASES


def compute_ruler_ticks(width_units):
    """Compute ruler tick positions for a ruler ``width_units`` long.

    Ticks are placed every quarter unit and classified so the renderer can
    size them: a major tick on every whole unit, a medium tick on every
    half unit and a minor tick on every remaining quarter unit.

    Args:
        width_units (float): Ruler length in real-world units (feet or
            metres). Values <= 0 yield no ticks.

    Returns:
        list[tuple[float, str]]: (position_in_units, kind) pairs ordered
            from the ruler's left end, where kind is 'major', 'medium' or
            'minor'.
    """
    if width_units is None or width_units <= 0:
        return []

    # Step in quarter units; a small epsilon keeps a tick that lands
    # exactly on the ruler end from being dropped by float rounding.
    quarter_count = int(math.floor(width_units / 0.25 + 1e-9))
    ticks = []
    for index in range(0, quarter_count + 1):
        position = index * 0.25
        if index % 4 == 0:
            kind = 'major'
        elif index % 2 == 0:
            kind = 'medium'
        else:
            kind = 'minor'
        ticks.append((position, kind))
    return ticks


def build_ruler_model(radius_px, gsd_cm_per_px, distance_unit):
    """Build the real-world ruler description for one AOI.

    The ruler measures the AOI's width (its diameter) and is calibrated in
    the unit chosen in preferences. When no ground sample distance is
    available the AOI cannot be measured, so None is returned and the
    caller omits the ruler.

    Args:
        radius_px (float): AOI radius in image pixels.
        gsd_cm_per_px (float | None): Ground sample distance in
            centimetres per pixel, or None when it cannot be computed.
        distance_unit (str): Distance-unit preference ('Feet'/'Meters';
            legacy 'ft'/'m' are also accepted).

    Returns:
        dict | None: None when the ruler cannot be built. Otherwise a dict
            with keys 'width_units', 'unit_label', 'pixels_per_unit',
            'ticks' and 'width_text'.
    """
    if not gsd_cm_per_px or gsd_cm_per_px <= 0 or not radius_px or radius_px <= 0:
        return None

    use_feet = _is_feet(distance_unit)
    unit_in_meters = _FOOT_IN_METERS if use_feet else 1.0
    unit_label = 'ft' if use_feet else 'm'

    meters_per_pixel = gsd_cm_per_px / 100.0
    diameter_meters = (2.0 * radius_px) * meters_per_pixel
    width_units = diameter_meters / unit_in_meters
    pixels_per_unit = unit_in_meters / meters_per_pixel

    return {
        'width_units': width_units,
        'unit_label': unit_label,
        'pixels_per_unit': pixels_per_unit,
        'ticks': compute_ruler_ticks(width_units),
        'width_text': f"{width_units:.2f} {unit_label}",
    }


def ruler_angle_from_drag(dx, dy, offset=90.0):
    """Map a handle-drag vector to a clamped ruler angle in degrees.

    The drag vector runs from the AOI centre to the cursor. ``offset`` is
    recorded when the handle is first grabbed (cursor angle minus the
    current ruler angle) so the ruler does not jump at the start of a
    drag. The result is clamped to +/- 90 degrees of horizontal.

    Args:
        dx (float): Cursor x minus AOI centre x, in scene units.
        dy (float): Cursor y minus AOI centre y, in scene units.
        offset (float): Grab offset in degrees.

    Returns:
        float: The ruler angle in degrees, within [-90, 90].
    """
    if dx == 0 and dy == 0:
        return 0.0
    angle = math.degrees(math.atan2(dy, dx)) - offset
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return max(-_MAX_RULER_ANGLE, min(_MAX_RULER_ANGLE, angle))


class AOISelectionOverlay(QGraphicsItem):
    """QGraphicsItem that decorates the selected AOI on the main image.

    The item is positioned at the AOI centre in scene (image-pixel)
    coordinates. The ruler's length tracks the AOI circle because it is
    drawn in scene units, while text, ticks, the number badge and the
    grab handle are counter-scaled by the current zoom so they keep a
    constant on-screen size. The ruler is drawn rotated by the current
    ruler angle; mouse interaction is handled by AOIOverlayController.
    """

    def __init__(self):
        super().__init__()
        self._radius = 0.0
        self._number = None
        self._ruler = None
        self._ruler_angle = 0.0     # degrees, [-90, 90]
        self._dragging = False      # True while the handle is being dragged
        self._last_lod = 1.0        # scene-to-device scale from the last paint
        self.setZValue(1000)        # above the image pixmap
        # Mouse handling is done by a viewport event filter, not the item,
        # so the item never blocks panning or region-zoom.
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.hide()

    def configure(self, center, radius, number, ruler_model):
        """Set what to draw and move the item onto the AOI.

        The ruler angle is intentionally left untouched so a refresh
        (e.g. a circle-toggle) keeps the user's rotation; it is reset
        separately via reset_ruler_angle() when a new AOI is selected.

        Args:
            center (tuple): AOI centre (x, y) in image pixels.
            radius (float): AOI radius in image pixels.
            number (int | None): Run-wide AOI number, or None to omit it.
            ruler_model (dict | None): Result of build_ruler_model(), or
                None to omit the ruler (e.g. when no scale is available).
        """
        self.prepareGeometryChange()
        self._radius = float(radius or 0.0)
        self._number = number
        self._ruler = ruler_model
        if center is not None:
            self.setPos(float(center[0]), float(center[1]))
        self.update()

    # ------------------------------------------------------------------ #
    #  Ruler rotation
    # ------------------------------------------------------------------ #
    def ruler_angle(self):
        """Return the current ruler angle in degrees."""
        return self._ruler_angle

    def set_ruler_angle(self, degrees):
        """Set the ruler angle, clamped to +/- 90 degrees, and repaint."""
        self._ruler_angle = max(-_MAX_RULER_ANGLE,
                                min(_MAX_RULER_ANGLE, float(degrees)))
        self.update()

    def reset_ruler_angle(self):
        """Return the ruler to horizontal (called when a new AOI is selected)."""
        self.set_ruler_angle(0.0)

    def set_dragging(self, dragging):
        """Flag whether the grab handle is being dragged (for highlighting)."""
        self._dragging = bool(dragging)
        self.update()

    def has_ruler(self):
        """Return True when a ruler (and therefore a grab handle) is shown."""
        return self._ruler is not None

    def handle_scene_pos(self):
        """Return the grab handle's current position in scene coordinates."""
        return self.mapToScene(self._handle_item_pos())

    # ------------------------------------------------------------------ #
    #  Geometry helpers
    # ------------------------------------------------------------------ #
    def _screen(self, distance):
        """Convert a screen-pixel distance to item units at the last zoom."""
        lod = self._last_lod if self._last_lod > 1e-9 else 1.0
        return distance / lod

    @staticmethod
    def _rotate_point(x, y, degrees):
        """Rotate (x, y) about the origin by ``degrees`` (clockwise, y-down)."""
        radians = math.radians(degrees)
        cos_a, sin_a = math.cos(radians), math.sin(radians)
        return QPointF(x * cos_a - y * sin_a, x * sin_a + y * cos_a)

    def _handle_item_pos(self):
        """Return the grab handle position in item coordinates."""
        if self._radius <= 0:
            return QPointF(0.0, 0.0)
        baseline_y = self._radius + self._screen(_RULER_GAP)
        return self._rotate_point(self._radius, baseline_y, self._ruler_angle)

    def boundingRect(self):
        """Return a generous item-local bounding rectangle.

        The square margin covers the ruler at every rotation and the
        screen-constant decorations across the zoom range an AOI is
        realistically reviewed at.
        """
        if self._radius <= 0:
            return QRectF()
        margin = self._radius + 420.0
        return QRectF(-margin, -margin, 2.0 * margin, 2.0 * margin)

    # ------------------------------------------------------------------ #
    #  Painting
    # ------------------------------------------------------------------ #
    def paint(self, painter, option, widget=None):
        """Render the number badge and (rotated) ruler for the selected AOI."""
        if self._number is None and self._ruler is None:
            return

        lod = QStyleOptionGraphicsItem.levelOfDetailFromTransform(
            painter.worldTransform()
        )
        if not lod or lod <= 1e-9:
            lod = 1.0
        self._last_lod = lod

        painter.setRenderHint(QPainter.Antialiasing, True)
        if self._ruler is not None:
            # The ruler swings around the AOI centre; the number badge does
            # not, so only the ruler is drawn inside the rotated frame.
            painter.save()
            painter.rotate(self._ruler_angle)
            self._paint_ruler(painter, lod)
            painter.restore()
        if self._number is not None:
            self._paint_number(painter, lod)

    def _paint_number(self, painter, lod):
        """Draw the run-wide AOI number badge just outside the circle."""
        text = f"#{self._number}"
        # Anchor at roughly 45 degrees up-and-right on the circle.
        diagonal = 0.7071
        painter.save()
        painter.translate(self._radius * diagonal, -self._radius * diagonal)
        painter.scale(1.0 / lod, 1.0 / lod)  # 1 unit == 1 screen pixel here

        font = QFont()
        font.setPointSize(_NUMBER_FONT_PT)
        font.setBold(True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        pad_x, pad_y = 6, 3
        badge = QRectF(
            0.0,
            -(metrics.height() + 2 * pad_y),
            metrics.horizontalAdvance(text) + 2 * pad_x,
            metrics.height() + 2 * pad_y,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 205))
        painter.drawRoundedRect(badge, 4.0, 4.0)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(badge, Qt.AlignCenter, text)
        painter.restore()

    def _paint_ruler(self, painter, lod):
        """Draw the real-world ruler (and grab handle) beneath the AOI circle.

        Runs inside a frame already rotated by the ruler angle.
        """
        ruler = self._ruler
        pixels_per_unit = ruler['pixels_per_unit']
        radius = self._radius

        def screen(distance):
            """Convert a screen-pixel distance to scene units at this zoom."""
            return distance / lod

        x_left = -radius
        x_right = radius
        baseline_y = radius + screen(_RULER_GAP)

        # Dark translucent strip so the ruler stays legible on any image.
        strip = QRectF(
            x_left - screen(8),
            baseline_y - screen(3),
            (x_right - x_left) + screen(16),
            screen(_RULER_STRIP_HEIGHT),
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 150))
        painter.drawRoundedRect(strip, screen(3), screen(3))

        # Baseline and ticks use a cosmetic pen so they stay 1px on screen.
        pen = QPen(QColor(255, 255, 255))
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLine(QPointF(x_left, baseline_y), QPointF(x_right, baseline_y))

        tick_length = {
            'major': screen(_TICK_MAJOR),
            'medium': screen(_TICK_MEDIUM),
            'minor': screen(_TICK_MINOR),
        }
        for position, kind in ruler['ticks']:
            tick_x = x_left + position * pixels_per_unit
            painter.drawLine(
                QPointF(tick_x, baseline_y),
                QPointF(tick_x, baseline_y + tick_length[kind]),
            )

        # Whole-unit labels under the major ticks.
        label_y = baseline_y + screen(_TICK_MAJOR + 2)
        for position, kind in ruler['ticks']:
            if kind != 'major':
                continue
            tick_x = x_left + position * pixels_per_unit
            self._draw_label(
                painter, lod, tick_x, label_y,
                str(int(round(position))), _TICK_LABEL_FONT_PT,
            )

        # Total width readout centred under the ruler.
        self._draw_label(
            painter, lod, 0.0, baseline_y + screen(30),
            ruler['width_text'], _READOUT_FONT_PT, bold=True,
        )

        # Grab handle at the ruler's right end.
        self._paint_handle(painter, QPointF(x_right, baseline_y), screen(_HANDLE_RADIUS))

    def _paint_handle(self, painter, center, handle_radius):
        """Draw the circular grab handle used to rotate the ruler."""
        outline = QPen(QColor(0, 0, 0, 220))
        outline.setCosmetic(True)
        painter.setPen(outline)
        fill = QColor(90, 200, 255) if self._dragging else QColor(255, 255, 255)
        painter.setBrush(fill)
        painter.drawEllipse(center, handle_radius, handle_radius)

    def _draw_label(self, painter, lod, item_x, item_y, text, point_size, bold=False):
        """Draw screen-constant, upright white text centred on a point.

        The text is counter-rotated by the ruler angle so it stays
        readable even when the ruler is swung.

        Args:
            painter: Active QPainter (already rotated by the ruler angle).
            lod: Current level of detail (scene-to-device scale).
            item_x: Anchor x in the rotated frame; text is centred on it.
            item_y: Anchor y in the rotated frame; the text top sits here.
            text: The string to draw.
            point_size: Font point size at 100% zoom.
            bold: Whether to embolden the text.
        """
        painter.save()
        painter.translate(item_x, item_y)
        painter.rotate(-self._ruler_angle)   # keep text upright
        painter.scale(1.0 / lod, 1.0 / lod)

        font = QFont()
        font.setPointSize(point_size)
        font.setBold(bold)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        width = metrics.horizontalAdvance(text)
        height = metrics.height()
        box = QRectF(-width / 2.0, 0.0, width, height)

        # Dark drop shadow then white text for contrast on bright imagery.
        painter.setPen(QPen(QColor(0, 0, 0, 210)))
        painter.drawText(box.translated(1.0, 1.0), Qt.AlignCenter, text)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(box, Qt.AlignCenter, text)
        painter.restore()
