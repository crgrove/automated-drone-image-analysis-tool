"""
GPSMapController - Manages GPS map visualization for the image viewer.

This controller handles the GPS map window lifecycle, data extraction,
and coordination between the map and main viewer.
"""

from PySide6.QtCore import QObject, Signal
from helpers.LocationInfo import LocationInfo
from core.services.LoggerService import LoggerService
import piexif
from datetime import datetime


class GPSMapController(QObject):
    """
    Controller for GPS map functionality.

    Manages GPS data extraction, map window creation, and image selection
    coordination between the map and main viewer.
    """

    # Signal emitted when an image is selected from the map
    image_selected = Signal(int)

    def __init__(self, parent_viewer, logger=None):
        """
        Initialize the GPS map controller.

        Args:
            parent_viewer: The main Viewer instance
            logger: Optional logger instance for error reporting
        """
        super().__init__()
        self.parent = parent_viewer
        self.logger = logger or LoggerService()
        self.map_dialog = None
        self.gps_data = []

    def show_map(self):
        """
        Show the GPS map window.

        Extracts GPS data from images and creates/shows the map dialog.
        """
        # Extract GPS data from all images
        self.extract_gps_data()

        if not self.gps_data:
            self.parent.status_controller.show_toast("No GPS data found in images", 3000, color="#F44336")
            return

        # Create and show the map dialog
        from .GPSMapDialog import GPSMapDialog

        # Find the current image in the GPS data list
        current_gps_index = None
        for i, data in enumerate(self.gps_data):
            if data['index'] == self.parent.current_image:
                current_gps_index = i
                break

        if self.map_dialog is None:
            self.map_dialog = GPSMapDialog(self.parent, self.gps_data, current_gps_index)
            self.map_dialog.image_selected.connect(self.on_map_image_selected)
        else:
            # Update with latest data if dialog already exists
            self.map_dialog.update_gps_data(self.gps_data, current_gps_index)

        self.map_dialog.show()
        self.map_dialog.raise_()
        self.map_dialog.activateWindow()

    def extract_gps_data(self):
        """
        Extract GPS coordinates and timestamps from all images.

        Populates self.gps_data with a list of dictionaries containing:
        - index: Image index in the viewer
        - latitude: GPS latitude
        - longitude: GPS longitude
        - timestamp: Image capture time
        - name: Image filename
        - has_aoi: Whether image has areas of interest
        """
        self.gps_data = []

        for idx, image in enumerate(self.parent.images):
            try:
                # Get EXIF data first, then extract GPS
                # This bypasses the JPEG-only restriction in LocationInfo.get_gps()
                from helpers.MetaDataHelper import MetaDataHelper
                exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
                gps_coords = LocationInfo.get_gps(exif_data=exif_data)

                if gps_coords:
                    # Extract timestamp from EXIF if available
                    timestamp = self.get_image_timestamp_from_exif(exif_data)

                    # Check if image has AOIs and count them
                    has_aoi = 'areas_of_interest' in image and len(image['areas_of_interest']) > 0
                    aoi_count = len(image.get('areas_of_interest', [])) if 'areas_of_interest' in image else 0

                    # Check if image is hidden
                    is_hidden = image.get('hidden', False)

                    # Check if image has any flagged AOIs
                    has_flagged = False
                    if 'areas_of_interest' in image:
                        for aoi in image['areas_of_interest']:
                            if aoi.get('flagged', False):
                                has_flagged = True
                                break

                    # Don't extract bearing here - do it lazily when needed
                    self.gps_data.append({
                        'index': idx,
                        'latitude': gps_coords['latitude'],
                        'longitude': gps_coords['longitude'],
                        'timestamp': timestamp,
                        'name': image.get('name', f'Image {idx + 1}'),
                        'has_aoi': has_aoi,
                        'aoi_count': aoi_count,
                        'hidden': is_hidden,
                        'has_flagged': has_flagged,
                        'bearing': None,  # Will be loaded on demand
                        'image_path': image['path']  # Store path for later bearing extraction
                    })
            except Exception as e:
                self.logger.log(f"Could not extract GPS from image {idx}: {str(e)}")

        # Sort by timestamp if available
        self.gps_data.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min)

    def get_image_timestamp_from_exif(self, exif_data):
        """
        Extract timestamp from EXIF data.

        Args:
            exif_data: Pre-loaded EXIF data dictionary

        Returns:
            datetime object or None if timestamp not found
        """
        try:

            if exif_data and 'Exif' in exif_data:
                # Try to get DateTimeOriginal
                datetime_original = exif_data['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
                if datetime_original:
                    datetime_str = datetime_original.decode('utf-8') if isinstance(datetime_original, bytes) else datetime_original
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')

                # Fallback to DateTime
                datetime_tag = exif_data['Exif'].get(piexif.ExifIFD.DateTime)
                if datetime_tag:
                    datetime_str = datetime_tag.decode('utf-8') if isinstance(datetime_tag, bytes) else datetime_tag
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')

        except Exception as e:
            self.logger.log(f"Could not extract timestamp: {str(e)}")

        return None

    def get_image_timestamp(self, image_path):
        """
        Extract timestamp from image EXIF data (compatibility method).

        Args:
            image_path: Path to the image file

        Returns:
            datetime object or None if timestamp not found
        """
        from helpers.MetaDataHelper import MetaDataHelper
        exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
        return self.get_image_timestamp_from_exif(exif_data)

    def get_image_bearing(self, image_path):
        """
        Extract bearing/yaw information from image.

        Args:
            image_path: Path to the image file

        Returns:
            float: Bearing in degrees (0-360), or None if not available
        """
        try:
            from core.services.ImageService import ImageService
            image_service = ImageService(image_path, '')
            bearing = image_service.get_drone_orientation()
            return bearing
        except Exception as e:
            self.logger.log(f"Could not extract bearing: {str(e)}")
            return None

    def on_map_image_selected(self, image_index):
        """
        Handle image selection from the map.

        Args:
            image_index: Index of the selected image
        """
        if 0 <= image_index < len(self.parent.images):
            self.parent.current_image = image_index
            self.parent._load_image()

    def update_current_image(self, image_index):
        """
        Update the map to highlight a new current image.

        Args:
            image_index: Index of the new current image in the viewer's image list
        """
        if self.map_dialog and self.map_dialog.isVisible():
            # Find the gps_data list index for this image
            for i, data in enumerate(self.gps_data):
                if data['index'] == image_index:
                    self.map_dialog.set_current_image(i)
                    break

    def close_map(self):
        """Close the GPS map window if it's open."""
        if self.map_dialog:
            self.map_dialog.close()
            self.map_dialog = None