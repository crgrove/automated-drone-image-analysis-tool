import numpy as np
import cv2
import piexif
from PIL import Image, UnidentifiedImageError
import utm
from helpers.MetaDataHelper import MetaDataHelper


class LocationInfo:
    """Provides functions to retrieve and convert locational data."""

    @staticmethod
    def get_gps(full_path=None, exif_data=None):
        """
        Retrieve the GPS EXIF data stored in an image file.

        Args:
            full_path (str): The path to the image file.

        Returns:
            dict: Contains the decimal latitude and longitude values from the GPS data.
        """
        if full_path:
            try:
                with Image.open(full_path) as img:
                    if img.format != "JPEG":
                        return {}
            except (UnidentifiedImageError, OSError):
                return {}
            exif_dict = MetaDataHelper.get_exif_data_piexif(full_path)

        if exif_data:
            exif_dict = exif_data

        if not exif_dict or 'GPS' not in exif_dict or not exif_dict['GPS']:
            return {}

        try:
            latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
            latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
            longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
            longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')

            lat_value = LocationInfo._convert_to_degrees(latitude)
            if latitude_ref != 'N':
                lat_value = -lat_value

            lon_value = LocationInfo._convert_to_degrees(longitude)
            if longitude_ref != 'E':
                lon_value = -lon_value

            return {'latitude': round(lat_value, 6), 'longitude': round(lon_value, 6)}

        except KeyError:
            return {}

    @staticmethod
    def convert_degrees_to_utm(lat, lng):
        """
        Convert decimal latitude and longitude values to UTM coordinates.

        Args:
            lat (float): The decimal latitude position.
            lng (float): The decimal longitude position.

        Returns:
            dict: Contains EASTING, NORTHING, ZONE_NUMBER, and ZONE_LETTER values representing the position in UTM.
        """
        utm_pos = utm.from_latlon(lat, lng)
        return {
            'easting': round(utm_pos[0], 2),
            'northing': round(utm_pos[1], 2),
            'zone_number': utm_pos[2],
            'zone_letter': utm_pos[3]
        }

    @staticmethod
    def convert_decimal_to_dms(lat, lng):
        """
        Convert decimal latitude and longitude values to degrees, minutes, seconds coordinates.

        Args:
            lat (float): The decimal latitude position.
            lng (float): The decimal longitude position.

        Returns:
            dict: Contains the degrees, minutes, and seconds values for latitude and longitude, including reference values.
        """
        is_positive = lat >= 0
        lat = abs(lat)
        minutes, seconds = divmod(lat * 3600, 60)
        degrees, minutes = divmod(minutes, 60)
        reference = 'N' if is_positive else 'S'
        latitude = {
            'degrees': int(degrees),
            'minutes': int(minutes),
            'seconds': round(seconds, 2),
            'reference': reference
        }

        is_positive = lng >= 0
        lng = abs(lng)
        minutes, seconds = divmod(lng * 3600, 60)
        degrees, minutes = divmod(minutes, 60)
        reference = 'E' if is_positive else 'W'
        longitude = {
            'degrees': int(degrees),
            'minutes': int(minutes),
            'seconds': round(seconds, 2),
            'reference': reference
        }

        return {'latitude': latitude, 'longitude': longitude}

    @staticmethod
    def format_coordinates(lat, lon, format_type='Decimal Degrees'):
        """
        Format GPS coordinates in various standard formats.

        Args:
            lat (float): Latitude in decimal degrees
            lon (float): Longitude in decimal degrees
            format_type (str): One of:
                - 'Decimal Degrees' (e.g., "37.123456, -122.123456")
                - 'Degrees Minutes Seconds' (e.g., "37°7'24.44\"N, 122°7'24.44\"W")
                - 'Degrees Decimal Minutes' (e.g., "37°7.4073'N, 122°7.4073'W")

        Returns:
            str: Formatted coordinate string
        """
        if format_type == 'Decimal Degrees':
            return f"{lat:.6f}, {lon:.6f}"

        elif format_type == 'Degrees Minutes Seconds':
            # Use existing convert_decimal_to_dms() and format the result
            dms = LocationInfo.convert_decimal_to_dms(lat, lon)
            lat_data = dms['latitude']
            lon_data = dms['longitude']
            lat_str = f"{lat_data['degrees']}°{lat_data['minutes']}'{lat_data['seconds']:.2f}\"{lat_data['reference']}"
            lon_str = f"{lon_data['degrees']}°{lon_data['minutes']}'{lon_data['seconds']:.2f}\"{lon_data['reference']}"
            return f"{lat_str}, {lon_str}"

        elif format_type == 'Degrees Decimal Minutes':
            # Calculate DDM using existing logic pattern
            lat_ddm = LocationInfo._format_decimal_to_ddm(lat, is_latitude=True)
            lon_ddm = LocationInfo._format_decimal_to_ddm(lon, is_latitude=False)
            return f"{lat_ddm}, {lon_ddm}"

        else:
            # Default to decimal degrees
            return f"{lat:.6f}, {lon:.6f}"

    @staticmethod
    def _format_decimal_to_ddm(decimal, is_latitude):
        """
        Convert decimal degrees to DDM (Degrees Decimal Minutes) format string.

        Args:
            decimal (float): Decimal degrees
            is_latitude (bool): True for latitude, False for longitude

        Returns:
            str: String in DDM format (e.g., "37°7.4073'N")
        """
        direction = 'N' if decimal >= 0 and is_latitude else 'S' if is_latitude else 'E' if decimal >= 0 else 'W'
        decimal = abs(decimal)
        degrees = int(decimal)
        minutes = (decimal - degrees) * 60

        return f"{degrees}°{minutes:.4f}'{direction}"

    @staticmethod
    def _convert_to_degrees(value):
        """
        Convert GPS coordinates stored in EXIF to degrees in float format.

        Args:
            value (exifread.utils.Ratio): The input value from the EXIF data.

        Returns:
            float: Decimal representation of the latitude or longitude.
        """
        d = float(value[0][0]) / float(value[0][1])
        m = float(value[1][0]) / float(value[1][1])
        s = float(value[2][0]) / float(value[2][1])

        return d + (m / 60.0) + (s / 3600.0)
