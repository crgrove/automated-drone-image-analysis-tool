"""
CoverageExtentService - Calculates geographic coverage extent polygons for images.

This service computes the field of view (FOV) polygons for images and unions
overlapping polygons to create consolidated coverage areas.
"""

import math
from typing import List, Dict, Any, Optional
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

from core.services.image.ImageService import ImageService
from core.services.LoggerService import LoggerService
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper
from helpers.PhotogrammetryHelper import validate_alignment


class CoverageExtentService:
    """
    Service for calculating image coverage extent polygons.

    Computes FOV polygons for images based on GPS, GSD, bearing, and image dimensions,
    then unions overlapping polygons to create consolidated coverage areas.
    """

    def __init__(self, custom_altitude_ft: Optional[float] = None, logger: Optional[LoggerService] = None,
                 use_terrain: bool = True):
        """
        Initialize the coverage extent service.

        Args:
            custom_altitude_ft: Optional custom altitude in feet for GSD calculations
            logger: Optional logger instance for error reporting
            use_terrain: Whether to use terrain (DEM) elevation data when
                deriving each image's effective AGL/GSD, matching the
                terrain-corrected AOI/FOV pipeline
        """
        self.custom_altitude_ft = custom_altitude_ft
        self.logger = logger or LoggerService()
        self.use_terrain = use_terrain
        self.earth_radius = 6371000  # meters
        # Camera yaw (deg) used by the most recent FOV polygon calculation, or
        # None when unavailable. Lets callers (the Align Image dialog) orient the
        # drone photo to the same heading that seeded the footprint estimate,
        # without decoding the image a second time.
        self.last_camera_yaw: Optional[float] = None

    def calculate_coverage_extents(self, images: List[Dict[str, Any]], progress_callback=None, cancel_check=None) -> Dict[str, Any]:
        """
        Calculate coverage extent polygons for all valid images.

        Args:
            images: List of image data dictionaries
            progress_callback: Optional callback function(current, total, message) for progress updates
            cancel_check: Optional function that returns True if operation should be cancelled

        Returns:
            Dictionary containing:
                - 'polygons': List of final polygon coordinates (after union)
                - 'image_count': Number of images successfully processed
                - 'skipped_count': Number of images skipped
                - 'total_area_sqm': Total coverage area in square meters
                - 'cancelled': True if operation was cancelled
        """
        valid_polygons = []
        processed_count = 0
        skipped_count = 0
        total_images = len(images)

        for idx, image in enumerate(images):
            # Check for cancellation
            if cancel_check and cancel_check():
                # self.logger.info("Coverage extent calculation cancelled by user")
                return {
                    'polygons': [],
                    'image_count': processed_count,
                    'skipped_count': skipped_count,
                    'total_area_sqm': 0,
                    'cancelled': True
                }

            # Update progress
            if progress_callback:
                image_name = image.get('name', f'Image {idx + 1}')
                progress_callback(idx, total_images, f"Processing {image_name}...")

            try:
                # Calculate FOV polygon for this image
                polygon_coords = self._calculate_image_fov_polygon(image)

                if polygon_coords:
                    # Create shapely Polygon from coordinates (lat, lon pairs)
                    polygon = Polygon([(lon, lat) for lat, lon in polygon_coords])
                    valid_polygons.append(polygon)
                    processed_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                self.logger.error(f"Error calculating FOV for image {idx}: {str(e)}")
                skipped_count += 1

        if not valid_polygons:
            return {
                'polygons': [],
                'image_count': 0,
                'skipped_count': skipped_count,
                'total_area_sqm': 0,
                'cancelled': False
            }

        # Update progress - starting union operation
        if progress_callback:
            progress_callback(total_images, total_images, "Merging overlapping coverage areas...")

        # Check for cancellation before union
        if cancel_check and cancel_check():
            # self.logger.info("Coverage extent calculation cancelled before union")
            return {
                'polygons': [],
                'image_count': processed_count,
                'skipped_count': skipped_count,
                'total_area_sqm': 0,
                'cancelled': True
            }

        # Union all overlapping polygons
        unioned = unary_union(valid_polygons)

        # Extract final polygon coordinates
        final_polygons = []
        total_area_sqm = 0

        if isinstance(unioned, Polygon):
            # Single polygon result
            coords = list(unioned.exterior.coords)
            final_polygons.append({
                'coordinates': [(lat, lon) for lon, lat in coords],
                'area_sqm': self._calculate_polygon_area_on_sphere(coords)
            })
            total_area_sqm = final_polygons[0]['area_sqm']
        elif isinstance(unioned, MultiPolygon):
            # Multiple separate polygons
            for poly in unioned.geoms:
                coords = list(poly.exterior.coords)
                area = self._calculate_polygon_area_on_sphere(coords)
                final_polygons.append({
                    'coordinates': [(lat, lon) for lon, lat in coords],
                    'area_sqm': area
                })
                total_area_sqm += area

        return {
            'polygons': final_polygons,
            'image_count': processed_count,
            'skipped_count': skipped_count,
            'total_area_sqm': total_area_sqm,
            'cancelled': False
        }

    def get_image_fov_corners(self, image: Dict[str, Any]) -> Optional[List[tuple]]:
        """
        Compute the estimated FOV corner coordinates for a single image.

        Public wrapper around the FOV polygon calculation, used by the Align
        Image dialog to seed its starting overlay.

        Args:
            image: Image data dictionary.

        Returns:
            List of four (latitude, longitude) tuples (TL, TR, BR, BL), or None.
        """
        return self._calculate_image_fov_polygon(image)

    def _calculate_image_fov_polygon(self, image: Dict[str, Any]) -> Optional[List[tuple]]:
        """
        Calculate the FOV polygon for a single image.

        Args:
            image: Image data dictionary

        Returns:
            List of (latitude, longitude) tuples for polygon corners, or None if calculation fails
        """
        self.last_camera_yaw = None
        try:
            # A manually aligned image's user-placed corners are its FOV.
            refinement = image.get('fov_alignment')
            if refinement and refinement.get('corners'):
                corners = refinement['corners']
                if validate_alignment(corners):
                    return [tuple(corner) for corner in corners]

            image_path = image.get('path', '')
            if not image_path:
                return None

            # Get EXIF data and GPS coordinates
            exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)

            if not gps_coords:
                return None

            image_lat = gps_coords['latitude']
            image_lon = gps_coords['longitude']

            # Load image service
            image_service = ImageService(image_path, image.get('mask_path', ''), calculated_bearing=image.get('bearing'))

            # Check gimbal angle - must be nadir (allowing for outward roll on
            # fixed-wing rigs like WALDO, where pitch stays at -90 but roll is
            # applied about the heading axis to push the footprint sideways).
            gimbal_pitch = image_service.get_camera_pitch()
            if gimbal_pitch is not None:
                # Nadir is typically -90 degrees (camera pointing straight down)
                # Allow range from -85 to -95 degrees (5 degree tolerance)
                if not (-95 <= gimbal_pitch <= -85):
                    self.logger.warning(f"Image {image.get('name', 'unknown')} skipped: gimbal not nadir ({gimbal_pitch:.1f}°)")
                    return None

            # Outward gimbal roll (e.g. WALDO ±22.5°) shifts the ground footprint
            # cross-track by h*tan(roll). >90° rolls are the DJI "inverted gimbal"
            # pattern where get_camera_yaw already flips yaw 180°, so skip those.
            gimbal_roll = image_service.get_gimbal_roll() or 0.0
            if abs(gimbal_roll) > 90.0:
                gimbal_roll = 0.0

            # Get image dimensions (needed first: terrain GSD samples the center pixel)
            img_array = image_service.img_array
            if img_array is None:
                return None

            height, width = img_array.shape[:2]

            # Get GSD — terrain-corrected at the image center when enabled, so
            # the footprint size reflects DEM-derived effective AGL (matching
            # the AOI / GPS-map FOV pipeline) instead of the drone's reported
            # altitude. Falls back to the flat-ground average GSD.
            gsd_cm = None
            effective_agl_m = None
            if self.use_terrain:
                try:
                    gsd_cm = image_service.compute_gsd_at_pixel(
                        width / 2.0, height / 2.0,
                        use_terrain=True,
                        custom_altitude_ft=self.custom_altitude_ft,
                    )
                    effective_agl_m = image_service.get_effective_agl_at_pixel(
                        width / 2.0, height / 2.0,
                        custom_altitude_ft=self.custom_altitude_ft,
                    )
                except Exception:
                    gsd_cm = None
                    effective_agl_m = None
            if gsd_cm is None or gsd_cm <= 0:
                gsd_cm = image_service.get_average_gsd(custom_altitude_ft=self.custom_altitude_ft)
            if gsd_cm is None or gsd_cm <= 0:
                self.logger.warning(f"Image {image.get('name', 'unknown')} skipped: no valid GSD")
                return None

            # Calculate image dimensions in meters
            gsd_m = gsd_cm / 100.0
            width_m = width * gsd_m
            height_m = height * gsd_m

            # Get drone orientation (bearing)
            bearing = image_service.get_camera_yaw()
            self.last_camera_yaw = bearing
            if bearing is None:
                bearing = 0  # Default to north if bearing not available

            # Calculate the four corners of the image in GPS coordinates
            # Corners in image space (centered at the drone-nadir point on the
            # ground plane). Outward roll shifts that center cross-track by
            # h*tan(roll); positive roll points the optical axis to the LEFT
            # of heading (matches AOIService convention), so the centroid
            # offset along the camera-X (right) axis is -h*tan(roll).
            agl_m = effective_agl_m  # DEM-corrected AGL when terrain resolved
            if agl_m is None or agl_m <= 0:
                agl_m = image_service.get_relative_altitude('m')
            if agl_m is None or agl_m <= 0:
                # Custom altitude already factored into GSD; back-derive in m.
                if self.custom_altitude_ft and self.custom_altitude_ft > 0:
                    agl_m = self.custom_altitude_ft / 3.28084
                else:
                    agl_m = 0.0
            roll_offset_x = -agl_m * math.tan(math.radians(gimbal_roll))

            corners_image = [
                (roll_offset_x - width_m / 2, -height_m / 2),  # Top-left
                (roll_offset_x + width_m / 2, -height_m / 2),  # Top-right
                (roll_offset_x + width_m / 2, height_m / 2),   # Bottom-right
                (roll_offset_x - width_m / 2, height_m / 2)    # Bottom-left
            ]

            # Rotate corners by bearing and convert to GPS
            bearing_rad = math.radians(-bearing)  # Negative for same rotation as map
            cos_b = math.cos(bearing_rad)
            sin_b = math.sin(bearing_rad)

            corners_gps = []

            for x, y in corners_image:
                # Rotate
                x_rot = x * cos_b - y * sin_b
                y_rot = x * sin_b + y * cos_b

                # Convert to lat/lon offset
                delta_lat = y_rot / self.earth_radius * (180 / math.pi)
                delta_lon = x_rot / (self.earth_radius * math.cos(math.radians(image_lat))) * (180 / math.pi)

                # Calculate corner GPS
                corner_lat = image_lat + delta_lat
                corner_lon = image_lon + delta_lon

                corners_gps.append((corner_lat, corner_lon))

            return corners_gps

        except Exception as e:
            self.logger.error(f"Error calculating FOV polygon: {str(e)}")
            return None

    def _calculate_polygon_area_on_sphere(self, coords: List[tuple]) -> float:
        """
        Calculate the area of a polygon on Earth's surface using spherical geometry.

        Args:
            coords: List of (lon, lat) tuples in degrees

        Returns:
            Area in square meters
        """
        try:
            # Use the spherical excess method for accurate area calculation
            # This is more accurate than planar calculations for larger areas

            if len(coords) < 3:
                return 0

            # Convert to radians and calculate area
            area = 0
            for i in range(len(coords) - 1):
                lon1, lat1 = math.radians(coords[i][0]), math.radians(coords[i][1])
                lon2, lat2 = math.radians(coords[i + 1][0]), math.radians(coords[i + 1][1])

                # Spherical excess contribution
                area += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))

            # Complete the calculation
            area = abs(area * self.earth_radius * self.earth_radius / 2)

            return area

        except Exception as e:
            self.logger.error(f"Error calculating polygon area: {str(e)}")
            return 0
