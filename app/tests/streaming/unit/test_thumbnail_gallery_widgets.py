"""Unit tests for thumbnail/gallery resource behavior."""

from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from core.controllers.streaming.shared_widgets import DetectionThumbnailWidget, Track
from core.services.streaming.contracts import FocusTarget
from core.views.streaming.components.TrackGalleryWidget import TrackGalleryWidget


def _populated_thumbnail_widget():
    """A shown thumbnail widget with visible slots, tracker isolated.

    The widget must be shown so slot labels report isVisible() True — the
    thumbnail render/focus-capture loop skips hidden slots.
    """
    widget = DetectionThumbnailWidget()
    widget.resize(600, 150)
    widget.show()
    QApplication.processEvents()
    widget._adjust_thumbnail_count()
    widget.tracker.update_track = lambda *a, **k: None
    assert widget.thumbnail_labels and widget.thumbnail_labels[0].isVisible()
    return widget


def _make_track(track_id: int) -> Track:
    thumbnail = np.full((24, 24, 3), 127, dtype=np.uint8)
    return Track(
        track_id=track_id,
        bbox=(1, 1, 10, 10),
        centroid=(6, 6),
        thumbnail=thumbnail,
        first_frame_index=track_id,
        first_timestamp=float(track_id),
        frame_resolution=(24, 24),
    )


def test_gallery_is_bounded(qapp):
    """Gallery should drop oldest items past the configured cap."""
    widget = TrackGalleryWidget()
    widget.max_items = 2
    try:
        widget.add_track(_make_track(1))
        widget.add_track(_make_track(2))
        widget.add_track(_make_track(3))

        assert widget.gallery_list.count() == 2
        # Newest item is inserted first.
        first_item_track = widget.gallery_list.item(0).data(Qt.UserRole)
        assert first_item_track.track_id == 3
    finally:
        widget.close()


def test_thumbnail_updates_tracks_only_for_visible_slots(qapp):
    """Track updates should run only for detections currently assigned to thumbnail slots."""
    widget = DetectionThumbnailWidget()
    widget.resize(600, 150)
    widget._adjust_thumbnail_count()

    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    det_visible = SimpleNamespace(
        centroid=(30, 30),
        bbox=(20, 20, 20, 20),
        metadata={"track_id": 10},
    )
    det_hidden = SimpleNamespace(
        centroid=(90, 90),
        bbox=(80, 80, 20, 20),
        metadata={"track_id": 20},
    )

    widget.tracker.update = lambda _detections: {0: det_visible}
    calls = []
    widget.tracker.update_track = lambda track_id, detection, _frame, _frame_index, _timestamp: calls.append(track_id)

    try:
        widget.update_thumbnails(frame, [det_visible, det_hidden], frame_index=5, timestamp=2.0)
        assert calls == [10]
    finally:
        widget.close()


def test_live_thumbnail_crop_is_square_for_wide_detection(qapp):
    """Live thumbnail strip should use a square crop for consistent slot fill."""
    widget = DetectionThumbnailWidget()
    try:
        x1, y1, x2, y2 = widget._compute_live_thumbnail_crop(
            frame_shape=(480, 640, 3),
            centroid=(200, 150),
            bbox=(150, 130, 160, 40),
            zoom=3.0,
        )

        assert (x2 - x1) == (y2 - y1)
        assert (x2 - x1) >= 60
    finally:
        widget.close()


def test_live_thumbnail_crop_stays_in_bounds_near_edges(qapp):
    """Square live thumbnail crops should clamp to the frame without going negative."""
    widget = DetectionThumbnailWidget()
    try:
        x1, y1, x2, y2 = widget._compute_live_thumbnail_crop(
            frame_shape=(120, 160, 3),
            centroid=(8, 10),
            bbox=(0, 0, 80, 20),
            zoom=3.0,
        )

        assert x1 >= 0
        assert y1 >= 0
        assert x2 <= 160
        assert y2 <= 120
        assert (x2 - x1) == (y2 - y1)
    finally:
        widget.close()


def test_thumbnail_click_emits_source_space_focus_target(qapp):
    """A populated slot click emits a FocusTarget in raw source coords (no rescale)."""
    widget = _populated_thumbnail_widget()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = SimpleNamespace(centroid=(320, 240), bbox=(300, 220, 40, 40), metadata={"track_id": 1})
    widget.tracker.update = lambda _detections: {0: det}

    received = []
    widget.thumbnail_focus_requested.connect(received.append)
    try:
        widget.update_thumbnails(frame, [det], frame_index=1, timestamp=1.0)

        assert 0 in widget._focus_targets
        target = widget._focus_targets[0]
        assert isinstance(target, FocusTarget)
        # Centroid used directly (already source-space); reference is (w, h).
        assert target.center_xy == (320, 240)
        assert target.reference_size == (640, 480)

        widget._on_thumbnail_clicked(0)
        assert len(received) == 1
        assert received[0].center_xy == (320, 240)
    finally:
        widget.close()


def test_real_label_click_emits_focus_target(qapp):
    """A real left-click on a populated slot label emits the focus target."""
    widget = _populated_thumbnail_widget()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = SimpleNamespace(centroid=(200, 150), bbox=(180, 130, 40, 40), metadata={"track_id": 2})
    widget.tracker.update = lambda _detections: {0: det}

    received = []
    widget.thumbnail_focus_requested.connect(received.append)
    try:
        widget.update_thumbnails(frame, [det], frame_index=1, timestamp=1.0)

        # A genuine mouse click drives ClickableThumbnailLabel.mousePressEvent.
        QTest.mouseClick(widget.thumbnail_labels[0], Qt.LeftButton)

        assert len(received) == 1
        assert received[0].center_xy == (200, 150)
    finally:
        widget.close()


