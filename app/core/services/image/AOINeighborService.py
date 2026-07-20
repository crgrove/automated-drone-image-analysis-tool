"""
AOINeighborService - Service for tracking AOIs across neighboring images.

Provides methods to:
- Calculate if a GPS coordinate falls within an image's coverage
- Convert GPS coordinates back to pixel coordinates
- Extract thumbnails from images at specific GPS locations
"""

import math
import numpy as np
import cv2
from pathlib import Path
from helpers.MetaDataHelper import MetaDataHelper
from helpers.LocationInfo import LocationInfo
from helpers.GeodesicHelper import GeodesicHelper
from helpers.PhotogrammetryHelper import FovHomography, validate_alignment
from core.services.image.ImageService import ImageService
from core.services.GSDService import GSDService
from core.services.LoggerService import LoggerService


class AOINeighborService:
    """Service for tracking AOI GPS coordinates across neighboring images."""

    def __init__(self):
        """Initialize the AOINeighborService."""
        self.logger = LoggerService()

    def get_image_coverage_info(self, image, agl_override_m=None):
        """
        Get the coverage information for an image including its corner GPS coordinates.

        Args:
            image (dict): Image metadata dict with 'path' key
            agl_override_m (float, optional): Manual AGL altitude override in meters

        Returns:
            dict or None: Coverage info with center GPS, corners, dimensions, orientation
        """
        try:
            image_service = ImageService(
                image['path'],
                image.get('mask_path', ''),
                calculated_bearing=image.get('bearing')
            )

            # Get EXIF data and GPS
            exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)
            if not gps_coords:
                return None
            lat0, lon0 = gps_coords['latitude'], gps_coords['longitude']

            # Get camera orientation
            yaw = image_service.get_camera_yaw() or 0.0
            pitch = image_service.get_camera_pitch()
            if pitch is None:
                pitch = -90  # assume nadir

            # A manually aligned image can produce coverage info even when its
            # metadata (altitude, intrinsics) is missing or unreliable.
            refinement = image.get('fov_alignment')
            has_refinement = bool(
                refinement and refinement.get('corners')
                and validate_alignment(refinement['corners'])
            )

            # Get altitude
            if agl_override_m and agl_override_m > 0:
                altitude = agl_override_m
            else:
                altitude = image_service.get_relative_altitude('m') or 0

            if altitude <= 0 and not has_refinement:
                return None

            # Get image dimensions
            img_array = image_service.img_array
            height, width = img_array.shape[:2]

            # Get camera intrinsics
            intrinsics = image_service.get_camera_intrinsics()
            if intrinsics is None:
                if not has_refinement:
                    return None
                focal_mm = sensor_w_mm = sensor_h_mm = None
            else:
                focal_mm = intrinsics['focal_length_mm']
                sensor_w_mm = intrinsics['sensor_width_mm']
                sensor_h_mm = intrinsics['sensor_height_mm']

            # Convert pitch to tilt angle
            tilt_angle = 90 + pitch
            tilt_angle = max(0, min(90, tilt_angle))

            return {
                'center_lat': lat0,
                'center_lon': lon0,
                'yaw': yaw,
                'pitch': pitch,
                'tilt_angle': tilt_angle,
                'altitude': altitude,
                'width': width,
                'height': height,
                'focal_mm': focal_mm,
                'sensor_w_mm': sensor_w_mm,
                'sensor_h_mm': sensor_h_mm,
                'fov_alignment': refinement if has_refinement else None,
                'image_service': image_service
            }

        except Exception as e:
            self.logger.error(f"AOINeighborService: Failed to get image coverage info - {e}")
            return None

    def gps_to_pixel(self, target_lat, target_lon, coverage_info):
        """
        Convert GPS coordinates to pixel coordinates in an image.

        Uses the analytical inverse of the 3D ray-cast in
        AOIService._calculate_ground_position for accurate results with
        both nadir and oblique imagery.

        Args:
            target_lat (float): Target latitude
            target_lon (float): Target longitude
            coverage_info (dict): Coverage info from get_image_coverage_info

        Returns:
            tuple or None: (x, y) pixel coordinates or None if not in image
        """
        try:
            # Manually aligned image: invert the homography directly.
            refinement = coverage_info.get('fov_alignment')
            if refinement and refinement.get('corners'):
                homography = FovHomography(
                    refinement['corners'],
                    coverage_info['width'], coverage_info['height'],
                    refinement.get('tie_points')
                )
                return homography.gps_to_pixel(target_lat, target_lon)

            lat0 = coverage_info['center_lat']
            lon0 = coverage_info['center_lon']
            yaw = coverage_info['yaw']
            pitch = coverage_info.get('pitch', -90)
            altitude = coverage_info['altitude']
            width = coverage_info['width']
            height = coverage_info['height']
            focal_mm = coverage_info['focal_mm']
            sensor_w_mm = coverage_info['sensor_w_mm']
            sensor_h_mm = coverage_info['sensor_h_mm']

            # Convert GPS difference to NED offset in meters
            R_earth = 6378137.0
            dlat_rad = math.radians(target_lat - lat0)
            dlon_rad = math.radians(target_lon - lon0)
            north = dlat_rad * R_earth
            east = dlon_rad * R_earth * math.cos(math.radians(lat0))

            # Build the same camera-to-NED rotation matrix as
            # AOIService._calculate_ground_position
            opt_elevation = math.radians(pitch)
            opt_azimuth = math.radians(yaw)

            cos_elev = math.cos(opt_elevation)
            sin_elev = math.sin(opt_elevation)
            cos_az = math.cos(opt_azimuth)
            sin_az = math.sin(opt_azimuth)

            # Optical axis (camera Z) in NED
            r3 = [cos_elev * cos_az, cos_elev * sin_az, -sin_elev]

            # Up direction in NED (for constructing camera frame)
            up_ned = [-sin_elev * cos_az, -sin_elev * sin_az, -cos_elev]

            # Camera Y (down in image) = -up_ned
            r2 = [sin_elev * cos_az, sin_elev * sin_az, cos_elev]

            # Camera X (right in image) = cross(opt_axis, up_ned), normalized
            r1 = [
                r3[1] * up_ned[2] - r3[2] * up_ned[1],
                r3[2] * up_ned[0] - r3[0] * up_ned[2],
                r3[0] * up_ned[1] - r3[1] * up_ned[0]
            ]
            norm = math.sqrt(r1[0] ** 2 + r1[1] ** 2 + r1[2] ** 2)
            if norm < 1e-10:
                return None
            r1 = [c / norm for c in r1]

            # Solve the inverse of the forward projection analytically.
            # Forward: ground = H * (R @ [a, b, 1]) / (R @ [a, b, 1])_z
            #   where a = (u-cx)/fx, b = (v-cy)/fy
            # Rearranging into a 2x2 linear system:
            #   a*(N*r1z - H*r1x) + b*(N*r2z - H*r2x) = H*r3x - N*r3z
            #   a*(E*r1z - H*r1y) + b*(E*r2z - H*r2y) = H*r3y - E*r3z
            H = altitude
            N = north
            E = east

            A11 = N * r1[2] - H * r1[0]
            A12 = N * r2[2] - H * r2[0]
            A21 = E * r1[2] - H * r1[1]
            A22 = E * r2[2] - H * r2[1]
            c1 = H * r3[0] - N * r3[2]
            c2 = H * r3[1] - E * r3[2]

            det = A11 * A22 - A12 * A21
            if abs(det) < 1e-12:
                return None

            a = (c1 * A22 - c2 * A12) / det
            b = (A11 * c2 - A21 * c1) / det

            # Convert normalized camera coordinates back to pixels
            fx = focal_mm / (sensor_w_mm / width)
            fy = focal_mm / (sensor_h_mm / height)
            cx = width / 2.0
            cy = height / 2.0

            u = a * fx + cx
            v = b * fy + cy

            # Verify the ray points downward (valid ground intersection)
            ray_z = r1[2] * a + r2[2] * b + r3[2]
            if ray_z <= 0:
                return None

            return (u, v)

        except Exception as e:
            self.logger.error(f"AOINeighborService: Failed to convert GPS to pixel - {e}")
            return None

    def is_point_in_image(self, pixel_x, pixel_y, width, height, margin=0):
        """
        Check if pixel coordinates are within the image bounds.

        Args:
            pixel_x (float): X coordinate in pixels
            pixel_y (float): Y coordinate in pixels
            width (int): Image width
            height (int): Image height
            margin (int): Optional margin to consider point out of bounds

        Returns:
            bool: True if point is within image bounds
        """
        return (margin <= pixel_x < width - margin and
                margin <= pixel_y < height - margin)

    def _get_image_center_gps(self, image):
        """
        Get the center GPS coordinates for an image (lightweight, no full coverage calc).

        Args:
            image (dict): Image metadata dict with 'path' key

        Returns:
            tuple or None: (latitude, longitude) or None if not available
        """
        try:
            exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)
            if gps_coords:
                return (gps_coords['latitude'], gps_coords['longitude'])
        except Exception:
            pass
        return None

    def _estimate_max_coverage_radius(self, images, agl_override_m=None):
        """
        Estimate the maximum ground coverage radius for images in the dataset.

        Samples a few images to determine the maximum distance from image center
        to corner, which represents the maximum radius where an AOI could be visible.

        Args:
            images (list): List of all images
            agl_override_m (float, optional): Manual AGL altitude override

        Returns:
            float: Maximum coverage radius in meters (default 500m if estimation fails)
        """
        max_radius = 0
        sample_count = min(10, len(images))  # Sample first few images

        for i in range(sample_count):
            try:
                coverage_info = self.get_image_coverage_info(images[i], agl_override_m)
                if coverage_info:
                    # Calculate diagonal coverage distance using GSD
                    gsd_service = GSDService(
                        focal_length=coverage_info['focal_mm'],
                        image_size=(coverage_info['width'], coverage_info['height']),
                        altitude=coverage_info['altitude'],
                        tilt_angle=coverage_info['tilt_angle'],
                        sensor=(coverage_info['sensor_w_mm'], coverage_info['sensor_h_mm'])
                    )
                    avg_gsd_cm = gsd_service.compute_average_gsd()
                    if avg_gsd_cm is None:
                        continue
                    avg_gsd_m = avg_gsd_cm / 100.0

                    # Diagonal distance from center to corner
                    half_width = (coverage_info['width'] / 2) * avg_gsd_m
                    half_height = (coverage_info['height'] / 2) * avg_gsd_m
                    radius = math.sqrt(half_width**2 + half_height**2)
                    max_radius = max(max_radius, radius)
            except Exception:
                continue

        # Add 20% buffer for safety, default to 500m if estimation fails
        return max_radius * 1.2 if max_radius > 0 else 500

    def extract_thumbnail(self, image_service, pixel_x, pixel_y, radius=100):
        """
        Extract a thumbnail centered at the given pixel coordinates.

        Args:
            image_service (ImageService): Image service with loaded image
            pixel_x (float): X coordinate in pixels
            pixel_y (float): Y coordinate in pixels
            radius (int): Radius of the thumbnail in pixels

        Returns:
            np.ndarray or None: Thumbnail image array (RGB)
        """
        try:
            img_array = image_service.img_array
            height, width = img_array.shape[:2]

            # Calculate bounding box
            x1 = max(0, int(pixel_x - radius))
            y1 = max(0, int(pixel_y - radius))
            x2 = min(width, int(pixel_x + radius))
            y2 = min(height, int(pixel_y + radius))

            # Extract the region
            if x2 <= x1 or y2 <= y1:
                return None

            thumbnail = img_array[y1:y2, x1:x2].copy()

            # Draw a circle at the center to indicate the AOI location
            center_x = int(pixel_x - x1)
            center_y = int(pixel_y - y1)
            cv2.circle(thumbnail, (center_x, center_y), 10, (255, 0, 0), 2)

            return thumbnail

        except Exception as e:
            self.logger.error(f"AOINeighborService: Failed to extract thumbnail - {e}")
            return None

    def find_aoi_in_neighbors(self, images, current_image_idx, aoi_gps, agl_override_m=None,
                              thumbnail_radius=100, progress_callback=None, max_results=50):
        """
        Find all images that contain the AOI GPS coordinate.

        Uses GPS-based filtering to efficiently search all images, not just
        sequential neighbors. This handles drone lawn-mower flight patterns
        where parallel flight paths may also contain the AOI.

        Args:
            images (list): List of all images
            current_image_idx (int): Index of the current image
            aoi_gps (tuple): (latitude, longitude) of the AOI
            agl_override_m (float, optional): Manual AGL altitude override
            thumbnail_radius (int): Radius of thumbnails to extract
            progress_callback (callable, optional): Callback for progress updates
            max_results (int): Maximum number of results to return (default 50)

        Returns:
            list: List of dicts with thumbnail info, sorted by image index
        """
        results = []
        target_lat, target_lon = aoi_gps

        if progress_callback:
            progress_callback("Calculating search area...")

        # Estimate maximum coverage radius for GPS-based pre-filtering
        max_coverage_radius = self._estimate_max_coverage_radius(images, agl_override_m)

        # Build list of candidate images based on GPS proximity
        candidates = []
        for i, image in enumerate(images):
            center_gps = self._get_image_center_gps(image)
            if center_gps:
                center_lat, center_lon = center_gps
                distance = GeodesicHelper.haversine_distance(
                    target_lat, target_lon, center_lat, center_lon
                )
                # Only consider images within maximum coverage radius
                if distance <= max_coverage_radius:
                    candidates.append((i, distance))

        # Sort candidates by distance (closest first for better UX)
        candidates.sort(key=lambda x: x[1])

        if progress_callback:
            progress_callback(f"Checking {len(candidates)} candidate images...")

        # Check each candidate image
        for idx, (i, _) in enumerate(candidates):
            if progress_callback:
                progress_callback(f"Checking image {idx + 1} of {len(candidates)}...")

            result = self._check_image_for_aoi(
                images[i], i, target_lat, target_lon, agl_override_m, thumbnail_radius
            )
            if result:
                # Mark if this is the current/originating image
                if i == current_image_idx:
                    result['is_current'] = True
                results.append(result)

                # Stop if we've hit the maximum
                if len(results) >= max_results:
                    break

        # Sort results by image index for consistent display order
        results.sort(key=lambda r: r['image_idx'])

        return results

    def _check_image_for_aoi(self, image, image_idx, target_lat, target_lon,
                             agl_override_m=None, thumbnail_radius=100):
        """
        Check if an AOI GPS coordinate is visible in an image and extract thumbnail.

        Args:
            image (dict): Image metadata dict
            image_idx (int): Image index
            target_lat (float): Target latitude
            target_lon (float): Target longitude
            agl_override_m (float, optional): Manual AGL altitude override
            thumbnail_radius (int): Radius of thumbnail to extract

        Returns:
            dict or None: Thumbnail info if AOI is visible, None otherwise
        """
        try:
            # Get coverage info for this image
            coverage_info = self.get_image_coverage_info(image, agl_override_m)
            if not coverage_info:
                return None

            # Convert GPS to pixel coordinates
            pixel_coords = self.gps_to_pixel(target_lat, target_lon, coverage_info)
            if not pixel_coords:
                return None

            pixel_x, pixel_y = pixel_coords

            # Check if point is within image bounds (with some margin)
            margin = thumbnail_radius // 2  # Use smaller margin for edge detection
            if not self.is_point_in_image(
                pixel_x, pixel_y,
                coverage_info['width'], coverage_info['height'],
                margin
            ):
                return None

            # Extract thumbnail
            image_service = coverage_info['image_service']
            thumbnail = self.extract_thumbnail(
                image_service, pixel_x, pixel_y, thumbnail_radius
            )
            if thumbnail is None:
                return None

            # Get image name
            image_name = Path(image['path']).name

            return {
                'image_idx': image_idx,
                'image_name': image_name,
                'image_path': image['path'],
                'pixel_x': pixel_x,
                'pixel_y': pixel_y,
                'thumbnail': thumbnail,
                'is_current': False
            }

        except Exception as e:
            self.logger.error(f"AOINeighborService: Error checking image {image_idx} - {e}")
            return None
