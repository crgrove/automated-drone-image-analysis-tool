
import os
import piexif
import pandas as pd
import cv2
import numpy as np
import json
import math
import zlib
import base64
from PIL import Image

from core.services.GSDService import GSDService

from helpers.MetaDataHelper import MetaDataHelper
from helpers.PickleHelper import PickleHelper
from helpers.LocationInfo import LocationInfo


class ImageService:
    """Service to calculate various drone and image attributes based on metadata."""

    def __init__(self, path, mask_path=None):
        """
        Initializes the ImageService by extracting Exif and XMP metadata.

        Args:
            path (str): The file path to the image.
            mask_path (str, optional): Path to the mask file containing thermal metadata.
        """
        self.exif_data = MetaDataHelper.get_exif_data_piexif(path)
        self.xmp_data = MetaDataHelper.get_xmp_data_merged(path)
        self.drone_make = MetaDataHelper.get_drone_make(self.exif_data)
        self.path = path
        self.mask_path = mask_path
        img = cv2.imdecode(np.fromfile(self.path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        self.img_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def get_relative_altitude(self, distance_unit):
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

    def get_drone_orientation(self):
        """
        Retrieves the yaw orientation of the drone (0–360 degrees).

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

    def get_gimbal_orientation(self):
        """Retrieve gimbal yaw and pitch from XMP metadata.

        Returns:
            tuple: (yaw, pitch) in degrees or (None, None) if unavailable.
        """
        if self.xmp_data is None or self.drone_make is None:
            return None, None

        yaw = MetaDataHelper.get_drone_xmp_attribute('Gimbal Yaw', self.drone_make, self.xmp_data)
        pitch = MetaDataHelper.get_drone_xmp_attribute('Gimbal Pitch', self.drone_make, self.xmp_data)
        try:
            yaw = float(yaw)
            pitch = float(pitch)
        except (TypeError, ValueError):
            return None, None

        if yaw < 0:
            yaw += 360
        return yaw, pitch

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

    def get_average_gsd(self):
        """
        Computes the estimated average Ground Sampling Distance (GSD).

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
        focal_length = focal_length[0] / focal_length[1]

        altitude_meters = MetaDataHelper.get_drone_xmp_attribute('AGL', self.drone_make, self.xmp_data)
        altitude_meters = float(altitude_meters) if altitude_meters else 100

        tilt_angle = MetaDataHelper.get_drone_xmp_attribute('Gimbal Pitch', self.drone_make, self.xmp_data)
        tilt_angle = abs(float(tilt_angle)) if tilt_angle else 0
        if not self._is_autel():
            tilt_angle = 90 - tilt_angle

        if tilt_angle > 60:
            return None

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

    def get_position(self, position_format):
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
        Loads thermal data from mask PNG metadata if available, otherwise from XMP.
        Returns a NumPy array in C or F.
        
        Args:
            unit (str): Temperature unit ('C' or 'F').
            
        Returns:
            np.ndarray or None: Temperature data array in the specified unit.
        """
        # First, try to load from mask PNG metadata if mask_path is provided
        if self.mask_path and os.path.exists(self.mask_path):
            try:
                # Open the mask PNG and read metadata
                mask_image = Image.open(self.mask_path)
                
                # Check if thermal data exists in metadata
                if hasattr(mask_image, 'text') and 'ThermalData' in mask_image.text:
                    encoded_data = mask_image.text.get('ThermalData')
                    compression = mask_image.text.get('ThermalDataCompression', '')
                    shape_str = mask_image.text.get('ThermalDataShape', '')
                    
                    if encoded_data and compression == 'zlib+base64':
                        # Decode from base64
                        compressed_data = base64.b64decode(encoded_data.encode('ascii'))
                        
                        # Decompress
                        temp_json = zlib.decompress(compressed_data).decode('utf-8')
                        
                        # Parse JSON
                        raw = json.loads(temp_json)
                        
                        # Convert to NumPy array
                        data = np.asarray(raw, dtype=np.float32)
                        
                        # Reshape if shape information is available
                        if shape_str:
                            try:
                                shape = json.loads(shape_str)
                                data = data.reshape(shape)
                            except Exception:
                                pass  # Keep flat if reshape fails
                        
                        # Convert units if needed
                        if unit == 'F':
                            data = data * 1.8 + 32.0
                        
                        return data
                        
            except Exception as e:
                # If reading from mask fails, fall back to XMP
                print(f"Warning: Failed to read thermal data from mask: {e}")
        
        # Fall back to XMP metadata (original method)
        raw = self.xmp_data.get('TemperatureData', None)
        if raw is None:
            return None
        
        # If it's a JSON string, decode it
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                # Malformed JSON or unexpected type
                return None
        
        # Ensure NumPy array for numeric ops
        data = np.asarray(raw, dtype=np.float32)
        
        if unit == 'F':
            data = data * 1.8 + 32.0
        
        return data

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

        return image_copy
    
    def apply_mask_highlight(self, image_array, mask_path, identifier_color=(255, 0, 255), areas_of_interest=None):
        """
        Applies a mask overlay to highlight detected pixels.
        
        Args:
            image_array (np.ndarray): The input image array in BGR format.
            mask_path (str): Path to the mask PNG file.
            identifier_color (tuple): RGB color tuple for highlighting (uses Object Identifier color).
            areas_of_interest (list, optional): Not used currently, but kept for future filtering.
            
        Returns:
            np.ndarray: The image array with mask applied.
        """
        if not mask_path or not os.path.exists(mask_path):
            return image_array
            
        # Load the mask
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            return image_array
        
        # Resize mask if needed to match image dimensions
        if mask.shape[:2] != image_array.shape[:2]:
            mask = cv2.resize(mask, (image_array.shape[1], image_array.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        highlighted_image = image_array.copy()
        
        # Apply the mask - white pixels (255) get colored, black (0) stay transparent
        # Image is in BGR format, identifier_color is RGB, so convert
        bgr_color = (int(identifier_color[2]), int(identifier_color[1]), int(identifier_color[0]))
        
        # Apply color to all white pixels in the mask
        mask_indices = mask > 0
        highlighted_image[mask_indices] = bgr_color
            
        return highlighted_image
    
    def highlight_aoi_pixels(self, image_array, areas_of_interest, highlight_color=(255, 0, 255)):
        """
        Highlights detected pixels within areas of interest.
        
        Args:
            image_array (np.ndarray): The input image array.
            areas_of_interest (list): List of AOI dictionaries with detected_pixels.
            highlight_color (tuple): RGB color tuple for highlighting (default: magenta).
            
        Returns:
            np.ndarray: The image array with highlighted pixels.
        """
        highlighted_image = image_array.copy()
        
        # Convert highlight color to numpy array
        highlight_color_array = np.array(highlight_color, dtype=np.uint8)
        
        for aoi in areas_of_interest or []:
            if "detected_pixels" in aoi and aoi["detected_pixels"]:
                for pixel in aoi["detected_pixels"]:
                    if isinstance(pixel, (list, tuple)) and len(pixel) >= 2:
                        x, y = int(pixel[0]), int(pixel[1])
                        # Check bounds
                        if 0 <= y < highlighted_image.shape[0] and 0 <= x < highlighted_image.shape[1]:
                            # Convert from BGR to RGB for display if needed
                            if len(highlighted_image.shape) == 3 and highlighted_image.shape[2] == 3:
                                highlighted_image[y, x] = highlight_color_array
                            
        return highlighted_image

    def highlight_pixels_of_interest(self, image_array, highlight_color=(255, 0, 255)):
        """
        Highlights pixels of interest stored in XMP metadata with the specified color.

        Args:
            image_array (np.ndarray): The input image array.
            highlight_color (tuple): RGB color tuple for highlighting (default: magenta).

        Returns:
            np.ndarray: The image array with highlighted pixels of interest.
        """
        try:
            # Get XMP data from the image
            xmp_data = MetaDataHelper.get_xmp_data(self.path, parse=True)
            if not xmp_data:
                return image_array

            # Look for pixels of interest in the custom namespace
            pixels_key = None
            for key in xmp_data.keys():
                if 'PixelsOfInterest' in key:
                    pixels_key = key
                    break

            if not pixels_key:
                return image_array

            # Parse the pixels of interest
            pixels_str = xmp_data[pixels_key]
            try:
                import json
                pixels_of_interest = json.loads(pixels_str)
            except (json.JSONDecodeError, TypeError):
                return image_array

            if not pixels_of_interest:
                return image_array

            # Create a copy of the image to avoid modifying the original
            highlighted_image = image_array.copy()

            # Convert highlight color to numpy array
            highlight_color_array = np.array(highlight_color, dtype=np.uint8)

            # Highlight each pixel with the specified color
            for pixel in pixels_of_interest:
                if isinstance(pixel, (list, tuple)) and len(pixel) >= 2:
                    x, y = int(pixel[0]), int(pixel[1])
                    # Check bounds
                    if 0 <= y < highlighted_image.shape[0] and 0 <= x < highlighted_image.shape[1]:
                        highlighted_image[y, x] = highlight_color_array

            return highlighted_image

        except Exception as e:
            # Log error if logger is available
            try:
                from core.services.LoggerService import LoggerService
                logger = LoggerService()
                logger.error(f"Error highlighting pixels of interest: {e}")
            except Exception:
                pass
            return image_array
