"""Unit tests for DetectionRenderer."""

import pytest
import numpy as np
from core.controllers.streaming.components.DetectionRenderer import DetectionRenderer, RenderConfig


class TestDetectionRenderer:
    """Test suite for DetectionRenderer."""

    def test_initialization(self):
        """Test renderer initialization."""
        renderer = DetectionRenderer()

        assert renderer.config is not None
        assert isinstance(renderer.config, RenderConfig)

    def test_initialization_with_config(self):
        """Test renderer initialization with custom config."""
        config = RenderConfig(
            show_boxes=True,
            show_labels=False,
            box_color=(255, 0, 0)
        )
        renderer = DetectionRenderer(config)

        assert renderer.config == config
        assert renderer.config.show_boxes is True
        assert renderer.config.show_labels is False
        assert renderer.config.box_color == (255, 0, 0)

    def test_render_empty_detections(self, sample_frame):
        """Test rendering with no detections."""
        renderer = DetectionRenderer()

        result = renderer.render(sample_frame, [])

        assert result is not None
        assert result.shape == sample_frame.shape
        assert np.array_equal(result, sample_frame)

    def test_render_with_detections(self, sample_frame, sample_detections):
        """Test rendering with detections."""
        renderer = DetectionRenderer()

        result = renderer.render(sample_frame, sample_detections)

        assert result is not None
        assert result.shape == sample_frame.shape
        # Frame should be modified (annotated)
        assert not np.array_equal(result, sample_frame)

    def test_render_with_stats(self, sample_frame, sample_detections):
        """Test rendering with statistics overlay."""
        config = RenderConfig(show_stats_overlay=True)
        renderer = DetectionRenderer(config)

        stats = {
            'fps': 30.0,
            'processing_time_ms': 33.3,
            'detection_count': 2
        }

        result = renderer.render(sample_frame, sample_detections, stats)

        assert result is not None
        assert result.shape == sample_frame.shape

    def test_render_without_boxes(self, sample_frame, sample_detections):
        """Test rendering without boxes."""
        config = RenderConfig(show_boxes=False)
        renderer = DetectionRenderer(config)

        result = renderer.render(sample_frame, sample_detections)

        assert result is not None
        # Should still render labels if enabled
        assert result.shape == sample_frame.shape

    def test_render_without_labels(self, sample_frame, sample_detections):
        """Test rendering without labels."""
        config = RenderConfig(show_labels=False)
        renderer = DetectionRenderer(config)

        result = renderer.render(sample_frame, sample_detections)

        assert result is not None
        assert result.shape == sample_frame.shape

    def test_render_custom_colors(self, sample_frame, sample_detections):
        """Test rendering with custom colors."""
        config = RenderConfig(box_color=(0, 0, 255))  # Red in BGR
        renderer = DetectionRenderer(config)

        result = renderer.render(sample_frame, sample_detections)

        assert result is not None
        assert result.shape == sample_frame.shape

    def test_render_detection_without_id(self, sample_frame):
        """Test rendering detection without ID."""
        detections = [
            {
                'bbox': (100, 100, 50, 50),
                'confidence': 0.85,
                'class_name': 'person'
                # No 'id' field
            }
        ]

        renderer = DetectionRenderer()
        result = renderer.render(sample_frame, detections)

        assert result is not None
        assert result.shape == sample_frame.shape
