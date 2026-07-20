"""Unit tests for CoverageExtentExportController."""

import pytest
from unittest.mock import MagicMock, patch

from core.controllers.images.viewer.exports.CoverageExtentExportController import (
    CoverageExtentExportController,
    CoverageExtentGenerationThread,
)


def _parent(distance_unit="ft"):
    parent = MagicMock()
    parent.distance_unit = distance_unit
    parent.images = [{"path": "a.jpg"}, {"path": "b.jpg"}]
    parent.status_controller = MagicMock()
    return parent


@pytest.fixture
def controller():
    return CoverageExtentExportController(_parent())


def test_init_stores_parent(controller):
    assert controller.parent is not None
    assert controller.coverage_thread is None
    assert controller.progress_dialog is None


# ---------------------------------------------------------------------------
# Thread behavior
# ---------------------------------------------------------------------------

def test_thread_cancel_sets_flag():
    thread = CoverageExtentGenerationThread(MagicMock(), MagicMock(), [], "/out.kml")
    assert thread._is_canceled is False
    thread.cancel()
    assert thread._is_canceled is True


def test_thread_emits_finished_on_success():
    coverage_service = MagicMock()
    coverage_service.calculate_coverage_extents.return_value = {
        "image_count": 2,
        "skipped_count": 0,
        "total_area_sqm": 1000.0,
        "polygons": [{"coords": []}],
        "cancelled": False,
    }
    kml_service = MagicMock()

    thread = CoverageExtentGenerationThread(
        coverage_service, kml_service, [{"path": "a.jpg"}], "/out.kml"
    )
    received = []
    thread.finished.connect(lambda d: received.append(d))

    thread.run()
    assert len(received) == 1
    assert received[0]["image_count"] == 2
    kml_service.generate_coverage_extent_kml.assert_called_once()


def test_thread_emits_canceled_when_coverage_cancelled():
    coverage_service = MagicMock()
    coverage_service.calculate_coverage_extents.return_value = {
        "image_count": 0, "skipped_count": 0, "total_area_sqm": 0.0, "polygons": [],
        "cancelled": True,
    }
    thread = CoverageExtentGenerationThread(coverage_service, MagicMock(), [], "/out.kml")
    cancelled = []
    thread.canceled.connect(lambda: cancelled.append(True))

    thread.run()
    assert cancelled == [True]


def test_thread_emits_finished_with_zero_images():
    coverage_service = MagicMock()
    coverage_service.calculate_coverage_extents.return_value = {
        "image_count": 0, "skipped_count": 5, "total_area_sqm": 0.0, "polygons": [],
        "cancelled": False,
    }
    kml_service = MagicMock()
    thread = CoverageExtentGenerationThread(coverage_service, kml_service, [], "/out.kml")
    received = []
    thread.finished.connect(lambda d: received.append(d))

    thread.run()
    assert received[0]["image_count"] == 0
    # KML generation should not happen when no valid images
    kml_service.generate_coverage_extent_kml.assert_not_called()


def test_thread_emits_error_on_exception():
    coverage_service = MagicMock()
    coverage_service.calculate_coverage_extents.side_effect = RuntimeError("fail")
    thread = CoverageExtentGenerationThread(coverage_service, MagicMock(), [], "/out.kml")
    errors = []
    thread.errorOccurred.connect(lambda msg: errors.append(msg))

    thread.run()
    assert errors == ["fail"]


# ---------------------------------------------------------------------------
# Controller callbacks
# ---------------------------------------------------------------------------

def test_on_generation_finished_shows_success_message():
    parent = _parent(distance_unit="ft")
    controller = CoverageExtentExportController(parent)
    controller.progress_dialog = MagicMock()
    coverage_data = {
        "image_count": 5,
        "skipped_count": 0,
        "total_area_sqm": 40468.6,  # exactly 10 acres
        "polygons": [{"coords": []}],
    }
    with patch(
        "core.controllers.images.viewer.exports.CoverageExtentExportController.QMessageBox"
    ):
        controller._on_generation_finished(coverage_data, "/out.kml")

    controller.progress_dialog.accept.assert_called_once()
    parent.status_controller.show_toast.assert_called_once()


