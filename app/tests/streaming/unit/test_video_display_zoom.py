"""Unit tests for StreamingVideoDisplay zoom/pan/frame-replacement behavior.

These assert against the zoomStack navigation model and scene invariants
(deterministic headless) rather than the rendered viewport transform.
"""

from unittest.mock import Mock

import numpy as np
from PySide6.QtCore import Qt, QEvent, QRectF
from PySide6.QtGui import QKeyEvent, QShowEvent
from PySide6.QtWidgets import QGraphicsPixmapItem

from core.services.streaming.contracts import FocusTarget
from core.views.streaming.components.StreamingVideoDisplay import StreamingVideoDisplay


def _frame(width, height, value=0):
    return np.full((height, width, 3), value, dtype=np.uint8)


def test_first_frame_installs_single_fullres_pixmap_in_small_viewport(qapp):
    """One scene unit == one source pixel; exactly one pixmap item regardless of viewport."""
    display = StreamingVideoDisplay()
    try:
        display.resize(100, 100)  # viewport smaller than the source frame
        display.update_frame(_frame(640, 480, 20))

        assert display.sceneRect().width() == 640
        assert display.sceneRect().height() == 480
        pixmap_items = [it for it in display.scene.items() if isinstance(it, QGraphicsPixmapItem)]
        assert len(pixmap_items) == 1
    finally:
        display.close()


def test_retained_pixmap_item_uses_smooth_transformation(qapp):
    """The retained pixmap item must downscale smoothly (parity with old QLabel)."""
    display = StreamingVideoDisplay()
    try:
        display.update_frame(_frame(640, 480))
        assert display._image.transformationMode() == Qt.SmoothTransformation
    finally:
        display.close()


def test_same_size_frame_replacement_skips_setimage_and_fit(qapp):
    """A same-resolution frame swaps the pixmap directly: no setImage/setSceneRect/fitInView."""
    display = StreamingVideoDisplay()
    try:
        display.update_frame(_frame(640, 480, 10))
        item = display._image
        old_key = item.pixmap().cacheKey()

        display.setImage = Mock(wraps=display.setImage)
        display.setSceneRect = Mock(wraps=display.setSceneRect)
        display.fitInView = Mock(wraps=display.fitInView)

        display.update_frame(_frame(640, 480, 200))  # different content, same size

        display.setImage.assert_not_called()
        display.setSceneRect.assert_not_called()
        display.fitInView.assert_not_called()
        # Same item object, but its pixmap was replaced.
        assert display._image is item
        assert item.pixmap().cacheKey() != old_key
    finally:
        display.close()


def test_transformation_mode_survives_direct_pixmap_swap(qapp):
    """Smooth transformation stays set across the direct-setPixmap fast path."""
    display = StreamingVideoDisplay()
    try:
        display.update_frame(_frame(640, 480, 10))
        display.update_frame(_frame(640, 480, 90))
        assert display._image.transformationMode() == Qt.SmoothTransformation
    finally:
        display.close()


def test_resolution_change_rebuilds_and_resets_zoom(qapp):
    """A genuine source-resolution change uses the full setImage/reset path and clears zoom."""
    display = StreamingVideoDisplay()
    try:
        emitted = []
        display.sourceResolutionChanged.connect(lambda: emitted.append(True))

        display.update_frame(_frame(640, 480))
        display.focus_on(FocusTarget(center_xy=(320, 240), reference_size=(640, 480)))
        assert display.zoomStack  # zoomed in

        display.update_frame(_frame(320, 240))  # new resolution

        assert emitted == [True]
        assert display.sceneRect().width() == 320
        assert display.sceneRect().height() == 240
        assert not display.zoomStack  # zoom reset on resolution change
    finally:
        display.close()


