import math
import numpy as np
import colorsys
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from helpers.MetaDataHelper import MetaDataHelper
from helpers.LocationInfo import LocationInfo
from core.services.image.ImageService import ImageService
from core.services.LoggerService import LoggerService

# Lazy import terrain service to avoid circular imports
_terrain_service = None


def _get_terrain_service():
    """Lazy initialization of terrain service singleton."""
    global _terrain_service
    if _terrain_service is None:
        try:
            from core.services.terrain import TerrainService
            _terrain_service = TerrainService()
        except Exception as e:
            # Terrain service not available
            pass
    return _terrain_service


@dataclass
class AOIGPSResult:
    """Result of AOI GPS calculation with metadata."""
    latitude: float
    longitude: float
    elevation_source: str  # 'terrain', 'flat', or 'error'
    terrain_elevation_m: Optional[float] = None
    effective_agl_m: Optional[float] = None
    geoid_correction_m: Optional[float] = None
    terrain_resolution_m: Optional[float] = None

    def to_tuple(self) -> Tuple[float, float]:
        """Return as simple (lat, lon) tuple for backward compatibility."""
        return (self.latitude, self.longitude)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'elevation_source': self.elevation_source,
            'terrain_elevation_m': self.terrain_elevation_m,
            'effective_agl_m': self.effective_agl_m,
            'geoid_correction_m': self.geoid_correction_m,
            'terrain_resolution_m': self.terrain_resolution_m
        }


