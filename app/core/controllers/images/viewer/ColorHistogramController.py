"""
ColorHistogramController - Orchestrates the hue histogram popup workflow.
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from core.services.LoggerService import LoggerService
from core.services.image.ColorHistogramService import ColorHistogramService
from core.views.images.viewer.dialogs.ColorHistogramDialog import ColorHistogramDialog
from helpers.TranslationMixin import TranslationMixin


class ColorHistogramController(TranslationMixin):
    """Controller that bridges viewer state with the hue histogram dialog."""

    COLOR_SPACE = 'HSV'
    COMPONENT = 'H'

    def __init__(self, parent_viewer):
        self.parent = parent_viewer
        self.logger = LoggerService()
        self.service = ColorHistogramService()

        self.dialog = None
        self.current_image_index = None
        self.current_image_array = None
        self.current_aois = []
        self.current_context = None
        self.active_range = None
        self.show_aoi_only = False
        self.hovered_range = None

        # Cache for the active-range visibility mask, keyed by
        # (image_index, active_min, active_max). Avoids recomputing the same
        # full-image boolean mask twice per refresh (it is read both directly
        # and inside get_hover_mask).
        self._visibility_cache = None

        # Dragging the hue range / hovering the chart fires a storm of change
        # events, each of which would otherwise re-render the full-resolution
        # image synchronously. Coalesce them: state updates immediately (so the
        # dialog stays correct) but the heavy viewer refresh is debounced.
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(40)
        self._refresh_timer.timeout.connect(self._refresh_view_from_cache)

    def open_dialog(self):
        """Open the hue histogram dialog for the current image."""
        if self.parent.is_thermal:
            return

        if not self.has_histogram_data():
            QMessageBox.information(
                self.parent,
                self.tr("Hue Histogram Unavailable"),
                self.tr(
                    "No color image data is available for the"
                    " current image."
                )
            )
            return

        dialog = self._ensure_dialog()
        self._sync_dialog_state()
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def on_image_data_updated(self, image_array, areas_of_interest):
        """Recompute histogram state after a new non-thermal image loads."""
        if self.parent.is_thermal or image_array is None:
            self.current_context = None
            self.current_image_array = None
            self.current_aois = []
            self.active_range = None
            self.hovered_range = None
            if self.dialog and self.dialog.isVisible():
                self.dialog.close()
            return

        image_changed = self.current_image_index != self.parent.current_image
        self.current_image_index = self.parent.current_image
        self.current_image_array = image_array
        self.current_aois = areas_of_interest or []

        self._load_context(
            reset_range=image_changed or self.active_range is None
        )

        if self.dialog and self.dialog.isVisible():
            self._sync_dialog_state()

    def get_visibility_mask(self):
        """Return the active hue visibility mask."""
        if not self.has_histogram_data():
            return None

        active_min, active_max = self._effective_range()
        full_min, full_max = self._full_range()
        if (
            abs(active_min - full_min) <= 1e-6
            and abs(active_max - full_max) <= 1e-6
        ):
            return None

        cache_key = (
            self.current_image_index,
            round(active_min, 6),
            round(active_max, 6),
        )
        if self._visibility_cache is not None and self._visibility_cache[0] == cache_key:
            return self._visibility_cache[1]

        mask = self.service.build_component_mask(
            self.current_context['component_matrix'],
            minimum=active_min,
            maximum=active_max,
        )
        self._visibility_cache = (cache_key, mask)
        return mask

    def get_hover_mask(self):
        """Return the hover highlight mask for the current hue bin."""
        if not self.has_histogram_data() or self.hovered_range is None:
            return None

        hover_mask = self.service.build_component_mask(
            self.current_context['component_matrix'],
            minimum=self.hovered_range[0],
            maximum=self.hovered_range[1],
        )
        visible_mask = self.get_visibility_mask()
        if visible_mask is not None:
            hover_mask &= visible_mask
        return hover_mask

    def has_histogram_data(self):
        """Return True when the current image has usable histogram data."""
        return (
            self.current_context is not None
            and self.current_image_array is not None
            and not self.parent.is_thermal
        )

    def cleanup(self):
        """Release dialog resources on viewer shutdown."""
        self._refresh_timer.stop()
        if self.dialog:
            try:
                self.dialog.close()
            except Exception as exc:
                self.logger.error(
                    f"Failed to close hue histogram dialog: {exc}"
                )
            self.dialog = None

    def _ensure_dialog(self):
        """Create the dialog lazily."""
        if self.dialog is None:
            self.dialog = ColorHistogramDialog(self.parent)
            self.dialog.rangeChanged.connect(self._on_range_changed)
            self.dialog.aoiOnlyModeChanged.connect(
                self._on_aoi_only_mode_changed
            )
            self.dialog.hoveredRangeChanged.connect(
                self._on_hovered_range_changed
            )
            self.dialog.dialogClosed.connect(self._on_dialog_closed)
        return self.dialog

    def _get_context(self):
        """Build histogram context for the current HSV Hue state."""
        return self.service.build_histogram_context(
            self.current_image_array,
            self.COLOR_SPACE,
            self.COMPONENT,
            areas_of_interest=self.current_aois,
        )

    def _load_context(self, reset_range=False):
        """Load the active histogram context from cache/service."""
        self.current_context = self._get_context()
        if not self.current_context:
            self.active_range = None
            self.hovered_range = None
            return

        if reset_range or self.active_range is None:
            self.active_range = self._full_range()
            self.hovered_range = None
        else:
            self.active_range = self._clamp_range(*self.active_range)
            if self.hovered_range is not None:
                self.hovered_range = self._clamp_range(*self.hovered_range)

    def _sync_dialog_state(self):
        """Push the current controller state into the dialog."""
        dialog = self._ensure_dialog()
        dialog.set_histogram_context(self.current_context)
        if self.current_context:
            dialog.set_aoi_only_mode(self.show_aoi_only)
            dialog.set_selected_range(*self._effective_range())

    def _on_range_changed(self, minimum, maximum):
        """Handle range selection updates from the dialog."""
        self.active_range = self._clamp_range(minimum, maximum)
        self._schedule_refresh()

    def _on_aoi_only_mode_changed(self, checked):
        """Persist AOI-only chart display state."""
        self.show_aoi_only = bool(checked)

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
            self._schedule_refresh()

    def _on_dialog_closed(self):
        """Reset transient histogram state when the popup closes."""
        if self.current_context:
            self.active_range = self._full_range()
        else:
            self.active_range = None
        self.hovered_range = None
        self.dialog = None
        self._refresh_view_from_cache()

    def _schedule_refresh(self):
        """Debounce viewer re-renders triggered by rapid range/hover changes."""
        self._refresh_timer.start()

    def _refresh_view_from_cache(self):
        """Refresh the displayed image without reloading from disk."""
        self._refresh_timer.stop()
        if hasattr(self.parent, 'image_load_controller'):
            self.parent.image_load_controller \
                .refresh_image_preserving_view_from_cache()

    def _full_range(self):
        """Return the full available histogram range."""
        histogram_data = self.current_context['histogram_data']
        return (
            float(histogram_data['min_temperature']),
            float(histogram_data['max_temperature'])
        )

    def _effective_range(self):
        """Return the active range or the full range if none is selected."""
        return self.active_range or self._full_range()

    def _clamp_range(self, minimum, maximum):
        """Clamp a hue range to the current histogram bounds."""
        full_min, full_max = self._full_range()
        minimum = max(full_min, min(float(minimum), full_max))
        maximum = max(full_min, min(float(maximum), full_max))
        if minimum > maximum:
            minimum, maximum = maximum, minimum
        return minimum, maximum
