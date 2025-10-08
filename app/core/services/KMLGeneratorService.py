import simplekml
import colorsys
import numpy as np
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper
from core.services.ImageService import ImageService


class KMLGeneratorService:
    """Service to generate a KML file with placemarks for flagged AOIs."""

    def __init__(self):
        """
        Initializes the KMLGeneratorService by creating a new KML document.
        """
        self.kml = simplekml.Kml()

    def add_aoi_placemark(self, name, lat, lon, description, color_rgb=None):
        """
        Adds an AOI placemark to the KML document with optional color.

        Args:
            name (str): The name/label for the placemark.
            lat (float): Latitude of the point.
            lon (float): Longitude of the point.
            description (str): Description text for the placemark.
            color_rgb (tuple): Optional RGB color tuple (R, G, B) for the icon.
        """
        pnt = self.kml.newpoint(name=name, coords=[(lon, lat)])
        pnt.description = description

        # Set icon color if provided
        if color_rgb:
            # KML uses ABGR format (Alpha, Blue, Green, Red) in hex
            r, g, b = color_rgb
            # Full opacity (FF) + BGR
            kml_color = f'ff{b:02x}{g:02x}{r:02x}'
            pnt.style.iconstyle.color = kml_color
            pnt.style.iconstyle.scale = 1.2

    def save_kml(self, path):
        """
        Saves the KML document to a file.

        Args:
            path (str): The file path where the KML document will be stored.
        """
        self.kml.save(path)

    def generate_kml_export(self, images, output_path):
        """
        Generates KML file with placemarks for each flagged AOI.

        Args:
            images (list of dict): List of image metadata dictionaries with flagged AOIs.
            output_path (str): The path to save the generated KML file.
        """
        for img_idx, image in enumerate(images):
            # Skip hidden images
            if image.get('hidden', False):
                continue

            image_name = image.get('name', f'Image {img_idx + 1}')
            image_path = image.get('path', '')

            # Get image GPS coordinates and metadata
            try:
                # Create ImageService to extract EXIF data
                image_service = ImageService(image_path, image.get('mask_path', ''))

                # Get GPS from EXIF data
                exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
                image_gps = LocationInfo.get_gps(exif_data=exif_data)

                if not image_gps:
                    continue

                # Get image dimensions and metadata
                img_array = image_service.img_array
                height, width = img_array.shape[:2]
                image_center = (width/2, height/2)
                # Use get_image_bearing() which accounts for both Flight Yaw and Gimbal Yaw
                bearing = image_service.get_image_bearing() or 0
                gsd_cm = image_service.get_average_gsd()

                # Check gimbal angle
                _, gimbal_pitch = image_service.get_gimbal_orientation()
                is_nadir = True
                if gimbal_pitch is not None:
                    is_nadir = (-95 <= gimbal_pitch <= -85)

            except Exception:
                continue

            # Process each flagged AOI
            aois = image.get('areas_of_interest', [])
            for aoi_idx, aoi in enumerate(aois):
                # Only export flagged AOIs
                if not aoi.get('flagged', False):
                    continue

                center = aoi.get('center', [0, 0])
                area = aoi.get('area', 0)
                radius = aoi.get('radius', 0)

                # Calculate AOI-specific GPS coordinates with fallback
                aoi_lat = image_gps['latitude']
                aoi_lon = image_gps['longitude']
                gps_note = ""

                # Try to calculate precise AOI GPS if conditions are met
                if gsd_cm and is_nadir:
                    try:
                        from core.controllers.viewer.gps.GPSMapController import GPSMapController
                        gps_controller = GPSMapController(None)

                        aoi_gps = gps_controller.calculate_aoi_gps_coordinates(
                            image_gps,
                            center,
                            image_center,
                            gsd_cm,
                            bearing
                        )

                        if aoi_gps:
                            aoi_lat = aoi_gps['latitude']
                            aoi_lon = aoi_gps['longitude']
                            gps_note = f"Precise AOI GPS (GSD: {gsd_cm:.2f} cm/px, Bearing: {bearing:.1f}°)\n"
                        else:
                            gps_note = "Image GPS (calculation failed)\n"
                    except Exception:
                        gps_note = "Image GPS (calculation error)\n"
                else:
                    # Missing required data - use image GPS
                    reasons = []
                    if not gsd_cm:
                        reasons.append("no GSD")
                    if not is_nadir and gimbal_pitch is not None:
                        reasons.append(f"gimbal {gimbal_pitch:.1f}°")
                    elif gimbal_pitch is None:
                        reasons.append("no gimbal data")

                    gps_note = f"Image GPS ({', '.join(reasons) if reasons else 'missing data'})\n"

                # Calculate color information
                color_info = ""
                marker_rgb = None
                try:
                    # Collect RGB values within the AOI
                    colors = []
                    cx, cy = center

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

                    if colors:
                        # Calculate average RGB
                        avg_rgb = np.mean(colors, axis=0).astype(int)
                        r, g, b = int(avg_rgb[0]), int(avg_rgb[1]), int(avg_rgb[2])

                        # Convert to HSV
                        h, _, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

                        # Create full saturation and full value version
                        full_sat_rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
                        marker_rgb = tuple(int(c * 255) for c in full_sat_rgb)

                        # Format color info
                        hex_color = '#{:02x}{:02x}{:02x}'.format(*marker_rgb)
                        hue_degrees = int(h * 360)
                        color_info = f"Color: Hue: {hue_degrees}° {hex_color}\n"

                except Exception:
                    pass

                # Create placemark name
                placemark_name = f"{image_name} - AOI {aoi_idx + 1}"

                # Get user comment if available
                user_comment = aoi.get('user_comment', '')

                # Build description
                description = ""
                if user_comment:
                    description = f'"{user_comment}"\n\n'

                description += (
                    f"Flagged AOI from {image_name}\n"
                    f"{gps_note}"
                    f"AOI Index: {aoi_idx + 1}\n"
                    f"Center: ({center[0]}, {center[1]})\n"
                    f"Area: {area:.0f} pixels\n"
                    f"{color_info}"
                )

                # Add placemark to KML
                self.add_aoi_placemark(
                    placemark_name,
                    aoi_lat,
                    aoi_lon,
                    description,
                    marker_rgb
                )

        self.save_kml(output_path)
