import os
from ast import literal_eval
import xml.etree.ElementTree as ET
from core.services.LoggerService import LoggerService

class XmlService:
	"""Service used to parse an ADIAT XML file"""
	def __init__(self, path = None):
		"""
		__init__ constructor for the service
		
		:String path: path to the XML file.
		"""
		self.logger = LoggerService()
		if path is not None:
			self.xml = ET.parse(path)
		else:
			self.xml = ET.Element('data')

	def getSettings(self):
		"""
		getSettings parses an ADIAT XML file returning the settings and image count
		
		:return List(Dictionary), Int: the settings from when the analysis was run and the number of images containing areas of interest
		"""

		root = self.xml.getroot()
		settings_xml = root.find('settings')
		settings = dict()
		if settings_xml is not None:
			settings['output_dir'] = settings_xml.get('output_dir')
			settings['input_dir'] = settings_xml.get('input_dir')
			if settings_xml.get('num_threads') is not None:
				settings['num_threads'] = int(settings_xml.get('num_threads'))
			if settings_xml.get('identifier_color') is not None:
				settings['identifier_color'] = literal_eval(settings_xml.get('identifier_color'))
			if settings_xml.get('min_area') is not None:
				settings['min_area'] = int(settings_xml.get('min_area'))
			if settings_xml.get('hist_ref_path') != "None":
				settings['hist_ref_path'] = settings_xml.get('hist_ref_path')
			if settings_xml.get('kmeans_clusters') != "None":
				settings['kmeans_clusters'] = int(settings_xml.get('kmeans_clusters'))
			settings['algorithm'] = settings_xml.get('algorithm')
			settings['thermal'] = settings_xml.get('thermal')
			settings['options'] = dict()
			options_xml = settings_xml.find('options')
			for option in options_xml:
				settings['options'] [option.get('name')] = option.get('value')
			images_xml = root.find('images')
			if images_xml is not None:
				image_count = len(images_xml)    
		return settings, image_count

	def getImages(self):
		"""
		getImages parses an ADIAT XML file returning the images
		
		:return List(Dictionary): the images containing areas of interest from when the analysis was run
		"""
		root = self.xml.getroot()
		images = []
		images_xml = root.find('images')
		if images_xml is not None:
			for image_xml in images_xml:
				image = dict()
				image['xml'] = image_xml
				image['path'] = image_xml.get('path')
				if image_xml.get('hidden'):
					image['hidden'] = (image_xml.get('hidden') == "True")
				else:
					image['hidden'] = False
				areas_of_interest  = []
				for area_of_interest_xml in image_xml:
					area_of_interest = dict()
					area_of_interest['area'] = float(area_of_interest_xml.get('area'))
					area_of_interest['center'] = literal_eval(area_of_interest_xml.get('center'))
					area_of_interest['radius'] = int(area_of_interest_xml.get('radius'))
					areas_of_interest.append(area_of_interest)
				image['areas_of_interest'] = areas_of_interest
				images.append(image)
		return images

	def addSettingsToXml(self, **kwargs):
		"""
		addSettingsToXml adds information about the parameters set by the user to the xml document
		"""
		try:
			settings_xml = self.xml.find("settings")
			if settings_xml is None:
				settings_xml = ET.SubElement(self.xml, "settings")
			for key, value in kwargs.items():
				if key == "options":
					options_xml = ET.SubElement(settings_xml, "options")
					for option_key, option_value in value.items():
						option_xml = ET.SubElement(options_xml, "option")
						option_xml.set("name", option_key)
						option_xml.set("value", str(option_value))
				else:
					settings_xml.set(key, str(value))
		except Exception as e:
			self.logger.error(e)

	def addImageToXml(self, img):
		"""
		addImageToXml adds an image to the xml document
		
		:Dictionary img: the full path to the output file and a list of areas of interest
		"""
		images_xml = self.xml.find("images")
		if images_xml is None:
			images_xml = ET.SubElement(self.xml, "images")
		image = ET.SubElement(images_xml, 'image')
		image.set('path',img["path"])
		image.set('hidden',"False")
		for area in img["aois"]:
			area_xml = ET.SubElement(image, 'areas_of_interest')
			area_xml.set('center', str(area['center']))
			area_xml.set('radius', str(area['radius']))
			area_xml.set('area', str(area['area']))

	def saveXmlFile(self, path):
		"""
		saveXmlFile saves the XML document to the specified path
		"""
		# Check if self.xml is an Element, not an ElementTree
		if isinstance(self.xml, ET.Element):
			# Wrap the root element with ElementTree
			mydata = ET.ElementTree(self.xml)
		else:
			mydata = self.xml  # If already ElementTree, use it as-is

		# Save the XML to the file
		with open(path, "wb") as fh:
			mydata.write(fh)