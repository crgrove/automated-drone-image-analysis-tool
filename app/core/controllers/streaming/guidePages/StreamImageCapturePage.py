"""
Image Capture page for the Streaming Guide wizard.
"""

import pandas as pd
from .BasePage import BasePage
from helpers.PickleHelper import PickleHelper
from core.services.GSDService import GSDService
from core.services.LoggerService import LoggerService
from core.services.streaming.RTMPStreamService import SOURCE_TYPE_FILE
from core.services.telemetry.VideoCaptureInfoService import detect_capture_info
from helpers.FormatHelper import FormatHelper


class StreamImageCapturePage(BasePage):
    """Page for image capture information (drone, altitude, GSD) for streaming."""

    def __init__(self, wizard_data, settings_service, dialog):
        """Initialize the page."""
        super().__init__(wizard_data, settings_service, dialog)
        self.logger = LoggerService()
        # Store camera groups: key = (manufacturer, model), value = list of sensor rows
        self.camera_groups = {}
        # (video, metadata file) we have already auto-detected, so
        # re-entering the page (Back/Continue) does not re-probe the file or
        # stomp on an override the operator has since made.
        self._detected_for_path = None

    def setup_ui(self):
        """Initialize UI components."""
        # Set default altitude unit based on preference
        # Handle both 'Meters'/'Feet' (from UI) and 'm'/'ft' (legacy/internal) formats
        distance_unit = self.settings_service.get_setting('DistanceUnit', 'Feet')
        if distance_unit in ('Meters', 'm'):
            self.dialog.altitudeUnitComboBox.setCurrentIndex(1)
            self.wizard_data['altitude_unit'] = 'm'
        else:  # 'Feet' or 'ft' or default
            self.dialog.altitudeUnitComboBox.setCurrentIndex(0)
            self.wizard_data['altitude_unit'] = 'ft'

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.dialog.droneComboBox.currentIndexChanged.connect(self._on_drone_changed)
        self.dialog.altitudeSlider.valueChanged.connect(self._on_altitude_changed)
        self.dialog.altitudeSpinBox.valueChanged.connect(self._on_altitude_spinbox_changed)
        self.dialog.altitudeUnitComboBox.currentIndexChanged.connect(self._on_altitude_unit_changed)

    def load_data(self):
        """Load drone data and preferences."""
        # Initialize altitude if not set
        if 'altitude' not in self.wizard_data:
            self.wizard_data['altitude'] = self.dialog.altitudeSlider.value()
        self._load_drone_data()
        self._load_preferences()

    def on_enter(self) -> None:
        """Pre-fill drone and altitude from the video, if we can read them.

        Only for File sources — a live feed has no file to inspect, and
        its telemetry has not started arriving yet.
        """
        self._autodetect_from_video()

    def validate(self) -> bool:
        """Validate that capture information is set."""
        return True  # All fields have defaults

    # ------------------------------------------------------------------
    # auto-detection
    # ------------------------------------------------------------------

    def _autodetect_from_video(self) -> None:
        """Read the aircraft and altitude out of the selected video.

        Both drive GSD, and both are recorded in the file for DJI
        aircraft: the airframe in the container's ``encoder`` tag and the
        altitude in the embedded telemetry. Guessing them by hand is
        error-prone in a way that matters — GSD scales with altitude and
        detection area with GSD², so a 2x altitude error is a ~4x area
        error, and sibling airframes carry different sensors entirely.

        Values are pre-selected, never forced: the operator can change
        either afterwards, and a manual change is not overwritten if they
        navigate back to this page.
        """
        if self.wizard_data.get("stream_type", SOURCE_TYPE_FILE) != SOURCE_TYPE_FILE:
            return

        video_path = (self.wizard_data.get("stream_url") or "").strip()
        metadata_path = (self.wizard_data.get("metadata_path") or "").strip()
        if not video_path:
            return
        # Keyed on the pair: choosing a metadata file on the previous page is
        # exactly the case where re-probing is worth it, because the altitude
        # may only be readable from that file.
        signature = (video_path, metadata_path)
        if signature == self._detected_for_path:
            return
        self._detected_for_path = signature

        try:
            info = detect_capture_info(
                video_path, logger=self.logger, metadata_path=metadata_path or None
            )
        except Exception as e:  # noqa: BLE001 - detection is advisory
            self.logger.debug(f"Capture auto-detection failed: {e}")
            return

        if info.has_device:
            self._select_detected_drone(info.make, info.model)
        if info.has_altitude:
            self._apply_detected_altitude(
                info.altitude_m, info.altitude_reference)

    def _select_detected_drone(self, make: str, model: str) -> None:
        """Select the combo entry matching a detected make/model."""
        combo = self.dialog.droneComboBox
        for index in range(combo.count()):
            row = combo.itemData(index)
            if not isinstance(row, pd.Series):
                continue
            row_make = self._cell(row, 'Manufacturer', 'Make')
            row_model = self._cell(row, 'Model')
            if (row_make.lower() == str(make).lower()
                    and row_model.lower() == str(model).lower()):
                combo.setCurrentIndex(index)
                self.logger.info(
                    f"Auto-selected {make} {model} from video metadata"
                )
                return

    def _apply_detected_altitude(self, altitude_m: float,
                                 reference: str = None) -> None:
        """Set the altitude control from a detected altitude.

        Usually the detected value is the log's takeoff-relative reading
        (SRT ``rel_alt`` — ATO), while the field asks for height above the
        ground being flown over, which is what GSD depends on. The two
        agree over flat terrain and diverge with relief, so that is a
        starting point the operator is told to check rather than an
        answer; the field's hint says so. Left as an autofill on purpose:
        it is right often enough to be worth offering, and correcting the
        number here would need a DEM lookup per frame.

        A log that resolved its own terrain AGL answers the field exactly,
        and ``reference`` says which of the two arrived so the log line
        does not claim a plane the number was not measured from.

        Args:
            altitude_m: The detected altitude, in metres.
            reference: One of ``FormatHelper.ALTITUDE_REFERENCE_*``.
                Defaults to takeoff-relative, the historical assumption.
        """
        unit = self.wizard_data.get('altitude_unit', 'ft')
        value = altitude_m if unit == 'm' else altitude_m * 3.28084
        value = int(round(value))

        slider = self.dialog.altitudeSlider
        # Clamp into the control's range rather than silently dropping a
        # value the slider cannot represent.
        value = max(slider.minimum(), min(value, slider.maximum()))

        slider.setValue(value)
        self.dialog.altitudeSpinBox.setValue(value)
        self.wizard_data['altitude'] = value
        plane = FormatHelper.altitude_reference_abbreviation(
            reference or FormatHelper.ALTITUDE_REFERENCE_TAKEOFF
        )
        self.logger.info(
            f"Auto-set altitude to {value} {unit} {plane} from video telemetry"
        )

    @staticmethod
    def _cell(row, *keys) -> str:
        """First non-empty value among ``keys`` in a drone table row."""
        for key in keys:
            if key in row.index:
                value = row[key]
                if pd.notna(value) and str(value).strip():
                    return str(value).strip()
        return ""

    def save_data(self):
        """Save capture information to wizard_data."""
        # Data is already saved via signal handlers
        pass

    def _load_drone_data(self):
        """Load drone data from pickle file and populate dropdown.

        Groups cameras by manufacturer + model, showing each camera only once.
        Stores all sensor configurations for each camera.
        """
        try:
            # Add default "Select Drone/Camera" option first
            self.dialog.droneComboBox.addItem(self.tr("Select Drone/Camera"), None)

            drones_df = PickleHelper.get_drone_sensor_info()
            if drones_df is None or drones_df.empty:
                self.dialog.droneComboBox.addItem(self.tr("No drones available"), None)
                return

            # Group cameras by manufacturer + model (unique cameras)
            for _, row in drones_df.iterrows():
                # Try multiple possible column names for manufacturer and model
                make = row.get('Make', row.get('Manufacturer', 'Unknown'))
                model = row.get('Model', row.get('Model (Exif)', 'Unknown'))
                if pd.isna(make):
                    make = 'Unknown'
                if pd.isna(model):
                    model = 'Unknown'

                camera_key = (make, model)

                if camera_key not in self.camera_groups:
                    self.camera_groups[camera_key] = []

                # Store all sensor configurations for this camera
                self.camera_groups[camera_key].append(row)

            # Group by manufacturer for display
            manufacturers = {}
            for (make, model), sensor_rows in self.camera_groups.items():
                if make not in manufacturers:
                    manufacturers[make] = []
                manufacturers[make].append((model, sensor_rows))

            # Add cameras grouped by manufacturer with section labels
            for make in sorted(manufacturers.keys()):
                # Add manufacturer section label (as a separator-like item)
                section_text = f"────── {make} ──────"
                self.dialog.droneComboBox.addItem(section_text, "__SECTION__")

                # Add all cameras for this manufacturer
                for model, sensor_rows in sorted(manufacturers[make], key=lambda x: x[0]):
                    display_text = f"  {model}"  # Indent models under manufacturer
                    # Store the first sensor row as the default selection
                    self.dialog.droneComboBox.addItem(display_text, sensor_rows[0])

            # Add "Other" option
            self.dialog.droneComboBox.addItem("──────────", "__SECTION__")
            self.dialog.droneComboBox.addItem(self.tr("Other"), None)

            # Try to load saved drone selection
            saved_drone_key = self.settings_service.get_setting("StreamingDroneSelection", "")
            if saved_drone_key:
                # Find matching drone in combo box
                saved_parts = saved_drone_key.split("|")
                if len(saved_parts) == 2:
                    saved_make, saved_model = saved_parts
                    # Search for matching item
                    for i in range(self.dialog.droneComboBox.count()):
                        drone_data = self.dialog.droneComboBox.itemData(i)
                        if isinstance(drone_data, pd.Series):
                            make = None
                            model = None
                            for key in ['Make', 'Manufacturer']:
                                if key in drone_data.index:
                                    make = drone_data[key]
                                    if pd.notna(make):
                                        break
                            for key in ['Model', 'Model (Exif)']:
                                if key in drone_data.index:
                                    model = drone_data[key]
                                    if pd.notna(model):
                                        break
                            if (make and model and
                                str(make).strip() == saved_make.strip() and
                                    str(model).strip() == saved_model.strip()):
                                self.dialog.droneComboBox.setCurrentIndex(i)
                                return  # Found and set, exit early

            # Set default selection to first item (Select Drone/Camera)
            self.dialog.droneComboBox.setCurrentIndex(0)

        except Exception as e:
            self.logger.error(f"Error loading drone data: {e}")
            self.dialog.droneComboBox.addItem(self.tr("Error loading drone data"), None)

    def _load_preferences(self):
        """Load existing preferences if available."""
        # Load distance unit preference (already set in setup_ui, but ensure altitude is converted)
        # Handle both 'Meters'/'Feet' (from UI) and 'm'/'ft' (legacy/internal) formats
        distance_unit = self.settings_service.get_setting('DistanceUnit', 'Feet')
        preferred_unit = 'm' if distance_unit in ('Meters', 'm') else 'ft'

        # Get current altitude value (default is 100 feet)
        current_altitude = self.wizard_data.get('altitude', self.dialog.altitudeSlider.value())

        # Convert altitude value based on preferred unit
        # The default altitude (100) is always in feet, so if preference is meters, convert it
        if preferred_unit == 'm':
            # If altitude value looks like it's in feet (> 50 is reasonable threshold for meters),
            # convert it to meters. Otherwise assume it's already in meters.
            if current_altitude > 50:
                # Likely in feet, convert to meters
                altitude_m = int(current_altitude / 3.28084)
            else:
                # Likely already in meters
                altitude_m = int(current_altitude)
            altitude_m = max(0, min(183, altitude_m))  # Clamp to slider range
            self.dialog.altitudeSlider.setMaximum(183)  # ~600ft in meters
            self.dialog.altitudeSpinBox.setMaximum(183)
            self.dialog.altitudeSlider.setValue(altitude_m)
            self.dialog.altitudeSpinBox.setValue(altitude_m)
            self.wizard_data['altitude'] = altitude_m
        else:  # preferred_unit == 'ft'
            # If altitude value looks like it's in meters (< 50), convert it to feet
            # Otherwise assume it's already in feet
            if current_altitude < 50:
                # Likely in meters, convert to feet
                altitude_ft = int(current_altitude * 3.28084)
            else:
                # Likely already in feet
                altitude_ft = int(current_altitude)
            altitude_ft = max(0, min(600, altitude_ft))  # Clamp to slider range
            self.dialog.altitudeSlider.setMaximum(600)
            self.dialog.altitudeSpinBox.setMaximum(600)
            self.dialog.altitudeSlider.setValue(altitude_ft)
            self.dialog.altitudeSpinBox.setValue(altitude_ft)
            self.wizard_data['altitude'] = altitude_ft

    def _on_drone_changed(self, index):
        """Handle drone selection change."""
        if index < 0:
            return

        drone_data = self.dialog.droneComboBox.itemData(index)

        # Skip section headers
        if isinstance(drone_data, str) and drone_data == "__SECTION__":
            return
        elif isinstance(drone_data, pd.Series):
            pass
        elif drone_data == "__SECTION__":
            return

        # Handle default "Select Drone/Camera" option or None
        if drone_data is None:
            self.wizard_data['drone'] = None
            self.wizard_data['drone_sensors'] = []
            self.dialog.gsdTextEdit.setPlainText("--")
            return

        if drone_data is not None:
            # Ensure we have a pandas Series
            if not isinstance(drone_data, pd.Series):
                if isinstance(drone_data, dict):
                    drone_data = pd.Series(drone_data)
                else:
                    self.logger.warning(f"Warning: drone_data is unexpected type: {type(drone_data)}")
                    self.dialog.gsdTextEdit.setPlainText(self.tr("-- (Invalid camera data)"))
                    return

            self.wizard_data['drone'] = drone_data

            # Find all sensor configurations for this camera
            make = None
            for key in ['Make', 'Manufacturer']:
                if key in drone_data.index:
                    make = drone_data[key]
                    if pd.notna(make):
                        break

            model = None
            for key in ['Model', 'Model (Exif)']:
                if key in drone_data.index:
                    model = drone_data[key]
                    if pd.notna(model):
                        break

            if pd.isna(make) or make == '':
                make = 'Unknown'
            if pd.isna(model) or model == '':
                model = 'Unknown'

            camera_key = (make, model)
            if camera_key in self.camera_groups:
                self.wizard_data['drone_sensors'] = self.camera_groups[camera_key]
            else:
                self.wizard_data['drone_sensors'] = [drone_data]

            # Save drone selection to settings
            drone_key = f"{make}|{model}"
            self.settings_service.set_setting("StreamingDroneSelection", drone_key)

            self._calculate_gsd()
        else:
            self.wizard_data['drone'] = None
            self.wizard_data['drone_sensors'] = []
            self.dialog.gsdTextEdit.setPlainText("--")
            # Clear saved selection if "Other" or "Select Drone/Camera" is selected
            self.settings_service.set_setting("StreamingDroneSelection", "")

    def _on_altitude_changed(self, value):
        """Handle altitude slider change."""
        self.dialog.altitudeSpinBox.blockSignals(True)
        self.dialog.altitudeSpinBox.setValue(value)
        self.dialog.altitudeSpinBox.blockSignals(False)
        self.wizard_data['altitude'] = value
        self._calculate_gsd()

    def _on_altitude_spinbox_changed(self, value):
        """Handle altitude spinbox change."""
        self.dialog.altitudeSlider.blockSignals(True)
        self.dialog.altitudeSlider.setValue(value)
        self.dialog.altitudeSlider.blockSignals(False)
        self.wizard_data['altitude'] = value
        self._calculate_gsd()

    def _on_altitude_unit_changed(self, index):
        """Handle altitude unit change."""
        unit = 'ft' if index == 0 else 'm'
        self.wizard_data['altitude_unit'] = unit

        # Convert altitude value
        current_value = self.dialog.altitudeSlider.value()
        if unit == 'm':
            # Convert feet to meters
            new_value = int(current_value / 3.28084)
            new_max = 183  # ~600ft
        else:
            # Convert meters to feet
            new_value = int(current_value * 3.28084)
            new_max = 600

        self.dialog.altitudeSlider.setMaximum(new_max)
        self.dialog.altitudeSpinBox.setMaximum(new_max)
        self.dialog.altitudeSlider.setValue(new_value)
        self.dialog.altitudeSpinBox.setValue(new_value)
        self._calculate_gsd()

    def _calculate_gsd(self):
        """Calculate and display GSD based on selected drone and altitude.

        For streaming, we use default image dimensions since we don't have an image file.
        """
        if self.wizard_data.get('drone') is None or not self.wizard_data.get('drone_sensors'):
            self.dialog.gsdTextEdit.setPlainText("--")
            return

        try:
            # Get altitude in meters - use current slider value if not in wizard_data
            altitude = self.wizard_data.get('altitude')
            if altitude is None:
                altitude = self.dialog.altitudeSlider.value()
                self.wizard_data['altitude'] = altitude

            altitude_unit = self.wizard_data.get('altitude_unit', 'ft')
            if altitude_unit == 'ft':
                altitude_m = altitude / 3.28084
            else:
                altitude_m = altitude

            if altitude_m <= 0:
                self.dialog.gsdTextEdit.setPlainText("--")
                return

            gsd_results = []
            self.wizard_data['gsd_list'] = []

            # For streaming, use default image dimensions (no image file available)
            image_width = 4000  # Default
            image_height = 3000  # Default

            # Calculate GSD for each sensor configuration
            for sensor_idx, drone_data in enumerate(self.wizard_data['drone_sensors']):
                sensor_width_mm = None
                sensor_height_mm = None
                focal_length_mm = None

                # Get sensor dimensions
                if 'sensor_w' in drone_data.index:
                    val = drone_data['sensor_w']
                    if pd.notna(val) and val != '':
                        try:
                            sensor_width_mm = float(val)
                        except (ValueError, TypeError):
                            pass

                if 'sensor_h' in drone_data.index:
                    val = drone_data['sensor_h']
                    if pd.notna(val) and val != '':
                        try:
                            sensor_height_mm = float(val)
                        except (ValueError, TypeError):
                            pass

                # Get image dimensions from database
                if image_width == 4000 and 'Image Width' in drone_data.index:
                    val = drone_data['Image Width']
                    if pd.notna(val):
                        try:
                            if isinstance(val, str) and ',' in val:
                                widths = [int(w.strip()) for w in val.split(',')]
                                image_width = widths[0] if widths else 4000
                            else:
                                image_width = int(float(val))
                        except (ValueError, TypeError):
                            pass

                # Check for focal length in database
                if not focal_length_mm:
                    for key in ['Focal Length', 'FocalLength', 'focal_length', 'Focal Length (mm)']:
                        if key in drone_data.index:
                            val = drone_data[key]
                            if pd.notna(val) and val != '':
                                try:
                                    focal_length_mm = float(val)
                                    break
                                except (ValueError, TypeError):
                                    continue

                # For streaming videos from drones, use a reasonable default focal length if not found
                # Most drone wide cameras use ~8-10mm focal length (focus at infinity)
                if not focal_length_mm:
                    # Default to 8.8mm which is common for DJI wide cameras
                    # This is a reasonable approximation for drone video streams
                    focal_length_mm = 8.8
                    # self.logger.info(f"Using default focal length {focal_length_mm}mm for streaming video (focus at infinity)")

                # Skip if missing sensor dimensions
                if not sensor_width_mm or not sensor_height_mm:
                    continue

                # Use GSDService if we have all required parameters
                if focal_length_mm and sensor_width_mm and sensor_height_mm:
                    try:
                        gsd_service = GSDService(
                            focal_length=focal_length_mm,
                            image_size=(image_width, image_height),
                            altitude=altitude_m,
                            tilt_angle=0,  # Assume nadir
                            sensor=(sensor_width_mm, sensor_height_mm)
                        )

                        avg_gsd_cm = gsd_service.compute_average_gsd()

                        if avg_gsd_cm:
                            sensor_name = self._get_sensor_name(drone_data, sensor_idx)
                            gsd_results.append(f"{sensor_name}: {round(avg_gsd_cm, 2):.2f} cm/pixel")
                            self.wizard_data['gsd_list'].append({
                                'sensor_name': sensor_name,
                                'gsd': round(avg_gsd_cm, 2),
                                'sensor_data': drone_data
                            })
                    except Exception as e:
                        self.logger.error(f"Error calculating GSD for sensor {sensor_idx}: {e}")
                        continue
                else:
                    # Missing sensor dimensions (focal length should always be available now with default)
                    sensor_name = self._get_sensor_name(drone_data, sensor_idx)
                    gsd_results.append(self.tr("{sensor_name}: Sensor dimensions not available").format(sensor_name=sensor_name))

            # Display results
            if gsd_results:
                self.dialog.gsdTextEdit.setPlainText("\n".join(gsd_results))
                self.wizard_data['gsd'] = None
            else:
                error_msg = self.tr("-- (Missing camera data)") + "\n\n"
                error_msg += self.tr("Unable to calculate GSD. Sensor dimensions are required.")
                self.dialog.gsdTextEdit.setPlainText(error_msg)
                self.wizard_data['gsd'] = None

        except Exception as e:
            self.logger.error(f"Error calculating GSD: {e}")
            self.dialog.gsdTextEdit.setPlainText(self.tr("-- (Error)"))

    def _get_sensor_name(self, drone_data, sensor_idx):
        """Get a descriptive name for the sensor configuration."""
        sensor_parts = []

        # Check for Image Source (DJI)
        for key in ['Image Source (XMP)', 'ImageSource', 'Image Source']:
            try:
                if key in drone_data.index:
                    val = drone_data[key]
                    if pd.notna(val) and str(val).strip():
                        sensor_parts.append(str(val).strip())
                        break
            except (KeyError, ValueError, TypeError):
                continue

        # Check for Camera type (Autel)
        for key in ['Camera', 'Camera Type']:
            try:
                if key in drone_data.index:
                    val = drone_data[key]
                    if pd.notna(val) and str(val).strip():
                        sensor_parts.append(str(val).strip())
                        break
            except (KeyError, ValueError, TypeError):
                continue

        # If no specific identifier, use sensor index
        if not sensor_parts:
            if len(self.wizard_data['drone_sensors']) > 1:
                sensor_parts.append(self.tr("Sensor {n}").format(n=sensor_idx + 1))
            else:
                sensor_parts.append(self.tr("Primary"))

        return " / ".join(sensor_parts) if sensor_parts else self.tr("Sensor")
