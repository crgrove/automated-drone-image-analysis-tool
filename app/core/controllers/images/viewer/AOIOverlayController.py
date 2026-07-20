"""
AOIOverlayController - Manages the on-image selected-AOI decoration.

Owns the AOISelectionOverlay graphics item and decides when it is shown:
it appears for the AOI the reviewer last clicked, carries that AOI's
run-wide number, and shows a real-world ruler when ground sample distance
is available. The decoration is tied to the AOI circle toggle, so hiding
the circles also hides the number badge and ruler.

It also handles the ruler's grab handle: a viewport event filter lets the
reviewer drag the handle to swing the ruler around the AOI centre so it
aligns with the object being measured. The rotation is clamped to 90
degrees each way and resets whenever a different AOI is selected.
"""

import math

from PySide6.QtCore import QObject, QEvent, Qt

from core.services.LoggerService import LoggerService
from core.views.images.viewer.widgets.AOISelectionOverlay import (
    AOISelectionOverlay, build_ruler_model, ruler_angle_from_drag,
)


# Grab tolerance for the ruler handle, in screen pixels.
_HANDLE_GRAB_RADIUS = 16


class AOIOverlayController(QObject):
    """Controller for the selected-AOI on-image overlay (number + ruler)."""

    def __init__(self, parent_viewer):
        """Initialize the overlay controller.

        Args:
            parent_viewer: The main Viewer instance.
        """
        super().__init__()
        self.parent = parent_viewer
        self.logger = LoggerService()
        # The graphics item is created lazily once the scene is available.
        self._overlay_item = None
        # The AOI dict currently decorated, or None when nothing is selected.
        self._current_aoi = None
        # Ruler grab-handle drag state.
        self._dragging = False
        self._drag_offset = 90.0
        self._filter_installed = False

    def show_for_aoi(self, aoi):
        """Decorate the given AOI on the main image.

        A new selection always starts with a horizontal ruler.

        Args:
            aoi (dict): The AOI dictionary (needs 'center'; 'radius' and
                'number' are used when present).
        """
        self._current_aoi = aoi if isinstance(aoi, dict) else None
        if self._current_aoi is not None and self._ensure_item():
            self._overlay_item.reset_ruler_angle()
        self.refresh()

    def clear(self):
        """Remove the decoration and forget the current AOI."""
        self._current_aoi = None
        self._dragging = False
        if self._overlay_item is not None:
            self._overlay_item.set_dragging(False)
            self._overlay_item.hide()

    def refresh(self):
        """Redraw the decoration for the current AOI, honoring the toggles.

        Safe to call at any time. The decoration is hidden when there is no
        selected AOI or when AOI circles are turned off, and the ruler is
        omitted when no ground sample distance is available for the image.
        The ruler angle is preserved so a refresh does not undo a rotation.
        """
        aoi = self._current_aoi
        if not aoi or not aoi.get('center'):
            self._hide_item()
            return

        # The ruler is tied to the AOI circles: hiding the circles hides it.
        if not self._aoi_circles_visible():
            self._hide_item()
            return

        if not self._ensure_item():
            return

        radius = aoi.get('radius', 0) or 0
        # The ruler can be toggled off on its own (Show Ruler button) while the
        # circle and number badge stay; a None model draws the badge alone.
        ruler_model = None
        if self._ruler_visible():
            ruler_model = build_ruler_model(
                radius, self._current_gsd_cm(), self._distance_unit()
            )
        self._overlay_item.configure(
            aoi.get('center'), radius, aoi.get('number'), ruler_model
        )
        self._overlay_item.show()

    def _hide_item(self):
        """Hide the overlay item if it exists."""
        if self._overlay_item is not None:
            self._overlay_item.hide()

    def _ensure_item(self):
        """Create the overlay item and attach it to the scene if needed.

        Returns:
            bool: True when the overlay item is available for use.
        """
        if self._overlay_item is not None:
            return True

        main_image = getattr(self.parent, 'main_image', None)
        if main_image is None or getattr(main_image, '_is_destroyed', False):
            return False
        scene = getattr(main_image, 'scene', None)
        if scene is None:
            return False

        self._overlay_item = AOISelectionOverlay()
        scene.addItem(self._overlay_item)
        # Repaint crisply whenever the view zooms, since the badge, ticks,
        # labels and handle are kept at a constant on-screen size.
        try:
            main_image.zoomChanged.connect(self._on_zoom_changed)
        except Exception:
            pass
        # Watch the viewport for grab-handle drags. The event filter only
        # consumes a press that lands on the handle, so panning, region
        # zoom and AOI clicks elsewhere are unaffected.
        if not self._filter_installed:
            try:
                main_image.viewport().installEventFilter(self)
                self._filter_installed = True
            except Exception:
                pass
        return True

    def _on_zoom_changed(self, _zoom):
        """Force a repaint when the view zoom changes."""
        if self._overlay_item is not None and self._overlay_item.isVisible():
            self._overlay_item.update()

    # ------------------------------------------------------------------ #
    #  Grab-handle drag handling
    # ------------------------------------------------------------------ #
    def eventFilter(self, obj, event):
        """Drag the ruler handle when the press lands on it.

        Returns True (consuming the event) only while a handle drag is in
        progress, so all other viewport interaction is left untouched.
        """
        item = self._overlay_item
        if item is not None and item.isVisible() and item.has_ruler():
            event_type = event.type()
            if (event_type == QEvent.MouseButtonPress
                    and event.button() == Qt.LeftButton):
                if self._is_on_handle(event):
                    self._begin_drag(event)
                    return True
            elif event_type == QEvent.MouseMove and self._dragging:
                self._apply_drag(event)
                return True
            elif event_type == QEvent.MouseButtonRelease and self._dragging:
                self._end_drag()
                return True
        return super().eventFilter(obj, event)

    def _event_scene_pos(self, event):
        """Map a viewport mouse event to scene coordinates, or None."""
        main_image = getattr(self.parent, 'main_image', None)
        if main_image is None:
            return None
        try:
            return main_image.mapToScene(event.position().toPoint())
        except Exception:
            return None

    def _is_on_handle(self, event):
        """Return True when the mouse event lands on the ruler grab handle."""
        scene_pos = self._event_scene_pos(event)
        if scene_pos is None:
            return False
        handle = self._overlay_item.handle_scene_pos()
        zoom = self.parent.main_image.getZoom() or 1.0
        tolerance = _HANDLE_GRAB_RADIUS / zoom   # screen pixels -> scene units
        dx = scene_pos.x() - handle.x()
        dy = scene_pos.y() - handle.y()
        return (dx * dx + dy * dy) <= tolerance * tolerance

    def _begin_drag(self, event):
        """Start a handle drag, recording the grab offset to avoid a jump."""
        dx, dy = self._drag_vector(event)
        if dx is None:
            return
        cursor_angle = math.degrees(math.atan2(dy, dx)) if (dx or dy) else 90.0
        self._drag_offset = cursor_angle - self._overlay_item.ruler_angle()
        self._dragging = True
        self._overlay_item.set_dragging(True)

    def _apply_drag(self, event):
        """Swing the ruler so its handle follows the cursor."""
        dx, dy = self._drag_vector(event)
        if dx is None:
            return
        angle = ruler_angle_from_drag(dx, dy, self._drag_offset)
        self._overlay_item.set_ruler_angle(angle)

    def _end_drag(self):
        """Finish a handle drag."""
        self._dragging = False
        if self._overlay_item is not None:
            self._overlay_item.set_dragging(False)

    def _drag_vector(self, event):
        """Return (dx, dy) from the AOI centre to the cursor, or (None, None)."""
        scene_pos = self._event_scene_pos(event)
        if scene_pos is None:
            return None, None
        center = self._overlay_item.pos()
        return scene_pos.x() - center.x(), scene_pos.y() - center.y()

    # ------------------------------------------------------------------ #
    #  Inputs
    # ------------------------------------------------------------------ #
    def _aoi_circles_visible(self):
        """Return True when AOI circles are currently shown on the image."""
        button = getattr(self.parent, 'showAOIsButton', None)
        if button is None:
            return True
        try:
            return button.isChecked()
        except Exception:
            return True

    def _ruler_visible(self):
        """Return True when the AOI ruler is enabled (defaults True when absent)."""
        button = getattr(self.parent, 'showRulerButton', None)
        if button is None:
            return True
        try:
            return button.isChecked()
        except Exception:
            return True

    def _current_gsd_cm(self):
        """Return the GSD in cm/px for the current image, or None if unavailable.

        Uses the very same average GSD the Measure tool and the scale bar
        use -- ImageService.get_average_gsd() with the altitude controller's
        effective altitude -- so the ruler's distances agree with them. The
        effective altitude lets the reviewer correct an inaccurate GPS
        altitude; ignoring it (or applying terrain refinement) made the
        ruler disagree with the other measurement tools.

        It is read straight from the loaded image's ImageService rather than
        the status message dict, because that dict is only populated near
        the end of an image load -- after the gallery has zoomed to the AOI.
        """
        service = getattr(self.parent, 'current_image_service', None)
        if service is None:
            return None
        try:
            return service.get_average_gsd(
                custom_altitude_ft=self._custom_altitude_ft()
            )
        except Exception:
            return None

    def _custom_altitude_ft(self):
        """Return the altitude controller's effective altitude (feet), or None.

        The reviewer can correct an inaccurate GPS altitude there; the
        Measure tool and the person-size reference both honor it, so the
        ruler must too.
        """
        controller = getattr(self.parent, 'altitude_controller', None)
        if controller is None:
            return None
        try:
            return controller.get_effective_altitude()
        except Exception:
            return None

    def _distance_unit(self):
        """Return the distance-unit preference ('Feet' or 'Meters')."""
        service = getattr(self.parent, 'settings_service', None)
        if service is not None:
            try:
                return service.get_setting('DistanceUnit', 'Feet')
            except Exception:
                pass
        return getattr(self.parent, 'distance_unit', 'Feet')
