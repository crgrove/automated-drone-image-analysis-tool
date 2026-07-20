"""
ThermalHistogramController - Orchestrates the thermal histogram popup workflow.
"""

from PySide6.QtWidgets import QMessageBox

from core.services.LoggerService import LoggerService
from core.services.image.ThermalHistogramService import ThermalHistogramService
from core.views.images.viewer.dialogs.ThermalHistogramDialog import ThermalHistogramDialog
from helpers.TranslationMixin import TranslationMixin


class ThermalHistogramController(TranslationMixin):
    """Controller that bridges thermal viewer state with the histogram dialog."""

    def __init__(self, parent_viewer):
        self.parent = parent_viewer
        self.logger = LoggerService()
        self.service = ThermalHistogramService()

        self.dialog = None
        self.histogram_data = None
        self.current_image_index = None
        self.active_range = None
        self.hovered_range = None

    def open_dialog(self):
        """Open the thermal histogram dialog for the current image."""
        if not self.has_histogram_data():
            QMessageBox.information(
                self.parent,
                self.tr("Thermal Histogram Unavailable"),
                self.tr("No thermal temperature data is available for the current image.")
            )
            return

        dialog = self._ensure_dialog()
        dialog.set_histogram_data(self.histogram_data, self.parent.temperature_unit)
        dialog.set_selected_range(*self._effective_range())
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def on_temperature_data_updated(self, temperature_data, areas_of_interest):
        """Recompute histogram state after a new image loads."""
        if temperature_data is None:
            self.histogram_data = None
            self.current_image_index = self.parent.current_image
            self.active_range = None
            self.hovered_range = None
            if self.dialog and self.dialog.isVisible():
                self.dialog.close()
            return

        image_changed = self.current_image_index != self.parent.current_image
        self.current_image_index = self.parent.current_image

        self.histogram_data = self.service.build_histogram_data(
            temperature_data,
            areas_of_interest=areas_of_interest,
            temperature_unit=self.parent.temperature_unit,
        )

        if not self.histogram_data:
            self.active_range = None
            self.hovered_range = None
            return

        if image_changed or self.active_range is None:
            self.active_range = self._full_range()
            self.hovered_range = None
        else:
            self.active_range = self._clamp_range(*self.active_range)
            if self.hovered_range is not None:
                self.hovered_range = self._clamp_range(*self.hovered_range)

        if self.dialog and self.dialog.isVisible():
            self.dialog.set_histogram_data(self.histogram_data, self.parent.temperature_unit)
            self.dialog.set_selected_range(*self._effective_range())

    def get_visibility_mask(self):
        """Return the active temperature visibility mask."""
        if not self.has_histogram_data():
            return None

        active_min, active_max = self._effective_range()
        full_min, full_max = self._full_range()

        if abs(active_min - full_min) <= 1e-6 and abs(active_max - full_max) <= 1e-6:
            return None

        return self.service.build_temperature_mask(
            self.parent.thermal_controller.temperature_data,
            minimum=active_min,
            maximum=active_max,
        )

    def get_hover_mask(self):
        """Return the hover highlight mask for the currently hovered histogram bin."""
        if not self.has_histogram_data() or self.hovered_range is None:
            return None

        hover_min, hover_max = self.hovered_range
        hover_mask = self.service.build_temperature_mask(
            self.parent.thermal_controller.temperature_data,
            minimum=hover_min,
            maximum=hover_max,
        )

        visible_mask = self.get_visibility_mask()
        if visible_mask is not None:
            hover_mask &= visible_mask

        return hover_mask

    def has_histogram_data(self):
        """Return True when the current image has usable thermal histogram data."""
        return self.histogram_data is not None and self.parent.thermal_controller.temperature_data is not None

    def cleanup(self):
        """Release dialog resources on viewer shutdown."""
        if self.dialog:
            try:
                self.dialog.close()
            except Exception as exc:
                self.logger.error(f"Failed to close thermal histogram dialog: {exc}")
            self.dialog = None

    def _ensure_dialog(self):
        """Create the dialog lazily."""
        if self.dialog is None:
            self.dialog = ThermalHistogramDialog(self.parent)
            self.dialog.rangeChanged.connect(self._on_range_changed)
            self.dialog.hoveredRangeChanged.connect(self._on_hovered_range_changed)
            self.dialog.dialogClosed.connect(self._on_dialog_closed)
        return self.dialog

    def _on_range_changed(self, minimum, maximum):
        """Handle range selection updates from the dialog."""
        self.active_range = self._clamp_range(minimum, maximum)
        self._refresh_view_from_cache()

    def _on_hovered_range_changed(self, hovered_range):
        """Handle hover-based highlight updates from the dialog."""
        if hovered_range is None:
            changed = self.hovered_range is not None
            self.hovered_range = None
        else:
            clamped = self._clamp_range(*hovered_range)
            changed = self.hovered_range != clamped
            self.hovered_range = clamped

        if changed:
            self._refresh_view_from_cache()

    def _on_dialog_closed(self):
        """Reset transient histogram state when the popup closes."""
        if self.histogram_data:
            self.active_range = self._full_range()
        else:
            self.active_range = None
        self.hovered_range = None
        self.dialog = None
        self._refresh_view_from_cache()

    def _refresh_view_from_cache(self):
        """Refresh the displayed image without reloading metadata from disk."""
        if hasattr(self.parent, 'image_load_controller'):
            self.parent.image_load_controller.refresh_image_preserving_view_from_cache()

    def _full_range(self):
        """Return the full available histogram range."""
        return (
            float(self.histogram_data['min_temperature']),
            float(self.histogram_data['max_temperature']),
        )

    def _effective_range(self):
        """Return the active range or the full range if none is selected."""
        return self.active_range or self._full_range()

    def _clamp_range(self, minimum, maximum):
        """Clamp a temperature range to the currently loaded histogram bounds."""
        full_min, full_max = self._full_range()
        minimum = max(full_min, min(float(minimum), full_max))
        maximum = max(full_min, min(float(maximum), full_max))
        if minimum > maximum:
            minimum, maximum = maximum, minimum
        return minimum, maximum
