"""
Test that wizard aggressiveness correctly maps to threshold and bins in the detector.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication

from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow

# Mock dependencies before importing
sys.modules['qtawesome'] = MagicMock()
sys.modules['helpers.IconHelper'] = MagicMock()


class TestWizardThresholdMapping:
    """Test that wizard settings correctly map to detector threshold and bins."""

    @patch('core.controllers.streaming.StreamViewerWindow.StreamCoordinator')
    @patch('core.controllers.streaming.StreamViewerWindow.DetectionRenderer')
    @patch('core.controllers.streaming.StreamViewerWindow.StreamStatistics')
    def test_moderate_aggressiveness_sets_30_percent_threshold(self, mock_stats, mock_renderer, mock_coord, qapp):
        """Test that Moderate aggressiveness (index 2) sets threshold to 30%."""
        viewer = StreamViewerWindow(algorithm_name="ColorAnomalyAndMotionDetection", theme="dark")
        try:
            QApplication.processEvents()

            # Apply wizard data with Moderate aggressiveness (should be 30%)
            wizard_data = {
                "algorithm": "ColorAnomalyAndMotionDetection",
                "algorithm_options": {
                    "color_rarity_percentile": 30.0,  # Moderate
                    "enable_color_quantization": True,
                    "enable_motion": False,
                },
            }

            viewer.apply_wizard_data(wizard_data)
            QApplication.processEvents()
            QApplication.processEvents()  # Extra process to ensure widget is ready

            # Verify the threshold slider was set to 30
            assert viewer.algorithm_widget is not None, "Algorithm widget should be loaded"
            assert hasattr(viewer.algorithm_widget, 'integrated_controls'), "Should have integrated_controls"

            slider = viewer.algorithm_widget.integrated_controls.color_rarity_percentile
            actual_value = slider.value()
            assert actual_value == 30, f"Threshold slider should be 30%, got {actual_value}%"

            # Verify the label was updated
            label = viewer.algorithm_widget.integrated_controls.color_percentile_label
            assert label.text() == "30%", f"Label should show '30%', got '{label.text()}'"
        finally:
            viewer.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    @patch('core.controllers.streaming.StreamViewerWindow.StreamCoordinator')
    @patch('core.controllers.streaming.StreamViewerWindow.DetectionRenderer')
    @patch('core.controllers.streaming.StreamViewerWindow.StreamStatistics')
    def test_all_aggressiveness_levels_map_correctly(self, mock_stats, mock_renderer, mock_coord, qapp):
        """Test all aggressiveness levels map to correct threshold values."""
        test_cases = [
            (80.0, "Very Conservative"),
            (50.0, "Conservative"),
            (30.0, "Moderate"),
            (15.0, "Aggressive"),
            (5.0, "Very Aggressive"),
        ]

        for percentile, label in test_cases:
            viewer = StreamViewerWindow(algorithm_name="ColorAnomalyAndMotionDetection", theme="dark")
            try:
                QApplication.processEvents()

                wizard_data = {
                    "algorithm": "ColorAnomalyAndMotionDetection",
                    "algorithm_options": {
                        "color_rarity_percentile": percentile,
                        "enable_color_quantization": True,
                        "enable_motion": False,
                    },
                }

                viewer.apply_wizard_data(wizard_data)
                QApplication.processEvents()
                QApplication.processEvents()

                slider = viewer.algorithm_widget.integrated_controls.color_rarity_percentile
                actual_value = slider.value()
                assert actual_value == int(percentile), \
                    f"{label} ({percentile}%) should set slider to {int(percentile)}, got {actual_value}"

                # Verify label
                label_widget = viewer.algorithm_widget.integrated_controls.color_percentile_label
                expected_text = f"{int(percentile)}%"
                assert label_widget.text() == expected_text, \
                    f"{label} should show '{expected_text}', got '{label_widget.text()}'"
            finally:
                viewer.close()
                QApplication.processEvents()  # Process events to ensure cleanup completes

    @patch('core.controllers.streaming.StreamViewerWindow.StreamCoordinator')
    @patch('core.controllers.streaming.StreamViewerWindow.DetectionRenderer')
    @patch('core.controllers.streaming.StreamViewerWindow.StreamStatistics')
    def test_color_quantization_bits_persists(self, mock_stats, mock_renderer, mock_coord, qapp):
        """Test that color quantization bits setting persists."""
        viewer = StreamViewerWindow(algorithm_name="ColorAnomalyAndMotionDetection", theme="dark")
        try:
            QApplication.processEvents()

            wizard_data = {
                "algorithm": "ColorAnomalyAndMotionDetection",
                "algorithm_options": {
                    "color_quantization_bits": 4,
                    "enable_color_quantization": True,
                },
            }

            viewer.apply_wizard_data(wizard_data)
            QApplication.processEvents()
            QApplication.processEvents()

            # Verify bits were set
            if hasattr(viewer.algorithm_widget, 'integrated_controls'):
                bits_spinbox = viewer.algorithm_widget.integrated_controls.color_quantization_bits
                assert bits_spinbox.value() == 4, f"Color quantization bits should be 4, got {bits_spinbox.value()}"
        finally:
            viewer.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
