import numpy as np
import cv2
import piexif
import imghdr
import utm
from helpers.MetaDataHelper import MetaDataHelper


class LocationInfo:
    """Provides functions to retrieve and convert locational data."""

    @staticmethod
    def get_gps(full_path):
        """
        Retrieve the GPS EXIF data stored in an image file.

        Args:
            full_path (str): The path to the image file.

        Returns:
            dict: Contains the decimal latitude and longitude values from the GPS data.
        """
        is_jpg = imghdr.what(full_path) == 'jpg' or imghdr.what(full_path) == 'jpeg'
        if not is_jpg:
            return {}

        exif_dict = MetaDataHelper.get_exif_data_piexif(full_path)
        if not exif_dict['GPS'] == {}:
            latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
            latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
            longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
            longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
            if latitude:
                lat_value = LocationInfo._convert_to_degrees(latitude)
                if latitude_ref != 'N':
                    lat_value = -lat_value
            else:
                return {}
            if longitude:
                lon_value = LocationInfo._convert_to_degrees(longitude)
                if longitude_ref != 'E':
                    lon_value = -lon_value
            else:
                return {}
        else:
            return {}
        return {'latitude': round(lat_value, 6), 'longitude': round(lon_value, 6)}

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
