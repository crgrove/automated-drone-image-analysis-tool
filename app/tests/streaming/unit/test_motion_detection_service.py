"""Unit tests for MotionDetectionService."""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from algorithms.streaming.ColorAnomalyAndMotionDetection.services.MotionDetectionService import (
    MotionDetectionService,
)
from algorithms.streaming.ColorAnomalyAndMotionDetection.services.shared_types import (
    ColorAnomalyAndMotionDetectionConfig,
    ContourMethod,
    MotionAlgorithm,
)


@pytest.fixture
def service():
    with patch(
        "algorithms.streaming.ColorAnomalyAndMotionDetection.services.MotionDetectionService.LoggerService"
    ):
        yield MotionDetectionService()


@pytest.fixture
def base_config():
    return ColorAnomalyAndMotionDetectionConfig(
        enable_motion=True,
        min_detection_area=10,
        max_detection_area=1_000_000,
        motion_threshold=20,
        morphology_kernel_size=3,
        enable_morphology=True,
        motion_algorithm=MotionAlgorithm.FRAME_DIFF,
        contour_method=ContourMethod.FIND_CONTOURS,
    )


def _frame(size=(100, 100), value=0):
    """Grayscale frame."""
    f = np.full(size, value, dtype=np.uint8)
    return f


def _frame_with_moving_object(size=(100, 100)):
    f = np.zeros(size, dtype=np.uint8)
    # Bright rectangle simulating a moving object
    f[30:50, 30:50] = 255
    return f


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def test_init_creates_background_subtractors(service):
    assert service._bg_subtractor_mog2 is not None
    assert service._bg_subtractor_knn is not None
    assert service._prev_gray is None
    assert service._persistence_frames == 3


def test_morph_kernel_cached_and_reused(service):
    k1 = service._get_morph_kernel(3)
    k2 = service._get_morph_kernel(3)
    assert k1 is k2
    k3 = service._get_morph_kernel(5)
    assert k3.shape == (5, 5)


# ---------------------------------------------------------------------------
# update_config
# ---------------------------------------------------------------------------

def test_update_config_changes_persistence_frames(service, base_config):
    base_config.persistence_frames = 7
    service.update_config(base_config)
    assert service._persistence_frames == 7


def test_update_config_reinitializes_subtractors(service, base_config):
    old_mog2 = service._bg_subtractor_mog2
    service.update_config(base_config)
    # Subtractors should have been replaced (reinitialized with new config)
    assert service._bg_subtractor_mog2 is not old_mog2


# ---------------------------------------------------------------------------
# detect() dispatch
# ---------------------------------------------------------------------------

def test_detect_returns_empty_when_motion_disabled(service):
    cfg = ColorAnomalyAndMotionDetectionConfig(enable_motion=False)
    assert service.detect(_frame(), cfg) == []


def test_detect_frame_diff_first_frame_returns_empty(service, base_config):
    result = service.detect(_frame(), base_config)
    assert result == []
    assert service._prev_gray is not None


def test_detect_frame_diff_finds_motion(service, base_config):
    # First frame
    service.detect(_frame(), base_config)
    # Second frame with significant change -> should find the moving rectangle
    result = service.detect(_frame_with_moving_object(), base_config)
    assert len(result) >= 1
    for det in result:
        assert det.detection_type == "baseline_motion"
        assert det.area >= base_config.min_detection_area


def test_detect_frame_diff_respects_max_detections(service, base_config):
    # Two objects; limit to 1
    service.detect(_frame(), base_config)
    next_frame = np.zeros((100, 100), dtype=np.uint8)
    next_frame[10:20, 10:20] = 255
    next_frame[60:70, 60:70] = 255
    result = service.detect(next_frame, base_config, max_detections=1)
    assert len(result) == 1


def test_detect_mog2_path(service, base_config):
    base_config.motion_algorithm = MotionAlgorithm.MOG2
    # Train background
    for _ in range(5):
        service.detect(_frame(), base_config)
    # Introduce motion
    result = service.detect(_frame_with_moving_object(), base_config)
    # MOG2 may or may not detect instantly, but should not raise
    for det in result:
        assert det.detection_type == "mog2_motion"


