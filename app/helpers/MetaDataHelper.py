from PIL import Image
from os import path
import exiftool
import piexif
import json
import numpy as np
import platform
class MetaDataHelper:

	@staticmethod	
	def getEXIFToolPath():
		if platform.system() == 'Windows':
			return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool.exe'))
		elif platform.system() == 'Darwin':
			return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool'))
	@staticmethod
	def transferExifPiexif(originFile, destinationFile):
		"""
		transferExifPiexif copies the exif information of an image file to another image file using piexif
		
		:String originFile: the path to the source file
		:String destinationFile: the path to the destination file
		"""
		try:
			piexif.transplant(originFile, destinationFile)
		except  piexif._exceptions.InvalidImageDataError as e:
			MetaDataHelper.transferExifPil(originFile, destinationFile)
		except  ValueError as ve:
			return
		
	@staticmethod
	def transferExifPil(originFile, destinationFile):
		"""
		transferExifPil copies the exif information of an image file to another image file using PIL
		
		:String originFile: the path to the source file
		:String destinationFile: the path to the destination file
		"""

		# load old image and extract EXIF
		image = Image.open(originFile)
		exif = image.info['exif']

		# load new image
		image_new = Image.open(destinationFile)
		image_new.save(destinationFile, 'JPEG', exif=exif)
	
	@staticmethod
	def transferExifExiftool(originFile, destinationFile):
		"""
		transferExifExiftool copies the exif information of an image file to another image file using Exiftool
		
		:String originFile: the path to the source file
		:String destinationFile: the path to the destination file
		"""
		with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
			et.execute("-tagsfromfile", originFile, "-exif", destinationFile, "-overwrite_original")
	
	@staticmethod      
	def transferXmpExiftool(originFile, destinationFile):
		"""
		transferXmpExiftool copies the xmp information of an image file to another image file using Exiftool
		
		:String originFile: the path to the source file
		:String destinationFile: the path to the destination file
		"""
		with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
			et.execute("-tagsfromfile", originFile, "-xmp", destinationFile, "-overwrite_original")
			
	def transferAll(originFile, destinationFile):
		"""
		transferAll copies the exif and xmp information of an image file to another image file using Exiftool
		
		:String originFile: the path to the source file
		:String destinationFile: the path to the destination file
		"""
		with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
			et.execute("-tagsfromfile", originFile,  destinationFile, "-overwrite_original", "--thumbnailimage")
	
	@staticmethod     	
	def transferTemperatureData(data, destinationFile):
		"""
		transferTemperatureData copies the temperature data from the original image to the Note field on the augmented image.
		
		:numpy.ndarray data: the path to the source file
		:String destinationFile: the path to the destination file
		"""
		json_data = json.dumps(data.tolist())
		with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
			  et.set_tags(
				[destinationFile],
				tags={"Notes": json_data},
				params=["-P", "-overwrite_original"]
		)
			  
	@staticmethod
	def getRawTemperatureData(file_path):
		"""
		getRawTemperatureData returns a byte string representing the temperature data
		:String full_path: the path to the image
		:return str: the bytes representing the temperature values
		"""
		with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
			thermal_img_bytes = et.execute("-b", "-RawThermalImage", file_path, raw_bytes=True)	
		return thermal_img_bytes
	@staticmethod     
	def getTemperatureData(file_path):
		"""
		getTemperatureData returns a numpy array of temeprature data from the notes field an image.
		:String full_path: the path to the image
		:return numpy.ndarray: array of temperature data
		"""
		with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
			json_data = et.get_tags([file_path], tags=['Notes'])[0]['XMP:Notes']
			data = json.loads(json_data)
			temperature_c = np.asarray(data)
			return temperature_c
	@staticmethod
	def getMetaData(file_path):
		"""
		getMetaData returns a dictionary representation of the metadata from a file
		:String full_path: the path to the image
		:return Dict: Key value pairs of metadata.
		"""
		with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
			return et.get_metadata([file_path])[0]
		
	@staticmethod
	def setTags(file_path, tags):
		"""
		setTags updates file metadata with tags provided
		:String full_path: the path to the image
		:Dict tags: dictionary of tags and values to be set
		"""
		with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
			et.set_tags([file_path],tags=tags, params=["-overwrite_original"])