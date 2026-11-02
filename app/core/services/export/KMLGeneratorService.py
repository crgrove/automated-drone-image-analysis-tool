import simplekml
from helpers.FormatHelper import FormatHelper
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper
from core.services.image.ImageService import ImageService
from core.services.image.AOIService import AOIService
from core.services.image.WingtraDataService import resolve_altitude_ft, wingtra_agl_ft


class KMLGeneratorService:
    """Service to generate a KML file with placemarks for flagged AOIs."""

    def __init__(self, custom_altitude_ft=None, use_terrain=True):
        """
        Initializes the KMLGeneratorService by creating a new KML document.

        Args:
            custom_altitude_ft: Optional custom altitude in feet to use for GSD calculations
            use_terrain: Whether to use terrain elevation data for AOI positioning
        """
        self.kml = simplekml.Kml()
        self.custom_altitude_ft = custom_altitude_ft
        self.use_terrain = use_terrain

    def add_aoi_placemark(self, name, lat, lon, description, color_rgb=None, folder=None):
        """
        Adds an AOI placemark to the KML document with optional color.

        Args:
            name (str): The name/label for the placemark.
            lat (float): Latitude of the point.
            lon (float): Longitude of the point.
            description (str): Description text for the placemark.
            color_rgb (tuple): Optional RGB color tuple (R, G, B) for the icon.
            folder: Optional simplekml Folder (from ``self.kml.newfolder``) to
                place the point in; the document root when None.
        """
        container = folder if folder is not None else self.kml
        pnt = container.newpoint(name=name, coords=[(lon, lat)])
        pnt.description = description

        # Set icon color if provided using StyleMap for proper normal/highlight states
        if color_rgb:
            # KML uses ABGR format (Alpha, Blue, Green, Red) in hex
            r, g, b = color_rgb
            # Full opacity (FF) + BGR
            kml_color = f'ff{b:02x}{g:02x}{r:02x}'

            # Create normal style
            normal_style = simplekml.Style()
            normal_style.iconstyle.color = kml_color
            normal_style.iconstyle.scale = 1.2
            normal_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'
            # Create highlight style (slightly larger and brighter)
            highlight_style = simplekml.Style()
            highlight_style.iconstyle.color = kml_color
            highlight_style.iconstyle.scale = 1.5
            highlight_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'

            # Create StyleMap
            style_map = simplekml.StyleMap()
            style_map.normalstyle = normal_style
            style_map.highlightstyle = highlight_style

            # Assign StyleMap to placemark
            pnt.stylemap = style_map

    def add_image_location_placemark(self, name, lat, lon, description):
        """
        Adds an image/drone location placemark to the KML document.

        Args:
            name (str): The name/label for the placemark (typically image name).
            lat (float): Latitude of the point.
            lon (float): Longitude of the point.
            description (str): Description text for the placemark.
        """
        pnt = self.kml.newpoint(name=name, coords=[(lon, lat)])
        pnt.description = description

        # Use a camera/drone icon style
        normal_style = simplekml.Style()
        normal_style.iconstyle.color = simplekml.Color.yellow
        normal_style.iconstyle.scale = 1.0
        normal_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/camera.png'

        highlight_style = simplekml.Style()
        highlight_style.iconstyle.color = simplekml.Color.yellow
        highlight_style.iconstyle.scale = 1.3
        highlight_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/camera.png'

        # Create StyleMap
        style_map = simplekml.StyleMap()
        style_map.normalstyle = normal_style
        style_map.highlightstyle = highlight_style

        # Assign StyleMap to placemark
        pnt.stylemap = style_map

    def add_flight_path(self, coordinates, name="Flight Path", description=None,
                        color_rgb=(0, 229, 255), width=3, mark_endpoints=True):
        """
        Adds the aircraft's flight path as a LineString.

        Used by streaming recording bundles to record where the aircraft
        actually flew while a recording was running, so the detections in
        the same document can be read against the track that produced them.

        Args:
            coordinates (list): Ordered ``(lat, lon)`` fixes. Fewer than two
                usable points draws nothing - a single fix is a position,
                not a path.
            name (str): Name shown in the KML tree.
            description (str): Optional description text.
            color_rgb (tuple): RGB line color, defaulting to the same cyan
                the live map draws the track in.
            width (int): Line width in pixels.
            mark_endpoints (bool): Also drop Start/End placemarks, so the
                direction of travel is readable without animating the path.

        Returns:
            The created LineString, or None when there was nothing to draw.
        """
        points = [
            (float(lon), float(lat))
            for lat, lon in (coordinates or [])
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float))
        ]
        if len(points) < 2:
            return None

        line = self.kml.newlinestring(name=name, coords=points)
        if description:
            line.description = description
        r, g, b = color_rgb
        # KML colors are ABGR hex, not RGB.
        line.style.linestyle.color = f'ff{b:02x}{g:02x}{r:02x}'
        line.style.linestyle.width = width
        line.tessellate = 1

        if mark_endpoints:
            start_lon, start_lat = points[0]
            end_lon, end_lat = points[-1]
            self.kml.newpoint(name=f'{name} - Start', coords=[(start_lon, start_lat)])
            self.kml.newpoint(name=f'{name} - End', coords=[(end_lon, end_lat)])

        return line

    def add_pod_overlay(self, image_path, box, name="POD Coverage",
                        description=None, packed=False, href=None):
        """
        Adds the POD heatmap as a KML GroundOverlay.

        Args:
            image_path (str): Path to the overlay PNG on disk.
            box (dict): WGS84 bounds {'north', 'south', 'east', 'west'}.
            name (str): Overlay name shown in the KML tree.
            description (str): Optional description text.
            packed (bool): Pack the image into the document so a .kmz save is
                self-contained. When False, the overlay references ``href``
                (or the absolute image path) instead.
            href (str): Relative href to use when not packing (e.g. a sidecar
                folder next to the .kml).

        Returns:
            The created GroundOverlay.
        """
        overlay = self.kml.newgroundoverlay(name=name)
        if packed:
            overlay.icon.href = self.kml.addfile(image_path)
        else:
            overlay.icon.href = href or image_path
        overlay.latlonbox.north = box['north']
        overlay.latlonbox.south = box['south']
        overlay.latlonbox.east = box['east']
        overlay.latlonbox.west = box['west']
        if description:
            overlay.description = description
        return overlay

    def save_kml(self, path):
        """
        Saves the KML document to a file.

        A ``.kmz`` path saves a zipped document (packing any files added via
        ``add_pod_overlay(packed=True)``); anything else saves plain KML.

        Args:
            path (str): The file path where the KML document will be stored.
        """
        if str(path).lower().endswith('.kmz'):
            self.kml.savekmz(path)
        else:
            self.kml.save(path)

    def generate_kml_export(self, images, output_path, progress_callback=None, cancel_check=None):
        """
        Generates KML file with placemarks for each flagged AOI.

        Args:
            images (list of dict): List of image metadata dictionaries with flagged AOIs.
            output_path (str): The path to save the generated KML file.
            progress_callback: Optional callback function(current, total, message) for progress updates
            cancel_check: Optional function that returns True if operation should be cancelled
        """
        # Count total AOIs for progress tracking
        total_aois = 0
        for image in images:
            if not image.get('hidden', False):
                aois = image.get('areas_of_interest', [])
                total_aois += sum(1 for aoi in aois if aoi.get('flagged', False))

        current_aoi_count = 0

        for img_idx, image in enumerate(images):
            # Check for cancellation
            if cancel_check and cancel_check():
                return  # Exit early if cancelled
            # Skip hidden images
            if image.get('hidden', False):
                continue

            image_name = image.get('name', f'Image {img_idx + 1}')
            image_path = image.get('path', '')

            # Get image GPS coordinates and metadata
            try:
                # Create ImageService to extract EXIF data
                image_service = ImageService(image_path, image.get('mask_path', ''), calculated_bearing=image.get('bearing'))

                # Get GPS from EXIF data as a dict (not formatted string)
                image_gps = LocationInfo.get_gps(exif_data=image_service.exif_data)

                if not image_gps:
                    continue

                # Get image dimensions and metadata
                img_array = image_service.img_array
                height, width = img_array.shape[:2]

            except Exception:
                continue

            # Process each flagged AOI
            aois = image.get('areas_of_interest', [])

            for aoi_idx, aoi in enumerate(aois):
                # Only export flagged AOIs
                if not aoi.get('flagged', False):
                    continue

                # Update progress
                current_aoi_count += 1
                if progress_callback:
                    progress_callback(
                        current_aoi_count,
                        total_aois,
                        f"Processing {image_name} - AOI {aoi_idx + 1}..."
                    )

                # Check for cancellation
                if cancel_check and cancel_check():
                    return  # Exit early if cancelled

                center = aoi.get('center', [0, 0])
                area = aoi.get('area', 0)
                # radius = aoi.get('radius', 0)  # Reserved for future use

                # Calculate AOI-specific GPS coordinates with fallback
                aoi_lat = image_gps['latitude']
                aoi_lon = image_gps['longitude']
                gps_note = ""

                # Try to calculate precise AOI GPS using AOIService
                try:
                    aoi_service = AOIService(image)

                    # The custom altitude set at initialization, else this
                    # image's Wingtra AGL - the same order the GPS map uses,
                    # so the exported AOI lands where the map shows it.
                    custom_alt_ft = resolve_altitude_ft(image, self.custom_altitude_ft)

                    # Calculate AOI GPS coordinates using the convenience method
                    result = aoi_service.calculate_gps_with_custom_altitude(image, aoi, custom_alt_ft, self.use_terrain)

                    if result:
                        aoi_lat, aoi_lon = result
                        gps_note = "Estimated AOI GPS\n"
                    else:
                        gps_note = "Image GPS (calculation failed)\n"
                except Exception as e:
                    gps_note = f"Image GPS (calculation error: {type(e).__name__})\n"

                # Calculate color information using AOIService
                color_info = ""
                marker_rgb = None
                try:
                    color_result = aoi_service.get_cached_or_representative_color(aoi)
                    if color_result:
                        marker_rgb = color_result['rgb']
                        color_info = f"Color: Hue: {color_result['hue_degrees']}° {color_result['hex']}\n"
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

    def generate_image_locations_kml(self, images, progress_callback=None, cancel_check=None):
        """
        Generates KML placemarks for drone/image locations.

        Args:
            images (list of dict): List of image metadata dictionaries.
            progress_callback: Optional callback function(current, total, message) for progress updates
            cancel_check: Optional function that returns True if operation should be cancelled
        """
        total_images = sum(1 for img in images if not img.get('hidden', False))
        current_image_count = 0

        for img_idx, image in enumerate(images):
            # Check for cancellation
            if cancel_check and cancel_check():
                return  # Exit early if cancelled

            # Skip hidden images
            if image.get('hidden', False):
                continue

            image_name = image.get('name', f'Image {img_idx + 1}')
            image_path = image.get('path', '')

            # Get image GPS coordinates
            try:
                # Create ImageService to extract EXIF data
                image_service = ImageService(image_path, image.get('mask_path', ''), calculated_bearing=image.get('bearing'))

                # Get GPS from EXIF data
                image_gps = LocationInfo.get_gps(exif_data=image_service.exif_data)

                if not image_gps:
                    continue

                # Get additional metadata for description.
                # Use custom altitude if provided, otherwise get from EXIF.
                # The reference plane travels with the value: an operator
                # override is a height above the ground being flown over,
                # a WALDO-prepassed image carries a terrain-referenced AGL,
                # and a DJI image carries height above the takeoff point.
                # All three used to be exported as "AGL".
                # Every reference plane this image has, resolved by the
                # service: the operator's override, or the image's own
                # figure plus the DEM-derived AGL beside it. A reader in
                # CalTopo or Google Earth has no tooltip to ask with.
                readings = image_service.get_altitude_readings(
                    'ft', use_terrain=self.use_terrain,
                    custom_altitude_ft=self.custom_altitude_ft,
                    offline_only=False,
                    terrain_agl_ft=wingtra_agl_ft(image))

                gimbal_pitch = image_service.get_camera_pitch()
                gimbal_yaw = image_service.get_camera_yaw()

                # Update progress
                current_image_count += 1
                if progress_callback:
                    progress_callback(
                        current_image_count,
                        total_images,
                        f"Processing {image_name}..."
                    )

                # Build description
                description = "Drone/Image Location\n"
                description += f"Image: {image_name}\n"
                description += f"GPS: {image_gps['latitude']:.6f}, {image_gps['longitude']:.6f}\n"

                for line in FormatHelper.altitude_lines(readings):
                    description += f"{line}\n"
                if gimbal_pitch is not None:
                    description += f"Gimbal Pitch: {gimbal_pitch:.1f}°\n"
                if gimbal_yaw is not None:
                    description += f"Gimbal Yaw: {gimbal_yaw:.1f}°\n"

                # Add placemark
                self.add_image_location_placemark(
                    image_name,
                    image_gps['latitude'],
                    image_gps['longitude'],
                    description
                )

            except Exception:
                # Silently continue on error - individual image location failures
                # shouldn't stop the entire export
                continue

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