def test_focus_on_maps_source_point_to_scene_independently_per_axis(qapp):
    """Focus scales X and Y independently and respects (width, height) ordering."""
    display = StreamingVideoDisplay()
    try:
        display.update_frame(_frame(640, 480))
        # Asymmetric reference: (160,60) in a 320x120 reference maps to (320,240)
        # in the 640x480 scene only if X uses width and Y uses height.
        display.focus_on(FocusTarget(center_xy=(160, 60), reference_size=(320, 120)))

        assert display.zoomStack
        zr = display.zoomStack[-1]
        assert abs(zr.center().x() - 320) < 2
        assert abs(zr.center().y() - 240) < 2
        # Visible rect is scene / scale on each axis.
        assert abs(zr.width() - 640 / display.FOCUS_SCALE) < 2
        assert abs(zr.height() - 480 / display.FOCUS_SCALE) < 2
    finally:
        display.close()


def test_focus_on_guards_zero_reference_dimensions(qapp):
    """A zero-dimension reference size must not zoom (no divide-by-zero)."""
    display = StreamingVideoDisplay()
    try:
        display.update_frame(_frame(640, 480))
        before = list(display.zoomStack)
        display.focus_on(FocusTarget(center_xy=(10, 10), reference_size=(0, 0)))
        assert list(display.zoomStack) == before
    finally:
        display.close()


def test_space_emits_play_pause_without_entering_pan(qapp):
    """Space is reserved for playback and never engages inherited Space-to-pan."""
    display = StreamingVideoDisplay()
    try:
        fired = []
        display.playPauseRequested.connect(lambda: fired.append(True))

        ev = QKeyEvent(QEvent.Type.KeyPress, Qt.Key_Space, Qt.KeyboardModifier.NoModifier)
        display.keyPressEvent(ev)

        assert fired == [True]
        assert display._space_held is False
        assert ev.isAccepted()
    finally:
        display.close()


def test_show_event_preserves_zoom(qapp):
    """Re-showing (Gallery -> Live View) must not reset the user's zoom."""
    display = StreamingVideoDisplay()
    try:
        display.resize(800, 600)
        display.update_frame(_frame(640, 480))
        display.focus_on(FocusTarget(center_xy=(320, 240), reference_size=(640, 480)))
        assert display.zoomStack
        center_before = display.zoomStack[-1].center()

        display.showEvent(QShowEvent())

        assert display.zoomStack  # not reset
        assert abs(display.zoomStack[-1].center().x() - center_before.x()) < 2
        assert abs(display.zoomStack[-1].center().y() - center_before.y()) < 2
    finally:
        display.close()


def test_clear_display_shows_translated_placeholder_and_drops_image(qapp):
    """clear_display renders the supplied placeholder and clears image/zoom."""
    display = StreamingVideoDisplay()
    try:
        display.update_frame(_frame(640, 480))
        display.focus_on(FocusTarget(center_xy=(320, 240), reference_size=(640, 480)))

        display.clear_display("Disconnected placeholder")

        assert display.has_placeholder()
        assert display.placeholder_message == "Disconnected placeholder"
        assert display._image is None
        assert not display.zoomStack
    finally:
        display.close()


def test_clear_display_resets_view_transform(qapp):
    """clear_display must reset the view matrix so the placeholder isn't scaled by a stale zoom."""
    display = StreamingVideoDisplay()
    try:
        display.resize(800, 600)
        display.update_frame(_frame(640, 480))
        display.focus_on(FocusTarget(center_xy=(320, 240), reference_size=(640, 480)))
        # (A fit/zoom may leave a non-identity transform.)

        display.clear_display("Disconnected")

        assert abs(display.transform().m11() - 1.0) < 1e-6
        assert abs(display.transform().m22() - 1.0) < 1e-6
        # getZoom() must not still report the pre-disconnect zoom.
        assert abs(display.getZoom() - 1.0) < 1e-6
    finally:
        display.close()


def test_update_frame_does_not_mutate_input_ndarray(qapp):
    """Zoom is display-only: the ndarray handed to recording/thumbnails is untouched."""
    display = StreamingVideoDisplay()
    try:
        frame = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        before = frame.copy()
        display.update_frame(frame)
        assert np.array_equal(frame, before)
    finally:
        display.close()
