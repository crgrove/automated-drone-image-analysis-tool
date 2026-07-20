"""
WingtraDataController - Handles Wingtra CSV data loading and session management.

Manages CSV parsing, image matching, per-image AGL computation via terrain
elevation, and provides override values for orientation and GSD calculations.
"""

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog

from core.services.LoggerService import LoggerService
from core.services.terrain.TerrainService import TerrainService
from core.views.images.viewer.dialogs.WingtraDataDialog import WingtraDataDialog


METERS_TO_FEET = 3.28084


@dataclass
class WingtraImageData:
    """Wingtra orientation and position data for a single image."""
    image_name: str
    latitude: float
    longitude: float
    altitude_asl: float  # meters (above sea level, from CSV)
    omega: float         # roll (degrees)
    phi: float           # pitch (degrees)
    kappa: float         # yaw (degrees)
    accuracy_h: float
    accuracy_v: float
    altitude_agl: Optional[float] = field(default=None)  # meters (computed)


class WingtraDataController:
    """Controller for managing Wingtra CSV data overrides."""

    REQUIRED_COLUMNS = [
        'image', 'latitude', 'longitude', 'altitude',
        'omega', 'phi', 'kappa'
    ]

    # Alternate column name mappings (case-insensitive, supports partial matches)
    # Wingtra format: "# image name", "latitude [decimal degrees]", etc.
    COLUMN_ALIASES = {
        'image': ['# image name', 'image name', 'image', 'image_name', 'filename', 'name', 'file'],
        'latitude': ['latitude [decimal degrees]', 'latitude', 'lat'],
        'longitude': ['longitude [decimal degrees]', 'longitude', 'lon', 'long'],
        'altitude': ['altitude [meter]', 'altitude [meters]', 'altitude', 'altitude_asl', 'alt', 'elevation'],
        'omega': ['omega [degrees]', 'omega [degree]', 'omega', 'roll'],
        'phi': ['phi [degrees]', 'phi [degree]', 'phi', 'pitch'],
        'kappa': ['kappa [degrees]', 'kappa [degree]', 'kappa', 'yaw', 'heading'],
        'accuracy_h': ['accuracy horizontal [meter]', 'accuracy horizontal [meters]',
                       'accuracy_h', 'accuracy_horizontal', 'h_accuracy', 'horizontal_accuracy'],
        'accuracy_v': ['accuracy vertical [meter]', 'accuracy vertical [meters]',
                       'accuracy_v', 'accuracy_vertical', 'v_accuracy', 'vertical_accuracy']
    }

    def __init__(self, parent_viewer):
        """Initialize the Wingtra data controller."""
        self.parent = parent_viewer
        self.logger = LoggerService()

        # Session-only storage (not persisted to XML)
        self.image_data: Dict[str, WingtraImageData] = {}
        self.csv_path: Optional[str] = None
        self.is_active: bool = False  # True when Wingtra data is loaded
        self._terrain_service: Optional[TerrainService] = None

    def _get_terrain_service(self) -> Optional[TerrainService]:
        """Lazily initialize terrain service."""
        if self._terrain_service is None:
            try:
                self._terrain_service = TerrainService()
            except Exception as e:
                self.logger.warning(f"Could not initialize terrain service: {e}")
        return self._terrain_service

    def _compute_agl_for_images(self, image_data: Dict[str, WingtraImageData]) -> int:
        """Compute per-image AGL using terrain elevation lookup.

        For each image, AGL = ASL altitude (from CSV) - ground elevation.
        Uses the geoid to convert between ellipsoidal (GPS/CSV) and
        orthometric (terrain) heights when available.

        Args:
            image_data: Dict of image name -> WingtraImageData

        Returns:
            Number of images where AGL was computed successfully.
        """
        terrain = self._get_terrain_service()
        if terrain is None:
            return 0

        computed = 0
        for data in image_data.values():
            result = terrain.get_elevation(data.latitude, data.longitude)
            if result.source == 'terrain' and result.elevation_m is not None:
                # CSV altitude is typically ellipsoidal (WGS84).
                # Terrain elevation is orthometric (EGM96).
                # Convert CSV altitude to orthometric for a proper AGL.
                asl_orthometric = data.altitude_asl
                if result.geoid_undulation_m is not None:
                    asl_orthometric = data.altitude_asl - result.geoid_undulation_m

                data.altitude_agl = max(1.0, asl_orthometric - result.elevation_m)
                computed += 1

        return computed

    def _get_distance_unit(self) -> str:
        """Get user's preferred distance unit."""
        if hasattr(self.parent, 'settings_service'):
            unit = self.parent.settings_service.get_setting('DistanceUnit', 'Feet')
            if unit in ('Meters', 'm'):
                return 'm'
        return 'ft'

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
            "Select Wingtra CSV File",
            initial_dir,
            "CSV files (*.csv);;All files (*.*)"
        )

        if not file_path:
            return  # User cancelled

        # Save directory for next time
        if hasattr(self.parent, 'settings_service'):
            self.parent.settings_service.set_setting('LastWingtraFolder', os.path.dirname(file_path))

        # Parse and validate CSV
        parsed_data, errors = self._parse_csv(file_path)

        if errors:
            self._show_parse_errors(errors)
            return

        if not parsed_data:
            QMessageBox.warning(
                self.parent,
                "Empty CSV",
                "The CSV file contains no valid data rows."
            )
            return

        # Match to current result images
        matched, unmatched_csv, unmatched_images = self._match_images(parsed_data)

        if not matched:
            self._show_no_matches_error(unmatched_csv, unmatched_images)
            return

        # Compute per-image AGL from terrain elevation
        agl_count = self._compute_agl_for_images(matched)

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
            msg = f"Wingtra data loaded: {len(matched)} images matched"
            if agl_count > 0:
                msg += f", {agl_count} AGL computed"
            self.parent.status_controller.show_toast(msg, 3000, color="#00C853")

        # Reload current image to apply overrides
        if hasattr(self.parent, 'image_load_controller'):
            self.parent.image_load_controller.load_image()

    def _parse_csv(self, file_path: str) -> Tuple[Dict[str, WingtraImageData], List[str]]:
        """
        Parse Wingtra CSV file.

        Returns:
            tuple: (parsed_data dict keyed by filename, error_list)
        """
        parsed_data = {}
        errors = []

        try:
            with open(file_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                # Validate columns exist
                if not reader.fieldnames:
                    errors.append("CSV file has no header row")
                    return {}, errors

                # Map actual column names to expected names
                column_map = self._build_column_map(reader.fieldnames)

                missing = [col for col in self.REQUIRED_COLUMNS if col not in column_map]
                if missing:
                    errors.append(f"Missing required columns: {', '.join(missing)}")
                    return {}, errors

                # Parse rows
                for row_num, row in enumerate(reader, start=2):
                    try:
                        image_name = row[column_map['image']].strip()
                        if not image_name:
                            continue

                        # Get accuracy values (optional)
                        accuracy_h = 0.0
                        accuracy_v = 0.0
                        if 'accuracy_h' in column_map:
                            try:
                                accuracy_h = float(row[column_map['accuracy_h']])
                            except (ValueError, KeyError):
                                pass
                        if 'accuracy_v' in column_map:
                            try:
                                accuracy_v = float(row[column_map['accuracy_v']])
                            except (ValueError, KeyError):
                                pass

                        data = WingtraImageData(
                            image_name=image_name,
                            latitude=float(row[column_map['latitude']]),
                            longitude=float(row[column_map['longitude']]),
                            altitude_asl=float(row[column_map['altitude']]),
                            omega=float(row[column_map['omega']]),
                            phi=float(row[column_map['phi']]),
                            kappa=float(row[column_map['kappa']]),
                            accuracy_h=accuracy_h,
                            accuracy_v=accuracy_v
                        )
                        parsed_data[image_name] = data

                    except (ValueError, KeyError) as e:
                        errors.append(f"Row {row_num}: {str(e)}")

        except FileNotFoundError:
            errors.append(f"File not found: {file_path}")
        except Exception as e:
            errors.append(f"Error reading CSV: {str(e)}")

        return parsed_data, errors

    def _build_column_map(self, fieldnames: List[str]) -> Dict[str, str]:
        """Build mapping from expected column names to actual CSV headers."""
        column_map = {}
        lower_fields = {f.lower().strip(): f for f in fieldnames}

        for expected, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                if alias.lower() in lower_fields:
                    column_map[expected] = lower_fields[alias.lower()]
                    break

        return column_map

    def _match_images(self, parsed_data: Dict[str, WingtraImageData]) -> Tuple[Dict[str, WingtraImageData], List[str], List[str]]:
        """
        Match CSV image names to result images.

        Returns:
            tuple: (matched_dict keyed by result image name, unmatched_csv_names, unmatched_image_names)
        """
        matched = {}

        # Get result image names
        result_names = set()
        result_name_map = {}  # lowercase -> original name
        for img in self.parent.images:
            name = img.get('name', '')
            if name:
                result_names.add(name)
                result_name_map[name.lower()] = name

        # Match CSV entries to result images
        matched_csv_names = set()
        for csv_name, data in parsed_data.items():
            # Try exact match first
            if csv_name in result_names:
                matched[csv_name] = data
                matched_csv_names.add(csv_name)
            else:
                # Try case-insensitive match
                csv_lower = csv_name.lower()
                if csv_lower in result_name_map:
                    result_name = result_name_map[csv_lower]
                    matched[result_name] = data
                    matched_csv_names.add(csv_name)

        # Find unmatched
        unmatched_csv = [name for name in parsed_data.keys() if name not in matched_csv_names]
        matched_result_names = set(matched.keys())
        unmatched_images = [name for name in result_names if name not in matched_result_names]

        return matched, unmatched_csv, unmatched_images

    def _show_parse_errors(self, errors: List[str]):
        """Show CSV parsing errors to user."""
        error_text = "\n".join(errors[:10])
        if len(errors) > 10:
            error_text += f"\n... and {len(errors) - 10} more errors"

        QMessageBox.critical(
            self.parent,
            "CSV Parse Error",
            f"Failed to parse Wingtra CSV:\n\n{error_text}"
        )

    def _show_no_matches_error(self, unmatched_csv: List[str], unmatched_images: List[str]):
        """Show error when no images match."""
        # Show a few example names to help debugging
        csv_examples = unmatched_csv[:3] if unmatched_csv else []
        img_examples = list(unmatched_images)[:3] if unmatched_images else []

        msg = (
            f"No images in the CSV match the current results.\n\n"
            f"CSV images: {len(unmatched_csv)}\n"
            f"Result images: {len(unmatched_images)}\n\n"
        )

        if csv_examples:
            msg += f"CSV examples: {', '.join(csv_examples)}\n"
        if img_examples:
            msg += f"Result examples: {', '.join(img_examples)}\n"

        msg += "\nEnsure image filenames in the CSV match exactly."

        QMessageBox.warning(
            self.parent,
            "No Matching Images",
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

            # Convert kappa (CCW, photogrammetric) to bearing (CW, geographic)
            bearing = (-data.kappa) % 360
            image['bearing'] = bearing

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
            # Convert kappa (CCW, photogrammetric) to bearing (CW, geographic)
            return (-data.kappa) % 360
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