def test_thumbnail_focus_target_cleared_when_slot_empties(qapp):
    """A slot that becomes unassigned drops its focus payload; empty clicks emit nothing."""
    widget = _populated_thumbnail_widget()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = SimpleNamespace(centroid=(100, 100), bbox=(90, 90, 20, 20), metadata={"track_id": 3})

    received = []
    widget.thumbnail_focus_requested.connect(received.append)
    try:
        widget.tracker.update = lambda _detections: {0: det}
        widget.update_thumbnails(frame, [det], frame_index=1, timestamp=1.0)
        assert 0 in widget._focus_targets

        widget.tracker.update = lambda _detections: {}
        widget.update_thumbnails(frame, [], frame_index=2, timestamp=2.0)
        assert 0 not in widget._focus_targets

        widget._on_thumbnail_clicked(0)
        assert received == []
    finally:
        widget.close()


def test_clear_thumbnails_drops_focus_targets(qapp):
    """clear_thumbnails wipes stored focus payloads."""
    widget = _populated_thumbnail_widget()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = SimpleNamespace(centroid=(50, 50), bbox=(40, 40, 20, 20), metadata={"track_id": 7})
    widget.tracker.update = lambda _detections: {0: det}
    try:
        widget.update_thumbnails(frame, [det], frame_index=1, timestamp=1.0)
        assert widget._focus_targets

        widget.clear_thumbnails()
        assert widget._focus_targets == {}
    finally:
        widget.close()


def test_hidden_thumbnail_retains_focus_target_on_reshow(qapp):
    """A slot hidden by shrinking keeps its payload and stays clickable when re-shown."""
    widget = _populated_thumbnail_widget()  # ~4 slots at 600px
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = SimpleNamespace(centroid=(300, 200), bbox=(290, 190, 20, 20), metadata={"track_id": 9})
    widget.tracker.update = lambda _detections: {2: det}  # populate slot 2

    received = []
    widget.thumbnail_focus_requested.connect(received.append)
    try:
        widget.update_thumbnails(frame, [det], frame_index=1, timestamp=1.0)
        assert 2 in widget._focus_targets and widget.thumbnail_labels[2].isVisible()

        # Shrink so slot 2 is hidden (retains its pixmap AND payload).
        widget.setFixedWidth(300)
        QApplication.processEvents()
        widget._adjust_thumbnail_count()
        assert not widget.thumbnail_labels[2].isVisible()
        assert 2 in widget._focus_targets

        # Widen so slot 2 is shown again with no intervening frame (paused).
        widget.setFixedWidth(600)
        QApplication.processEvents()
        widget._adjust_thumbnail_count()
        assert widget.thumbnail_labels[2].isVisible()
        assert 2 in widget._focus_targets

        widget._on_thumbnail_clicked(2)
        assert len(received) == 1
    finally:
        widget.close()


def test_new_frame_invalidates_hidden_thumbnail_before_reshow(qapp):
    """An intervening update drops hidden pixmaps and click targets."""
    widget = _populated_thumbnail_widget()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    old_det = SimpleNamespace(
        centroid=(300, 200),
        bbox=(290, 190, 20, 20),
        metadata={"track_id": 9},
    )
    new_det = SimpleNamespace(
        centroid=(100, 100),
        bbox=(90, 90, 20, 20),
        metadata={"track_id": 10},
    )

    received = []
    widget.thumbnail_focus_requested.connect(received.append)
    try:
        widget.tracker.update = lambda _detections: {2: old_det}
        widget.update_thumbnails(frame, [old_det], frame_index=1, timestamp=1.0)

        widget.setFixedWidth(300)
        QApplication.processEvents()
        widget._adjust_thumbnail_count()
        hidden = widget.thumbnail_labels[2]
        assert not hidden.isVisible()
        assert hidden.pixmap() is not None and not hidden.pixmap().isNull()
        assert 2 in widget._focus_targets

        # A newer frame updates only currently visible slots. The hidden slot
        # must be invalidated rather than retaining frame 1's image and target.
        widget.tracker.update = lambda _detections: {0: new_det}
        widget.update_thumbnails(frame, [new_det], frame_index=2, timestamp=2.0)
        assert hidden.pixmap() is None or hidden.pixmap().isNull()
        assert 2 not in widget._focus_targets

        widget.setFixedWidth(600)
        QApplication.processEvents()
        widget._adjust_thumbnail_count()
        assert hidden.isVisible()
        assert hidden.pixmap() is None or hidden.pixmap().isNull()

        widget._on_thumbnail_clicked(2)
        assert received == []
    finally:
        widget.close()


def test_clear_thumbnails_clears_hidden_labels(qapp):
    """Hidden thumbnails must be cleared too, so they don't reappear after a new source."""
    widget = _populated_thumbnail_widget()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    det = SimpleNamespace(centroid=(300, 200), bbox=(290, 190, 20, 20), metadata={"track_id": 9})
    widget.tracker.update = lambda _detections: {2: det}
    try:
        widget.update_thumbnails(frame, [det], frame_index=1, timestamp=1.0)
        widget.setFixedWidth(300)
        QApplication.processEvents()
        widget._adjust_thumbnail_count()
        hidden = widget.thumbnail_labels[2]
        assert not hidden.isVisible()
        assert hidden.pixmap() is not None and not hidden.pixmap().isNull()

        widget.clear_thumbnails()

        assert hidden.pixmap() is None or hidden.pixmap().isNull()
        assert widget._focus_targets == {}
    finally:
        widget.close()
