import numpy as np
import cv2
import piexif
class LocationInfo:
	@staticmethod
	def getGPS(filepath):
		exif_dict = piexif.load(filepath)
		latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
		latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
		longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
		longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
		if latitude:
			lat_value = LocationInfo.__convert_to_degress(latitude)
			if latitude_ref != 'N':
				lat_value = -lat_value
		else:
			return {}
		if longitude:
			lon_value = LocationInfo.__convert_to_degress(longitude)
			if longitude_ref != 'E':
				lon_value = -lon_value
		else:
			return {}
		return {'latitude': str(lat_value), 'longitude': str(lon_value)}
	
	@staticmethod
	def __convert_to_degress(value):
		"""
		Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
		:param value:
		:type value: exifread.utils.Ratio
		:rtype: float
		"""
		d = float(value[0][0]) / float(value[0][1])
		m = float(value[1][0]) / float(value[1][1])
		s = float(value[2][0]) / float(value[2][1])

		return d + (m / 60.0) + (s / 3600.0)