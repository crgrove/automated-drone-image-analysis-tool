import os
import math
from ast import literal_eval
from datetime import datetime
import uuid
import xml.etree.ElementTree as ET
from core.services.GridReviewService import GridReviewService
from core.services.LoggerService import LoggerService


class XmlService:
    """Service for parsing and modifying an ADIAT XML file.

    Provides utilities for reading and writing ADIAT analysis results in XML format,
    including settings, images, and areas of interest.

    Attributes:
        xml_path: Path to the XML file, or None if creating new.
        xml: ElementTree instance for the XML document.
        logger: LoggerService instance for logging.
    """

    def __init__(self, path=None):
        """Initialize the XmlService with an optional XML file path.

        Args:
            path: Path to the XML file. If None, creates a new empty XML tree.
        """
        self.xml_path = path
        self.logger = LoggerService()

        if path is not None:
            self.xml = ET.parse(path)
        else:
            root = ET.Element('data')
            self.xml = ET.ElementTree(root)  # Ensures self.xml is an ElementTree

    def get_settings(self):
        """Parse the XML file to retrieve settings and the count of images with areas of interest.

        Returns:
            Tuple of (settings_dict, image_count) where settings_dict contains
            analysis settings and image_count is the number of images with areas
            of interest.
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
                result = literal_eval(value) if value and value != "None" else default
                # Normalize to tuple of integers to ensure consistent format
                if isinstance(result, (tuple, list)) and len(result) >= 3:
                    return (int(result[0]), int(result[1]), int(result[2]))
                return default
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
            if options_xml is not None:
                for option in options_xml:
                    settings['options'][option.get('name')] = option.get('value')

        images_xml = root.find('images')
        if images_xml is not None:
            image_count = len(images_xml)

        return settings, image_count

    def get_images(self):
        """Parse the XML file to retrieve images with areas of interest.

        Returns:
            List of dictionaries containing image details and areas of interest
            from the analysis. Each dict includes 'path', 'mask_path', 'bearing'
            metadata if present, and 'areas_of_interest' list.
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
                    'path': path,  # Current/resolved image path
                    'xml_path': image_xml.get('path'),  # Original path from XML (for legacy cache lookups)
                    'mask_path': mask_path,  # Mask file path (if using new approach)
                    'hidden': image_xml.get('hidden') == "True" if image_xml.get('hidden') else False
                }

                # Load image dimensions if present
                if image_xml.get('width'):
                    try:
                        image['width'] = int(image_xml.get('width'))
                    except (ValueError, TypeError):
                        image['width'] = None
                else:
                    image['width'] = None

                if image_xml.get('height'):
                    try:
                        image['height'] = int(image_xml.get('height'))
                    except (ValueError, TypeError):
                        image['height'] = None
                else:
                    image['height'] = None

                # Load bearing metadata if present
                if image_xml.get('bearing'):
                    image['bearing'] = float(image_xml.get('bearing'))
                if image_xml.get('bearing_source'):
                    image['bearing_source'] = image_xml.get('bearing_source')
                if image_xml.get('bearing_quality'):
                    image['bearing_quality'] = image_xml.get('bearing_quality')

                # Load manual FOV alignment if present
                fov_alignment = self._parse_fov_alignment(image_xml)
                if fov_alignment is not None:
                    image['fov_alignment'] = fov_alignment

                # Load grid review state if present (None when absent/malformed)
                image['grid_review'] = self._parse_grid_review(image_xml)

                areas_of_interest = []
                # NOTE: every child element of <image> is treated as an AOI here,
                # in this and every shipped version of ADIAT. New per-image state
                # MUST be stored as attributes on <image> (like 'hidden',
                # 'bearing*', 'fov_*', 'grid_*'), never as child elements, or old
                # builds will mis-parse it as an AOI.
                for area_of_interest_xml in image_xml:
                    area_of_interest = {
                        'area': float(area_of_interest_xml.get('area', "0")),
                        'center': literal_eval(area_of_interest_xml.get('center', "(0, 0)")),
                        'radius': int(area_of_interest_xml.get('radius', "0")),
                        'xml': area_of_interest_xml  # Store XML element reference for updating
                    }
                    # Load the persisted run-wide unique AOI number when present.
                    # Legacy result files omit it; XmlService.ensure_aoi_numbers
                    # backfills numbers the first time such a file is opened.
                    number_attr = area_of_interest_xml.get('number')
                    if number_attr is not None:
                        try:
                            area_of_interest['number'] = int(number_attr)
                        except (ValueError, TypeError):
                            pass
                    # Add optional fields if they exist (for backward compatibility)
                    if area_of_interest_xml.get('contour'):
                        area_of_interest['contour'] = literal_eval(area_of_interest_xml.get('contour'))
                    if area_of_interest_xml.get('detected_pixels'):
                        area_of_interest['detected_pixels'] = literal_eval(area_of_interest_xml.get('detected_pixels'))
                    # Always set flagged status (default to False if not present)
                    area_of_interest['flagged'] = area_of_interest_xml.get('flagged') == 'True'
                    # Load user comment (default to empty string if not present)
                    area_of_interest['user_comment'] = area_of_interest_xml.get('user_comment', '')
                    # Load user_created flag (default to False if not present)
                    area_of_interest['user_created'] = area_of_interest_xml.get('user_created') == 'True'
                    # Load confidence scoring data if present
                    if area_of_interest_xml.get('confidence'):
                        area_of_interest['confidence'] = float(area_of_interest_xml.get('confidence'))
                    if area_of_interest_xml.get('score_type'):
                        area_of_interest['score_type'] = area_of_interest_xml.get('score_type')
                    if area_of_interest_xml.get('raw_score'):
                        area_of_interest['raw_score'] = float(area_of_interest_xml.get('raw_score'))
                    if area_of_interest_xml.get('score_method'):
                        area_of_interest['score_method'] = area_of_interest_xml.get('score_method')
                    # Load temperature data if present (for thermal datasets)
                    if area_of_interest_xml.get('temperature'):
                        area_of_interest['temperature'] = float(area_of_interest_xml.get('temperature'))
                    # Load color cache data if present
                    if area_of_interest_xml.get('color_rgb'):
                        area_of_interest['color_info'] = {
                            'rgb': literal_eval(area_of_interest_xml.get('color_rgb')),
                            'hex': area_of_interest_xml.get('color_hex', ''),
                            'hue_degrees': float(area_of_interest_xml.get('color_hue', 0))
                        }
                    # Load team assignment if present
                    team_value = area_of_interest_xml.get('team', '')
                    if team_value:
                        area_of_interest['team'] = team_value

                    areas_of_interest.append(area_of_interest)
                image['areas_of_interest'] = areas_of_interest
                images.append(image)

        return images

    def ensure_aoi_numbers(self, images):
        """Backfill run-wide unique AOI numbers onto legacy result files.

        Every AOI carries a persistent 'number' that is unique across the
        whole run, letting reviewers track a specific AOI even after the
        gallery is re-sorted or filtered. Result files produced before this
        feature lack the number; this method walks every AOI in
        viewer/display order and assigns one to any AOI missing it. AOIs
        that already have a number keep it, so numbers stay stable across
        sessions and survive AOI deletion. New numbers are written onto
        both the AOI dict and its backing XML element; the caller is
        responsible for saving the file.

        Args:
            images: The images list returned by get_images().

        Returns:
            bool: True if at least one number was assigned, meaning the
                file should be saved to persist the change.
        """
        highest = 0
        for image in images or []:
            for aoi in image.get('areas_of_interest', []):
                number = aoi.get('number')
                if isinstance(number, int) and number > highest:
                    highest = number

        next_number = highest + 1
        changed = False
        for image in images or []:
            for aoi in image.get('areas_of_interest', []):
                if isinstance(aoi.get('number'), int):
                    continue
                aoi['number'] = next_number
                xml_element = aoi.get('xml')
                if xml_element is not None:
                    xml_element.set('number', str(next_number))
                next_number += 1
                changed = True

        return changed

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

        # Store image dimensions if available
        if 'width' in img and img['width']:
            image.set('width', str(img['width']))
        if 'height' in img and img['height']:
            image.set('height', str(img['height']))

        temp_count = 0  # Track AOIs with temperature data
        for area in img["aois"]:
            area_xml = ET.SubElement(image, 'areas_of_interest')
            area_xml.set('center', str(area['center']))
            area_xml.set('radius', str(area['radius']))
            area_xml.set('area', str(area['area']))
            # Persist the run-wide unique AOI number when present
            if area.get('number') is not None:
                area_xml.set('number', str(area['number']))
            # Add flagged status if present
            if 'flagged' in area:
                area_xml.set('flagged', str(area['flagged']))
            # Save user comment if present
            if 'user_comment' in area and area['user_comment']:
                area_xml.set('user_comment', str(area['user_comment']))
            # Save confidence scoring data if present
            if 'confidence' in area:
                area_xml.set('confidence', str(area['confidence']))
            if 'score_type' in area:
                area_xml.set('score_type', str(area['score_type']))
            if 'raw_score' in area:
                area_xml.set('raw_score', str(area['raw_score']))
            if 'score_method' in area:
                area_xml.set('score_method', str(area['score_method']))
            # Save temperature data if present (for thermal datasets)
            if 'temperature' in area and area['temperature'] is not None:
                area_xml.set('temperature', str(area['temperature']))
                temp_count += 1
            # Save color cache data if present
            if 'color_info' in area and area['color_info']:
                color_info = area['color_info']
                if 'rgb' in color_info:
                    area_xml.set('color_rgb', str(color_info['rgb']))
                if 'hex' in color_info:
                    area_xml.set('color_hex', str(color_info['hex']))
                if 'hue_degrees' in color_info:
                    area_xml.set('color_hue', str(color_info['hue_degrees']))
            # Optionally save contour and detected_pixels if available
            # Note: These can be large, so we might want to make this configurable
            if 'contour' in area and area['contour']:
                area_xml.set('contour', str(area['contour']))
            if 'detected_pixels' in area and area['detected_pixels']:
                # Only save a limited number of pixels to avoid huge XML files
                # Full pixel data is preserved in the image XMP metadata
                if len(area['detected_pixels']) <= 100:
                    area_xml.set('detected_pixels', str(area['detected_pixels']))

        # Debug logging for temperature save
        if temp_count > 0:
            # self.logger.debug(f"Saved {temp_count} AOIs with temperature data for image {img.get('path', 'unknown')}")
            pass

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

    def get_review_metadata(self):
        """
        Get review metadata from the XML file.

        Returns:
            dict: Dictionary containing review_id, reviewer_name, and review_date, or None if not present.
        """
        root = self.xml.getroot()
        review_meta_xml = root.find("review_metadata")

        if review_meta_xml is not None:
            return {
                'review_id': review_meta_xml.get('review_id', ''),
                'reviewer_name': review_meta_xml.get('reviewer_name', ''),
                'review_date': review_meta_xml.get('review_date', '')
            }

        return None

    def add_review_metadata(self, review_id, reviewer_name, review_date):
        """
        Add or update review metadata in the XML document.

        Args:
            review_id (str): Unique identifier for this review session (UUID).
            reviewer_name (str): Name of the reviewer.
            review_date (str): ISO format date/time of the review.
        """
        try:
            root = self.xml.getroot()
            review_meta_xml = root.find("review_metadata")

            if review_meta_xml is None:
                # Create new review_metadata element as first child
                review_meta_xml = ET.Element("review_metadata")
                root.insert(0, review_meta_xml)

            # Set attributes
            review_meta_xml.set('review_id', review_id)
            review_meta_xml.set('reviewer_name', reviewer_name)
            review_meta_xml.set('review_date', review_date)

        except Exception as e:
            self.logger.error(f"Error adding review metadata: {e}")

    def ensure_review_id(self):
        """
        Ensure a review_id exists in the XML. Generate one if not present.

        Returns:
            str: The review_id (existing or newly generated).
        """
        review_meta = self.get_review_metadata()

        if review_meta and review_meta.get('review_id'):
            return review_meta['review_id']

        # Generate new review ID
        review_id = str(uuid.uuid4())
        review_date = datetime.now().isoformat()
        self.add_review_metadata(review_id, '', review_date)

        return review_id

    def set_image_bearing(self, image_path, bearing_deg, source='calculated', quality='good'):
        """
        Set bearing metadata for an image in the XML.

        Args:
            image_path (str): Path to the image (should match the 'path' attribute or resolved path).
            bearing_deg (float): Bearing in degrees [0, 360).
            source (str): Source of bearing ('kml', 'gpx', 'csv', 'auto_prev_next', etc.).
            quality (str): Quality indicator ('good', 'turn_inferred', 'gap', 'hover_estimate').

        Returns:
            bool: True if image was found and updated, False otherwise.
        """
        try:
            root = self.xml.getroot()
            images_xml = root.find('images')

            if images_xml is None:
                return False

            # Normalize path for comparison
            image_path_norm = os.path.normpath(image_path)

            for image_xml in images_xml:
                # Get stored path and resolve it
                stored_path = image_xml.get('path')
                if stored_path:
                    stored_path = stored_path.replace('/', os.sep)
                    if not os.path.isabs(stored_path) and self.xml_path:
                        xml_dir = os.path.dirname(self.xml_path)
                        stored_path = os.path.join(xml_dir, stored_path)
                    stored_path_norm = os.path.normpath(stored_path)

                    # Check if paths match
                    if stored_path_norm == image_path_norm:
                        # Set bearing attributes
                        image_xml.set('bearing', f"{bearing_deg:.2f}")
                        image_xml.set('bearing_source', source)
                        image_xml.set('bearing_quality', quality)
                        return True

            self.logger.warning(f"Image not found in XML for bearing update: {image_path}")
            return False

        except Exception as e:
            self.logger.error(f"Error setting image bearing: {e}")
            return False

    @staticmethod
    def _parse_fov_alignment(image_xml):
        """Parse manual FOV alignment attributes from an <image> element.

        Args:
            image_xml: The <image> ElementTree element.

        Returns:
            dict with 'corners' (4 (lat, lon) tuples, TL TR BR BL order),
            'tie_points' (list of (u, v, lat, lon) tuples) and 'rotation'
            (float degrees), or None when the image has no usable alignment.
        """
        corner_keys = ('fov_corner_tl', 'fov_corner_tr', 'fov_corner_br', 'fov_corner_bl')
        raw_corners = [image_xml.get(key) for key in corner_keys]
        if any(value is None for value in raw_corners):
            return None

        corners = []
        try:
            for value in raw_corners:
                lat_str, lon_str = value.split(',')
                lat, lon = float(lat_str), float(lon_str)
                if not (math.isfinite(lat) and math.isfinite(lon)):
                    return None
                corners.append((lat, lon))
        except (ValueError, AttributeError):
            # Malformed corner data - treat the image as unrefined.
            return None

        tie_points = []
        raw_tie_points = image_xml.get('fov_tie_points')
        if raw_tie_points:
            try:
                for u, v, lat, lon in literal_eval(raw_tie_points):
                    tie_points.append((float(u), float(v), float(lat), float(lon)))
            except (ValueError, SyntaxError, TypeError):
                # Malformed tie points - drop them but keep the corners.
                tie_points = []

        rotation = 0.0
        raw_rotation = image_xml.get('fov_align_rotation')
        if raw_rotation:
            try:
                rotation = float(raw_rotation)
            except ValueError:
                rotation = 0.0

        return {'corners': corners, 'tie_points': tie_points, 'rotation': rotation}

    def _find_image_element(self, image_path):
        """Find the <image> element whose resolved path matches image_path.

        Args:
            image_path (str): Path to the image (matches 'path' or resolved path).

        Returns:
            The matching <image> ElementTree element, or None.
        """
        root = self.xml.getroot()
        images_xml = root.find('images')
        if images_xml is None:
            return None

        image_path_norm = os.path.normpath(image_path)

        for image_xml in images_xml:
            stored_path = image_xml.get('path')
            if not stored_path:
                continue
            stored_path = stored_path.replace('/', os.sep)
            if not os.path.isabs(stored_path) and self.xml_path:
                xml_dir = os.path.dirname(self.xml_path)
                stored_path = os.path.join(xml_dir, stored_path)
            if os.path.normpath(stored_path) == image_path_norm:
                return image_xml

        return None

    def set_image_fov_alignment(self, image_path, corners, tie_points=None, rotation=0.0):
        """Store manual FOV alignment data for an image as <image> attributes.

        Mirrors the bearing cache: the four user-aligned footprint corners, any
        optional interior tie points, and the viewing rotation are written as
        attributes on the matching <image> element.

        Args:
            image_path (str): Path to the image (matches 'path' or resolved path).
            corners (list): Four (lat, lon) pairs in TL, TR, BR, BL order.
            tie_points (list): Optional list of (u, v, lat, lon) tuples.
            rotation (float): Viewing rotation in degrees (dialog restore only).

        Returns:
            bool: True if the image was found and updated, False otherwise.
        """
        try:
            if corners is None or len(corners) != 4:
                return False

            image_xml = self._find_image_element(image_path)
            if image_xml is None:
                self.logger.warning(f"Image not found in XML for FOV alignment update: {image_path}")
                return False

            corner_keys = ('fov_corner_tl', 'fov_corner_tr', 'fov_corner_br', 'fov_corner_bl')
            for key, (lat, lon) in zip(corner_keys, corners):
                image_xml.set(key, f"{float(lat):.8f},{float(lon):.8f}")

            if tie_points:
                normalized = [
                    (float(u), float(v), float(lat), float(lon))
                    for u, v, lat, lon in tie_points
                ]
                image_xml.set('fov_tie_points', repr(normalized))
            elif 'fov_tie_points' in image_xml.attrib:
                del image_xml.attrib['fov_tie_points']

            image_xml.set('fov_align_rotation', f"{float(rotation):.4f}")
            return True

        except Exception as e:
            self.logger.error(f"Error setting image FOV alignment: {e}")
            return False

    @staticmethod
    def _parse_grid_review(image_xml):
        """Parse grid review attributes from an <image> element.

        Args:
            image_xml: The <image> ElementTree element.

        Returns:
            dict with 'rows' (int), 'cols' (int) and 'reviewed' (set of
            row-major cell indices), or None when the image has no usable
            grid review state.
        """
        rows_attr = image_xml.get('grid_rows')
        cols_attr = image_xml.get('grid_cols')
        if rows_attr is None or cols_attr is None:
            return None

        try:
            rows = int(rows_attr)
            cols = int(cols_attr)
        except (ValueError, TypeError):
            # Malformed grid dimensions - treat the image as unreviewed.
            return None

        if rows < 1 or cols < 1:
            return None

        reviewed = GridReviewService.parse_reviewed(image_xml.get('grid_reviewed'))
        return {'rows': rows, 'cols': cols, 'reviewed': reviewed}

    def set_image_grid_review(self, image_xml, rows, cols, reviewed_cells):
        """Store grid review state for an image as <image> attributes.

        Grid state is stored as attributes (never child elements) so old
        ADIAT builds, which treat every <image> child as an AOI, keep
        loading these files correctly.

        Args:
            image_xml: The <image> ElementTree element to update.
            rows (int): Number of grid rows.
            cols (int): Number of grid columns.
            reviewed_cells: Iterable of reviewed row-major cell indices.

        Returns:
            bool: True on success, False otherwise.
        """
        try:
            image_xml.set('grid_rows', str(int(rows)))
            image_xml.set('grid_cols', str(int(cols)))
            image_xml.set('grid_reviewed', GridReviewService.serialize_reviewed(reviewed_cells))
            return True
        except Exception as e:
            self.logger.error(f"Error setting image grid review state: {e}")
            return False

    def clear_image_grid_review(self, image_xml):
        """Remove any grid review attributes from an <image> element.

        Args:
            image_xml: The <image> ElementTree element to update.

        Returns:
            bool: True on success, False otherwise.
        """
        try:
            for attr in ('grid_rows', 'grid_cols', 'grid_reviewed'):
                if attr in image_xml.attrib:
                    del image_xml.attrib[attr]
            return True
        except Exception as e:
            self.logger.error(f"Error clearing image grid review state: {e}")
            return False

    def clear_image_fov_alignment(self, image_path):
        """Remove any manual FOV alignment attributes for an image.

        Args:
            image_path (str): Path to the image.

        Returns:
            bool: True if the image was found, False otherwise.
        """
        try:
            image_xml = self._find_image_element(image_path)
            if image_xml is None:
                return False

            for attr in ('fov_corner_tl', 'fov_corner_tr', 'fov_corner_br',
                         'fov_corner_bl', 'fov_tie_points', 'fov_align_rotation'):
                if attr in image_xml.attrib:
                    del image_xml.attrib[attr]
            return True

        except Exception as e:
            self.logger.error(f"Error clearing image FOV alignment: {e}")
            return False

    def get_team_planning(self):
        """Load team definitions from the XML <team_planning> block.

        Returns:
            list[dict]: Team definitions, each with 'name' and 'color' keys.
                        Empty list if no team planning data exists.
        """
        root = self.xml.getroot()
        planning_xml = root.find('team_planning')
        teams = []
        if planning_xml is not None:
            for team_xml in planning_xml.findall('team'):
                teams.append({
                    'name': team_xml.get('name', ''),
                    'color': team_xml.get('color', '#888888'),
                })
        return teams

    def save_team_planning(self, teams):
        """Persist team definitions into the XML <team_planning> block.

        Replaces any existing block with the supplied list.

        Args:
            teams: list[dict] with 'name' and 'color' keys per team.
        """
        root = self.xml.getroot()
        existing = root.find('team_planning')
        if existing is not None:
            root.remove(existing)

        if teams:
            planning_xml = ET.SubElement(root, 'team_planning')
            for team in teams:
                team_xml = ET.SubElement(planning_xml, 'team')
                team_xml.set('name', team['name'])
                team_xml.set('color', team['color'])

    def save_aoi_team(self, image_index, aoi_index, team_name, images):
        """Set (or clear) the team assignment for a single AOI and persist to XML.

        Args:
            image_index: Index of the image in the images list.
            aoi_index: Index of the AOI within the image.
            team_name: Team name string, or '' to clear assignment.
            images: The live images list (same refs as Viewer.images).
        """
        if 0 <= image_index < len(images):
            image = images[image_index]
            aois = image.get('areas_of_interest', [])
            if 0 <= aoi_index < len(aois):
                aoi = aois[aoi_index]
                if team_name:
                    aoi['team'] = team_name
                else:
                    aoi.pop('team', None)
                xml_el = aoi.get('xml')
                if xml_el is not None:
                    if team_name:
                        xml_el.set('team', team_name)
                    elif 'team' in xml_el.attrib:
                        del xml_el.attrib['team']

    def get_image_bearing(self, image_path):
        """
        Get bearing metadata for an image from the XML.

        Args:
            image_path (str): Path to the image.

        Returns:
            dict or None: Dictionary with 'bearing', 'source', 'quality', or None if not found.
        """
        try:
            root = self.xml.getroot()
            images_xml = root.find('images')

            if images_xml is None:
                return None

            # Normalize path for comparison
            image_path_norm = os.path.normpath(image_path)

            for image_xml in images_xml:
                # Get stored path and resolve it
                stored_path = image_xml.get('path')
                if stored_path:
                    stored_path = stored_path.replace('/', os.sep)
                    if not os.path.isabs(stored_path) and self.xml_path:
                        xml_dir = os.path.dirname(self.xml_path)
                        stored_path = os.path.join(xml_dir, stored_path)
                    stored_path_norm = os.path.normpath(stored_path)

                    # Check if paths match
                    if stored_path_norm == image_path_norm:
                        if image_xml.get('bearing'):
                            return {
                                'bearing': float(image_xml.get('bearing')),
                                'source': image_xml.get('bearing_source', 'unknown'),
                                'quality': image_xml.get('bearing_quality', 'unknown')
                            }
                        return None

            return None

        except Exception as e:
            self.logger.error(f"Error getting image bearing: {e}")
            return None

    def set_multiple_bearings(self, bearing_results):
        """
        Set bearing metadata for multiple images efficiently.

        Args:
            bearing_results (dict): Dictionary mapping image paths to bearing result objects.
                Each result should have: bearing_deg, source, quality attributes.

        Returns:
            int: Number of images successfully updated.
        """
        try:
            updated_count = 0

            for image_path, result in bearing_results.items():
                success = self.set_image_bearing(
                    image_path,
                    result.bearing_deg,
                    result.source,
                    result.quality
                )
                if success:
                    updated_count += 1

            # self.logger.info(f"Updated bearing metadata for {updated_count}/{len(bearing_results)} images")
            return updated_count

        except Exception as e:
            self.logger.error(f"Error setting multiple bearings: {e}")
            return 0
