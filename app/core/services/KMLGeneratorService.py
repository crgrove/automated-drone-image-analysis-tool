import simplekml
import colorsys
import numpy as np
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper
from core.services.ImageService import ImageService
from core.services.AOIService import AOIService

class KMLGeneratorService:
    """Service to generate a KML file with placemarks for flagged AOIs."""

    def __init__(self, custom_altitude_ft=None):
        """
        Initializes the KMLGeneratorService by creating a new KML document.

        Args:
            custom_altitude_ft: Optional custom altitude in feet to use for GSD calculations
        """
        self.kml = simplekml.Kml()
        self.custom_altitude_ft = custom_altitude_ft

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

                # Get GPS from EXIF data as a dict (not formatted string)
                image_gps = LocationInfo.get_gps(exif_data=image_service.exif_data)

                if not image_gps:
                    continue

                # Get image dimensions and metadata
                img_array = image_service.img_array
                height, width = img_array.shape[:2]

            except Exception as e:
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

                # Try to calculate precise AOI GPS using AOIService
                try:
                    aoi_service = AOIService(image)

                    # Use custom altitude if one was set during initialization
                    custom_alt_ft = self.custom_altitude_ft

                    # Calculate AOI GPS coordinates using the convenience method
                    result = aoi_service.calculate_gps_with_custom_altitude(image, aoi, custom_alt_ft)

                    if result:
                        aoi_lat, aoi_lon = result
                        gps_note = f"Precise AOI GPS (pinhole camera model)\n"
                    else:
                        gps_note = "Image GPS (calculation failed)\n"
                except Exception as e:
                    gps_note = f"Image GPS (calculation error: {type(e).__name__})\n"

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

    def generate_coverage_extent_kml(self, coverage_data: dict, output_path: str):
        """
        Generate KML file with polygons representing image coverage extents.

        Args:
            coverage_data (dict): Coverage data from CoverageExtentService with:
                - 'polygons': List of polygon dicts with 'coordinates' and 'area_sqm'
                - 'image_count': Number of images processed
                - 'total_area_sqm': Total coverage area
            output_path (str): The path to save the generated KML file.
        """
        polygons = coverage_data.get('polygons', [])
        image_count = coverage_data.get('image_count', 0)
        total_area_sqm = coverage_data.get('total_area_sqm', 0)

        if not polygons:
            return

        # Add document-level description with both metric and English units
        total_area_sqkm = total_area_sqm / 1_000_000
        total_area_acres = total_area_sqm / 4046.86  # 1 acre = 4046.86 m²

        self.kml.document.name = "Image Coverage Extent"
        self.kml.document.description = (
            f"Geographic coverage extent from {image_count} image(s)\n"
            f"Total coverage area: {total_area_sqkm:.3f} km² ({total_area_acres:.2f} acres)\n"
            f"Number of separate areas: {len(polygons)}"
        )

        # Create a polygon for each coverage area
        for idx, polygon_data in enumerate(polygons):
            coords = polygon_data['coordinates']
            area_sqm = polygon_data['area_sqm']
            area_sqkm = area_sqm / 1_000_000
            area_acres = area_sqm / 4046.86

            # Create polygon name
            if len(polygons) == 1:
                poly_name = "Coverage Extent"
            else:
                poly_name = f"Coverage Area {idx + 1}"

            # Convert coordinates to KML format (lon, lat)
            kml_coords = [(lon, lat) for lat, lon in coords]

            # Create polygon
            pol = self.kml.newpolygon(name=poly_name)
            pol.outerboundaryis = kml_coords

            # Set polygon description with both metric and English units
            pol.description = (
                f"Coverage area: {area_sqkm:.3f} km² ({area_acres:.2f} acres)\n"
                f"Area in square meters: {area_sqm:.0f} m²\n"
                f"Number of corners: {len(coords)}"
            )

            # Style the polygon
            pol.style.linestyle.color = simplekml.Color.rgb(0, 100, 200)  # Dark blue outline
            pol.style.linestyle.width = 2
            pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.rgb(0, 150, 255))  # Semi-transparent blue fill
            pol.style.polystyle.outline = 1

        self.save_kml(output_path)