class AOIService:
    """Provides geospatial utilities for Areas of Interest (AOIs) in drone imagery."""

    # Maximum iterations for terrain-corrected position convergence
    MAX_TERRAIN_ITERATIONS = 3
    # Convergence threshold in meters
    CONVERGENCE_THRESHOLD_M = 1.0

    def __init__(self, image, img_array=None):
        """
        Args:
            image (dict): Image metadata dict (must include 'path', optionally 'mask_path', etc.)
            img_array (np.ndarray, optional): Pre-loaded image array (RGB format).
                                              If provided, avoids reloading from disk.
        """
        self.logger = LoggerService()
        self.image_service = ImageService(
            image['path'],
            image.get('mask_path', ''),
            img_array=img_array
        )

    def estimate_aoi_gps(self, image, aoi, agl_override_m=None, use_terrain=True):
        """
        Estimates the GPS coordinates of an AOI.

        Uses terrain elevation data when available for more accurate positioning,
        with fallback to flat ground plane assumption.

        Args:
            image (dict): Image metadata dict
            aoi (dict): AOI with 'center' as (x, y) pixel coordinates.
            agl_override_m (float, optional): Manual AGL altitude (meters).
            use_terrain (bool): Whether to use terrain elevation data if available.

        Returns:
            AOIGPSResult or None: Result with coordinates and metadata, or None if not calculable.
        """
        try:
            # --- Step 1: Load EXIF and orientation ---
            exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)
            if not gps_coords:
                if self.logger:
                    self.logger.warning(f"AOIService: Cannot estimate GPS - No GPS coordinates in EXIF for {image['path']}")
                return None
            lat0, lon0 = gps_coords['latitude'], gps_coords['longitude']

            # Get camera orientation
            yaw = self.image_service.get_camera_yaw() or 0.0
            pitch = self.image_service.get_camera_pitch()
            if pitch is None:
                pitch = -90  # assume nadir

            # Get altitude - use override or get from ImageService
            if agl_override_m and agl_override_m > 0:
                reported_agl = agl_override_m
            else:
                # Use ImageService method to get relative altitude (AGL) in meters
                reported_agl = self.image_service.get_relative_altitude('m') or 0

            # Get absolute altitude (GPS altitude) for cases where RelativeAltitude is unreliable
            absolute_alt = self.image_service.get_asl_altitude('m')

            # --- Step 2: Camera intrinsics ---
            img_array = self.image_service.img_array
            img_height, img_width = img_array.shape[:2]

            intrinsics = self.image_service.get_camera_intrinsics()
            if intrinsics is None:
                if self.logger:
                    self.logger.warning(f"AOIService: Cannot estimate GPS - Camera intrinsics (sensor/focal) not found for {image['path']}")
                return None

            focal_mm = intrinsics['focal_length_mm']
            sensor_w_mm = intrinsics['sensor_width_mm']
            sensor_h_mm = intrinsics['sensor_height_mm']

            cx, cy = img_width / 2.0, img_height / 2.0

            # --- Step 3: Get AOI position ---
            u, v = aoi['center']

            # --- Step 4: Determine altitude to use ---
            # Check if we should use terrain-based altitude calculation
            terrain_service = _get_terrain_service() if use_terrain else None
            use_terrain_agl = False
            geoid_undulation = None

            # If RelativeAltitude is very low (< 10m) but we have AbsoluteAltitude and terrain,
            # calculate AGL from terrain data instead
            if (reported_agl < 10 and absolute_alt and absolute_alt > 50 and
                    terrain_service and terrain_service.enabled):

                # Get geoid undulation to convert ellipsoidal to orthometric height
                geoid_undulation = terrain_service.get_geoid_undulation(lat0, lon0)

                # Convert GPS altitude (ellipsoidal) to orthometric
                if geoid_undulation is not None:
                    drone_orthometric = absolute_alt - geoid_undulation
                else:
                    drone_orthometric = absolute_alt

                # Get terrain elevation at drone position
                drone_terrain = terrain_service.get_elevation(lat0, lon0)

                if drone_terrain.source == 'terrain' and drone_terrain.elevation_m is not None:
                    # Calculate AGL from terrain
                    terrain_based_agl = drone_orthometric - drone_terrain.elevation_m

                    # Use terrain-based AGL if it's reasonable
                    if terrain_based_agl > 5:
                        reported_agl = terrain_based_agl
                        use_terrain_agl = True
                        if self.logger:
                            self.logger.info(
                                f"AOIService: Using terrain-based AGL ({terrain_based_agl:.1f}m) "
                                f"instead of low RelativeAltitude"
                            )

            if reported_agl <= 0:
                if self.logger:
                    self.logger.warning(f"AOIService: Cannot estimate GPS - Invalid AGL altitude ({reported_agl}m) for {image['path']}")
                return None

            # --- Step 5: Initial calculation with determined AGL ---
            initial_result = self._calculate_ground_position(
                lat0, lon0, u, v, cx, cy, img_width, img_height,
                focal_mm, sensor_w_mm, sensor_h_mm,
                reported_agl, pitch, yaw
            )

            if initial_result is None:
                if self.logger:
                    self.logger.warning(f"AOIService: Cannot estimate GPS - Ray casting failed to intersect ground for {image['path']}. Check camera pitch.")
                return None

            initial_lat, initial_lon = initial_result

            # --- Step 6: Terrain-corrected calculation (if enabled and not already using terrain AGL) ---
            if terrain_service and terrain_service.enabled:
                return self._calculate_with_terrain(
                    image, aoi, lat0, lon0,
                    initial_lat, initial_lon,
                    u, v, cx, cy, img_width, img_height,
                    focal_mm, sensor_w_mm, sensor_h_mm,
                    reported_agl, pitch, yaw,
                    terrain_service,
                    absolute_alt,
                    geoid_undulation
                )

            # No terrain data - return flat terrain result
            return AOIGPSResult(
                latitude=initial_lat,
                longitude=initial_lon,
                elevation_source='flat',
                effective_agl_m=reported_agl
            )

        except Exception as e:
            if self.logger:
                self.logger.error(f"AOIService: Failed to calculate AOI GPS - {e}")
            return None

    def _calculate_ground_position(
        self,
        drone_lat: float, drone_lon: float,
        u: float, v: float,
        cx: float, cy: float,
        img_width: int, img_height: int,
        focal_mm: float, sensor_w_mm: float, sensor_h_mm: float,
        altitude_m: float, pitch_deg: float, yaw_deg: float
    ) -> Optional[Tuple[float, float]]:
        """
        Calculate ground position using 3D ray-casting projection.

        This method properly handles oblique imagery by casting a ray from the
        camera through the image pixel and finding its intersection with the
        ground plane.

        Args:
            drone_lat, drone_lon: Drone GPS position
            u, v: Pixel coordinates of AOI center
            cx, cy: Image center coordinates
            img_width, img_height: Image dimensions
            focal_mm, sensor_w_mm, sensor_h_mm: Camera intrinsics
            altitude_m: Altitude above ground in meters
            pitch_deg: Camera pitch in degrees (-90=nadir, 0=horizontal)
            yaw_deg: Camera yaw in degrees (0=North, 90=East)

        Returns:
            (lat, lon) or None
        """
        if altitude_m <= 0:
            return None

        # Step 1: Convert pixel to normalized camera coordinates
        # Focal length in pixels
        fx = focal_mm / (sensor_w_mm / img_width)
        fy = focal_mm / (sensor_h_mm / img_height)

        # Ray direction in camera frame (X=right, Y=down, Z=forward)
        x_cam = (u - cx) / fx
        y_cam = (v - cy) / fy
        z_cam = 1.0

        ray_cam = np.array([x_cam, y_cam, z_cam])
        ray_cam = ray_cam / np.linalg.norm(ray_cam)

        # Step 2: Build rotation matrix from camera frame to NED frame
        # Camera pitch: angle from horizontal (-90° = nadir, 0° = horizontal)
        # For the optical axis direction in NED:
        #   elevation angle = pitch (negative means below horizontal)
        #   azimuth = yaw (0° = North, 90° = East)

        opt_elevation = math.radians(pitch_deg)
        opt_azimuth = math.radians(yaw_deg)

        # Optical axis (camera Z) direction in NED
        opt_axis_ned = np.array([
            math.cos(opt_elevation) * math.cos(opt_azimuth),  # North
            math.cos(opt_elevation) * math.sin(opt_azimuth),  # East
            -math.sin(opt_elevation)                           # Down
        ])

        # Camera Y direction (down in image) in NED
        # This lies in the vertical plane containing the optical axis
        # "Up" in camera frame points toward the horizon (opposite of gravity component)
        up_ned = np.array([
            -math.sin(opt_elevation) * math.cos(opt_azimuth),
            -math.sin(opt_elevation) * math.sin(opt_azimuth),
            -math.cos(opt_elevation)
        ])
        cam_y_ned = -up_ned  # Camera Y = down = negative up

        # Camera X direction (right in image) in NED
        # Perpendicular to both optical axis and up direction
        cam_x_ned = np.cross(opt_axis_ned, up_ned)
        cam_x_ned = cam_x_ned / np.linalg.norm(cam_x_ned)

        # Rotation matrix: columns are camera axes expressed in NED
        R_cam_to_ned = np.column_stack([cam_x_ned, cam_y_ned, opt_axis_ned])

        # Step 3: Transform ray from camera to NED frame
        ray_ned = R_cam_to_ned @ ray_cam
        ray_ned = ray_ned / np.linalg.norm(ray_ned)

        # Step 4: Ray-plane intersection
        # Drone is at altitude above ground, ground is at z=0 in local NED
        # Ray: P(t) = origin + t * direction
        # Ground plane: z = 0
        # We need ray to point downward (positive Down component)

        if ray_ned[2] <= 0:
            # Ray points upward or horizontal - no ground intersection
            return None

        # t = altitude / ray_down (ray goes from -altitude to 0)
        t = altitude_m / ray_ned[2]

        # Ground intersection in local NED (relative to drone position)
        ground_north = ray_ned[0] * t
        ground_east = ray_ned[1] * t

        # Step 5: Convert NED offset to GPS coordinates
        R_earth = 6378137.0
        dlat = ground_north / R_earth
        dlon = ground_east / (R_earth * math.cos(math.radians(drone_lat)))

        lat = drone_lat + math.degrees(dlat)
        lon = drone_lon + math.degrees(dlon)

        return (lat, lon)

    def _calculate_with_terrain(
        self,
        image: dict, aoi: dict,
        drone_lat: float, drone_lon: float,
        initial_lat: float, initial_lon: float,
        u: float, v: float,
        cx: float, cy: float,
        img_width: int, img_height: int,
        focal_mm: float, sensor_w_mm: float, sensor_h_mm: float,
        reported_agl: float, pitch: float, yaw: float,
        terrain_service,
        absolute_alt: Optional[float] = None,
        precomputed_geoid: Optional[float] = None
    ) -> AOIGPSResult:
        """
        Calculate AOI position using terrain elevation data with iterative refinement.

        The algorithm:
        1. Start with initial flat-terrain estimate
        2. Query terrain elevation at estimated position
        3. Calculate effective AGL considering terrain
        4. Recalculate position with corrected AGL
        5. Iterate until convergence

        Args:
            pitch: Camera pitch in degrees (-90=nadir, 0=horizontal)
            absolute_alt: GPS altitude (ellipsoidal) if available
            precomputed_geoid: Pre-computed geoid undulation if available
        """
        current_lat = initial_lat
        current_lon = initial_lon
        terrain_elevation = None
        effective_agl = reported_agl
        terrain_resolution = None

        # Get terrain elevation at drone position for reference
        drone_terrain = terrain_service.get_elevation(drone_lat, drone_lon)

        # Get geoid undulation at drone position (use precomputed if available)
        if precomputed_geoid is not None:
            geoid_undulation = precomputed_geoid
        else:
            geoid_undulation = terrain_service.get_geoid_undulation(drone_lat, drone_lon)

        # Calculate drone absolute elevation (orthometric)
        drone_absolute_elev = None
        if absolute_alt is not None and geoid_undulation is not None:
            # Convert GPS altitude (ellipsoidal) to orthometric
            drone_absolute_elev = absolute_alt - geoid_undulation
        elif drone_terrain.source == 'terrain' and drone_terrain.elevation_m is not None:
            # Estimate from terrain + reported AGL
            drone_absolute_elev = drone_terrain.elevation_m + reported_agl

        # Iterative refinement
        for iteration in range(self.MAX_TERRAIN_ITERATIONS):
            # Query terrain at current estimated position
            terrain_result = terrain_service.get_elevation(current_lat, current_lon)

            if terrain_result.source != 'terrain' or terrain_result.elevation_m is None:
                # No terrain data available - return flat result
                return AOIGPSResult(
                    latitude=initial_lat,
                    longitude=initial_lon,
                    elevation_source='flat',
                    effective_agl_m=reported_agl,
                    geoid_correction_m=geoid_undulation
                )

            terrain_elevation = terrain_result.elevation_m
            terrain_resolution = terrain_result.resolution_m

            # Calculate effective AGL
            if drone_absolute_elev is not None:
                # Best case: we have absolute elevation
                # Effective AGL at AOI = drone_absolute - aoi_terrain
                effective_agl = drone_absolute_elev - terrain_elevation

                # Clamp to minimum positive value
                effective_agl = max(1.0, effective_agl)
            else:
                # Fallback: use reported AGL adjusted for terrain difference
                if drone_terrain.source == 'terrain' and drone_terrain.elevation_m is not None:
                    terrain_diff = drone_terrain.elevation_m - terrain_elevation
                    effective_agl = reported_agl + terrain_diff
                    effective_agl = max(1.0, effective_agl)
                else:
                    effective_agl = reported_agl

            # Recalculate position with corrected AGL
            new_result = self._calculate_ground_position(
                drone_lat, drone_lon, u, v, cx, cy, img_width, img_height,
                focal_mm, sensor_w_mm, sensor_h_mm,
                effective_agl, pitch, yaw
            )

            if new_result is None:
                break

            new_lat, new_lon = new_result

            # Check for convergence
            dlat_m = (new_lat - current_lat) * 111320  # Approximate meters
            dlon_m = (new_lon - current_lon) * 111320 * math.cos(math.radians(current_lat))
            displacement = math.sqrt(dlat_m ** 2 + dlon_m ** 2)

            current_lat = new_lat
            current_lon = new_lon

            if displacement < self.CONVERGENCE_THRESHOLD_M:
                break

        return AOIGPSResult(
            latitude=current_lat,
            longitude=current_lon,
            elevation_source='terrain',
            terrain_elevation_m=terrain_elevation,
            effective_agl_m=effective_agl,
            geoid_correction_m=geoid_undulation,
            terrain_resolution_m=terrain_resolution
        )

    def estimate_aoi_gps_legacy(self, image, aoi, agl_override_m=None):
        """
        Legacy method for backward compatibility.

        Returns simple (lat, lon) tuple instead of AOIGPSResult.
        """
        result = self.estimate_aoi_gps(image, aoi, agl_override_m, use_terrain=False)
        if result:
            return result.to_tuple()
        return None

    def calculate_gps_with_custom_altitude(self, image, aoi, custom_altitude_ft=None, use_terrain=True):
        """
        Calculate AOI GPS with optional custom altitude in feet.

        Convenience method that handles altitude unit conversion from feet to meters.

        Args:
            image (dict): Image metadata dict
            aoi (dict): AOI with 'center' as (x, y) pixel coordinates
            custom_altitude_ft (float, optional): Custom altitude override in feet
            use_terrain (bool): Whether to use terrain elevation data

        Returns:
            (float, float) or None: (latitude, longitude) or None if not calculable
        """
        agl_override_m = None
        if custom_altitude_ft and custom_altitude_ft > 0:
            agl_override_m = custom_altitude_ft * 0.3048  # Convert feet to meters

        result = self.estimate_aoi_gps(image, aoi, agl_override_m, use_terrain)
        if result:
            return result.to_tuple()
        return None

    def calculate_gps_with_metadata(self, image, aoi, custom_altitude_ft=None, use_terrain=True):
        """
        Calculate AOI GPS and return full result with elevation metadata.

        Args:
            image (dict): Image metadata dict
            aoi (dict): AOI with 'center' as (x, y) pixel coordinates
            custom_altitude_ft (float, optional): Custom altitude override in feet
            use_terrain (bool): Whether to use terrain elevation data

        Returns:
            AOIGPSResult or None
        """
        agl_override_m = None
        if custom_altitude_ft and custom_altitude_ft > 0:
            agl_override_m = custom_altitude_ft * 0.3048

        return self.estimate_aoi_gps(image, aoi, agl_override_m, use_terrain)

    def get_aoi_gps_with_metadata(self, image, aoi, aoi_index, custom_altitude_ft=None, use_terrain=True):
        """
        Calculate AOI GPS and return with metadata.

        Args:
            image (dict): Image metadata dict
            aoi (dict): AOI dictionary
            aoi_index (int): Index of the AOI
            custom_altitude_ft (float, optional): Custom altitude override in feet
            use_terrain (bool): Whether to use terrain elevation data

        Returns:
            dict or None: Dict with coordinates and metadata, or None if calculation fails
        """
        result = self.calculate_gps_with_metadata(image, aoi, custom_altitude_ft, use_terrain)

        if not result:
            return None

        return {
            'latitude': result.latitude,
            'longitude': result.longitude,
            'aoi_index': aoi_index,
            'pixel_area': aoi.get('area', 0),
            'center_pixels': aoi['center'],
            'elevation_source': result.elevation_source,
            'terrain_elevation_m': result.terrain_elevation_m,
            'effective_agl_m': result.effective_agl_m,
            'geoid_correction_m': result.geoid_correction_m,
            'terrain_resolution_m': result.terrain_resolution_m
        }

    def get_aoi_representative_color(self, aoi):
        """
        Calculate a representative color for an AOI.

        Returns a vibrant marker color based on the average hue of pixels within the AOI,
        with full saturation and value for visibility on maps and exports.

        Args:
            aoi (dict): AOI with 'center', 'radius', and optionally 'detected_pixels'

        Returns:
            dict or None: {
                'rgb': (r, g, b),           # Vibrant marker color (0-255)
                'hex': '#rrggbb',           # Hex color string
                'hue_degrees': int,         # Hue in degrees (0-360)
                'avg_rgb': (r, g, b)        # Original average RGB
            } or None if calculation fails
        """
        try:
            img_array = self.image_service.img_array
            height, width = img_array.shape[:2]

            center = aoi.get('center', [0, 0])
            radius = aoi.get('radius', 0)
            cx, cy = center

            # Collect RGB values within the AOI
            colors = []

            # If we have detected pixels, use those
            if 'detected_pixels' in aoi and aoi['detected_pixels']:
                for pixel in aoi['detected_pixels']:
                    if isinstance(pixel, (list, tuple)) and len(pixel) >= 2:
                        px, py = int(pixel[0]), int(pixel[1])
                        if 0 <= py < height and 0 <= px < width:
                            colors.append(img_array[py, px])
            # Otherwise sample within the circle
            else:
                for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
                    for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
                        if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                            colors.append(img_array[y, x])

            if not colors:
                return None

            # Calculate average RGB
            avg_rgb = np.mean(colors, axis=0).astype(int)
            r, g, b = int(avg_rgb[0]), int(avg_rgb[1]), int(avg_rgb[2])

            # Convert to HSV
            h, _, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

            # Create full saturation and full value version for vibrant marker
            full_sat_rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            marker_rgb = tuple(int(c * 255) for c in full_sat_rgb)

            # Format color info
            hex_color = '#{:02x}{:02x}{:02x}'.format(*marker_rgb)
            hue_degrees = int(h * 360)

            return {
                'rgb': marker_rgb,
                'hex': hex_color,
                'hue_degrees': hue_degrees,
                'avg_rgb': (r, g, b)
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"AOIService: Failed to calculate AOI color - {e}")
            return None

    @staticmethod
    def is_terrain_available() -> bool:
        """Check if terrain service is available and enabled."""
        service = _get_terrain_service()
        return service is not None and service.enabled

    @staticmethod
    def get_terrain_service_info() -> Optional[Dict[str, Any]]:
        """Get information about the terrain service."""
        service = _get_terrain_service()
        if service:
            return service.get_service_info()
        return None
