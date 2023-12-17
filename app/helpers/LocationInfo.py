import numpy as np
import cv2
import piexif
import imghdr
import utm

class LocationInfo:
	"""Provides functions to retrieve and convert locational data"""
	@staticmethod
	def getGPS(full_path):
		"""
		getGPS retrieves the gps EXIF data stored in an image file
        
        :String full_path: the path to the image file
		:return Dictionary: contains the decimal latitude and longitude values from the gps data
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
		return {'latitude': round(lat_value,6), 'longitude': round(lon_value,6)}
	
	@staticmethod
	def convertDegreesToUtm(lat, lng):
		"""
		convertDegreesToUtm takes decimal latitude and longitude values and converts to UTM coordiantes
		:float lat: the decimal latitude position
		:float longitude: the decimal latitude position
		:return Dictionary: EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER values representing the position in UTM
		"""
		utm_pos = utm.from_latlon(lat, lng)
		return {'easting': round(utm_pos[0],2), 'northing': round(utm_pos[1],2), 'zone_number': utm_pos[2], 'zone_letter': utm_pos[3]}
	
	@staticmethod
	def convertDecimalToDms(lat, lng):
		"""
		convertDecimalToDms takes decimal latitude and longitude values and converts to degrees, minutes, seconds coordinates
		:float lat: the decimal latitude position
		:float longitude: the decimal latitude position
		:return Dictionary: contains the degrees, minutes, seconds values for lat and lng as well as the reference values
		"""
		is_positive = lat >= 0
		lat = abs(lat)
		minutes,seconds = divmod(lat*3600,60)
		degrees,minutes = divmod(minutes,60)
		degrees = degrees
		reference = 'N' if is_positive else 'S'
		latitude = {'degrees': int(degrees), 'minutes': int(minutes), 'seconds': round(seconds,2), 'reference': reference}
		
		is_positive = lng >= 0
		lng = abs(lng)
		minutes,seconds = divmod(lng*3600,60)
		degrees,minutes = divmod(minutes,60)
		degrees = degrees
		reference = 'E' if is_positive else 'W'
		longitude = {'degrees': int(degrees), 'minutes': int(minutes), 'seconds': round(seconds,2), 'reference': reference}
		
		return{'latitude':latitude, 'longitude':longitude}
	
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