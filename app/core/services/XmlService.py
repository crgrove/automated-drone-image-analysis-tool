import logging
from ast import literal_eval
import xml.etree.ElementTree as ET

class XmlService:
    """Service used to parse an ADIAT XML file"""
    def __init__(self, path = None):
        """
		__init__ constructor for the service
        
        :String path: path to the XML file.
		"""
        self.path = path

    def getSettings(self, path= None):
        """
		getSettings parses an ADIAT XML file returning the settings and image count
        
        :String path: path to the XML file.
        :return List(Dictionary), Int: the settings from when the analysis was run and the number of images containing areas of interest
		"""
        if path is not None:
            my_path = path
        else:
            my_path = self.path
        if my_path is not None:
            tree = ET.parse(my_path)
            root = tree.getroot()
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
                settings['options'] = dict()
                options_xml = settings_xml.find('options')
                for option in options_xml:
                    settings['options'] [option.get('name')] = option.get('value')
            images_xml = root.find('images')
            if images_xml is not None:
                image_count = len(images_xml)    
        return settings, image_count

    def getImages(self, path= None):
        """
		getImages parses an ADIAT XML file returning the images
        
        :String path: path to the XML file.
        :return List(Dictionary): the images containing areas of interest from when the analysis was run
        """
        if path is not None:
            my_path = path
        else:
            my_path = self.path
        if my_path is not None:
            tree = ET.parse(my_path)
            root = tree.getroot()
            images = []
            images_xml = root.find('images')
            if images_xml is not None:
                for image_xml in images_xml:
                    image = dict()
                    image['path'] = image_xml.get('path')
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
