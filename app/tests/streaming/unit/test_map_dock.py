"""Unit tests for :class:`MapDock` (plan §15 M3).

The Leaflet/QtWebEngine path is hard to drive in unit tests (it requires
a live HTML render pipeline), so these focus on:

* Construction succeeds in both interactive and fallback modes.
* :meth:`add_detection` accepts geo-tagged detections and rejects
  malformed ones without raising.
* :meth:`focus_detection` is a safe no-op when called with invalid input.
* :meth:`clear` resets the detection count.
"""

from __future__ import annotations

import os
import sys

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.views.flight.MapDock import MapDock  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_dock_constructs_in_either_mode(qapp) -> None:
    dock = MapDock()
    # Either path is acceptable — the test is just that construction
    # doesn't raise and the dock reports a sensible mode flag.
    assert isinstance(dock.is_interactive, bool)
    assert dock.detection_count == 0


def test_add_detection_increments_count(qapp) -> None:
    dock = MapDock()
    detection = {
        "track_key": "t1",
        "class_name": "person",
        "confidence": 0.9,
        "location": {"lat": 30.1, "lon": -97.5},
    }
    dock.add_detection(detection)
    assert dock.detection_count == 1


def test_add_detection_dedupes_by_track_key(qapp) -> None:
    dock = MapDock()
    detection = {
        "track_key": "t1",
        "class_name": "person",
        "location": {"lat": 30.1, "lon": -97.5},
    }
    dock.add_detection(detection)
    dock.add_detection(detection)  # same key → still 1
    assert dock.detection_count == 1


def test_add_detection_skips_missing_location(qapp) -> None:
    dock = MapDock()
    dock.add_detection({"track_key": "no-loc", "class_name": "person"})
    dock.add_detection({"track_key": "bad", "location": {"lat": "nope", "lon": None}})
    assert dock.detection_count == 0


def test_add_detection_ignores_non_dict_input(qapp) -> None:
    dock = MapDock()
    dock.add_detection(None)
    dock.add_detection("string")
    dock.add_detection(42)
    assert dock.detection_count == 0


def test_focus_detection_safe_with_missing_location(qapp) -> None:
    dock = MapDock()
    # Should not raise, even when the detection lacks coordinates.
    dock.focus_detection({"class_name": "person"})
    dock.focus_detection({})
    dock.focus_detection(None)


def test_clear_resets_state(qapp) -> None:
    dock = MapDock()
    dock.add_detection({
        "track_key": "t1",
        "class_name": "person",
        "location": {"lat": 30.1, "lon": -97.5},
    })
    assert dock.detection_count == 1
    dock.clear()
    assert dock.detection_count == 0