def test_detect_knn_path(service, base_config):
    base_config.motion_algorithm = MotionAlgorithm.KNN
    for _ in range(5):
        service.detect(_frame(), base_config)
    result = service.detect(_frame_with_moving_object(), base_config)
    for det in result:
        assert det.detection_type == "knn_motion"


def test_detect_connected_components_branch(service, base_config):
    base_config.contour_method = ContourMethod.CONNECTED_COMPONENTS
    service.detect(_frame(), base_config)
    result = service.detect(_frame_with_moving_object(), base_config)
    assert len(result) >= 1
    assert result[0].metadata.get("contour_method") == "connected_components"


def test_frame_diff_shape_mismatch_resets_prev(service, base_config):
    service.detect(_frame(size=(100, 100)), base_config)
    # Shape mismatch -> prev_gray replaced, no detections
    result = service.detect(_frame(size=(50, 50)), base_config)
    assert result == []
    assert service._prev_gray.shape == (50, 50)


# ---------------------------------------------------------------------------
# check_camera_movement
# ---------------------------------------------------------------------------

def test_check_camera_movement_disabled(service):
    cfg = ColorAnomalyAndMotionDetectionConfig(pause_on_camera_movement=False)
    assert service.check_camera_movement(_frame(), cfg) is False


def test_check_camera_movement_first_frame_returns_false(service):
    cfg = ColorAnomalyAndMotionDetectionConfig(pause_on_camera_movement=True)
    assert service.check_camera_movement(_frame(), cfg) is False
    assert service._prev_gray is not None


def test_check_camera_movement_detects_large_change(service):
    cfg = ColorAnomalyAndMotionDetectionConfig(
        pause_on_camera_movement=True, camera_movement_threshold=0.1
    )
    # First frame (all black)
    service.check_camera_movement(_frame(size=(100, 100), value=0), cfg)
    # Huge change (all white). Comparison via bool() because the implementation
    # returns a numpy bool, not a Python bool.
    result = service.check_camera_movement(_frame(size=(100, 100), value=255), cfg)
    assert bool(result) is True


def test_check_camera_movement_small_change_returns_false(service):
    cfg = ColorAnomalyAndMotionDetectionConfig(
        pause_on_camera_movement=True, camera_movement_threshold=0.5
    )
    service.check_camera_movement(_frame(size=(100, 100), value=100), cfg)
    # Identical frame -> no change
    assert bool(service.check_camera_movement(_frame(size=(100, 100), value=100), cfg)) is False


def test_check_camera_movement_shape_mismatch_resets(service):
    cfg = ColorAnomalyAndMotionDetectionConfig(pause_on_camera_movement=True)
    service.check_camera_movement(_frame(size=(50, 50)), cfg)
    result = service.check_camera_movement(_frame(size=(100, 100)), cfg)
    assert result is False
    assert service._prev_gray.shape == (100, 100)


# ---------------------------------------------------------------------------
# reset / reset_background_models
# ---------------------------------------------------------------------------

def test_reset_clears_prev_frame(service):
    service._prev_gray = _frame()
    service._detection_masks = [1, 2, 3]
    service.reset()
    assert service._prev_gray is None
    assert service._detection_masks == []


def test_reset_background_models_reinitializes(service):
    old_mog2 = service._bg_subtractor_mog2
    service.reset_background_models()
    assert service._bg_subtractor_mog2 is not None
    assert service._bg_subtractor_mog2 is not old_mog2
    assert service._prev_gray is None


# ---------------------------------------------------------------------------
# _extract_motion_blobs_connected_components
# ---------------------------------------------------------------------------

def test_connected_components_filters_by_area(service, base_config):
    base_config.min_detection_area = 100
    base_config.max_detection_area = 1000
    mask = np.zeros((50, 50), dtype=np.uint8)
    # Small blob (9 pixels) - below threshold
    mask[5:8, 5:8] = 255
    # Big blob (400 pixels) - within threshold
    mask[20:40, 20:40] = 255
    detections = service._extract_motion_blobs_connected_components(
        mask, base_config, "t", "TEST"
    )
    assert len(detections) == 1
    assert detections[0].area >= 100


def test_connected_components_empty_mask(service, base_config):
    mask = np.zeros((50, 50), dtype=np.uint8)
    detections = service._extract_motion_blobs_connected_components(
        mask, base_config, "t", "TEST"
    )
    assert detections == []
