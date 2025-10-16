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
import math


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

        # Show current AOI if one is selected
        self.update_aoi_on_map()

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
                self.logger.error(f"Could not extract GPS from image {idx}: {str(e)}")

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
            self.logger.error(f"Could not extract timestamp: {str(e)}")

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
            # Use get_image_bearing() which accounts for both Flight Yaw and Gimbal Yaw
            bearing = image_service.get_image_bearing()
            return bearing
        except Exception as e:
            self.logger.error(f"Could not extract bearing: {str(e)}")
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

            # Clear AOI marker when switching images (will be re-added if AOI is selected)
            self.map_dialog.update_aoi_marker(None, None)

    def close_map(self):
        """Close the GPS map window if it's open."""
        if self.map_dialog:
            self.map_dialog.close()
            self.map_dialog = None

    def calculate_aoi_gps_coordinates(self, image_gps, aoi_center, image_center, gsd_cm, bearing_deg):
        """
        Calculate GPS coordinates for an AOI based on its pixel position.

        Args:
            image_gps: Dict with 'latitude' and 'longitude' of image center
            aoi_center: Tuple (x, y) of AOI center in pixels
            image_center: Tuple (width/2, height/2) of image center in pixels
            gsd_cm: Ground sampling distance in centimeters
            bearing_deg: Image bearing/yaw in degrees (0-360)

        Returns:
            Dict with 'latitude' and 'longitude' of the AOI, or None if calculation fails
        """
        try:
            # Convert GSD from cm to meters
            gsd_m = gsd_cm / 100.0

            # Calculate pixel offset from image center
            dx_pixels = aoi_center[0] - image_center[0]
            dy_pixels = aoi_center[1] - image_center[1]

            # Convert pixel offset to meters
            # In image coordinates: X is right, Y is down
            # We want: X (east), Y (north) in meters
            dx_image = dx_pixels * gsd_m  # Right is positive
            dy_image = dy_pixels * gsd_m  # Down is positive

            # Convert bearing to radians
            # Bearing is clockwise from north (0° = North, 90° = East, etc.)
            # We need to use negative bearing to transform from image to world coordinates
            # This matches how the map view rotates: self.rotate(-bearing)
            bearing_rad = math.radians(-bearing_deg)

            # Apply rotation to get world coordinates
            # When bearing is 0 (north): image top points north
            # When bearing is 90 (east): image top points east, image right points south
            # The transformation from image to world coordinates uses -bearing:
            # world_north = -image_y * cos(-bearing) + image_x * sin(-bearing)
            # world_east = image_x * cos(-bearing) + image_y * sin(-bearing)

            north_meters = -dy_image * math.cos(bearing_rad) + dx_image * math.sin(bearing_rad)
            east_meters = dx_image * math.cos(bearing_rad) + dy_image * math.sin(bearing_rad)

            # Convert meters offset to lat/lon degrees
            # Approximate conversion (accurate for small distances)
            lat = image_gps['latitude']
            lon = image_gps['longitude']

            # Earth radius in meters
            earth_radius = 6371000

            # Convert meters to degrees
            delta_lat = north_meters / earth_radius * (180 / math.pi)
            delta_lon = east_meters / (earth_radius * math.cos(math.radians(lat))) * (180 / math.pi)

            # Calculate AOI GPS coordinates
            aoi_lat = lat + delta_lat
            aoi_lon = lon + delta_lon

            return {
                'latitude': aoi_lat,
                'longitude': aoi_lon
            }

        except Exception as e:
            self.logger.error(f"Error calculating AOI GPS coordinates: {e}")
            return None

    def get_current_aoi_gps(self):
        """
        Get GPS coordinates for the currently selected AOI.

        Returns:
            Dict with AOI GPS data including coordinates and metadata, or None
        """
        try:
            # Check if we have a selected AOI
            if not hasattr(self.parent, 'aoi_controller') or self.parent.aoi_controller.selected_aoi_index < 0:
                return None

            # Get current image data
            current_image = self.parent.images[self.parent.current_image]

            # Get AOI data
            aoi_index = self.parent.aoi_controller.selected_aoi_index
            if 'areas_of_interest' not in current_image or aoi_index >= len(current_image['areas_of_interest']):
                return None

            aoi = current_image['areas_of_interest'][aoi_index]

            # Get image GPS coordinates
            from helpers.MetaDataHelper import MetaDataHelper
            exif_data = MetaDataHelper.get_exif_data_piexif(current_image['path'])
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)

            if not gps_coords:
                return None

            # Get image dimensions
            from core.services.ImageService import ImageService
            image_service = ImageService(current_image['path'], current_image.get('mask_path', ''))
            img_array = image_service.img_array
            height, width = img_array.shape[:2]

            # Check gimbal pitch angle - must be within 5 degrees of nadir
            _, gimbal_pitch = image_service.get_gimbal_orientation()
            if gimbal_pitch is not None:
                # Nadir is typically -90 degrees for most drones (camera pointing straight down)
                # Allow range from -85 to -95 degrees (5 degree tolerance)
                if not (-95 <= gimbal_pitch <= -85):
                    # Show toast message about gimbal angle
                    if hasattr(self.parent, 'status_controller'):
                        self.parent.status_controller.show_toast(
                            f"Gimbal angle not nadir ({gimbal_pitch:.1f}°). AOI GPS location not calculated.",
                            4000,
                            color="#FF9800"
                        )
                    return None

            # Get bearing
            # Use get_drone_orientation() to match the Drone Orientation displayed in viewer
            # For nadir shots (required by gimbal pitch check above), drone orientation is correct
            bearing = image_service.get_drone_orientation()
            if bearing is None:
                bearing = 0  # Default to north if bearing not available

            # Get custom altitude if available
            custom_alt = self.parent.custom_agl_altitude_ft if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0 else None

            # Get GSD (Ground Sampling Distance)
            gsd_value = self.parent.messages.get('GSD (cm/px)', None)
            if gsd_value:
                # Extract numeric value from string like "2.5 cm/px"
                try:
                    gsd_cm = float(gsd_value.split()[0])
                except (ValueError, IndexError):
                    gsd_cm = self.calculate_gsd_for_image(current_image['path'], custom_altitude_ft=custom_alt)
                    if gsd_cm is None:
                        return None
            else:
                # Try to calculate GSD if not in messages
                gsd_cm = self.calculate_gsd_for_image(current_image['path'], custom_altitude_ft=custom_alt)
                if gsd_cm is None:
                    return None

            # Calculate AOI GPS coordinates
            aoi_gps = self.calculate_aoi_gps_coordinates(
                gps_coords,
                aoi['center'],
                (width/2, height/2),
                gsd_cm,
                bearing
            )

            if not aoi_gps:
                return None

            # Add AOI metadata
            aoi_gps['aoi_index'] = aoi_index
            aoi_gps['pixel_area'] = aoi.get('area', 0)
            aoi_gps['center_pixels'] = aoi['center']
            aoi_gps['image_index'] = self.parent.current_image
            aoi_gps['image_name'] = current_image.get('name', 'Unknown')

            # Get color/temperature info if available
            if hasattr(self.parent.aoi_controller, 'calculate_aoi_average_info'):
                avg_info, _ = self.parent.aoi_controller.calculate_aoi_average_info(
                    aoi,
                    self.parent.is_thermal,
                    self.parent.temperature_data,
                    self.parent.temperature_unit
                )
                aoi_gps['avg_info'] = avg_info

            return aoi_gps

        except Exception as e:
            self.logger.error(f"Error getting current AOI GPS: {e}")
            return None

    def calculate_gsd_for_image(self, image_path, custom_altitude_ft=None):
        """
        Calculate GSD for an image if not already available.

        Args:
            image_path: Path to the image file
            custom_altitude_ft: Optional custom altitude in feet

        Returns:
            GSD in cm/px or None if calculation fails
        """
        try:
            from core.services.ImageService import ImageService
            image_service = ImageService(image_path, '')

            # Use the existing ImageService method to get average GSD
            avg_gsd = image_service.get_average_gsd(custom_altitude_ft=custom_altitude_ft)
            return avg_gsd

        except Exception:
            return None

    def update_aoi_on_map(self):
        """Update the AOI display on the map if it's open."""
        if self.map_dialog and self.map_dialog.isVisible():
            aoi_gps = self.get_current_aoi_gps()

            # Get the identifier color from settings
            identifier_color = self.parent.settings.get('identifier_color', [255, 255, 0])

            self.map_dialog.update_aoi_marker(aoi_gps, identifier_color)
