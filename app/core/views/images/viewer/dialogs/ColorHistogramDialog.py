"""
ColorHistogramDialog - Popup dialog for hue histogram interaction.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout

from core.views.images.viewer.ui.ColorHistogramDialog_ui import Ui_ColorHistogramDialog
from core.views.components.HueRingSelector import HueRingSelector
from core.views.images.viewer.widgets.ThermalHistogramChart import ThermalHistogramChart
from helpers.TranslationMixin import TranslationMixin


class ColorHistogramDialog(TranslationMixin, QDialog, Ui_ColorHistogramDialog):
    """Dialog that hosts the interactive hue histogram widget."""

    rangeChanged = Signal(float, float)
    aoiOnlyModeChanged = Signal(bool)
    hoveredRangeChanged = Signal(object)
    dialogClosed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.histogram_context = None

        self.chartWidget = ThermalHistogramChart(self.chartContainer)
        self.chartWidget.set_empty_state_text(
            self.tr("No hue histogram data available")
        )
        chart_layout = QVBoxLayout(self.chartContainer)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.addWidget(self.chartWidget)

        # Hue domain (degrees) the histogram operates in; updated by set_range.
        self._hue_domain = (0.0, 360.0)
        self.hueWheelSelector = HueRingSelector(self.rangeSliderContainer)
        slider_layout = QVBoxLayout(self.rangeSliderContainer)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.addWidget(self.hueWheelSelector)

        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.buttonBox.rejected.connect(self.close)
        self.resetRangeButton.clicked.connect(self.reset_range)
        self.resetZoomButton.clicked.connect(self.reset_zoom)
        self.showAoiOnlyCheckBox.toggled.connect(self._on_aoi_only_toggled)
        self.hueWheelSelector.valueChanged.connect(self._on_hue_ring_changed)
        self.chartWidget.hoveredRangeChanged.connect(self._on_hovered_range_changed)
        self.chartWidget.zoomRangeSelected.connect(self._on_chart_zoom_selected)
        self.chartWidget.zoomResetRequested.connect(self.reset_zoom)

    def set_histogram_context(self, histogram_context):
        """Load histogram context for HSV Hue."""
        self.histogram_context = histogram_context
        if not histogram_context:
            self.chartWidget.set_histogram_data(None)
            self.hueWheelSelector.setEnabled(False)
            self.minValueLabel.setText(self.tr("Minimum: --"))
            self.maxValueLabel.setText(self.tr("Maximum: --"))
            self.hoverInfoLabel.setText(
                self.tr("Hover over the histogram to inspect a hue band.")
            )
            self.resetZoomButton.setEnabled(False)
            return

        histogram_data = histogram_context['histogram_data']
        minimum = float(histogram_data['min_temperature'])
        maximum = float(histogram_data['max_temperature'])

        self.chartWidget.set_histogram_data(histogram_data)
        self.hueWheelSelector.setEnabled(True)
        self._hue_domain = (minimum, maximum)
        self.set_selected_range(minimum, maximum)
        self._update_hover_label(None)
        self._update_zoom_button_state()

    def set_selected_range(self, minimum, maximum, emit_signal=False):
        """Synchronize the chart and hue wheel to a selected range."""
        if not self.histogram_context:
            return

        h, h_minus, h_plus = self._range_to_hsv(float(minimum), float(maximum))
        self.hueWheelSelector.blockSignals(True)
        self.hueWheelSelector.set_values(h, h_minus, h_plus)
        self.hueWheelSelector.blockSignals(False)
        self.chartWidget.set_selection_range(minimum, maximum, emit_signal=False)
        self._update_range_labels(float(minimum), float(maximum))

        if emit_signal:
            self.rangeChanged.emit(float(minimum), float(maximum))

    def reset_range(self):
        """Reset the visible hue range to the full span."""
        if not self.histogram_context:
            return
        histogram_data = self.histogram_context['histogram_data']
        self.set_selected_range(
            histogram_data['min_temperature'],
            histogram_data['max_temperature'],
            emit_signal=True
        )

    def reset_zoom(self):
        """Reset histogram zoom to the full range."""
        if not self.histogram_context:
            return
        self.chartWidget.reset_view_range()
        self._update_zoom_button_state()

    def set_aoi_only_mode(self, enabled):
        """Update the chart to show only AOI/anomaly bins."""
        self.showAoiOnlyCheckBox.blockSignals(True)
        self.showAoiOnlyCheckBox.setChecked(bool(enabled))
        self.showAoiOnlyCheckBox.blockSignals(False)
        self.chartWidget.set_show_aoi_only(enabled)

    def closeEvent(self, event):
        self.dialogClosed.emit()
        super().closeEvent(event)

    def _on_hue_ring_changed(self, h, h_minus, h_plus):
        """Handle hue-ring updates (centre + range) from the shared selector."""
        minimum, maximum = self._hsv_to_range(h, h_minus, h_plus)
        self.set_selected_range(minimum, maximum, emit_signal=True)

    def _range_to_hsv(self, lower, upper):
        """Convert an absolute [lower, upper] hue range to the ring's
        normalized (centre, minus, plus) model (all 0-1)."""
        dmin, dmax = self._hue_domain
        span = dmax - dmin
        if span <= 0:
            return 0.0, 0.0, 0.0
        center = (lower + upper) / 2.0
        h = max(0.0, min(1.0, (center - dmin) / span))
        h_minus = max(0.0, min(1.0, (center - lower) / span))
        h_plus = max(0.0, min(1.0, (upper - center) / span))
        return h, h_minus, h_plus

    def _hsv_to_range(self, h, h_minus, h_plus):
        """Convert the ring's normalized (centre, minus, plus) model back to an
        absolute [lower, upper] hue range in the histogram domain."""
        dmin, dmax = self._hue_domain
        span = dmax - dmin
        lower = dmin + (h - h_minus) * span
        upper = dmin + (h + h_plus) * span
        lower = max(dmin, min(lower, dmax))
        upper = max(dmin, min(upper, dmax))
        if lower > upper:
            lower, upper = upper, lower
        return lower, upper

    def _on_aoi_only_toggled(self, checked):
        """Handle toggling between full and AOI-only histogram views."""
        self.chartWidget.set_show_aoi_only(checked)
        self.aoiOnlyModeChanged.emit(bool(checked))

    def _on_hovered_range_changed(self, hovered_range):
        """Relay hovered range changes and update the caption."""
        self._update_hover_label(hovered_range)
        self.hoveredRangeChanged.emit(hovered_range)

    def _on_chart_zoom_selected(self, minimum, maximum):
        """Apply histogram-only zoom from a drag gesture."""
        self.chartWidget.set_view_range(minimum, maximum)
        self._update_zoom_button_state()

    def _update_hover_label(self, hovered_range):
        """Update hover information text."""
        if hovered_range is None:
            self.hoverInfoLabel.setText(
                self.tr("Hover over the histogram to inspect a hue band.")
            )
            return

        lower, upper = hovered_range
        self.hoverInfoLabel.setText(
            self.tr("Hover hue: {value}°").format(
                value=str(int(round(float(lower))))
            )
        )

    def _update_range_labels(self, minimum, maximum):
        """Update the visible hue range labels."""
        self.minValueLabel.setText(
            self.tr("Minimum: {minimum}°").format(
                minimum=str(int(round(minimum)))
            )
        )
        self.maxValueLabel.setText(
            self.tr("Maximum: {maximum}°").format(
                maximum=str(int(round(maximum)))
            )
        )

    def _update_zoom_button_state(self):
        """Enable Reset Zoom only while zoomed in."""
        if not self.histogram_context:
            self.resetZoomButton.setEnabled(False)
            return

        histogram_data = self.histogram_context['histogram_data']
        full_min = float(histogram_data['min_temperature'])
        full_max = float(histogram_data['max_temperature'])
        view_min, view_max = self.chartWidget.view_range()
        zoomed = (
            abs(view_min - full_min) > 1e-6
            or abs(view_max - full_max) > 1e-6
        )
        self.resetZoomButton.setEnabled(zoomed)
