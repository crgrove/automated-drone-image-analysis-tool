"""
Image Capture page for the Image Analysis Guide wizard.
"""

import pandas as pd
import piexif
from pathlib import Path
import os

from .BasePage import BasePage
from helpers.PickleHelper import PickleHelper
from core.services.GSDService import GSDService
from core.services.image.ImageService import ImageService


class ImageCapturePage(BasePage):
    """Page for image capture information (drone, altitude, GSD)."""

    def __init__(self, wizard_data, settings_service, dialog):
        """Initialize the page."""
        super().__init__(wizard_data, settings_service, dialog)
        # Store camera groups: key = (manufacturer, model), value = list of sensor rows
        self.camera_groups = {}

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
        self._load_drone_data()
        self._load_preferences()

    def validate(self) -> bool:
        """Validate that capture information is set."""
        return True  # All fields have defaults

    def save_data(self):
        """Save capture information to wizard_data."""
        # Data is already saved via signal handlers
        pass

    def on_enter(self):
        """Called when entering the page."""
        # Trigger scan if we have input directory but no first image
        if self.wizard_data.get('input_directory') and not self.wizard_data.get('first_image_path'):
            self.scan_input_directory()

    def scan_input_directory(self):
        """Public method to trigger input directory scan."""
        self._scan_input_directory()

    def _load_drone_data(self):
        """Load drone data from pickle file and populate dropdown.

        Groups cameras by manufacturer + model, showing each camera only once.
        Stores all sensor configurations for each camera.
        """
        try:
            # Add default "Select Drone/Camera" option first
            self.dialog.droneComboBox.addItem("Select Drone/Camera", None)

            drones_df = PickleHelper.get_drone_sensor_info()
            if drones_df is None or drones_df.empty:
                self.dialog.droneComboBox.addItem("No drones available", None)
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
                # Use a special marker to identify section headers
                section_text = f"────── {make} ──────"
                self.dialog.droneComboBox.addItem(section_text, "__SECTION__")

                # Add all cameras for this manufacturer
                for model, sensor_rows in sorted(manufacturers[make], key=lambda x: x[0]):
                    display_text = f"  {model}"  # Indent models under manufacturer
                    # Store the first sensor row as the default selection
                    # All sensors will be available for GSD calculation
                    self.dialog.droneComboBox.addItem(display_text, sensor_rows[0])

            # Add "Other" option
            self.dialog.droneComboBox.addItem("──────────", "__SECTION__")
            self.dialog.droneComboBox.addItem("Other", None)

            # Try to load saved drone selection
            saved_drone_key = self.settings_service.get_setting("ImageAnalysisDroneSelection", "")
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
            print(f"Error loading drone data: {e}")
            self.dialog.droneComboBox.addItem("Error loading drone data", None)

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

        # Skip section headers - check if it's the special marker string
        # Handle both string comparison and pandas Series
        if isinstance(drone_data, str) and drone_data == "__SECTION__":
            return
        elif isinstance(drone_data, pd.Series):
            # If it's a Series, it's not a section header
            pass
        elif drone_data == "__SECTION__":
            # Fallback for other types
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
                # Try to convert if it's a dict or other type
                if isinstance(drone_data, dict):
                    drone_data = pd.Series(drone_data)
                else:
                    print(f"Warning: drone_data is unexpected type: {type(drone_data)}")
                    self.dialog.gsdTextEdit.setPlainText("-- (Invalid camera data)")
                    return

            self.wizard_data['drone'] = drone_data

            # Find all sensor configurations for this camera
            # Use .get() with default, then try direct access
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
            self.settings_service.set_setting("ImageAnalysisDroneSelection", drone_key)

            self._calculate_gsd()
        else:
            self.wizard_data['drone'] = None
            self.wizard_data['drone_sensors'] = []
            self.dialog.gsdTextEdit.setPlainText("--")
            # Clear saved selection if "Other" or "Select Drone/Camera" is selected
            self.settings_service.set_setting("ImageAnalysisDroneSelection", "")

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

        Calculates GSD for all sensor configurations of the selected camera.
        Uses GSDService directly, following the same pattern as ImageService.
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

            # Create ImageService once if we have an image (reuse for all sensors)
            image_service = None
            if self.wizard_data.get('first_image_path'):
                try:
                    image_service = ImageService(self.wizard_data['first_image_path'])
                except Exception as e:
                    print(f"Error creating ImageService: {e}")

            # Calculate GSD for each sensor configuration
            for sensor_idx, drone_data in enumerate(self.wizard_data['drone_sensors']):
                # Get camera parameters from drone data (following ImageService pattern)
                # ImageService.get_average_gsd() gets:
                # - focal_length from EXIF (not available in wizard)
                # - sensor_w, sensor_h from camera_info DataFrame
                # - image_width, image_height from EXIF

                sensor_width_mm = None
                sensor_height_mm = None
                image_width = 4000  # Default
                image_height = 3000  # Default
                focal_length_mm = None

                # Get sensor dimensions - ImageService uses 'sensor_w' and 'sensor_h' from camera_info
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

                # Get image dimensions from EXIF if we have an image, otherwise from database
                if image_service:
                    try:
                        exif_image_width = image_service.exif_data.get("Exif", {}).get(piexif.ExifIFD.PixelXDimension)
                        exif_image_height = image_service.exif_data.get("Exif", {}).get(piexif.ExifIFD.PixelYDimension)
                        if exif_image_width:
                            image_width = exif_image_width
                        if exif_image_height:
                            image_height = exif_image_height
                    except Exception:
                        pass

                # Fallback to database if image dimensions not available from EXIF
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

                # Try to get focal length from first image if available
                # Use ImageService.get_camera_intrinsics() which handles EXIF extraction
                if not focal_length_mm and image_service:
                    try:
                        intrinsics = image_service.get_camera_intrinsics()
                        if intrinsics:
                            focal_length_mm = intrinsics['focal_length_mm']
                    except Exception as e:
                        print(f"Error getting focal length from image: {e}")

                # Check for focal length in database (unlikely, but check anyway)
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

                # Skip if missing sensor dimensions
                if not sensor_width_mm or not sensor_height_mm:
                    continue

                # Use GSDService if we have all required parameters
                if focal_length_mm and sensor_width_mm and sensor_height_mm:
                    try:
                        # Use GSDService exactly as ImageService.get_average_gsd() does
                        # ImageService uses tilt_angle = 0 (nadir) when pitch is None
                        gsd_service = GSDService(
                            focal_length=focal_length_mm,
                            image_size=(image_width, image_height),
                            altitude=altitude_m,
                            tilt_angle=0,  # Assume nadir (same as ImageService default when pitch is None)
                            sensor=(sensor_width_mm, sensor_height_mm)
                        )

                        avg_gsd_cm = gsd_service.compute_average_gsd()

                        if avg_gsd_cm:
                            sensor_name = self._get_sensor_name(drone_data, sensor_idx)
                            # Round to 2 decimal places like ImageService does
                            gsd_results.append(f"{sensor_name}: {round(avg_gsd_cm, 2):.2f} cm/pixel")
                            self.wizard_data['gsd_list'].append({
                                'sensor_name': sensor_name,
                                'gsd': round(avg_gsd_cm, 2),
                                'sensor_data': drone_data
                            })
                    except Exception as e:
                        print(f"Error calculating GSD for sensor {sensor_idx}: {e}")
                        continue
                else:
                    # Missing focal length
                    sensor_name = self._get_sensor_name(drone_data, sensor_idx)
                    if self.wizard_data.get('first_image_path'):
                        gsd_results.append(f"{sensor_name}: Focal length not found in image EXIF")
                    else:
                        gsd_results.append(f"{sensor_name}: Select input directory to extract focal length from images")

            # Display results
            if gsd_results:
                self.dialog.gsdTextEdit.setPlainText("\n".join(gsd_results))
                self.wizard_data['gsd'] = None
            else:
                error_msg = "-- (Missing camera data)\n\n"
                error_msg += "Unable to calculate GSD. Sensor dimensions found, but:\n"
                error_msg += "• Focal length is required (available from image EXIF data)\n\n"
                error_msg += "GSD calculation requires an actual image file to extract focal length."
                self.dialog.gsdTextEdit.setPlainText(error_msg)
                self.wizard_data['gsd'] = None

        except Exception as e:
            print(f"Error calculating GSD: {e}")
            self.dialog.gsdTextEdit.setPlainText("-- (Error)")

    def _get_sensor_name(self, drone_data, sensor_idx):
        """Get a descriptive name for the sensor configuration."""
        # Try to identify sensor type
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
                sensor_parts.append(f"Sensor {sensor_idx + 1}")
            else:
                sensor_parts.append("Primary")

        return " / ".join(sensor_parts) if sensor_parts else "Sensor"

    def _scan_input_directory(self):
        """Scan input directory for first image and extract metadata to populate defaults."""
        input_dir = self.wizard_data.get('input_directory', '')
        if not input_dir or not os.path.isdir(input_dir):
            return

        # Find first image file
        image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.irg'}
        first_image_path = None

        try:
            # Walk through directory to find first image
            for root, dirs, files in os.walk(input_dir):
                for file in sorted(files):  # Sort for consistent selection
                    file_path = Path(file)
                    if file_path.suffix.lower() in image_extensions:
                        first_image_path = os.path.join(root, file)
                        break
                if first_image_path:
                    break
        except Exception as e:
            print(f"Error scanning input directory: {e}")
            return

        if not first_image_path or not os.path.exists(first_image_path):
            return

        self.wizard_data['first_image_path'] = first_image_path

        # Extract metadata from first image
        try:
            image_service = ImageService(first_image_path)

            # Get altitude from image
            altitude_m = image_service.get_relative_altitude('m')
            if altitude_m and altitude_m > 0:
                # Set altitude based on current unit preference
                if self.wizard_data['altitude_unit'] == 'ft':
                    altitude_ft = altitude_m * 3.28084
                    altitude_ft = max(0, min(600, altitude_ft))  # Clamp to slider range
                    self.dialog.altitudeSpinBox.setValue(int(altitude_ft))
                    self.wizard_data['altitude'] = altitude_ft
                else:
                    altitude_m = max(0, min(183, altitude_m))  # Clamp to slider range
                    self.dialog.altitudeSpinBox.setValue(int(altitude_m))
                    self.wizard_data['altitude'] = altitude_m

            # Get camera info to match drone selection
            # ImageService._get_camera_info() already matches the image to the database
            camera_info = image_service._get_camera_info()

            # Use ImageService's drone_make property (already extracted)
            make = image_service.drone_make

            # Get model from EXIF (ImageService doesn't expose this as a property)
            exif_model = image_service.exif_data.get("0th", {}).get(piexif.ImageIFD.Model)
            model = None
            if exif_model:
                model = exif_model.decode('utf-8').strip().rstrip("\x00")

            # If we have camera_info, use it directly to find the matching combo box item
            # camera_info is already filtered to match the image, so we can use it directly
            if camera_info is not None and not camera_info.empty:
                # Get the first row from camera_info (it's already matched)
                camera_row = camera_info.iloc[0]

                # Try to find this exact row in the combo box by matching key fields
                # We'll match on Manufacturer and Model (Exif) which should be unique
                camera_manufacturer = None
                camera_model_exif = None

                for key in ['Manufacturer', 'Make']:
                    if key in camera_row.index:
                        val = camera_row[key]
                        if pd.notna(val) and val != '':
                            camera_manufacturer = str(val).strip()
                            break

                for key in ['Model (Exif)', 'Model']:
                    if key in camera_row.index:
                        val = camera_row[key]
                        if pd.notna(val) and val != '':
                            camera_model_exif = str(val).strip()
                            break

                # Try to find exact match in combo box
                if camera_manufacturer and camera_model_exif:
                    for i in range(self.dialog.droneComboBox.count()):
                        drone_data = self.dialog.droneComboBox.itemData(i)

                        # Skip section headers and None items
                        if drone_data is None or (isinstance(drone_data, str) and drone_data == "__SECTION__"):
                            continue

                        if isinstance(drone_data, pd.Series):
                            # Check if this row matches our camera_info row
                            drone_manufacturer = None
                            drone_model_exif = None

                            for key in ['Manufacturer', 'Make']:
                                if key in drone_data.index:
                                    val = drone_data[key]
                                    if pd.notna(val) and val != '':
                                        drone_manufacturer = str(val).strip()
                                        break

                            for key in ['Model (Exif)', 'Model']:
                                if key in drone_data.index:
                                    val = drone_data[key]
                                    if pd.notna(val) and val != '':
                                        drone_model_exif = str(val).strip()
                                        break

                            # Exact match on manufacturer and model
                            if (drone_manufacturer and drone_model_exif and
                                    drone_manufacturer.lower() == camera_manufacturer.lower() and
                                    drone_model_exif.lower() == camera_model_exif.lower()):
                                self.dialog.droneComboBox.setCurrentIndex(i)
                                print(
                                    f"Matched camera using camera_info: "
                                    f"{camera_manufacturer} {camera_model_exif} -> "
                                    f"Selected index {i}"
                                )
                                # Recalculate GSD with focal length from image
                                self._calculate_gsd()
                                return  # Found exact match, we're done

            # Fallback: Try to find matching camera in dropdown using make/model
            if make and model:
                make_lower = make.lower().strip()
                model_lower = model.lower().strip()

                best_match_index = None
                best_match_score = 0

                for i in range(self.dialog.droneComboBox.count()):
                    drone_data = self.dialog.droneComboBox.itemData(i)

                    # Skip section headers and None items
                    if drone_data is None or (isinstance(drone_data, str) and drone_data == "__SECTION__"):
                        continue

                    if isinstance(drone_data, pd.Series):
                        drone_make = None
                        drone_model = None

                        for key in ['Make', 'Manufacturer']:
                            if key in drone_data.index:
                                val = drone_data[key]
                                if pd.notna(val) and val != '':
                                    drone_make = str(val).strip()
                                    break

                        for key in ['Model', 'Model (Exif)']:
                            if key in drone_data.index:
                                val = drone_data[key]
                                if pd.notna(val) and val != '':
                                    drone_model = str(val).strip()
                                    break

                        if drone_make and drone_model:
                            drone_make_lower = drone_make.lower()
                            drone_model_lower = drone_model.lower()

                            # Calculate match score
                            score = 0

                            # Exact match gets highest score
                            if make_lower == drone_make_lower:
                                score += 10
                            elif make_lower in drone_make_lower or drone_make_lower in make_lower:
                                score += 5

                            if model_lower == drone_model_lower:
                                score += 10
                            elif model_lower in drone_model_lower or drone_model_lower in model_lower:
                                score += 5

                            # If we have a good match, use it
                            if score > best_match_score:
                                best_match_score = score
                                best_match_index = i

                # Select the best match if we found one
                if best_match_index is not None and best_match_score >= 5:
                    self.dialog.droneComboBox.setCurrentIndex(best_match_index)
                    print(f"Matched camera: {make} {model} -> Selected index {best_match_index}")
                else:
                    print(f"Could not match camera: {make} {model} (best score: {best_match_score})")

            # Recalculate GSD with focal length from image
            self._calculate_gsd()

        except Exception as e:
            print(f"Error extracting metadata from first image: {e}")
