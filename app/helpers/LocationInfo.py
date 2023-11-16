import numpy as np
import cv2
import piexif
import imghdr
class LocationInfo:
	"""Provides functions to retrieve and convert locational data"""
	@staticmethod
	def getGPS(full_path):
		"""
		getGPS retrieves the gps EXIF data stored in an image file
        
        :String full_path: the path to the image file
		:return Dictionary: contains the latitude and longitude values from the gps data
		"""
		is_jpg = imghdr.what(full_path) == 'jpg' or imghdr.what(full_path) == 'jpeg'
		if not is_jpg:
			return {}
		
		exif_dict = piexif.load(full_path)
		if not exif_dict['GPS'] == {}:
			latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
			latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
			longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
			longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
			if latitude:
				lat_value = LocationInfo.__convert_to_degrees(latitude)
				if latitude_ref != 'N':
					lat_value = -lat_value
			else:
				return {}
			if longitude:
				lon_value = LocationInfo.__convert_to_degrees(longitude)
				if longitude_ref != 'E':
					lon_value = -lon_value
			else:
				return {}
		else:
			return {}
		return {'latitude': str(lat_value), 'longitude': str(lon_value)}
	
	@staticmethod
	def __convert_to_degrees(value):
		"""
		__convert_to_degrees Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
		:exifread.utils.Ratio value: the input value from the EXIF data
		:return float: decimal representation of the latitude or longitude
		"""
		d = float(value[0][0]) / float(value[0][1])
		m = float(value[1][0]) / float(value[1][1])
		s = float(value[2][0]) / float(value[2][1])

		return d + (m / 60.0) + (s / 3600.0)