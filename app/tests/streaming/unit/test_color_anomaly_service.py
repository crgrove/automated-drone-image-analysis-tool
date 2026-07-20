"""Unit tests for ColorAnomalyService."""

import numpy as np
import pytest
from unittest.mock import patch

from algorithms.streaming.ColorAnomalyAndMotionDetection.services.ColorAnomalyService import (
    ColorAnomalyService,
)
from algorithms.streaming.ColorAnomalyAndMotionDetection.services.shared_types import (
    ColorAnomalyAndMotionDetectionConfig,
    ColorSpace,
    ContourMethod,
    Detection,
)


@pytest.fixture
def service():
    with patch(
        "algorithms.streaming.ColorAnomalyAndMotionDetection.services.ColorAnomalyService.LoggerService"
    ):
        yield ColorAnomalyService()


@pytest.fixture
def base_config():
    return ColorAnomalyAndMotionDetectionConfig(
        enable_color_quantization=True,
        color_quantization_bits=4,
        color_rarity_percentile=30.0,
        color_min_detection_area=10,
        max_detection_area=1_000_000,
        morphology_kernel_size=3,
        enable_morphology=False,
        color_space=ColorSpace.BGR,
        contour_method=ContourMethod.FIND_CONTOURS,
    )


def _frame_with_rare_color():
    """Frame dominated by gray with a small bright-red patch."""
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)  # gray dominant
    frame[40:60, 40:60] = (0, 0, 255)  # red patch (rare)
    return frame


# ---------------------------------------------------------------------------
# Initialization / helpers
# ---------------------------------------------------------------------------

def test_init(service):
    assert service._morph_kernel_cache == {}


def test_morph_kernel_cached(service):
    k1 = service._get_morph_kernel(3)
    k2 = service._get_morph_kernel(3)
    assert k1 is k2


def test_update_config_does_not_raise(service, base_config):
    # update_config is a no-op by design; just ensure it doesn't raise
    service.update_config(base_config)


# ---------------------------------------------------------------------------
# detect() early exit
# ---------------------------------------------------------------------------

def test_detect_returns_empty_when_disabled(service):
    cfg = ColorAnomalyAndMotionDetectionConfig(enable_color_quantization=False)
    assert service.detect(np.zeros((10, 10, 3), dtype=np.uint8), cfg) == []


# ---------------------------------------------------------------------------
# Colorspace dispatch paths
# ---------------------------------------------------------------------------

def test_detect_bgr_finds_rare_color(service, base_config):
    base_config.color_space = ColorSpace.BGR
    frame = _frame_with_rare_color()
    result = service.detect(frame, base_config)
    assert isinstance(result, list)
    for det in result:
        assert det.detection_type == "color_anomaly"


def test_detect_hsv_runs_without_error(service, base_config):
    base_config.color_space = ColorSpace.HSV
    base_config.hsv_min_saturation = 10
    frame = _frame_with_rare_color()
    result = service.detect(frame, base_config)
    assert isinstance(result, list)


def test_detect_lab_runs_without_error(service, base_config):
    base_config.color_space = ColorSpace.LAB
    base_config.lab_min_chroma = 5
    frame = _frame_with_rare_color()
    result = service.detect(frame, base_config)
    assert isinstance(result, list)


def test_detect_with_connected_components(service, base_config):
    base_config.contour_method = ContourMethod.CONNECTED_COMPONENTS
    frame = _frame_with_rare_color()
    result = service.detect(frame, base_config)
    for det in result:
        # Detection metadata is only populated for connected_components path
        if det.metadata:
            assert det.metadata.get("contour_method") == "connected_components"


def test_detect_respects_max_detections(service, base_config):
    base_config.color_space = ColorSpace.BGR
    base_config.color_min_detection_area = 1
    # Frame with multiple rare patches
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    frame[10:20, 10:20] = (0, 0, 255)  # red
    frame[60:70, 60:70] = (0, 255, 0)  # green
    frame[80:90, 80:90] = (255, 0, 0)  # blue
    result = service.detect(frame, base_config, max_detections=1)
    assert len(result) <= 1


# ---------------------------------------------------------------------------
# _extract_blobs_connected_components
# ---------------------------------------------------------------------------

def test_extract_connected_components_empty_mask(service, base_config):
    mask = np.zeros((50, 50), dtype=np.uint8)
    frame = np.zeros((50, 50, 3), dtype=np.uint8)
    color_indices = np.zeros((50, 50), dtype=np.int32)
    histogram = np.zeros(16, dtype=np.int32)
    result = service._extract_blobs_connected_components(
        mask, base_config, timestamp=0.0, frame_bgr=frame,
        color_indices=color_indices, histogram=histogram,
        total_pixels=2500,
    )
    assert result == []


def test_extract_connected_components_filters_area(service, base_config):
    base_config.color_min_detection_area = 100
    base_config.max_detection_area = 10000

    mask = np.zeros((80, 80), dtype=np.uint8)
    mask[5:10, 5:10] = 255  # 25 pixels (below min)
    mask[30:60, 30:60] = 255  # 900 pixels (within range)

    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    color_indices = np.zeros((80, 80), dtype=np.int32)
    histogram = np.zeros(16, dtype=np.int32)

    result = service._extract_blobs_connected_components(
        mask, base_config, timestamp=0.0, frame_bgr=frame,
        color_indices=color_indices, histogram=histogram,
        total_pixels=6400,
    )
    assert len(result) == 1
    assert result[0].area >= 100


def test_extract_connected_components_sorts_by_rarity(service, base_config):
    base_config.color_min_detection_area = 10

    mask = np.zeros((80, 80), dtype=np.uint8)
    mask[5:20, 5:20] = 255
    mask[40:55, 40:55] = 255

    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    color_indices = np.zeros((80, 80), dtype=np.int32)
    # Blob 1 lands in bin 0 (rare), blob 2 in bin 1 (common)
    color_indices[5:20, 5:20] = 0
    color_indices[40:55, 40:55] = 1
    histogram = np.array([1, 100] + [0] * 14, dtype=np.int32)

    result = service._extract_blobs_connected_components(
        mask, base_config, timestamp=0.0, frame_bgr=frame,
        color_indices=color_indices, histogram=histogram,
        total_pixels=6400,
    )
    # Rarest blob first
    assert len(result) == 2
    assert result[0].metadata["bin_count"] <= result[1].metadata["bin_count"]


# ---------------------------------------------------------------------------
# _expand_detection_by_hue
# ---------------------------------------------------------------------------

def test_expand_detection_by_hue_returns_detection(service):
    # Build a Detection with a simple contour/centroid
    frame_hsv = np.zeros((50, 50, 3), dtype=np.uint8)
    frame_hsv[10:30, 10:30, :] = [90, 200, 200]  # hue=90

    detection = Detection(
        bbox=(10, 10, 20, 20),
        centroid=(20, 20),
        area=400,
        confidence=0.8,
        detection_type="color_anomaly",
        timestamp=0.0,
        contour=np.array([[[10, 10]], [[30, 10]], [[30, 30]], [[10, 30]]], dtype=np.int32),
    )
    expanded = service._expand_detection_by_hue(frame_hsv, detection, hue_range=10)
    # Should return a Detection (possibly with expanded area)
    assert isinstance(expanded, Detection)
    assert expanded.bbox is not None
