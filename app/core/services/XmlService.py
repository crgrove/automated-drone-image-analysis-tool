import os
from ast import literal_eval
import xml.etree.ElementTree as ET
from core.services.LoggerService import LoggerService


class XmlService:
    """Service for parsing and modifying an ADIAT XML file."""

    def __init__(self, path=None):
        """
        Initialize the XmlService with an optional XML file path.

        Args:
            path (str, optional): Path to the XML file.
        """
        self.logger = LoggerService()
        if path is not None:
            self.xml = ET.parse(path)
        else:
            self.xml = ET.Element('data')

    def getSettings(self):
        """
        Parse the XML file to retrieve settings and the count of images with areas of interest.

        Returns:
            tuple: A dictionary containing settings from the analysis and an integer for the number of images with areas of interest.
        """
        root = self.xml.getroot()
        settings_xml = root.find('settings')
        settings = {}
        image_count = 0
        if settings_xml is not None:
            settings['output_dir'] = settings_xml.get('output_dir')
            settings['input_dir'] = settings_xml.get('input_dir')
            if settings_xml.get('num_threads') is not None:
                settings['num_threads'] = int(settings_xml.get('num_threads'))
            if settings_xml.get('identifier_color') is not None:
                settings['identifier_color'] = literal_eval(settings_xml.get('identifier_color'))
            if settings_xml.get('min_area') is not None:
                settings['min_area'] = int(settings_xml.get('min_area'))
            if settings_xml.get('max_area') is not None:
                settings['max_area'] = int(settings_xml.get('max_area'))
            if settings_xml.get('hist_ref_path') != "None":
                settings['hist_ref_path'] = settings_xml.get('hist_ref_path')
            if settings_xml.get('kmeans_clusters') != "None":
                settings['kmeans_clusters'] = int(settings_xml.get('kmeans_clusters'))
            settings['algorithm'] = settings_xml.get('algorithm')
            settings['thermal'] = settings_xml.get('thermal')
            settings['options'] = {}
            options_xml = settings_xml.find('options')
            for option in options_xml:
                settings['options'][option.get('name')] = option.get('value')
            images_xml = root.find('images')
            if images_xml is not None:
                image_count = len(images_xml)
        return settings, image_count

    def getImages(self):
        """
        Parse the XML file to retrieve images with areas of interest.

        Returns:
            list[dict]: A list of dictionaries containing image details and areas of interest from the analysis.
        """
        root = self.xml.getroot()
        images = []
        images_xml = root.find('images')
        if images_xml is not None:
            for image_xml in images_xml:
                image = {
                    'xml': image_xml,
                    'path': image_xml.get('path'),
                    'hidden': image_xml.get('hidden') == "True" if image_xml.get('hidden') else False
                }
                areas_of_interest = []
                for area_of_interest_xml in image_xml:
                    area_of_interest = {
                        'area': float(area_of_interest_xml.get('area')),
                        'center': literal_eval(area_of_interest_xml.get('center')),
                        'radius': int(area_of_interest_xml.get('radius'))
                    }
                    areas_of_interest.append(area_of_interest)
                image['areas_of_interest'] = areas_of_interest
                images.append(image)
        return images

    def addSettingsToXml(self, **kwargs):
        """
        Add user-defined settings to the XML document.

        Args:
            **kwargs: Key-value pairs representing settings and their values.
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
        Add an image entry to the XML document.

        Args:
            img (dict): Dictionary with image path and areas of interest.
        """
        images_xml = self.xml.find("images")
        if images_xml is None:
            images_xml = ET.SubElement(self.xml, "images")
        image = ET.SubElement(images_xml, 'image')
        image.set('path', img["path"])
        image.set('hidden', "False")
        for area in img["aois"]:
            area_xml = ET.SubElement(image, 'areas_of_interest')
            area_xml.set('center', str(area['center']))
            area_xml.set('radius', str(area['radius']))
            area_xml.set('area', str(area['area']))

    def saveXmlFile(self, path):
        """
        Save the XML document to the specified path.

        Args:
            path (str): The full path where the XML file will be saved.
        """
        if isinstance(self.xml, ET.Element):
            mydata = ET.ElementTree(self.xml)
        else:
            mydata = self.xml

        with open(path, "wb") as fh:
            mydata.write(fh)
