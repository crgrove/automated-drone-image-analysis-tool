
import os
import piexif
import pandas as pd
import cv2
import numpy as np
import json
import math
import zlib
import base64
import tifffile
from PIL import Image

from core.services.GSDService import GSDService

from helpers.MetaDataHelper import MetaDataHelper
from helpers.PickleHelper import PickleHelper
from helpers.LocationInfo import LocationInfo


class ImageService:
    """Service to calculate various drone and image attributes based on metadata."""

    def __init__(self, path, mask_path=None, img_array=None, calculated_bearing=None):
        """
        Initializes the ImageService by extracting Exif and XMP metadata.

        Args:
            path (str): The file path to the image.
            mask_path (str, optional): Path to the mask file containing thermal metadata.
            img_array (np.ndarray, optional): Pre-loaded image array (RGB format).
                                              If provided, skips loading from disk.
            calculated_bearing (float, optional): Calculated bearing in degrees [0, 360).
                                                 Used as fallback if EXIF bearing is missing.
        """
        self.exif_data = MetaDataHelper.get_exif_data_piexif(path)
        self.xmp_data = MetaDataHelper.get_xmp_data_merged(path)
        self.drone_make = MetaDataHelper.get_drone_make(self.exif_data)
        self.path = path
        self.mask_path = mask_path
        self.calculated_bearing = calculated_bearing

        # Use pre-loaded array if provided, otherwise load from disk
        if img_array is not None:
            self.img_array = img_array
        else:
            img = cv2.imdecode(np.fromfile(self.path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError(f"Could not load image: {self.path}")
            self.img_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def get_relative_altitude(self, distance_unit= 'm'):
        """
        Retrieves the drone's relative altitude from metadata.

        Args:
            distance_unit (str): Unit to return altitude in ('ft' or 'm').

        Returns:
            float or None: Relative altitude in the specified unit, or None if unavailable.
        """
        METERS_TO_FEET = 3.28084
        if self.xmp_data is None or self.drone_make is None:
            return None

        altitude_meters = MetaDataHelper.get_drone_xmp_attribute('AGL', self.drone_make, self.xmp_data)

        if altitude_meters:
            try:
                altitude_meters = float(altitude_meters)
                return round(altitude_meters * METERS_TO_FEET, 2) if distance_unit == 'ft' else altitude_meters
            except ValueError:
                return None
        return None

    def get_asl_altitude(self, distance_unit):
        """Retrieve the drone's altitude above sea level from EXIF data.

        Args:
            distance_unit (str): Unit to return altitude in ("ft" or "m").

        Returns:
            float or None: Altitude in the requested unit, or None if unavailable.
        """
        METERS_TO_FEET = 3.28084

        if self.exif_data is None:
            return None

        gps_ifd = self.exif_data.get("GPS")
        if not gps_ifd:
            return None

        altitude = gps_ifd.get(piexif.GPSIFD.GPSAltitude)
        if altitude is None:
            return None

        try:
            if isinstance(altitude, tuple):
                altitude = altitude[0] / altitude[1]
            else:
                altitude = float(altitude)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

        ref = gps_ifd.get(piexif.GPSIFD.GPSAltitudeRef, 0)
        if ref == 1:
            altitude = -altitude

        return round(altitude * METERS_TO_FEET, 2) if distance_unit == 'ft' else altitude

    def get_camera_pitch(self):
        """
        Get camera pitch angle (standard photogrammetry convention).
        
        Convention: -90° = nadir (straight down), 0° = horizontal, +90° = straight up.

        Returns:
            float or None: Camera pitch in degrees (-90 to +90), or None if unavailable.
        """
        if self.xmp_data is None or self.drone_make is None:
            return None

        pitch = MetaDataHelper.get_drone_xmp_attribute('Gimbal Pitch', self.drone_make, self.xmp_data)
        if pitch is None:
            return None
        
        try:
            pitch = float(pitch)
        except (TypeError, ValueError):
            return None
        
        # Normalize to [-180, 180] range
        while pitch > 180:
            pitch -= 360
        while pitch < -180:
            pitch += 360
        
        # For DJI drones, gimbal pitch is already in the correct convention
        # (-90 = nadir, 0 = horizontal, +90 = up)
        # For Autel, may need different handling (add if needed)
        
        return pitch

    def get_gimbal_roll(self):
        """Retrieve gimbal roll from XMP metadata.

        Returns:
            float or None: Roll in degrees, or None if unavailable.
        """
        if self.xmp_data is None or self.drone_make is None:
            return None

        roll = MetaDataHelper.get_drone_xmp_attribute('Gimbal Roll', self.drone_make, self.xmp_data)
        try:
            return float(roll)
        except (TypeError, ValueError):
            return None

    def get_camera_yaw(self):
        """
        Get the camera yaw/bearing (direction the camera is pointing).

        Priority order:
        1. Gimbal Yaw (actual camera direction) - most accurate
        2. Flight Yaw (drone body direction) - fallback from EXIF
        3. Calculated Bearing (from track/GPS) - fallback from bearing recovery

        Returns:
            float or None: Camera yaw in degrees (0-360), or None if unavailable.
        """
        # Prefer gimbal yaw if available (actual camera direction)
        if self.xmp_data is not None and self.drone_make is not None:
            gimbal_yaw = MetaDataHelper.get_drone_xmp_attribute('Gimbal Yaw', self.drone_make, self.xmp_data)
            if gimbal_yaw is not None:
                try:
                    yaw = float(gimbal_yaw)
                    if yaw < 0:
                        yaw += 360
                    return yaw
                except (TypeError, ValueError):
                    pass

        # Fall back to flight yaw (drone body direction)
        flight_yaw = self._get_drone_orientation()
        if flight_yaw is not None:
            return flight_yaw

        # Final fallback: use calculated bearing if available
        if self.calculated_bearing is not None:
            return self.calculated_bearing

        return None

    def get_camera_intrinsics(self):
        """
        Get camera intrinsics for photogrammetric calculations.

        Returns:
            dict or None: Dictionary with 'focal_length_mm', 'sensor_width_mm', 'sensor_height_mm',
                         or None if camera info is unavailable.
        """
        # Get focal length from EXIF
        focal_length = self.exif_data["Exif"].get(piexif.ExifIFD.FocalLength)
        if focal_length is None:
            return None
        focal_length_mm = focal_length[0] / focal_length[1]

        # Get sensor size from camera database
        camera_info = self._get_camera_info()
        if camera_info is None or camera_info.empty:
            return None

        sensor_width_mm = float(camera_info['sensor_w'].iloc[0])
        sensor_height_mm = float(camera_info['sensor_h'].iloc[0])

        return {
            'focal_length_mm': focal_length_mm,
            'sensor_width_mm': sensor_width_mm,
            'sensor_height_mm': sensor_height_mm
        }

    def get_camera_hfov(self):
        """Compute the camera's horizontal field of view in degrees.

        Returns:
            float or None: Horizontal FOV in degrees, or None if data missing.
        """
        camera_info = self._get_camera_info()
        if camera_info is None or camera_info.empty:
            return None

        focal_length = self.exif_data["Exif"].get(piexif.ExifIFD.FocalLength)
        if focal_length is None:
            return None
        focal_length = focal_length[0] / focal_length[1]

        sensor_w = float(camera_info['sensor_w'].iloc[0])
        hfov = 2 * math.atan(sensor_w / (2 * focal_length))
        return math.degrees(hfov)

    def get_average_gsd(self, custom_altitude_ft=None):
        """
        Computes the estimated average Ground Sampling Distance (GSD).

        Args:
            custom_altitude_ft (float, optional): Custom altitude in feet to use instead of XMP data.
                                                  Useful when XMP altitude is negative or incorrect.

        Returns:
            float or None: Average GSD in cm/pixel, or None if required data is missing.
        """
        image_width = self.exif_data["Exif"].get(piexif.ExifIFD.PixelXDimension)
        image_height = self.exif_data["Exif"].get(piexif.ExifIFD.PixelYDimension)

        model = self.exif_data["0th"].get(piexif.ImageIFD.Model)
        if model:
            model = model.decode('utf-8').strip().rstrip("\x00")
        if not model or not self.drone_make:
            return None

        focal_length = self.exif_data["Exif"].get(piexif.ExifIFD.FocalLength)
        if focal_length is None:
            return None
        focal_length = focal_length[0] / focal_length[1]

        # Use custom altitude if provided, otherwise get from XMP
        if custom_altitude_ft is not None and custom_altitude_ft > 0:
            # Convert feet to meters
            altitude_meters = custom_altitude_ft / 3.28084
        else:
            altitude_meters = self.get_relative_altitude()
        
        if altitude_meters is None:
            return None

        # Get camera pitch and convert to tilt angle from nadir
        # Pitch: -90° = nadir, 0° = horizontal → Tilt: 0° = nadir, 90° = horizontal
        pitch = self.get_camera_pitch()
        if pitch is None:
            tilt_angle = 0  # Assume nadir if not available
        else:
            tilt_angle = 90 + pitch
            tilt_angle = max(0, min(90, tilt_angle))  # Clamp to [0, 90]

        if tilt_angle > 60:
            return None  # Too oblique for accurate GSD calculation

        camera_info = self._get_camera_info()

        if camera_info is None:
            return None
        if camera_info.empty:
            return None

        sensor_w = float(camera_info['sensor_w'].iloc[0])
        sensor_h = float(camera_info['sensor_h'].iloc[0])
        sensor = (sensor_w, sensor_h)

        gsd_service = GSDService(
            focal_length=focal_length,
            image_size=(image_width, image_height),
            altitude=altitude_meters,
            tilt_angle=tilt_angle,
            sensor=sensor
        )
        return round(gsd_service.compute_average_gsd(), 2)

    def get_position(self, position_format = 'Lat/Long - Decimal Degrees'):
        """
        Formats the GPS position based on the specified output format.

        Args:
            position_format (str): One of 'Lat/Long - Decimal Degrees',
                                   'Lat/Long - Degrees, Minutes, Seconds', or 'UTM'.

        Returns:
            str or None: Formatted position string or None if GPS data unavailable.
        """
        gps_coords = LocationInfo.get_gps(exif_data=self.exif_data)
        if gps_coords is None or gps_coords == {}:
            return None

        if position_format == 'Lat/Long - Decimal Degrees':
            return f"{gps_coords['latitude']}, {gps_coords['longitude']}"
        elif position_format == 'Lat/Long - Degrees, Minutes, Seconds':
            dms = LocationInfo.convert_decimal_to_dms(gps_coords['latitude'], gps_coords['longitude'])
            return (
                f"{dms['latitude']['degrees']}°{dms['latitude']['minutes']}'{dms['latitude']['seconds']}\"{dms['latitude']['reference']} "
                f"{dms['longitude']['degrees']}°{dms['longitude']['minutes']}'{dms['longitude']['seconds']}\"{dms['longitude']['reference']}"
            )
        elif position_format == 'UTM':
            utm = LocationInfo.convert_degrees_to_utm(gps_coords['latitude'], gps_coords['longitude'])
            return f"{utm['zone_number']}{utm['zone_letter']} {utm['easting']} {utm['northing']}"

    def get_thermal_data(self, unit):
        """
        Loads thermal data from a multi-band mask GeoTIFF.
        Band 0 = mask, Bands 1..N = temperature data.

        Args:
            unit (str): Temperature unit ('C' or 'F').

        Returns:
            np.ndarray or None: Temperature data array in the specified unit.
        """
        if not self.mask_path or not os.path.exists(self.mask_path):
            return None

        try:
            # Read all bands from the TIFF
            data = tifffile.imread(self.mask_path)

            # Ensure 3D shape (bands, height, width)
            if data.ndim == 2:
                # Only one band, no thermal data
                return None
            elif data.ndim == 3:
                # (bands, height, width)
                if data.shape[0] < 2:
                    return None  # no thermal bands present
                # Take only the first thermal band (band 1) for backward compatibility
                # Most thermal algorithms only store one temperature band anyway
                thermal_data = data[1].astype(np.float32)  # Shape: (height, width)
            else:
                return None

            # Convert units if needed
            if unit.upper() == 'F':
                thermal_data = thermal_data * 1.8 + 32.0

            return thermal_data

        except Exception as e:
            print(f"Warning: Failed to read thermal data from {self.mask_path}: {e}")
            return None

    def _is_autel(self):
        """
        Checks if the drone is made by Autel

        Returns:
            boolean: True if the drone is an Autel
        """
        return self.drone_make in ('Autel', 'Autel Robotics')

    def _get_camera_info(self):
        """
        Retrieves camera specification information from a drone metadata lookup table.

        This method uses EXIF and XMP metadata to determine the drone's camera model,
        image source, and ISO sensitivity, then filters the drone metadata DataFrame
        to return the matching camera configuration.

        Returns:
            pandas.DataFrame or None: A filtered DataFrame containing camera specifications
            that match the current image's metadata, or None if the model or drone make is not found.
        """
        drones_df = PickleHelper.get_drone_sensor_info()

        # Check if drones_df was loaded successfully
        if drones_df is None or drones_df.empty:
            return None

        model = self.exif_data["0th"].get(piexif.ImageIFD.Model)
        if model:
            model = model.decode('utf-8').strip().rstrip("\x00")
        if not model or not self.drone_make:
            return None

        # Try multiple ways to get ImageSource
        image_source = MetaDataHelper.get_drone_xmp_attribute('ImageSource', self.drone_make, self.xmp_data)
        if not image_source:
            # Try direct lookup in xmp_data with various keys
            for key in ['ImageSource', 'XMP:ImageSource', 'drone-dji:ImageSource']:
                if key in self.xmp_data:
                    image_source = self.xmp_data[key]
                    break

        image_width = self.exif_data["Exif"].get(piexif.ExifIFD.PixelXDimension)

        iso = self.exif_data["Exif"].get(piexif.ExifIFD.ISOSpeedRatings)
        if image_source is not None and self.drone_make == 'DJI':
            def image_width_matches(row):
                # Skip width check if no width is specified in the row
                if pd.isna(row['Image Width']) or not str(row['Image Width']).strip():
                    return True
                # Handle multiple widths in the cell
                widths = [int(w.strip()) for w in str(row['Image Width']).replace(',', ' ').split()]
                return image_width in widths

            matching_rows = drones_df[
                (drones_df['Manufacturer'] == 'DJI') &
                (drones_df['Model (Exif)'].str.contains(model, na=False)) &
                (drones_df['Image Source (XMP)'] == image_source)
            ]

            matching_rows = matching_rows[matching_rows.apply(image_width_matches, axis=1)]

            return matching_rows
        elif self._is_autel():
            if iso == 0:
                return drones_df[
                    (drones_df['Model (Exif)'] == model) &
                    (drones_df['Camera'] == 'Thermal')
                ]
            else:
                return drones_df[
                    (drones_df['Model (Exif)'] == model) &
                    (drones_df['Camera'] != 'Thermal')
                ]
        else:
            return drones_df[
                (drones_df['Model (Exif)'] == model)
            ]

    def _get_drone_orientation(self):
        """
        Retrieves the yaw orientation of the drone body (0–360 degrees).
        
        Private method - use get_camera_yaw() instead for the camera direction.

        Returns:
            float or None: Yaw in degrees, or None if unavailable.
        """
        if self.xmp_data is None or self.drone_make is None:
            return None

        yaw = MetaDataHelper.get_drone_xmp_attribute('Flight Yaw', self.drone_make, self.xmp_data)
        if yaw is None:
            return None

        yaw = float(yaw)
        return 360 + yaw if yaw < 0 else yaw
        
    def circle_areas_of_interest(self, identifier_color, areas_of_interest):
        """
        Augments the image with contour outlines or circles for areas of interest.

        Returns:
            (augmented_image: np.ndarray, areas_of_interest: list[dict])
        """
        image_copy = self.img_array.copy()

        # Expect identifier_color as RGB; OpenCV uses BGR
        bgr = (int(identifier_color[2]), int(identifier_color[1]), int(identifier_color[0]))

        for aoi in areas_of_interest or []:
            # Get center and radius for circle drawing
            cx, cy = aoi.get("center", (0, 0))
            r = int(aoi.get("radius", 0))
            center = (int(cx), int(cy))

            # Draw contour outline if available (this is the actual combined boundary)
            if "contour" in aoi and aoi["contour"] and len(aoi["contour"]) > 2:
                # Convert contour points back to numpy array format for OpenCV
                contour = np.array(aoi["contour"], dtype=np.int32)
                if len(contour.shape) == 2:
                    contour = contour.reshape((-1, 1, 2))
                # Draw contour with solid line
                cv2.polylines(image_copy, [contour], True, bgr, thickness=2)

                # Also draw the minimum enclosing circle with dotted line for reference
                if r > 0:
                    # Draw dotted circle by drawing small arcs
                    for angle in range(0, 360, 10):
                        start_angle = angle
                        end_angle = angle + 5
                        cv2.ellipse(image_copy, center, (r, r), 0, start_angle, end_angle, bgr, thickness=1)
            elif r > 0:
                # Fallback to circle if no contour data (for backward compatibility)
                cv2.circle(image_copy, center, r, bgr, thickness=2)

            # Add confidence label if available
            if "confidence" in aoi:
                confidence = aoi["confidence"]
                # Position label above the AOI circle
                label_pos = (int(cx - r), int(cy - r - 10))
                # Ensure label stays within image bounds
                label_pos = (max(5, label_pos[0]), max(20, label_pos[1]))

                # Create confidence text
                conf_text = f"{confidence:.1f}%"

                # Choose text color based on confidence level
                if confidence >= 75:
                    text_color = (0, 255, 0)  # Green (BGR) for high confidence
                elif confidence >= 50:
                    text_color = (0, 215, 255)  # Gold (BGR) for medium-high confidence
                elif confidence >= 25:
                    text_color = (0, 165, 255)  # Orange (BGR) for medium-low confidence
                else:
                    text_color = (107, 107, 255)  # Red (BGR) for low confidence

                # Draw text background for better visibility
                (text_width, text_height), baseline = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(image_copy,
                             (label_pos[0] - 2, label_pos[1] - text_height - 2),
                             (label_pos[0] + text_width + 2, label_pos[1] + baseline + 2),
                             (0, 0, 0), -1)  # Black background

                # Draw confidence text
                cv2.putText(image_copy, conf_text, label_pos,
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        return image_copy
