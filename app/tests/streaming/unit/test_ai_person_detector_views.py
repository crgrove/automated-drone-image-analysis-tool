"""Unit tests for streaming AI Person Detector control widget."""

from algorithms.streaming.AIPersonDetector.views.AIPersonDetectorControlWidget import (
    AIPersonDetectorControlWidget,
)


class TestAIPersonDetectorControlWidget:
    """Test suite for AIPersonDetectorControlWidget."""

    def test_initialization_creates_expected_tabs(self, qapp):
        """Widget should use tabbed layout like other streaming algorithms."""
        widget = AIPersonDetectorControlWidget()

        assert widget.tabs.count() == 4
        assert widget.tabs.tabText(0) == "Person Detection"
        assert widget.tabs.tabText(1) == "Input && Processing"
        assert widget.tabs.tabText(2) == "Frame"
        assert widget.tabs.tabText(3) == "Rendering && Cleanup"

    def test_get_config_includes_shared_container_settings(self, qapp):
        """Configuration should include shared input/frame/rendering settings."""
        widget = AIPersonDetectorControlWidget()
        config = widget.get_config()

        assert "person_detector_confidence" in config
        assert "processing_width" in config
        assert "processing_height" in config
        assert "target_fps" in config
        assert "render_shape" in config
        assert "render_text" in config
        assert "mask_enabled" in config
        assert "max_detections" in config
        assert config["person_detector_confidence"] == 50
        assert config["target_fps"] is None
        assert config["processing_width"] == 1280
        assert config["processing_height"] == 720
        assert config["show_labels"] is True
        assert config["max_detections"] == 25
        assert config["enable_temporal_voting"] is False
        assert config["enable_aspect_ratio_filter"] is False
        assert widget.input_processing_tab.frame_rate_preset.currentData() == "source"

    def test_set_config_maps_legacy_fields(self, qapp):
        """Legacy fields should map into shared rendering/input controls."""
        widget = AIPersonDetectorControlWidget()
        widget.set_config(
            {
                "person_detector_confidence": 70,
                "cpu_only": True,
                "high_resolution_model": True,
                "show_labels": False,
                "max_detections": 5,
                "target_fps": 15,
                "processing_width": 99999,
                "processing_height": 99999,
            }
        )

        config = widget.get_config()
        assert config["person_detector_confidence"] == 70
        assert config["cpu_only"] is True
        assert config["high_resolution_model"] is True
        assert config["show_labels"] is False
        assert config["max_detections"] == 5
        assert config["target_fps"] == 15

    def test_unsupported_shared_controls_are_hidden(self, qapp):
        """AIPerson widget should hide shared controls the service does not support."""
        widget = AIPersonDetectorControlWidget()

        assert widget.input_processing_tab.render_at_processing_res.isVisible() is False
        assert widget.rendering_tab.render_contours.isVisible() is False
