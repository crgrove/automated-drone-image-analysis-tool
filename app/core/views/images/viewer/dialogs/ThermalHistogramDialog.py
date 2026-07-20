"""
ThermalHistogramDialog - Popup dialog for thermal histogram interaction.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout

from core.views.images.viewer.ui.ThermalHistogramDialog_ui import Ui_ThermalHistogramDialog
from core.views.images.viewer.widgets.ThermalHistogramChart import ThermalHistogramChart
from core.views.images.viewer.widgets.ThermalRangeSlider import ThermalRangeSlider
from helpers.TranslationMixin import TranslationMixin


class ThermalHistogramDialog(TranslationMixin, QDialog, Ui_ThermalHistogramDialog):
    """Dialog that hosts the interactive temperature histogram widget."""

    rangeChanged = Signal(float, float)
    hoveredRangeChanged = Signal(object)
    dialogClosed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.temperature_unit = 'C'
        self.histogram_data = None

        self.chartWidget = ThermalHistogramChart(self.chartContainer)
        self.chartWidget.set_empty_state_text(
            self.tr("No thermal histogram data available")
        )
        chart_layout = QVBoxLayout(self.chartContainer)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.addWidget(self.chartWidget)

        self.rangeSlider = ThermalRangeSlider(self.rangeSliderContainer)
        slider_layout = QVBoxLayout(self.rangeSliderContainer)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.addWidget(self.rangeSlider)

        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.buttonBox.rejected.connect(self.close)
        self.resetRangeButton.clicked.connect(self.reset_range)
        self.resetZoomButton.clicked.connect(self.reset_zoom)
        self.rangeSlider.valuesChanged.connect(self._on_slider_range_changed)
        self.chartWidget.hoveredRangeChanged.connect(self._on_hovered_range_changed)
        self.chartWidget.zoomRangeSelected.connect(self._on_chart_zoom_selected)
        self.chartWidget.zoomResetRequested.connect(self.reset_zoom)

    def set_histogram_data(self, histogram_data, temperature_unit):
        """Load histogram data into the dialog."""
        self.histogram_data = histogram_data
        self.temperature_unit = temperature_unit or 'C'

        if not histogram_data:
            self.chartWidget.set_histogram_data(None)
            self.minValueLabel.setText(self.tr("Minimum: --"))
            self.maxValueLabel.setText(self.tr("Maximum: --"))
            self.hoverInfoLabel.setText(self.tr("Hover over the histogram to inspect a temperature band."))
            return

        minimum = float(histogram_data['min_temperature'])
        maximum = float(histogram_data['max_temperature'])

        self.chartWidget.set_histogram_data(histogram_data)
        self.rangeSlider.set_range(minimum, maximum)
        self.set_selected_range(minimum, maximum)
        self.resetZoomButton.setEnabled(False)
        self._update_hover_label(None)

    def set_selected_range(self, minimum, maximum, emit_signal=False):
        """Synchronize the chart and slider to a selected range."""
        if not self.histogram_data:
            return

        self.rangeSlider.blockSignals(True)
        self.rangeSlider.set_values(float(minimum), float(maximum), emit_signal=False)
        self.rangeSlider.blockSignals(False)

        self.chartWidget.set_selection_range(minimum, maximum, emit_signal=False)
        self._update_range_labels(float(minimum), float(maximum))

        if emit_signal:
            self.rangeChanged.emit(float(minimum), float(maximum))

    def reset_range(self):
        """Reset the selected range to the full histogram span."""
        if not self.histogram_data:
            return

        minimum = float(self.histogram_data['min_temperature'])
        maximum = float(self.histogram_data['max_temperature'])
        self.set_selected_range(minimum, maximum, emit_signal=True)

    def reset_zoom(self):
        """Reset the histogram x-axis zoom to the full range."""
        if not self.histogram_data:
            return

        self.chartWidget.reset_view_range()
        self._update_zoom_button_state()

    def closeEvent(self, event):
        self.dialogClosed.emit()
        super().closeEvent(event)

    def _on_slider_range_changed(self, minimum, maximum):
        """Handle two-handled slider updates."""
        self.set_selected_range(minimum, maximum, emit_signal=True)

    def _on_chart_zoom_selected(self, minimum, maximum):
        """Apply histogram-only zoom from a drag gesture."""
        self.chartWidget.set_view_range(minimum, maximum)
        self._update_zoom_button_state()

    def _on_hovered_range_changed(self, hovered_range):
        """Relay hovered range changes and update the caption."""
        self._update_hover_label(hovered_range)
        self.hoveredRangeChanged.emit(hovered_range)

    def _update_hover_label(self, hovered_range):
        """Update the hover information label."""
        if hovered_range is None:
            self.hoverInfoLabel.setText(self.tr("Hover over the histogram to inspect a temperature band."))
            return

        lower, upper = hovered_range
        self.hoverInfoLabel.setText(
            self.tr("Hover band: {lower:.1f} to {upper:.1f} °{unit}").format(
                lower=lower,
                upper=upper,
                unit=self.temperature_unit
            )
        )

    def _update_range_labels(self, minimum, maximum):
        """Update the visible temperature range labels."""
        self.minValueLabel.setText(
            self.tr("Minimum: {minimum:.1f} °{unit}").format(
                minimum=minimum,
                unit=self.temperature_unit
            )
        )
        self.maxValueLabel.setText(
            self.tr("Maximum: {maximum:.1f} °{unit}").format(
                maximum=maximum,
                unit=self.temperature_unit
            )
        )

    def _update_zoom_button_state(self):
        """Enable the zoom reset button only while zoomed in."""
        if not self.histogram_data:
            self.resetZoomButton.setEnabled(False)
            return

        full_min = float(self.histogram_data['min_temperature'])
        full_max = float(self.histogram_data['max_temperature'])
        view_min, view_max = self.chartWidget.view_range()
        zoomed = abs(view_min - full_min) > 1e-6 or abs(view_max - full_max) > 1e-6
        self.resetZoomButton.setEnabled(zoomed)
