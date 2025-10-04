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
                # Check for new mask-based approach
                mask_path = image_xml.get('mask_path', "")
                path = image_xml.get('path')

                # For mask files, they're stored as just filenames, so build full path
                if mask_path and self.xml_path:
                    # Mask files are in the same directory as the XML file
                    xml_dir = os.path.dirname(self.xml_path)
                    mask_path = os.path.join(xml_dir, mask_path)

                # Original image paths might be absolute or relative
                if path:
                    # Convert forward slashes back to platform-specific separator
                    path = path.replace('/', os.sep)

                    if not os.path.isabs(path) and self.xml_path:
                        # If relative, make it relative to XML location
                        dir = os.path.dirname(self.xml_path)
                        path = os.path.join(dir, path)

                image = {
                    'xml': image_xml,
                    'path': path,  # Original image path
                    'mask_path': mask_path,  # Mask file path (if using new approach)
                    'hidden': image_xml.get('hidden') == "True" if image_xml.get('hidden') else False
                }

                areas_of_interest = []
                for area_of_interest_xml in image_xml:
                    area_of_interest = {
                        'area': float(area_of_interest_xml.get('area', "0")),
                        'center': literal_eval(area_of_interest_xml.get('center', "(0, 0)")),
                        'radius': int(area_of_interest_xml.get('radius', "0")),
                        'xml': area_of_interest_xml  # Store XML element reference for updating
                    }
                    # Add optional fields if they exist (for backward compatibility)
                    if area_of_interest_xml.get('contour'):
                        area_of_interest['contour'] = literal_eval(area_of_interest_xml.get('contour'))
                    if area_of_interest_xml.get('detected_pixels'):
                        area_of_interest['detected_pixels'] = literal_eval(area_of_interest_xml.get('detected_pixels'))
                    # Always set flagged status (default to False if not present)
                    area_of_interest['flagged'] = area_of_interest_xml.get('flagged') == 'True'
                    # Load user comment (default to empty string if not present)
                    area_of_interest['user_comment'] = area_of_interest_xml.get('user_comment', '')
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

        # Check if this is a mask path (ends with .tif) or original image path
        if img["path"] and img["path"].endswith('.tif'):
            # This is a mask file, store just the filename as mask_path
            # This avoids path duplication issues
            image.set('mask_path', img["path"])
            # Store the original path as relative if possible
            if "original_path" in img:
                original_path = img["original_path"]
                # Try to make the path relative to the XML file location
                if self.xml_path and os.path.isabs(original_path):
                    try:
                        xml_dir = os.path.dirname(self.xml_path)
                        relative_path = os.path.relpath(original_path, xml_dir)
                        # Only use relative path if it doesn't go up too many levels
                        # (to avoid ../../../.. type paths that might break)
                        # Use forward slashes for consistency and cross-platform compatibility
                        relative_path = relative_path.replace('\\', '/')
                        if not relative_path.startswith('../../..'):
                            original_path = relative_path
                    except ValueError:
                        # Different drives on Windows, keep absolute
                        pass
                image.set('path', original_path)
        else:
            # Legacy support - old style with duplicated images
            image.set('path', img["path"])
        image.set('hidden', "False")

        for area in img["aois"]:
            area_xml = ET.SubElement(image, 'areas_of_interest')
            area_xml.set('center', str(area['center']))
            area_xml.set('radius', str(area['radius']))
            area_xml.set('area', str(area['area']))
            # Add flagged status if present
            if 'flagged' in area:
                area_xml.set('flagged', str(area['flagged']))
            # Save user comment if present
            if 'user_comment' in area and area['user_comment']:
                area_xml.set('user_comment', str(area['user_comment']))
            # Optionally save contour and detected_pixels if available
            # Note: These can be large, so we might want to make this configurable
            if 'contour' in area and area['contour']:
                area_xml.set('contour', str(area['contour']))
            if 'detected_pixels' in area and area['detected_pixels']:
                # Only save a limited number of pixels to avoid huge XML files
                # Full pixel data is preserved in the image XMP metadata
                if len(area['detected_pixels']) <= 100:
                    area_xml.set('detected_pixels', str(area['detected_pixels']))

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
