import math
import numpy as np
import colorsys
from pathlib import Path
from helpers.MetaDataHelper import MetaDataHelper
from helpers.LocationInfo import LocationInfo
from core.services.ImageService import ImageService
from core.services.LoggerService import LoggerService


class AOIService:
    """Provides geospatial utilities for Areas of Interest (AOIs) in drone imagery."""

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

    def estimate_aoi_gps(self, image, aoi, agl_override_m=None):
        """
        Estimates the GPS coordinates of an AOI using a pinhole projection on a flat ground plane.

        Args:
            image (dict): Image metadata dict
            aoi (dict): AOI with 'center' as (x, y) pixel coordinates.
            agl_override_m (float, optional): Manual AGL altitude (meters).

        Returns:
            (float, float) or None: (latitude, longitude) or None if not calculable.
        """
        try:
            # --- Step 1: Load EXIF and orientation ---
            exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)
            if not gps_coords:
                return None
            lat0, lon0 = gps_coords['latitude'], gps_coords['longitude']

            # Get camera orientation
            yaw = self.image_service.get_camera_yaw() or 0.0
            pitch = self.image_service.get_camera_pitch()
            if pitch is None:
                pitch = -90  # assume nadir
            roll = self.image_service.get_gimbal_roll() or 0.0

            # Get altitude - use override or get from ImageService
            if agl_override_m and agl_override_m > 0:
                altitude = agl_override_m
            else:
                # Use ImageService method to get relative altitude (AGL) in meters
                altitude = self.image_service.get_relative_altitude('m') or 0
            
            if altitude <= 0:
                return None

            # --- Step 2: Camera intrinsics ---
            img_array = self.image_service.img_array
            height, width = img_array.shape[:2]
            
            # Get camera intrinsics (focal length and sensor size)
            intrinsics = self.image_service.get_camera_intrinsics()
            if intrinsics is None:
                return None
            
            focal_mm = intrinsics['focal_length_mm']
            sensor_w_mm = intrinsics['sensor_width_mm']
            sensor_h_mm = intrinsics['sensor_height_mm']
            
            fx = width * (focal_mm / sensor_w_mm)
            fy = height * (focal_mm / sensor_h_mm)
            cx, cy = width / 2.0, height / 2.0

            # --- Step 3: Get AOI position and calculate offsets ---
            u, v = aoi['center']
            pixel_offset_x = u - cx
            pixel_offset_y = v - cy
            
            # Convert pitch to tilt angle for GSD calculation
            # Pitch: -90° = nadir → Tilt: 0° = nadir
            # Pitch: 0° = horizontal → Tilt: 90° = horizontal
            tilt_angle = 90 + pitch
            tilt_angle = max(0, min(90, tilt_angle))  # Clamp to [0, 90]
            
            # --- Step 4: Convert pixel offset to ground distance ---
            # Initialize GSDService with camera parameters
            from core.services.GSDService import GSDService
            gsd_service = GSDService(
                focal_length=focal_mm,
                image_size=(width, height),
                altitude=altitude,
                tilt_angle=tilt_angle,
                sensor=(sensor_w_mm, sensor_h_mm)
            )
            
            # Use GSDService to compute ground distance with variable GSD accounting
            # Note: GSDService uses (row, col) convention
            ground_offset_x, ground_offset_y = gsd_service.compute_ground_distance(cy, cx, v, u)
            
            # --- Step 5: Rotate to NED coordinates by bearing ---
            # For a camera at bearing θ (measured clockwise from North):
            # - Image top points at bearing θ
            # - Image right points at bearing θ + 90°
            # - Pixel offset X (right) is along θ + 90°
            # - Pixel offset Y (down) is along θ + 180° (opposite of top)
            
            yaw_rad = math.radians(yaw)
            cos_yaw = math.cos(yaw_rad)
            sin_yaw = math.sin(yaw_rad)
            
            # Transform to NED:
            # North = -X * sin(bearing) - Y * cos(bearing)
            # East  = X * cos(bearing) - Y * sin(bearing)
            north = -ground_offset_x * sin_yaw - ground_offset_y * cos_yaw
            east = ground_offset_x * cos_yaw - ground_offset_y * sin_yaw

            # --- Step 6: Convert to GPS ---
            # Coordinate system: X=East, Y=North in local tangent plane
            # North offset increases latitude, East offset increases longitude (in western hemisphere, longitude is negative, so east is less negative)
            R_earth = 6378137.0
            dlat = north / R_earth  # North offset -> latitude change
            dlon = east / (R_earth * math.cos(math.radians(lat0)))  # East offset -> longitude change
            lat = lat0 + math.degrees(dlat)
            lon = lon0 + math.degrees(dlon)

            return (lat, lon)

        except Exception as e:
            if self.logger:
                self.logger.error(f"AOIService: Failed to calculate AOI GPS - {e}")
            return None

    def calculate_gps_with_custom_altitude(self, image, aoi, custom_altitude_ft=None):
        """
        Calculate AOI GPS with optional custom altitude in feet.
        
        Convenience method that handles altitude unit conversion from feet to meters.

        Args:
            image (dict): Image metadata dict
            aoi (dict): AOI with 'center' as (x, y) pixel coordinates
            custom_altitude_ft (float, optional): Custom altitude override in feet

        Returns:
            (float, float) or None: (latitude, longitude) or None if not calculable
        """
        agl_override_m = None
        if custom_altitude_ft and custom_altitude_ft > 0:
            agl_override_m = custom_altitude_ft * 0.3048  # Convert feet to meters

        return self.estimate_aoi_gps(image, aoi, agl_override_m)

    def get_aoi_gps_with_metadata(self, image, aoi, aoi_index, custom_altitude_ft=None):
        """
        Calculate AOI GPS and return with metadata.

        Args:
            image (dict): Image metadata dict
            aoi (dict): AOI dictionary
            aoi_index (int): Index of the AOI
            custom_altitude_ft (float, optional): Custom altitude override in feet

        Returns:
            dict or None: Dict with 'latitude', 'longitude', 'aoi_index', 'pixel_area', 
                         'center_pixels' or None if calculation fails
        """
        result = self.calculate_gps_with_custom_altitude(image, aoi, custom_altitude_ft)

        if not result:
            return None

        lat, lon = result

        return {
            'latitude': lat,
            'longitude': lon,
            'aoi_index': aoi_index,
            'pixel_area': aoi.get('area', 0),
            'center_pixels': aoi['center']
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