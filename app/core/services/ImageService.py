
import piexif
import pandas as pd
import cv2
import numpy as np
import json

from core.services.GSDService import GSDService

from helpers.MetaDataHelper import MetaDataHelper
from helpers.PickleHelper import PickleHelper
from helpers.LocationInfo import LocationInfo


class ImageService:
    """Service to calculate various drone and image attributes based on metadata."""

    def __init__(self, path):
        """
        Initializes the ImageService by extracting Exif and XMP metadata.

        Args:
            path (str): The file path to the image.
        """
        self.exif_data = MetaDataHelper.get_exif_data_piexif(path)
        self.xmp_data = MetaDataHelper.get_xmp_data(path, True)
        self.drone_make = MetaDataHelper.get_drone_make(self.exif_data)
        self.path = path
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
        Loads thermal data from the image.

        Returns:
            np.ndarray: Array of thermal values in Celsius or Fahrenheit.
        """
        data = self.xmp_data.get('TemperatureData', [])
        return (data * 1.8) + 32 if unit == 'F' else data

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

        model = self.exif_data["0th"].get(piexif.ImageIFD.Model)
        if model:
            model = model.decode('utf-8').strip().rstrip("\x00")
        if not model or not self.drone_make:
            return None

        image_source = MetaDataHelper.get_drone_xmp_attribute('ImageSource', self.drone_make, self.xmp_data)
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
        

    def circle_areas_of_interest(self, identifier_color, aoi_radius, combine_aois):
        """
        Augments the image with circles around areas of interest.

        Returns:
            (augmented_image: np.ndarray, areas_of_interest: list[dict])
        """
        image_copy = self.img_array.copy()

        # 1) Get AOIs from XMP and JSON-decode if needed
        raw = self.xmp_data.get('AreasOfInterest', [])
        if isinstance(raw, str):
            try:
                contours_or_items = json.loads(raw)
            except Exception:
                contours_or_items = []
        else:
            contours_or_items = raw or []

        if not contours_or_items:
            return image_copy, []

        # 2) Split into two categories:
        #    - ready-made items with {'center','radius'} (no contour needed)
        #    - raw shapes (contours/pixels) needing minEnclosingCircle
        ready_items = []
        raw_contours = []

        for entry in contours_or_items:
            if isinstance(entry, dict) and 'center' in entry and 'radius' in entry:
                # normalize types
                c = entry['center']
                center = (int(c[0]), int(c[1]))
                radius = int(entry['radius'])
                area = int(entry.get('area', 0))
                ready_items.append({'center': center, 'radius': radius, 'area': area})
            else:
                # try to interpret as a contour/pixel list -> (N,1,2) int32
                try:
                    arr = np.asarray(entry, dtype=np.int32)
                    if arr.ndim == 2 and arr.shape[1] == 2:
                        arr = arr.reshape(-1, 1, 2)
                    elif arr.ndim == 3 and arr.shape[1] == 1 and arr.shape[2] == 2:
                        pass
                    else:
                        continue  # skip malformed
                    raw_contours.append(arr)
                except Exception:
                    continue

        areas_of_interest = []
        temp_mask = np.zeros(image_copy.shape[:2], dtype=np.uint8)

        # 3) Draw circles for ready-made items
        for it in ready_items:
            center = it['center']
            radius = it['radius'] + int(aoi_radius)
            # union into mask
            cv2.circle(temp_mask, center, radius, 255, -1)
            if not combine_aois:
                areas_of_interest.append({'center': center, 'radius': radius, 'area': int(it.get('area', 0))})
                cv2.circle(image_copy, center, radius,
                        (identifier_color[2], identifier_color[1], identifier_color[0]), 2)

        # 4) Circles for raw contours
        for cnt in raw_contours:
            # area by filling contour
            mask = np.zeros(image_copy.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, thickness=-1)
            area = int(cv2.countNonZero(mask))

            (x, y), r = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(r) + int(aoi_radius)

            cv2.circle(temp_mask, center, radius, 255, -1)

            if not combine_aois:
                areas_of_interest.append({'center': center, 'radius': radius, 'area': area})
                cv2.circle(image_copy, center, radius,
                        (identifier_color[2], identifier_color[1], identifier_color[0]), 2)

        # Early return if we’re not combining
        if not combine_aois:
            areas_of_interest.sort(key=lambda item: (item['center'][1], item['center'][0]))
            return image_copy, areas_of_interest

        # 5) Combine overlapping circles by iterating union mask until stable
        prev_count = -1
        while True:
            new_contours, _ = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(new_contours) == prev_count:
                break
            prev_count = len(new_contours)
            for cnt in new_contours:
                (x, y), r = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(r)
                cv2.circle(temp_mask, center, radius, 255, -1)

        # 6) Final AOIs from combined mask
        combined_contours, _ = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        areas_of_interest = []
        for cnt in combined_contours:
            mask = np.zeros(image_copy.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, thickness=-1)
            area = int(cv2.countNonZero(mask))

            (x, y), r = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(r)

            areas_of_interest.append({'center': center, 'radius': radius, 'area': area})
            cv2.circle(image_copy, center, radius,
                    (identifier_color[2], identifier_color[1], identifier_color[0]), 2)

        areas_of_interest.sort(key=lambda item: (item['center'][1], item['center'][0]))
        return image_copy, areas_of_interest