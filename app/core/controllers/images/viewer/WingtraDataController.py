"""WingtraDataController - the operator's side of loading a Wingtra CSV.

Prompts for the file, reports what matched, and writes the result into the
viewer's image dicts so every downstream consumer (R-key rotation, the GPS
map, KML export, coverage extent) picks it up through the ordinary
``image['bearing']`` path.

The CSV is found for the operator when the results open
(:meth:`WingtraDataController.auto_load_on_open`); Shift+W remains the
manual route.

The reading, matching and altitude work lives in
:mod:`core.services.image.WingtraDataService` - it is parsing and I/O, not UI
orchestration (CLAUDE.md 2.1) - and this class keeps the accessors
``ImageService`` calls into.
"""

import os
from typing import Dict, Optional, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QDialog, QInputDialog
)

from core.services.LoggerService import LoggerService
from core.services.image.WingtraDataService import (
    GEOTAGS_DECLINED,
    GEOTAGS_LOADED,
    METERS_TO_FEET,
    WingtraCsvCandidate,
    WingtraImageData,
    apply_geotag,
    compute_agl,
    find_wingtra_csvs,
    is_wingtra_image,
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

        # Session-only storage. Only the CSV's path is persisted (in
        # ADIAT_Data.xml); the data is re-read from it on each open.
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

    def prompt_and_load_csv(self, start_dir: Optional[str] = None):
        """Show file dialog and load Wingtra CSV data.

        Args:
            start_dir: Folder to open the dialog in; the last folder a CSV was
                picked from when None (Shift+W).
        """
        initial_dir = ""
        if start_dir and os.path.isdir(start_dir):
            initial_dir = start_dir
        elif hasattr(self.parent, 'settings_service'):
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

        self.load_csv(file_path, confirm=True)

    def auto_load_on_open(self):
        """Load, or offer, the run's Wingtra geotags when the results open.

        Shift+W is undiscoverable, and without the geotags every Wingtra
        footprint, bearing and AGL is quietly wrong. So, in order:

        - results already linked to a CSV reload it without asking (or stay
          quiet, if the operator declined it before);
        - otherwise a geotags CSV beside the source images is offered;
        - otherwise, for imagery that says it is Wingtra, the operator is
          asked whether to browse for the CSV.
        """
        if not self.parent.images:
            return

        link = self._get_geotags_link()
        if link is not None:
            if link['status'] == GEOTAGS_DECLINED:
                return
            if link['status'] == GEOTAGS_LOADED and os.path.isfile(link['csv_path']):
                self.load_csv(link['csv_path'], confirm=False)
                return
            # A linked CSV that has since moved falls through to a fresh search.

        image_paths = [img['path'] for img in self.parent.images if img.get('path')]
        candidates = find_wingtra_csvs(image_paths, self._result_image_names())

        if not candidates:
            if image_paths and is_wingtra_image(image_paths[0]):
                self._ask_to_browse(os.path.dirname(image_paths[0]))
            return

        chosen = self._ask_to_load(candidates)
        if chosen is None:
            self._set_geotags_link(candidates[0].path, GEOTAGS_DECLINED)
            return
        self.load_csv(chosen.path, confirm=False)

    def load_csv(self, file_path: str, confirm: bool) -> bool:
        """Read a Wingtra CSV, match it to the results and apply it.

        Args:
            file_path: The geotags CSV.
            confirm: Show the match summary and let the operator cancel. False
                when they have already agreed to this file.

        Returns:
            True when the data was applied.
        """
        parsed_data, errors = parse_wingtra_csv(file_path)

        if errors:
            self._show_parse_errors(errors)
            return False

        if not parsed_data:
            QMessageBox.warning(
                self.parent,
                self.tr("Empty CSV"),
                self.tr("The CSV file contains no valid data rows.")
            )
            return False

        matched, unmatched_csv, unmatched_images = match_image_names(
            parsed_data, self._result_image_names())

        if not matched:
            self._show_no_matches_error(unmatched_csv, unmatched_images)
            return False

        # Frames that produced no AOI need a bearing and an AGL too: coverage
        # extent and POD are computed over the whole flight, not the results.
        source_only, _, _ = match_image_names(
            parsed_data, self._source_only_image_names())
        applied = dict(source_only)
        applied.update(matched)

        # Per-image AGL from terrain elevation, geoid-corrected. A terrain
        # lookup per image takes seconds on a full flight.
        app = QApplication.instance()
        if app is not None:
            app.setOverrideCursor(Qt.WaitCursor)
        try:
            compute_agl(applied, logger=self.logger)
        finally:
            if app is not None:
                app.restoreOverrideCursor()
        # Reported against the results, which is what the operator matched.
        agl_count = sum(1 for data in matched.values() if data.altitude_agl is not None)

        if confirm:
            dialog = WingtraDataDialog(
                self.parent,
                matched_count=len(matched),
                unmatched_csv_count=len(unmatched_csv),
                unmatched_images_count=len(unmatched_images),
                agl_computed_count=agl_count,
                distance_unit=self._get_distance_unit()
            )

            if dialog.exec() != QDialog.Accepted:
                return False  # User cancelled

        # Store the data
        self.image_data = applied
        self.csv_path = file_path
        self.is_active = True

        # Inject bearing and AGL into image dicts so all consumers pick them up
        self._inject_into_image_dicts(applied)

        # Remember the link so reopening these results reloads it.
        self._set_geotags_link(file_path, GEOTAGS_LOADED)

        if agl_count > 0:
            msg = self.tr(
                "Wingtra data loaded: {matched} images matched, "
                "{agl} AGL computed"
            ).format(matched=len(matched), agl=agl_count)
        else:
            msg = self.tr(
                "Wingtra data loaded: {matched} images matched"
            ).format(matched=len(matched))
        self._show_toast(msg, 3000, color="#00C853")

        # Reload current image to apply overrides
        if hasattr(self.parent, 'image_load_controller'):
            self.parent.image_load_controller.load_image()
        return True

    def _ask_to_load(self, candidates: List[WingtraCsvCandidate]) -> Optional[WingtraCsvCandidate]:
        """Ask whether to load the geotags found; with several, which one.

        Returns:
            The chosen candidate, or None when the operator declined.
        """
        total = len(self._result_image_names())
        title = self.tr("Wingtra Geotags Found")
        later = self.tr("You can also load geotags later with Shift+W.")

        if len(candidates) == 1:
            candidate = candidates[0]
            text = self.tr(
                "Wingtra geotags found - Load?\n\n"
                "{file}\n"
                "{matched} of {total} images in these results match.\n\n"
                "{later}"
            ).format(file=candidate.path, matched=candidate.matched_count,
                     total=total, later=later)
            answer = QMessageBox.question(
                self.parent, title, text,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return candidate if answer == QMessageBox.Yes else None

        items = [
            self.tr("{file} ({matched} of {total} images match)").format(
                file=os.path.basename(c.path), matched=c.matched_count, total=total)
            for c in candidates
        ]
        text = self.tr(
            "Wingtra geotags found - Load?\n\n"
            "More than one geotags file matches these results. Choose one, "
            "or Cancel to skip.\n\n"
            "{later}"
        ).format(later=later)
        item, ok = QInputDialog.getItem(self.parent, title, text, items, 0, False)
        if not ok or item not in items:
            return None
        return candidates[items.index(item)]

    def _ask_to_browse(self, start_dir: str):
        """Wingtra imagery with no geotags CSV nearby: offer to pick one.

        Declining is remembered so reopening the results does not ask again;
        cancelling the file dialog is not, since the operator wanted the file
        and may simply not have found it yet.
        """
        answer = QMessageBox.question(
            self.parent,
            self.tr("Wingtra Imagery"),
            self.tr(
                "Load Wingtra GeoTag .csv file?\n\n"
                "These results are Wingtra imagery. Its geotags CSV supplies the "
                "camera orientation and altitude needed for accurate footprints, "
                "bearings and AGL.\n\n"
                "You can also load it later with Shift+W."
            ),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if answer != QMessageBox.Yes:
            self._set_geotags_link('', GEOTAGS_DECLINED)
            return
        self.prompt_and_load_csv(start_dir)

    def _get_geotags_link(self) -> Optional[dict]:
        """The CSV these results are linked to in ADIAT_Data.xml, if any."""
        xml_service = getattr(self.parent, 'xml_service', None)
        if xml_service is None:
            return None
        return xml_service.get_wingtra_geotags()

    def _set_geotags_link(self, csv_path: str, status: str):
        """Record the CSV link in ADIAT_Data.xml so the next open honours it.

        A write failure costs only the convenience on reopen, so it is
        logged rather than shown.
        """
        xml_service = getattr(self.parent, 'xml_service', None)
        xml_path = getattr(self.parent, 'xml_path', None)
        if xml_service is None or not xml_path:
            return
        try:
            xml_service.set_wingtra_geotags(csv_path, status)
            xml_service.save_xml_file(xml_path)
        except Exception as e:  # noqa: BLE001 - persistence is best-effort
            self.logger.error(f"Could not record Wingtra geotags link in {xml_path}: {e}")

    def _show_toast(self, text: str, msec: int, color: str):
        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast(text, msec, color=color)

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

    def _image_dicts(self):
        """Every image dict a geotag can land in: the results, then the
        flight's frames that produced no AOI (``parent.source_images``). A
        frame with an AOI is the same dict object in both lists, so each is
        yielded once."""
        seen = set()
        source_images = getattr(self.parent, 'source_images', None) or []
        for image in list(self.parent.images) + list(source_images):
            if id(image) in seen:
                continue
            seen.add(id(image))
            yield image

    def _source_only_image_names(self) -> List[str]:
        """Filenames of the flight's frames that are not in the results."""
        result_ids = {id(image) for image in self.parent.images}
        source_images = getattr(self.parent, 'source_images', None) or []
        return [image.get('name', '') for image in source_images
                if id(image) not in result_ids and image.get('name')]

    def _inject_into_image_dicts(self, matched: Dict[str, WingtraImageData]):
        """Inject bearing and per-image AGL into every image dict and gps_data.

        This ensures all consumers (R-key rotation, GPS map, KML export,
        coverage extent, POD) automatically get the Wingtra orientation data
        through the standard image['bearing'] path.
        """
        for image in self._image_dicts():
            name = image.get('name', '')
            data = matched.get(name)
            if data is None:
                continue

            apply_geotag(image, data)

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
        for image in self._image_dicts():
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