def test_on_generation_finished_no_valid_images_shows_warning():
    parent = _parent()
    controller = CoverageExtentExportController(parent)
    controller.progress_dialog = MagicMock()
    coverage_data = {
        "image_count": 0,
        "skipped_count": 5,
        "total_area_sqm": 0.0,
        "polygons": [],
    }
    with patch(
        "core.controllers.images.viewer.exports.CoverageExtentExportController.QMessageBox"
    ) as MockQMB:
        controller._on_generation_finished(coverage_data, "/out.kml")

    MockQMB.warning.assert_called_once()


def test_on_generation_cancelled_shows_toast():
    parent = _parent()
    controller = CoverageExtentExportController(parent)
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True
    controller.coverage_thread = MagicMock()
    controller.coverage_thread.isRunning.return_value = False

    controller._on_generation_cancelled()

    parent.status_controller.show_toast.assert_called_once()


def test_on_generation_error_shows_critical_message():
    parent = _parent()
    controller = CoverageExtentExportController(parent)
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True

    with patch(
        "core.controllers.images.viewer.exports.CoverageExtentExportController.QMessageBox"
    ) as MockQMB:
        controller._on_generation_error("boom")

    MockQMB.critical.assert_called_once()
    parent.status_controller.show_toast.assert_called_once()


# ---------------------------------------------------------------------------
# Unit conversion in success message
# ---------------------------------------------------------------------------

def test_show_success_uses_acres_for_feet():
    parent = _parent(distance_unit="ft")
    controller = CoverageExtentExportController(parent)
    coverage_data = {
        "image_count": 5,
        "skipped_count": 0,
        "total_area_sqm": 40468.6,  # 10 acres
        "polygons": [],
    }
    with patch(
        "core.controllers.images.viewer.exports.CoverageExtentExportController.QMessageBox"
    ) as MockQMB:
        controller._show_success_message(coverage_data, "/out.kml")

    # Check that "acres" appears in the message
    MockQMB.information.assert_called_once()
    call_args = MockQMB.information.call_args
    message = call_args[0][2]
    assert "acres" in message.lower() or "10.00" in message


def test_show_success_uses_kmsq_for_meters():
    parent = _parent(distance_unit="m")
    controller = CoverageExtentExportController(parent)
    coverage_data = {
        "image_count": 5,
        "skipped_count": 0,
        "total_area_sqm": 1_000_000.0,  # 1 km²
        "polygons": [],
    }
    with patch(
        "core.controllers.images.viewer.exports.CoverageExtentExportController.QMessageBox"
    ) as MockQMB:
        controller._show_success_message(coverage_data, "/out.kml")

    call_args = MockQMB.information.call_args
    message = call_args[0][2]
    assert "km" in message.lower() or "1.000" in message


def test_show_no_valid_images_error_shows_counts():
    parent = _parent()
    controller = CoverageExtentExportController(parent)
    coverage_data = {"image_count": 3, "skipped_count": 7, "total_area_sqm": 0.0, "polygons": []}
    with patch(
        "core.controllers.images.viewer.exports.CoverageExtentExportController.QMessageBox"
    ) as MockQMB:
        controller._show_no_valid_images_error(coverage_data)

    call_args = MockQMB.warning.call_args
    message = call_args[0][2]
    assert "3" in message  # processed
    assert "7" in message  # skipped


def test_show_success_includes_skip_info_when_skipped():
    parent = _parent(distance_unit="ft")
    controller = CoverageExtentExportController(parent)
    coverage_data = {
        "image_count": 5,
        "skipped_count": 3,  # some were skipped
        "total_area_sqm": 4046.86,  # 1 acre
        "polygons": [],
    }
    with patch(
        "core.controllers.images.viewer.exports.CoverageExtentExportController.QMessageBox"
    ) as MockQMB:
        controller._show_success_message(coverage_data, "/out.kml")

    message = MockQMB.information.call_args[0][2]
    assert "skipped" in message.lower()


# ---------------------------------------------------------------------------
# Progress updates
# ---------------------------------------------------------------------------

def test_on_progress_updated_forwards_to_dialog():
    controller = CoverageExtentExportController(_parent())
    controller.progress_dialog = MagicMock()
    controller._on_progress_updated(5, 10, "Working...")
    controller.progress_dialog.update_progress.assert_called_once_with(5, 10, "Working...")


def test_on_progress_updated_no_dialog():
    controller = CoverageExtentExportController(_parent())
    controller.progress_dialog = None
    # Should not raise
    controller._on_progress_updated(5, 10, "Working...")
