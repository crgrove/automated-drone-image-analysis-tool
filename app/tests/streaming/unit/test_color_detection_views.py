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
        assert len(widget.color_ranges) > 0  # Should have default red range
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

    def test_add_color(self, qapp):
        """Test adding a color range."""
        widget = ColorDetectionControlWidget()
        initial_count = len(widget.color_ranges)

        # Mock the ColorRangeDialog to return a result
        # Patch where it's used in the widget module
        with patch('algorithms.streaming.ColorDetection.views.ColorDetectionControlWidget.ColorRangeDialog') as mock_dialog:
            mock_instance = mock_dialog.return_value
            mock_instance.exec.return_value = QDialog.DialogCode.Accepted
            mock_instance.get_hsv_ranges.return_value = {
                'h': 0.0,  # Red in normalized 0-1
                's': 1.0,
                'v': 1.0,
                'h_minus': 20/360.0,  # Fixed: should be normalized 0-1, not 0-179
                'h_plus': 20/360.0,
                's_minus': 0.2,  # Fixed: should be normalized 0-1, not 0-255
                's_plus': 0.2,
                'v_minus': 0.2,
                'v_plus': 0.2
            }

            widget._on_add_color()

            # Should have added a new color range
            assert len(widget.color_ranges) == initial_count + 1

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
