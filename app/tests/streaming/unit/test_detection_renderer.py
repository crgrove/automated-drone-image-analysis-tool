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

    def test_render_with_normalized_metadata_controls_shape_and_color(self, sample_frame):
        """Renderer should honor normalized per-detection render metadata."""
        detections = [
            {
                'bbox': (60, 60, 40, 40),
                'centroid': (80, 80),
                'confidence': 0.9,
                'class_name': 'Color_0',
                'metadata': {
                    'render_shape': 2,
                    'render_text': True,
                    'render_color': (0, 0, 255),
                    'render_label': 'Tracked',
                }
            }
        ]

        renderer = DetectionRenderer()
        result = renderer.render(sample_frame, detections)

        assert result is not None
        assert result.shape == sample_frame.shape
        assert not np.array_equal(result, sample_frame)

    def test_render_skips_detections_marked_hidden(self, sample_frame):
        """Renderer should skip detections explicitly marked as non-rendered."""
        detections = [
            {
                'bbox': (40, 40, 20, 20),
                'confidence': 0.9,
                'class_name': 'hidden',
                'metadata': {'render_skip': True}
            }
        ]

        renderer = DetectionRenderer()
        result = renderer.render(sample_frame, detections)

        assert np.array_equal(result, sample_frame)

    def test_render_can_draw_in_place_when_copy_disabled(self, sample_frame):
        """Renderer should support drawing directly onto an owned display frame."""
        detections = [{'bbox': (40, 40, 20, 20), 'confidence': 0.9, 'class_name': 'person'}]
        renderer = DetectionRenderer()
        original = sample_frame.copy()

        result = renderer.render(sample_frame, detections, copy_frame=False)

        assert result is sample_frame
        assert not np.array_equal(result, original)
