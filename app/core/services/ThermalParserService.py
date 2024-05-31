import numpy as np
from helpers.MetaDataHelper import MetaDataHelper

from core.services.thermalParserServices.DjiThermalParserService import DjiThermalParserService
from core.services.thermalParserServices.FlirThermalParserService import FlirThermalParserService
from core.services.thermalParserServices.AutelThermalParserService import AutelThermalImageParser

class ThermalParserService:
	"""Base class for thermal parser services"""
	FLIR_MODELS = [
	'Flir b60',
	'FLIR E40',
	'FLIR T640',
	'FLIR',
	'FLIR AX8',
	'XT2',
	'XTR'
	]

	DJI_MODELS = [
	'ZH20T',
	'XT S',
	'MAVIC2-ENTERPRISE-ADVANCED',
	'ZH20N',
	'M3T',
	'M30T'
	]

	AUTEL_MODELS = [
	'XK729',
	'XL709',
	'XL801',
	'MODELX'
	]

	def __init__(
			self,
			dtype=np.float32,
	):
		self.dtype = dtype
	def getModelandPlatform(self, meta_fields):
		"""
		getPlatform returns a string representing the camera model and platform (Flir, DJI, or Autel)
		:Dict meta_fields: Dictionary of metadata key value pairs
		:return String, String: the name of the camera model and platform
		"""
		if 'CameraModel' in meta_fields:
			camera_model = meta_fields['CameraModel']
		else:
			camera_model = meta_fields['Model']
		if camera_model in self.FLIR_MODELS:
			return camera_model, 'FLIR'
		elif camera_model in self.DJI_MODELS:
			return camera_model, 'DJI'
		elif camera_model in self.AUTEL_MODELS:
			return camera_model, 'AUTEL'
		else:
			return 'Not Supported', 'None'

	def parseFile(self, full_path: str, palette: str = "White Hot"):
		"""
		parseFile processes a single thermal image returning the temperate and visual representation

		:String full_path: the path to the image being analyzed
		:String input_dir: the base input folder
		:String output_dir: the base output folder
		:return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
		data = MetaDataHelper.getMetaData(full_path)
		meta_fields = dict([
			(k.split(':')[1].strip(), v) for k, v in data.items() if ':' in k
			])
		camera_model, platform = self.getModelandPlatform(meta_fields)
		if platform == 'FLIR':
			kwargs = dict((name, float(meta_fields[key])) for name, key in [
				('emissivity', 'Emissivity'),
				('ir_window_transmission', 'IRWindowTransmission'),
				('planck_r1', 'PlanckR1'),
				('planck_b', 'PlanckB'),
				('planck_f', 'PlanckF'),
				('planck_o', 'PlanckO'),
				('planck_r2', 'PlanckR2'),
				('ata1', 'AtmosphericTransAlpha1'),
				('ata2', 'AtmosphericTransAlpha2'),
				('atb1', 'AtmosphericTransBeta1'),
				('atb2', 'AtmosphericTransBeta2'),
				('atx', 'AtmosphericTransX'),
			] if key in meta_fields)
			for name, key in [
				('object_distance', 'ObjectDistance'),
				('atmospheric_temperature', 'AtmosphericTemperature'),
				('reflected_apparent_temperature', 'ReflectedApparentTemperature'),
				('ir_window_temperature', 'IRWindowTemperature'),
				('relative_humidity', 'RelativeHumidity'),
			]:
				if key in meta_fields:
					kwargs[name] = float(meta_fields[key])
			try:
				parser = FlirThermalParserService(self.dtype)
				temps = parser.temperatures(
					filepath_image=full_path,
					**kwargs,
				)
				img = parser.image(temps, palette)
				return temps, img
			except Exception as e:
				print(e)
				raise Exception("Invalid image file")
		elif platform == 'DJI':
			kwargs = dict()
			for name, key in [
				('object_distance', 'ObjectDistance'),
				('relative_humidity', 'RelativeHumidity'),
				('emissivity', 'Emissivity'),
				('reflected_apparent_temperature', 'Reflection'),
			]:
				if key in meta_fields:
					kwargs[name] = float(meta_fields[key])
			if camera_model != 'M30T':
				kwargs['image_height'] = int(meta_fields['ImageHeight'])
				kwargs['image_width'] = int(meta_fields['ImageWidth'])
			if 'emissivity' in kwargs:
				kwargs['emissivity'] /= 100
			if camera_model in ['MAVIC2-ENTERPRISE-ADVANCED','ZH20N','M3T','M30T']:
				kwargs['m2ea_mode'] = True
			try:
				parser = DjiThermalParserService(self.dtype)
				temps =  parser.temperatures(
					filepath_image=full_path,
					**kwargs,
				)
				img = parser.image(full_path,palette)
				return temps, img
			except Exception as e:
				print(e)
				raise Exception("Invalid image file")
		elif platform == 'AUTEL':
			kwargs = dict()
			kwargs['image_height'] = int(meta_fields['ImageHeight'])
			kwargs['image_width'] = int(meta_fields['ImageWidth'])
			try:
				parser = AutelThermalImageParser(self.dtype)
				temps =  parser.temperatures(
					filepath_image=full_path,
					**kwargs,
				)
				img = parser.image(temps, palette)
				return temps, img
			except Exception as e:
				print(e)
				raise Exception("Invalid image file")