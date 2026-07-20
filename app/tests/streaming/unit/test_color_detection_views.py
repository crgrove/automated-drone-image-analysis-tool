"""Unit tests for ColorDetection UI views."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from algorithms.streaming.ColorDetection.views.ColorDetectionControlWidget import ColorDetectionControlWidget
from algorithms.Shared.views import HSVColorRowWidget, ColorRangeDialog
from PySide6.QtGui import QColor


class TestColorDetectionControlWidget:
    """Test suite for ColorDetectionControlWidget."""

    def test_initialization(self, qapp):
        """Test widget initialization."""
        widget = ColorDetectionControlWidget()

        assert widget is not None
        assert len(widget.color_ranges) == 0  # Should start with no color ranges
        assert hasattr(widget, 'tabs')

    def test_get_config(self, qapp):
        """Test configuration retrieval."""
        widget = ColorDetectionControlWidget()

        config = widget.get_config()

        assert isinstance(config, dict)
        assert 'color_ranges' in config
        assert 'processing_resolution' in config
        assert 'render_shape' in config
        assert 'min_area' in config
        assert 'max_area' in config
        assert config['target_fps'] is None
        assert widget.input_processing_tab.frame_rate_preset.currentData() == "source"

    def test_add_color(self, qapp):
        """Test adding a color range."""
        widget = ColorDetectionControlWidget()
        initial_count = len(widget.color_ranges)

        # Test adding a color using the actual implementation method
        # This simulates selecting a color from the color selection menu
        test_color = QColor(255, 0, 0)  # Red
        widget._on_color_selected_from_menu(test_color)

        # Should have added a new color range
        assert len(widget.color_ranges) == initial_count + 1
        assert widget.color_ranges[0]['color'] == test_color

    def test_remove_color_range(self, qapp):
        """Test removing a color range."""
        widget = ColorDetectionControlWidget()
        initial_count = len(widget.color_ranges)

        # Add a second color range first
        widget.color_ranges.append({
            'name': 'Green',
            'color': QColor(0, 255, 0),
            'hue_minus': 15,
            'hue_plus': 15,
            'sat_minus': 40,
            'sat_plus': 40,
            'val_minus': 40,
            'val_plus': 40
        })
        widget._update_color_ranges_display()

        # Remove the first widget
        if len(widget.color_range_widgets) > 1:
            widget._on_remove_color_range(widget.color_range_widgets[0])
            assert len(widget.color_ranges) == initial_count  # Should have removed one

    def test_get_config_has_no_recent_color_side_effects(self, qapp):
        """Reading config should not write to recent-colors storage."""
        widget = ColorDetectionControlWidget()
        widget._on_color_selected_from_menu(QColor(255, 0, 0))

        widget.recent_colors_service.add_hsv_color = Mock()
        widget.recent_colors_service.add_rgb_color = Mock()

        _ = widget.get_config()

        widget.recent_colors_service.add_hsv_color.assert_not_called()
        widget.recent_colors_service.add_rgb_color.assert_not_called()

    def test_frame_tab_config_can_clear_mask_path(self, qapp):
        """FrameTab set_config should clear mask path when given None."""
        widget = ColorDetectionControlWidget()

        widget.frame_tab.set_config({'mask_image_path': '/tmp/mask.png'})
        assert widget.frame_tab.get_config()['mask_image_path'] == '/tmp/mask.png'

        widget.frame_tab.set_config({'mask_image_path': None})
        assert widget.frame_tab.get_config()['mask_image_path'] is None


class TestHSVColorRangeRowWidget:
    """Test suite for HSVColorRowWidget (shared widget)."""

    def test_initialization(self, qapp):
        """Test widget initialization."""
        widget = HSVColorRowWidget(
            color=QColor(255, 0, 0),
            h_minus=20,
            h_plus=20,
            s_minus=50,  # Percentage
            s_plus=50,
            v_minus=50,
            v_plus=50
        )

        assert widget is not None
        assert hasattr(widget, 'color')
        assert hasattr(widget, 'hMinEdit')
        assert hasattr(widget, 'sMinEdit')
        assert hasattr(widget, 'vMinEdit')

    def test_get_hsv_ranges(self, qapp):
        """Test getting HSV ranges dictionary."""
        widget = HSVColorRowWidget(
            color=QColor(255, 0, 0),
            h_minus=20,
            h_plus=20,
            s_minus=50,
            s_plus=50,
            v_minus=50,
            v_plus=50
        )

        result = widget.get_hsv_ranges()

        assert isinstance(result, dict)
        assert 'h' in result
        assert 's' in result
        assert 'v' in result
        assert 'h_minus' in result
        assert 'h_plus' in result
        assert 's_minus' in result
        assert 's_plus' in result
        assert 'v_minus' in result
        assert 'v_plus' in result

    def test_range_changed_signal(self, qapp):
        """Test that changing range emits signal."""
        widget = HSVColorRowWidget(
            color=QColor(255, 0, 0),
            h_minus=20,
            h_plus=20,
            s_minus=50,
            s_plus=50,
            v_minus=50,
            v_plus=50
        )

        signal_emitted = False

        def on_changed():
            nonlocal signal_emitted
            signal_emitted = True

        widget.changed.connect(on_changed)

        # Change S min value
        widget.sMinEdit.setText("30")
        widget.sMinEdit.editingFinished.emit()

        # Signal should be emitted
        assert signal_emitted
