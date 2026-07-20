"""StreamingVideoDisplay - zoomable live video widget for streaming viewers.

A thin subclass of :class:`QtImageViewer` adapted for a live frame stream:

* Retains ONE full-resolution pixmap item where one scene unit equals one
  source pixel, so focus targets map straight from source coordinates.
* Same-resolution frames replace the pixmap directly (no ``setImage`` /
  ``setSceneRect`` / ``updateViewer`` / ``fitInView``), so per-frame cost stays
  flat and the user's zoom/pan is preserved across frames. This deliberately
  avoids the resize<->fitInView churn that can freeze the viewer at ~30fps.
* The first frame and any genuine source-resolution change rebuild via
  ``setImage`` and refit, clearing any stale zoom.
* Space is reserved for playback (emits :attr:`playPauseRequested`) and never
  enters the inherited Space-to-pan mode.
* Zoom/pan is preserved across tab switches (``showEvent`` does not reset it).

Zoom is display-only: :meth:`update_frame` never mutates the ndarray it
receives, so recordings and thumbnail extraction still see the full frame.
"""

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QGraphicsView

from core.services.LoggerService import LoggerService
from core.services.streaming.contracts import FocusTarget
from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer


class StreamingVideoDisplay(QtImageViewer):
    """Live video display with Results-Viewer-style zoom/pan navigation."""

    # Emitted when the user presses Space over the video (reserved for the
    # playback toggle instead of the inherited Space-to-pan behavior).
    playPauseRequested = Signal()

    # Emitted when a frame with a new source resolution forces a full reset.
    sourceResolutionChanged = Signal()

    # Fixed focus magnification, matching the Results Viewer's gallery zoom.
    FOCUS_SCALE = 6.0

    def __init__(self, window=None, parent=None):
        super().__init__(window, parent=parent)
        self.logger = LoggerService()

        # QtImageViewer references self.ROIs on some inherited paths but never
        # initializes it; guard defensively without expanding into a base-class
        # repair (streaming does not use ROIs).
        self.ROIs = []

        # (width, height) of the pixmap currently installed in the scene.
        self._source_size = None
        self._placeholder_item = None
        self._placeholder_message = None

        self.setStyleSheet("QGraphicsView { background-color: black; border: 1px solid gray; }")
        self.setMinimumSize(640, 480)
        # Center a small placeholder scene (default QGraphicsView alignment).
        self.setAlignment(Qt.AlignCenter)
        # The view must accept focus so it can receive Space/nav keys.
        self.setFocusPolicy(Qt.StrongFocus)

        self._show_placeholder(self.tr("No Stream Connected"))

    # ------------------------------------------------------------------ #
    #  Frame presentation
    # ------------------------------------------------------------------ #
    def update_frame(self, frame: np.ndarray):
        """Display a new BGR frame. Never mutates *frame* (display-only zoom)."""
        if self._is_destroyed:
            return
        try:
            height, width = frame.shape[:2]
            if width <= 0 or height <= 0:
                return

            # cv2.cvtColor allocates a fresh RGB buffer, so the caller's ndarray
            # (which recording/thumbnail extraction reuse) is left untouched.
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * width
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)

            new_size = (width, height)
            first_frame = self._image is None or self._source_size is None
            resolution_changed = (not first_frame) and new_size != self._source_size

            if first_frame or resolution_changed:
                # Full (re)build: create/replace the pixmap item, reset the
                # scene rect and refit. Clears any stale zoom on a real
                # resolution change.
                self._clear_placeholder()
                self.setImage(pixmap)
                if self._image is not None:
                    self._image.setTransformationMode(Qt.SmoothTransformation)
                self._source_size = new_size
                self.resetZoom()
                if resolution_changed:
                    self.sourceResolutionChanged.emit()
            else:
                # Steady state: swap the pixmap on the retained item only. No
                # setSceneRect / updateViewer / fitInView, so a zoomed live
                # stream never re-fits per frame.
                self._image.setPixmap(pixmap)
        except Exception as e:
            self.logger.error(f"Error updating streaming frame: {e}")

    def clear_display(self, message: str):
        """Reset to the placeholder state (replaces the old QLabel API).

        Clears the retained image and any zoom/pan, then shows *message*
        (already translated by the caller).
        """
        if self._is_destroyed:
            return
        self.clearImage()
        self._image = None
        self._source_size = None
        if self.zoomStack:
            self.zoomStack.clear()
        self._show_placeholder(message)

    @property
    def placeholder_message(self):
        """The message currently shown as the placeholder, or None."""
        return self._placeholder_message

    def has_placeholder(self):
        """True when the disconnected placeholder is currently displayed."""
        return self._placeholder_item is not None

    # ------------------------------------------------------------------ #
    #  Focus (zoom-to-detection)
    # ------------------------------------------------------------------ #
    def focus_on(self, target: FocusTarget, scale: float = None):
        """Center the view on *target* at *scale*x (default :attr:`FOCUS_SCALE`).

        The target is in source-frame coordinates paired with the resolution it
        was measured against; it is mapped independently on each axis into the
        current full-resolution scene, so it stays correct across resolutions.
        """
        if self._is_destroyed or not self.hasImage() or self._source_size is None:
            return
        if target is None:
            return
        if scale is None:
            scale = self.FOCUS_SCALE

        cx, cy = target.center_xy
        ref_w, ref_h = target.reference_size
        scene_w, scene_h = self._source_size
        if ref_w <= 0 or ref_h <= 0 or scene_w <= 0 or scene_h <= 0:
            return

        scene_x = cx * (scene_w / ref_w)
        scene_y = cy * (scene_h / ref_h)
        # zoomToArea unpacks center as QPointF(*center_xy): pass a 2-tuple.
        self.zoomToArea((scene_x, scene_y), scale)

    # ------------------------------------------------------------------ #
    #  Placeholder helpers
    # ------------------------------------------------------------------ #
    def _show_placeholder(self, message: str):
        self._clear_placeholder()
        if self._is_destroyed:
            return
        # Reset the view matrix so a leftover zoom transform from a prior stream
        # does not scale the placeholder text (otherwise the disconnected message
        # renders oversized). clearZoom only empties the zoom stack; the actual
        # QGraphicsView transform must be reset explicitly. Sync the inherited
        # _zoom bookkeeping so getZoom() no longer reports the pre-reset value.
        self.resetTransform()
        self._emit_zoom_if_changed()
        item = self.scene.addText(message)
        item.setDefaultTextColor(QColor(150, 150, 150))
        self._placeholder_item = item
        self._placeholder_message = message
        # A small scene rect + center alignment keeps the text centered at a
        # natural size without a fit transform.
        self.setSceneRect(item.boundingRect())

    def _clear_placeholder(self):
        if self._placeholder_item is not None:
            try:
                self.scene.removeItem(self._placeholder_item)
            except (RuntimeError, ValueError):
                pass
            self._placeholder_item = None
            self._placeholder_message = None

    # ------------------------------------------------------------------ #
    #  Qt events
    # ------------------------------------------------------------------ #
    def keyPressEvent(self, ev):
        # Reserve Space for the playback toggle. Intercepting it here (before
        # QtImageViewer's Space branch) means _space_held is never set, so the
        # inherited Space+left-drag pan can never engage.
        if ev.key() == Qt.Key_Space:
            if not ev.isAutoRepeat():
                self.playPauseRequested.emit()
            ev.accept()
            return
        super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev):
        if ev.key() == Qt.Key_Space:
            ev.accept()
            return
        super().keyReleaseEvent(ev)

    def showEvent(self, ev):
        # Deliberately bypass QtImageViewer.showEvent (which calls resetZoom and
        # would wipe the user's zoom every time the Live View tab is re-shown).
        try:
            QGraphicsView.showEvent(self, ev)
        except RuntimeError:
            self._is_destroyed = True
            return
        if self._is_destroyed or not self.hasImage():
            return
        if self.width() <= 0 or self.height() <= 0:
            return
        if self.zoomStack:
            # Re-apply the preserved zoom rect for the new viewport size.
            self.updateViewer()
        else:
            scene_rect = self._safe_scene_rect()
            if scene_rect:
                self.fitInView(scene_rect, self.aspectRatioMode)

    def resizeEvent(self, ev):
        # QtImageViewer.resizeEvent re-applies the zoom rect when zoomed; for
        # the unzoomed case it is a no-op, so explicitly refit the full scene.
        super().resizeEvent(ev)
        if self._is_destroyed or not self.hasImage():
            return
        if not self.zoomStack and self.width() > 0 and self.height() > 0:
            scene_rect = self._safe_scene_rect()
            if scene_rect:
                self.fitInView(scene_rect, self.aspectRatioMode)
