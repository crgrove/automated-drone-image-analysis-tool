"""Unit tests for ColorAnomalyAndMotionDetectionControlWidget."""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from algorithms.streaming.ColorAnomalyAndMotionDetection.views.ColorAnomalyAndMotionDetectionControlWidget import ColorAnomalyAndMotionDetectionControlWidget
from algorithms.streaming.ColorAnomalyAndMotionDetection.services import (
    MotionAlgorithm, FusionMode
)


class TestColorAnomalyAndMotionDetectionControlWidget:
    """Test suite for ColorAnomalyAndMotionDetectionControlWidget."""

    def test_initialization(self, qapp):
        """Test widget initialization."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        assert widget is not None
        assert widget.tabs is not None
        assert widget.tabs.count() == 5  # Should have 5 tabs

    def test_tabs_exist(self, qapp):
        """Test that all expected tabs exist."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        tab_names = [widget.tabs.tabText(i) for i in range(widget.tabs.count())]
        assert "Input && Processing" in tab_names  # Note: UI uses && for & in tab names
        assert "Motion Detection" in tab_names
        assert "Color Anomaly" in tab_names
        assert "Fusion && Cleanup" in tab_names  # Updated name
        assert "Rendering" in tab_names

    def test_input_tab_controls(self, qapp):
        """Test Input & Processing tab controls."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Check resolution preset exists (in shared InputProcessingTab)
        assert hasattr(widget, 'input_processing_tab')
        assert hasattr(widget.input_processing_tab, 'resolution_preset')
        assert widget.input_processing_tab.resolution_preset.count() > 0
        assert "720P (1280x720)" in [widget.input_processing_tab.resolution_preset.itemText(i) for i in range(widget.input_processing_tab.resolution_preset.count())]

        # Check custom resolution inputs exist
        assert hasattr(widget.input_processing_tab, 'processing_width')
        assert hasattr(widget.input_processing_tab, 'processing_height')

        # Check performance options
        assert hasattr(widget.input_processing_tab, 'render_at_processing_res')
        # Note: enable_morphology is not in UI (removed per user request)

    def test_motion_tab_controls(self, qapp):
        """Test Motion Detection tab controls."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Check enable motion checkbox
        assert hasattr(widget, 'enable_motion')
        assert widget.enable_motion.isChecked() is False  # Default OFF

        # Check algorithm combo
        assert hasattr(widget, 'motion_algorithm')
        assert widget.motion_algorithm.count() == 3
        assert widget.motion_algorithm.currentText() == "MOG2"

        # Check detection parameters
        assert hasattr(widget, 'motion_threshold')
        assert hasattr(widget, 'min_detection_area')
        assert hasattr(widget, 'max_detection_area')
        assert hasattr(widget, 'blur_kernel_size')
        assert hasattr(widget, 'morphology_kernel_size')

        # Check background subtraction
        assert hasattr(widget, 'bg_history')
        assert hasattr(widget, 'bg_var_threshold')
        assert hasattr(widget, 'bg_detect_shadows')

        # Check persistence filter
        assert hasattr(widget, 'persistence_frames')
        assert hasattr(widget, 'persistence_threshold')

        # Check camera movement
        assert hasattr(widget, 'pause_on_camera_movement')
        assert hasattr(widget, 'camera_movement_threshold')
        assert hasattr(widget, 'camera_movement_label')

    def test_color_tab_controls(self, qapp):
        """Test Color Anomaly tab controls."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Check enable color quantization
        assert hasattr(widget, 'enable_color_quantization')
        assert widget.enable_color_quantization.isChecked() is True  # Default ON

        # Check quantization parameters (sliders with labels)
        assert hasattr(widget, 'color_quantization_bits')
        assert hasattr(widget, 'color_bits_label')
        assert hasattr(widget, 'color_rarity_percentile')
        assert hasattr(widget, 'color_percentile_label')

        # Check detection area
        assert hasattr(widget, 'color_min_detection_area')
        assert hasattr(widget, 'color_max_detection_area')

        # Check hue expansion
        assert hasattr(widget, 'enable_hue_expansion')
        assert widget.enable_hue_expansion.isChecked() is False  # Default OFF
        assert hasattr(widget, 'hue_expansion_range')
        assert hasattr(widget, 'hue_range_label')

    def test_fusion_tab_controls(self, qapp):
        """Test Fusion & Temporal tab controls."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Check enable fusion
        assert hasattr(widget, 'enable_fusion')
        assert widget.enable_fusion.isChecked() is False  # Default OFF

        # Check fusion mode
        assert hasattr(widget, 'fusion_mode')
        assert widget.fusion_mode.currentText() == "UNION"

        # Check temporal voting
        assert hasattr(widget, 'enable_temporal_voting')
        assert widget.enable_temporal_voting.isChecked() is True  # Default ON
        assert hasattr(widget, 'temporal_window_frames')
        assert widget.temporal_window_frames.value() == 5  # Default 5
        assert hasattr(widget, 'temporal_threshold_frames')
        assert widget.temporal_threshold_frames.value() == 3  # Default 3

    def test_fpr_tab_controls(self, qapp):
        """Test False Pos. Reduction tab controls."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Check aspect ratio filter
        assert hasattr(widget, 'enable_aspect_ratio_filter')
        assert widget.enable_aspect_ratio_filter.isChecked() is False  # Default OFF
        assert hasattr(widget, 'min_aspect_ratio')
        assert hasattr(widget, 'max_aspect_ratio')

        # Check detection clustering
        assert hasattr(widget, 'enable_detection_clustering')
        assert widget.enable_detection_clustering.isChecked() is False  # Default OFF
        assert hasattr(widget, 'clustering_distance')
        assert widget.clustering_distance.value() == 50  # Default 50

        # Check color exclusion
        assert hasattr(widget, 'enable_color_exclusion')
        assert hasattr(widget, 'color_wheel')
        # ColorWheelWidget has 18 hue colors
        assert widget.color_wheel is not None

    def test_rendering_tab_controls(self, qapp):
        """Test Rendering tab controls."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Check shape options (in shared RenderingTab)
        assert hasattr(widget, 'rendering_tab')
        assert hasattr(widget.rendering_tab, 'render_shape')
        assert widget.rendering_tab.render_shape.currentText() == "Circle"  # Default Circle

        # Check visual options (in shared RenderingTab)
        assert hasattr(widget.rendering_tab, 'render_text')
        assert hasattr(widget.rendering_tab, 'render_contours')
        assert hasattr(widget.rendering_tab, 'use_detection_color')
        assert widget.rendering_tab.use_detection_color.isChecked() is True  # Default ON

        # Check performance limits
        assert hasattr(widget.rendering_tab, 'max_detections_to_render')
        assert widget.rendering_tab.max_detections_to_render.value() == 100  # Default 100


    def test_default_values(self, qapp):
        """Test that default values match original implementation."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()
        config = widget.get_config()

        # Input tab defaults
        assert config['render_at_processing_res'] is True
        # Note: enable_morphology not in UI, uses service default

        # Motion tab defaults
        assert config['enable_motion'] is False
        assert config['motion_algorithm'] == MotionAlgorithm.MOG2
        assert config['motion_threshold'] == 10
        assert config['min_detection_area'] == 5
        assert config['max_detection_area'] == 1000
        assert config['bg_history'] == 50
        assert config['bg_var_threshold'] == 10.0
        assert config['pause_on_camera_movement'] is True
        assert config['camera_movement_threshold'] == 0.15  # 15% / 100.0

        # Color tab defaults
        assert config['enable_color_quantization'] is True
        assert config['color_quantization_bits'] == 4
        assert config['color_rarity_percentile'] == 30.0
        assert config['color_min_detection_area'] == 15
        assert config['enable_hue_expansion'] is False

        # Fusion tab defaults
        assert config['enable_fusion'] is False
        assert config['fusion_mode'] == FusionMode.UNION
        assert config['enable_temporal_voting'] is True
        assert config['temporal_window_frames'] == 5
        assert config['temporal_threshold_frames'] == 3

        # FPR tab defaults
        assert config['enable_aspect_ratio_filter'] is False
        assert config['enable_detection_clustering'] is False
        assert config['clustering_distance'] == 50
        assert config['enable_color_exclusion'] is False

        # Rendering tab defaults
        assert config['render_shape'] == 1  # Circle
        assert config['use_detection_color_for_rendering'] is True
        assert config['max_detections_to_render'] == 100

    def test_resolution_preset_changes(self, qapp):
        """Test resolution preset changes."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Test Custom preset enables inputs
        widget.input_processing_tab.resolution_preset.setCurrentText("Custom")
        assert widget.input_processing_tab.processing_width.isEnabled() is True
        assert widget.input_processing_tab.processing_height.isEnabled() is True

        # Test preset disables inputs and sets values
        widget.input_processing_tab.resolution_preset.setCurrentText("1080P (1920x1080)")
        assert widget.input_processing_tab.processing_width.isEnabled() is False
        assert widget.input_processing_tab.processing_height.isEnabled() is False
        assert widget.input_processing_tab.processing_width.value() == 1920
        assert widget.input_processing_tab.processing_height.value() == 1080

        # Test Original preset
        widget.input_processing_tab.resolution_preset.setCurrentText("Original")
        assert widget.input_processing_tab.processing_width.isEnabled() is False
        assert widget.input_processing_tab.processing_height.isEnabled() is False

    def test_slider_labels_update(self, qapp):
        """Test that slider labels update correctly."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Test camera movement threshold label
        widget.camera_movement_threshold.setValue(25)
        widget.update_camera_movement_label()
        assert widget.camera_movement_label.text() == "25%"

        # Test color bits label
        widget.color_quantization_bits.setValue(5)
        widget.update_color_bits_label()
        assert widget.color_bits_label.text() == "5 bits"

        # Test color percentile label
        widget.color_rarity_percentile.setValue(40)
        widget.update_color_percentile_label()
        assert widget.color_percentile_label.text() == "40%"

        # Test hue range label
        widget.hue_expansion_range.setValue(10)
        widget.update_hue_range_label()
        assert widget.hue_range_label.text() == "±10 (~20°)"

    def test_config_emission(self, qapp):
        """Test that config changes emit signals."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        configs_received = []

        def on_config_changed(config):
            configs_received.append(config)

        widget.configChanged.connect(on_config_changed)

        # Change a control
        widget.enable_motion.setChecked(True)
        QTest.qWait(10)  # Allow signal to propagate

        assert len(configs_received) > 0
        assert configs_received[-1]['enable_motion'] is True

    def test_config_round_trip(self, qapp):
        """Test that config can be retrieved and matches widget state."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Get initial config
        initial_config = widget.get_config()

        # Change some values
        widget.enable_motion.setChecked(True)
        widget.motion_threshold.setValue(15)
        widget.enable_color_quantization.setChecked(False)

        # Get updated config
        updated_config = widget.get_config()

        # Verify changes are reflected
        assert updated_config['enable_motion'] is True
        assert updated_config['motion_threshold'] == 15
        assert updated_config['enable_color_quantization'] is False

        # Verify other values unchanged
        assert updated_config['enable_fusion'] == initial_config['enable_fusion']
        assert updated_config['temporal_window_frames'] == initial_config['temporal_window_frames']

    def test_motion_algorithm_enum_mapping(self, qapp):
        """Test that motion algorithm is correctly mapped to enum."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        widget.motion_algorithm.setCurrentText("FRAME_DIFF")
        config = widget.get_config()
        assert config['motion_algorithm'] == MotionAlgorithm.FRAME_DIFF

        widget.motion_algorithm.setCurrentText("KNN")
        config = widget.get_config()
        assert config['motion_algorithm'] == MotionAlgorithm.KNN

        widget.motion_algorithm.setCurrentText("MOG2")
        config = widget.get_config()
        assert config['motion_algorithm'] == MotionAlgorithm.MOG2

    def test_fusion_mode_enum_mapping(self, qapp):
        """Test that fusion mode is correctly mapped to enum."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        widget.fusion_mode.setCurrentText("UNION")
        config = widget.get_config()
        assert config['fusion_mode'] == FusionMode.UNION

        widget.fusion_mode.setCurrentText("INTERSECTION")
        config = widget.get_config()
        assert config['fusion_mode'] == FusionMode.INTERSECTION

        widget.fusion_mode.setCurrentText("COLOR_PRIORITY")
        config = widget.get_config()
        assert config['fusion_mode'] == FusionMode.COLOR_PRIORITY

        widget.fusion_mode.setCurrentText("MOTION_PRIORITY")
        config = widget.get_config()
        assert config['fusion_mode'] == FusionMode.MOTION_PRIORITY

    def test_color_exclusion_hue_ranges(self, qapp):
        """Test that color exclusion hue ranges are built correctly."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        # Enable color exclusion
        widget.enable_color_exclusion.setChecked(True)

        # Select some hues using the color wheel (Red and Yellow-Green)
        # Red is at 0°, Yellow-Green is at 100°
        widget.color_wheel.set_selected_hues([0, 100])

        config = widget.get_config()

        assert config['enable_color_exclusion'] is True
        # Color wheel selection should result in excluded hue ranges
        # The exact number depends on how the widget converts selections to ranges
        assert 'excluded_hue_ranges' in config
        assert isinstance(config['excluded_hue_ranges'], list)

        # Verify hue ranges are in OpenCV scale (0-179) if any exist
        for hue_min, hue_max in config['excluded_hue_ranges']:
            assert 0 <= hue_min <= 179
            assert 0 <= hue_max <= 179
            assert hue_min < hue_max

    def test_original_resolution_handling(self, qapp):
        """Test that Original resolution preset is handled correctly."""
        widget = ColorAnomalyAndMotionDetectionControlWidget()

        widget.input_processing_tab.resolution_preset.setCurrentText("Original")
        config = widget.get_config()

        # Original should set very large values (99999)
        assert config['processing_width'] >= 99999
        assert config['processing_height'] >= 99999
