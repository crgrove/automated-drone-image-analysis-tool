"""Tests for the stacked-point chooser on GPSMapView.

WALDO produces two captures at the same instant and GPS position, so one map
point can stand for several images. First-hit-wins made every image after the
first unreachable by click; the chooser menu makes them all reachable.
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from core.views.images.viewer.widgets.GPSMapView import GPSMapView


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def _entry(index, name, lat, lon, aoi_count=1, has_flagged=False, hidden=False,
           is_source_only=False, timestamp=None):
    return {
        'index': index, 'name': name, 'latitude': lat, 'longitude': lon,
        'timestamp': timestamp, 'aoi_count': aoi_count,
        'has_flagged': has_flagged, 'hidden': hidden,
        'is_source_only': is_source_only,
    }


def _view(entries):
    view = GPSMapView()
    view.current_zoom = 15
    view.gps_data = entries
    view.draw_gps_points()
    return view


def _marker_view_pos(view, marker_index):
    return view.mapFromScene(view.point_items[marker_index].pos())


def _press(view, view_pos):
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(view_pos),
        QPointF(view_pos),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    view.mousePressEvent(event)


# The WALDO pair: two images at one position, plus a distant third image.
PAIR_LAT, PAIR_LON = 36.10000, -118.20000


def _pair_data():
    return [
        _entry(0, 'pairA.jpg', PAIR_LAT, PAIR_LON, aoi_count=3,
               timestamp=datetime(2026, 6, 1, 10, 15, 42)),
        _entry(1, 'pairB.jpg', PAIR_LAT, PAIR_LON, aoi_count=1, has_flagged=True,
               timestamp=datetime(2026, 6, 1, 10, 15, 42)),
        _entry(2, 'far.jpg', PAIR_LAT + 1.0, PAIR_LON + 1.0),
    ]


def test_hit_test_collects_all_coincident_markers(app):
    view = _view(_pair_data())
    hits = view._hit_test_points(_marker_view_pos(view, 0))
    assert [h['index'] for h in hits] == [0, 1]


def test_hit_test_single_marker(app):
    view = _view(_pair_data())
    hits = view._hit_test_points(_marker_view_pos(view, 2))
    assert [h['index'] for h in hits] == [2]


def test_hit_test_excludes_source_only_dots(app):
    data = _pair_data()
    data.append(_entry(None, 'source_only.jpg', PAIR_LAT, PAIR_LON,
                       aoi_count=0, is_source_only=True))
    view = _view(data)
    hits = view._hit_test_points(_marker_view_pos(view, 0))
    assert [h['index'] for h in hits] == [0, 1]


def test_single_hit_emits_point_clicked_without_chooser(app):
    view = _view(_pair_data())
    emitted = []
    view.point_clicked.connect(emitted.append)
    with patch.object(view, '_show_point_chooser') as mock_chooser:
        _press(view, _marker_view_pos(view, 2))
    assert emitted == [2]
    mock_chooser.assert_not_called()


def test_multi_hit_opens_chooser_instead_of_emitting(app):
    view = _view(_pair_data())
    emitted = []
    view.point_clicked.connect(emitted.append)
    with patch.object(view, '_show_point_chooser') as mock_chooser:
        _press(view, _marker_view_pos(view, 0))
    assert emitted == []
    mock_chooser.assert_called_once()
    entries = mock_chooser.call_args.args[0]
    assert [e['index'] for e in entries] == [0, 1]


def test_chooser_labels_and_trigger_emit_selected_index(app):
    view = _view(_pair_data())
    holder = {}
    real_create = view._create_popup_menu

    def capture():
        menu = real_create()
        menu.exec = lambda pos: None  # do not block the test
        holder['menu'] = menu
        return menu

    view._create_popup_menu = capture
    view._show_point_chooser(view.gps_data[:2], QPoint(0, 0))

    actions = holder['menu'].actions()
    assert len(actions) == 2
    assert 'pairA.jpg' in actions[0].text()
    assert '10:15:42' in actions[0].text()
    assert '3 AOIs' in actions[0].text()
    assert actions[1].text().startswith('🚩')
    assert 'pairB.jpg' in actions[1].text()

    emitted = []
    view.point_clicked.connect(emitted.append)
    actions[1].trigger()
    assert emitted == [1]


def test_chooser_marks_hidden_entries(app):
    data = [
        _entry(0, 'shown.jpg', PAIR_LAT, PAIR_LON),
        _entry(1, 'hidden.jpg', PAIR_LAT, PAIR_LON, hidden=True),
    ]
    view = _view(data)
    holder = {}
    real_create = view._create_popup_menu

    def capture():
        menu = real_create()
        menu.exec = lambda pos: None
        holder['menu'] = menu
        return menu

    view._create_popup_menu = capture
    view._show_point_chooser(data, QPoint(0, 0))
    assert '(hidden)' in holder['menu'].actions()[1].text()


def test_stacked_tooltip_reports_image_count(app):
    view = _view(_pair_data())
    assert '2 images at this location' in view.point_items[0].toolTip()
    assert '2 images at this location' in view.point_items[1].toolTip()
    assert 'images at this location' not in view.point_items[2].toolTip()
