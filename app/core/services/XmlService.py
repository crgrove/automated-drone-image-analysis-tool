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
        self.xml_path = path
        self.logger = LoggerService()

        if path is not None:
            self.xml = ET.parse(path)
        else:
            root = ET.Element('data')
            self.xml = ET.ElementTree(root)  # Ensures self.xml is an ElementTree

    def get_settings(self):
        """
        Parse the XML file to retrieve settings and the count of images with areas of interest.

        Returns:
            tuple: A dictionary containing settings from the analysis and an integer for the number of images with areas of interest.
        """
        root = self.xml.getroot()
        settings_xml = root.find("settings")
        settings = {}
        image_count = 0

        if settings_xml is not None:
            def safe_int(value, default=0):
                """Helper function to safely convert a value to int, handling 'None' values."""
                return int(value) if value and value != "None" else default

            def safe_eval(value, default=(0, 0, 0)):
                """Helper function to safely evaluate a tuple, handling 'None' values."""
                return literal_eval(value) if value and value != "None" else default
            settings['output_dir'] = settings_xml.get('output_dir', "")
            settings['input_dir'] = settings_xml.get('input_dir', "")
            settings['num_processes'] = safe_int(settings_xml.get('num_processes'), 1)
            settings['identifier_color'] = safe_eval(settings_xml.get('identifier_color'), (0, 0, 0))
            settings['aoi_radius'] = safe_int(settings_xml.get('aoi_radius'), 0)
            settings['min_area'] = safe_int(settings_xml.get('min_area'), 10)
            settings['max_area'] = safe_int(settings_xml.get('max_area'), 0)
            settings['hist_ref_path'] = settings_xml.get('hist_ref_path', "") if settings_xml.get('hist_ref_path') != "None" else ""
            settings['kmeans_clusters'] = safe_int(settings_xml.get('kmeans_clusters'), 0)
            settings['algorithm'] = settings_xml.get('algorithm', "default")
            settings['thermal'] = settings_xml.get('thermal', "False")

            settings['options'] = {}
            options_xml = settings_xml.find('options')
            if options_xml:
                for option in options_xml:
                    settings['options'][option.get('name')] = option.get('value')

        images_xml = root.find('images')
        if images_xml is not None:
            image_count = len(images_xml)

        return settings, image_count

    def get_images(self):
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
                path = image_xml.get('path')

                # Ensure path resolution even when xml_path is None
                if self.xml_path and not os.path.isabs(path):
                    dir = os.path.dirname(self.xml_path)
                    path = os.path.join(dir, path)

                image = {
                    'xml': image_xml,
                    'path': path,
                    'hidden': image_xml.get('hidden') == "True" if image_xml.get('hidden') else False
                }

                areas_of_interest = []
                for area_of_interest_xml in image_xml:
                    area_of_interest = {
                        'area': float(area_of_interest_xml.get('area', "0")),
                        'center': literal_eval(area_of_interest_xml.get('center', "(0, 0)")),
                        'radius': int(area_of_interest_xml.get('radius', "0"))
                    }
                    areas_of_interest.append(area_of_interest)
                image['areas_of_interest'] = areas_of_interest
                images.append(image)

        return images

    def add_settings_to_xml(self, **kwargs):
        """
        Add user-defined settings to the XML document.

        Args:
            **kwargs: Key-value pairs representing settings and their values.
        """
        try:
            root = self.xml.getroot()  # Ensure we are working with the root element
            settings_xml = root.find("settings")
            if settings_xml is None:
                settings_xml = ET.SubElement(root, "settings")

            for key, value in kwargs.items():

                if key == "options":
                    options_xml = settings_xml.find("options")
                    if options_xml is None:
                        options_xml = ET.SubElement(settings_xml, "options")
                    for option_key, option_value in value.items():
                        option_xml = ET.SubElement(options_xml, "option")
                        option_xml.set("name", option_key)
                        option_xml.set("value", str(option_value) if option_value else "")
                else:
                    val = str(value) if value else ""
                    settings_xml.set(key, val)
        except Exception as e:
            self.logger.error(e)

    def add_image_to_xml(self, img):
        """
        Add an image entry to the XML document.

        Args:
            img (dict): Dictionary with image path and areas of interest.
        """
        root = self.xml.getroot()
        images_xml = root.find("images")
        if images_xml is None:
            images_xml = ET.SubElement(root, "images")

        image = ET.SubElement(images_xml, 'image')
        image.set('path', img["path"])
        image.set('hidden', "False")

    def save_xml_file(self, path):
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
