"""WingtraDataController - the operator's side of loading a Wingtra CSV.

Prompts for the file, reports what matched, and writes the result into the
viewer's image dicts so every downstream consumer (R-key rotation, the GPS
map, KML export, coverage extent) picks it up through the ordinary
``image['bearing']`` path.

The reading, matching and altitude work lives in
:mod:`core.services.image.WingtraDataService` - it is parsing and I/O, not UI
orchestration (CLAUDE.md 2.1) - and this class keeps the accessors
``ImageService`` calls into.
"""

import os
from typing import Dict, Optional, List

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog

from core.services.LoggerService import LoggerService
from core.services.image.WingtraDataService import (
    METERS_TO_FEET,
    WingtraImageData,
    compute_agl,
    kappa_to_bearing,
    match_image_names,
    parse_wingtra_csv,
    summarize_errors,
)
from core.views.images.viewer.dialogs.WingtraDataDialog import WingtraDataDialog
from helpers.TranslationMixin import TranslationMixin

# Example names shown when nothing matched; enough to spot a naming
# mismatch, few enough to stay readable in a message box.
_EXAMPLE_NAMES = 3


class WingtraDataController(TranslationMixin):
    """Controller for managing Wingtra CSV data overrides."""

    def __init__(self, parent_viewer):
        """Initialize the Wingtra data controller."""
        self.parent = parent_viewer
        self.logger = LoggerService()

        # Session-only storage (not persisted to XML)
        self.image_data: Dict[str, WingtraImageData] = {}
        self.csv_path: Optional[str] = None
        self.is_active: bool = False  # True when Wingtra data is loaded

    def _get_distance_unit(self) -> str:
        """Get user's preferred distance unit."""
        if hasattr(self.parent, 'settings_service'):
            unit = self.parent.settings_service.get_setting('DistanceUnit', 'Feet')
            if unit in ('Meters', 'm'):
                return 'm'
        return 'ft'

    def _result_image_names(self) -> List[str]:
        """Filenames of the loaded results, for matching against the CSV."""
        return [img.get('name', '') for img in self.parent.images
                if img.get('name')]

    def prompt_and_load_csv(self):
        """Show file dialog and load Wingtra CSV data."""
        # Get initial directory from settings if available
        initial_dir = ""
        if hasattr(self.parent, 'settings_service'):
            initial_dir = self.parent.settings_service.get_setting('LastWingtraFolder', '')
            if initial_dir and not os.path.exists(initial_dir):
                initial_dir = ""

        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            self.tr("Select Wingtra CSV File"),
            initial_dir,
            self.tr("CSV files (*.csv);;All files (*.*)")
        )

        if not file_path:
            return  # User cancelled

        # Save directory for next time
        if hasattr(self.parent, 'settings_service'):
            self.parent.settings_service.set_setting('LastWingtraFolder', os.path.dirname(file_path))

        parsed_data, errors = parse_wingtra_csv(file_path)

        if errors:
            self._show_parse_errors(errors)
            return

        if not parsed_data:
            QMessageBox.warning(
                self.parent,
                self.tr("Empty CSV"),
                self.tr("The CSV file contains no valid data rows.")
            )
            return

        matched, unmatched_csv, unmatched_images = match_image_names(
            parsed_data, self._result_image_names())

        if not matched:
            self._show_no_matches_error(unmatched_csv, unmatched_images)
            return

        # Per-image AGL from terrain elevation, geoid-corrected.
        agl_count = compute_agl(matched, logger=self.logger)

        # Show match summary dialog
        dialog = WingtraDataDialog(
            self.parent,
            matched_count=len(matched),
            unmatched_csv_count=len(unmatched_csv),
            unmatched_images_count=len(unmatched_images),
            agl_computed_count=agl_count,
            distance_unit=self._get_distance_unit()
        )

        if dialog.exec() != QDialog.Accepted:
            return  # User cancelled

        # Store the data
        self.image_data = matched
        self.csv_path = file_path
        self.is_active = True

        # Inject bearing and AGL into image dicts so all consumers pick them up
        self._inject_into_image_dicts(matched)

        # Show success toast
        if hasattr(self.parent, 'status_controller'):
            if agl_count > 0:
                msg = self.tr(
                    "Wingtra data loaded: {matched} images matched, "
                    "{agl} AGL computed"
                ).format(matched=len(matched), agl=agl_count)
            else:
                msg = self.tr(
                    "Wingtra data loaded: {matched} images matched"
                ).format(matched=len(matched))
            self.parent.status_controller.show_toast(msg, 3000, color="#00C853")

        # Reload current image to apply overrides
        if hasattr(self.parent, 'image_load_controller'):
            self.parent.image_load_controller.load_image()

    def _show_parse_errors(self, errors: List[str]):
        """Show CSV parsing errors to user."""
        QMessageBox.critical(
            self.parent,
            self.tr("CSV Parse Error"),
            self.tr("Failed to parse Wingtra CSV:\n\n{errors}").format(
                errors=summarize_errors(errors))
        )

    def _show_no_matches_error(self, unmatched_csv: List[str], unmatched_images: List[str]):
        """Show error when no images match."""
        # Show a few example names to help debugging
        csv_examples = list(unmatched_csv)[:_EXAMPLE_NAMES]
        img_examples = list(unmatched_images)[:_EXAMPLE_NAMES]

        msg = self.tr(
            "No images in the CSV match the current results.\n\n"
            "CSV images: {csv_count}\n"
            "Result images: {image_count}\n\n"
        ).format(csv_count=len(unmatched_csv), image_count=len(unmatched_images))

        if csv_examples:
            msg += self.tr("CSV examples: {names}\n").format(
                names=', '.join(csv_examples))
        if img_examples:
            msg += self.tr("Result examples: {names}\n").format(
                names=', '.join(img_examples))

        msg += self.tr("\nEnsure image filenames in the CSV match exactly.")

        QMessageBox.warning(
            self.parent,
            self.tr("No Matching Images"),
            msg
        )

    def _inject_into_image_dicts(self, matched: Dict[str, WingtraImageData]):
        """Inject bearing and per-image AGL into self.parent.images dicts and gps_data.

        This ensures all consumers (R-key rotation, GPS map, KML export,
        coverage extent) automatically get the Wingtra orientation data
        through the standard image['bearing'] path.
        """
        # Build lookup from image name -> image dict for quick access
        for image in self.parent.images:
            name = image.get('name', '')
            data = matched.get(name)
            if data is None:
                continue

            image['bearing'] = kappa_to_bearing(data.kappa)

            if data.altitude_agl is not None:
                image['wingtra_agl_ft'] = data.altitude_agl * METERS_TO_FEET

        # Also update gps_data entries (separate list used by GPS map)
        if hasattr(self.parent, 'gps_map_controller'):
            for entry in self.parent.gps_map_controller.gps_data:
                idx = entry.get('index')
                if idx is not None and 0 <= idx < len(self.parent.images):
                    img = self.parent.images[idx]
                    bearing = img.get('bearing')
                    if bearing is not None:
                        entry['bearing'] = bearing
                    agl = img.get('wingtra_agl_ft')
                    if agl is not None:
                        entry['wingtra_agl_ft'] = agl

    # Override getters for ImageService integration
    def get_wingtra_data(self, image_name: str) -> Optional[WingtraImageData]:
        """Get Wingtra data for a specific image."""
        if not self.is_active:
            return None
        return self.image_data.get(image_name)

    def get_camera_yaw(self, image_name: str) -> Optional[float]:
        """Get camera yaw as geographic bearing (CW from North)."""
        data = self.get_wingtra_data(image_name)
        if data:
            return kappa_to_bearing(data.kappa)
        return None

    def get_camera_pitch(self, image_name: str) -> Optional[float]:
        """Get camera pitch (phi) for image.

        Converts from Wingtra convention (0 = nadir) to standard
        photogrammetry convention (-90 = nadir, 0 = horizontal).
        """
        data = self.get_wingtra_data(image_name)
        if data:
            return data.phi - 90.0
        return None

    def get_gimbal_roll(self, image_name: str) -> Optional[float]:
        """Get gimbal roll (omega) for image."""
        data = self.get_wingtra_data(image_name)
        if data:
            return data.omega
        return None

    def get_altitude_agl_ft(self, image_name: str) -> Optional[float]:
        """Get per-image AGL altitude in feet, computed from terrain elevation.

        Args:
            image_name: Image filename.

        Returns:
            AGL altitude in feet, or None if not computed.
        """
        data = self.get_wingtra_data(image_name)
        if data and data.altitude_agl is not None:
            return data.altitude_agl * METERS_TO_FEET
        return None

    def clear_data(self):
        """Clear all Wingtra data and deactivate overrides."""
        # Remove injected values from image dicts
        for image in self.parent.images:
            image.pop('bearing', None)
            image.pop('wingtra_agl_ft', None)

        # Clear gps_data bearings and AGL
        if hasattr(self.parent, 'gps_map_controller'):
            for entry in self.parent.gps_map_controller.gps_data:
                entry['bearing'] = None
                entry.pop('wingtra_agl_ft', None)

        self.image_data = {}
        self.csv_path = None
        self.is_active = False
