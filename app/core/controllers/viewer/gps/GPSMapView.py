"""
GPSMapView - Custom QGraphicsView widget for GPS map visualization.

This widget renders map tiles, GPS points, connection lines, and handles user interaction.
"""

import math
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPolygonItem, QWidget, QLabel
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QTimer
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QWheelEvent, QMouseEvent, QPainter, QPixmap, QFont, QPalette, QPolygonF
from .MapTileLoader import MapTileLoader


class GPSMapView(QGraphicsView):
    """
    Custom graphics view for displaying and interacting with GPS points on a map.

    Renders map tiles, GPS locations as points, connects them chronologically,
    and handles zoom/pan/click interactions.
    """

    # Signal emitted when a GPS point is clicked
    point_clicked = Signal(int)

    def __init__(self, parent=None):
        """Initialize the GPS map view."""
        super().__init__(parent)

        # Create scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # Allow scrollbars when needed for panning
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Map tile loader
        self.tile_loader = MapTileLoader()
        self.tile_loader.tile_loaded.connect(self.on_tile_loaded)

        # Map tiles storage - keep tiles from all zoom levels
        self.tile_items = {}  # Dictionary of (x, y, zoom): QGraphicsPixmapItem
        self.all_tile_items = {}  # Cache all tiles ever loaded
        self.current_zoom = 15  # Default zoom level

        # GPS data storage
        self.gps_data = []
        self.point_items = []  # List of QGraphicsEllipseItem for each point
        self.path_item = None  # Connection lines
        self.current_image_index = -1
        self.aoi_color = QColor(255, 140, 0)  # Default orange

        # AOI marker storage
        self.aoi_marker = None  # Current AOI marker
        self.aoi_data = None  # Current AOI metadata

        # FOV (Field of View) box for current image
        self.fov_box = None

        # Map bounds
        self.min_lat = None
        self.max_lat = None
        self.min_lon = None
        self.max_lon = None

        # Base zoom level (calculated from GPS bounds)
        self.base_zoom = 10

        # Map rotation
        self.is_rotated = False
        self.current_bearing = None

        # Track zoom scale separately from rotation
        self.zoom_scale = 1.0

        # Tile loading timer
        self.tile_timer = QTimer()
        self.tile_timer.timeout.connect(self.load_visible_tiles)
        self.tile_timer.setSingleShot(True)

        # Performance optimization
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)

        # Initialize compass rose overlay
        self._init_compass_rose()

    def _init_compass_rose(self):
        """Initialize the compass rose overlay widget."""
        # Initialize as None first
        self.compass_container = None
        self.compass_label = None

    def _create_compass_rose(self):
        """Create the compass rose overlay widget."""
        if self.compass_container is not None:
            # If already created, just ensure it's visible and raised
            self.compass_container.setVisible(True)
            self.compass_container.show()
            self.compass_container.raise_()
            self._position_compass()  # Reposition in case window size changed
            return

        # Check if viewport is ready and has size
        vp = self.viewport()
        if not vp or vp.width() == 0 or vp.height() == 0:
            # Try again later if viewport not ready
            QTimer.singleShot(50, self._create_compass_rose)
            return

        # Create compass rose container widget
        self.compass_container = QWidget(vp)
        self.compass_container.setFixedSize(70, 70)
        self.compass_container.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.compass_container.setAttribute(Qt.WA_StyledBackground, True)
        self.compass_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 120);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 50);
            }
        """)

        # Create compass label
        self.compass_label = QLabel(self.compass_container)
        self.compass_label.setFixedSize(60, 60)
        self.compass_label.move(5, 5)  # Center within container
        self.compass_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Position in bottom-right corner
        self._position_compass()

        # Draw initial north-up compass (0 or current rotation)
        rotation = self.current_bearing if self.is_rotated and self.current_bearing else 0
        self._draw_compass_rose(rotation)

        # Ensure the compass is visible and on top
        self.compass_container.setVisible(True)
        self.compass_container.show()
        self.compass_container.raise_()

    def _position_compass(self):
        """Position the compass rose in the bottom-right corner."""
        if not self.compass_container:
            return

        margin = 12
        vp = self.viewport()
        vp_width = vp.width()
        vp_height = vp.height()

        # Position in bottom-right corner
        x = vp_width - self.compass_container.width() - margin
        y = vp_height - self.compass_container.height() - margin

        # Ensure minimum margins
        x = max(margin, x)
        y = max(margin, y)

        self.compass_container.move(x, y)
        self.compass_container.raise_()

    def _ensure_compass_on_top(self):
        """Ensure the compass rose stays on top of all other widgets."""
        if self.compass_container and self.compass_container.isVisible():
            self.compass_container.raise_()
            # Also ensure it's visible
            self.compass_container.show()

    def _maintain_compass(self):
        """Maintain compass visibility and position after view changes."""
        if not self.compass_container:
            # Create compass if it doesn't exist
            self._create_compass_rose()
        else:
            # Reposition and ensure visibility
            self._position_compass()
            self.compass_container.setVisible(True)
            self.compass_container.show()
            self.compass_container.raise_()

    def _get_ironbow_color(self, normalized):
        """
        Get Ironbow thermal palette color for normalized value.

        Args:
            normalized: Value from 0.0 to 1.0

        Returns:
            QColor representing the Ironbow color at that position
        """
        # Ironbow palette keypoints
        # Position: (R, G, B)
        keypoints = [
            (0.0, (0, 0, 0)),        # Black
            (0.13, (20, 11, 52)),    # Very dark blue
            (0.25, (48, 22, 138)),   # Dark blue
            (0.38, (86, 44, 162)),   # Purple-blue
            (0.5, (128, 47, 142)),   # Purple
            (0.63, (185, 50, 104)),  # Red-purple
            (0.75, (231, 82, 64)),   # Red-orange
            (0.88, (253, 155, 49)),  # Orange-yellow
            (0.95, (254, 215, 102)),  # Yellow
            (1.0, (255, 254, 189))   # Light yellow-white
        ]

        # Find the two keypoints to interpolate between
        for i in range(len(keypoints) - 1):
            pos1, color1 = keypoints[i]
            pos2, color2 = keypoints[i + 1]

            if pos1 <= normalized <= pos2:
                # Interpolate between the two colors
                if pos2 - pos1 > 0:
                    t = (normalized - pos1) / (pos2 - pos1)
                else:
                    t = 0

                r = int(color1[0] + t * (color2[0] - color1[0]))
                g = int(color1[1] + t * (color2[1] - color1[1]))
                b = int(color1[2] + t * (color2[2] - color1[2]))

                return QColor(r, g, b)

        # Fallback (shouldn't happen with normalized values 0-1)
        return QColor(255, 254, 189)  # Light yellow-white

    def _draw_compass_rose(self, rotation_angle):
        """
        Draw the compass rose with the given rotation.

        Args:
            rotation_angle: Rotation angle in degrees (0 = north up)
        """
        # Make sure compass is created
        if not self.compass_label:
            return

        # Create a 60x60 pixmap for the compass
        size = 60
        canvas = QPixmap(size, size)
        canvas.fill(Qt.transparent)

        p = QPainter(canvas)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # Center point
        cx = size / 2
        cy = size / 2

        # Draw compass rose
        # Main arrow (north pointer)
        arrow_length = 20
        arrow_width = 6

        # Save state and apply rotation
        p.save()
        p.translate(cx, cy)
        p.rotate(rotation_angle)

        # Draw north arrow (red)
        p.setPen(QPen(QColor(255, 0, 0), 2))
        p.setBrush(QBrush(QColor(255, 0, 0)))
        north_arrow = QPainterPath()
        north_arrow.moveTo(0, -arrow_length)
        north_arrow.lineTo(-arrow_width/2, 0)
        north_arrow.lineTo(arrow_width/2, 0)
        north_arrow.closeSubpath()
        p.drawPath(north_arrow)

        # Draw south arrow (white)
        p.setPen(QPen(QColor(255, 255, 255), 2))
        p.setBrush(QBrush(QColor(255, 255, 255)))
        south_arrow = QPainterPath()
        south_arrow.moveTo(0, arrow_length)
        south_arrow.lineTo(-arrow_width/2, 0)
        south_arrow.lineTo(arrow_width/2, 0)
        south_arrow.closeSubpath()
        p.drawPath(south_arrow)

        # Draw east arrow (gray)
        p.setPen(QPen(QColor(180, 180, 180), 1))
        p.setBrush(QBrush(QColor(180, 180, 180)))
        east_arrow = QPainterPath()
        east_arrow.moveTo(arrow_length * 0.7, 0)
        east_arrow.lineTo(0, -arrow_width/2 * 0.7)
        east_arrow.lineTo(0, arrow_width/2 * 0.7)
        east_arrow.closeSubpath()
        p.drawPath(east_arrow)

        # Draw west arrow (gray)
        west_arrow = QPainterPath()
        west_arrow.moveTo(-arrow_length * 0.7, 0)
        west_arrow.lineTo(0, -arrow_width/2 * 0.7)
        west_arrow.lineTo(0, arrow_width/2 * 0.7)
        west_arrow.closeSubpath()
        p.drawPath(west_arrow)

        # Draw center circle
        p.setPen(QPen(QColor(0, 0, 0), 2))
        p.setBrush(QBrush(QColor(255, 255, 255)))
        p.drawEllipse(QPointF(0, 0), 3, 3)

        p.restore()

        # Draw cardinal direction labels
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        p.setFont(font)

        # Calculate label positions based on rotation
        label_radius = 25
        labels = [
            ('N', 0),    # North
            ('E', 90),   # East
            ('S', 180),  # South
            ('W', 270)   # West
        ]

        for label_text, base_angle in labels:
            # Apply rotation to label position
            angle_rad = math.radians(base_angle + rotation_angle - 90)  # -90 to convert from compass to math angles
            label_x = cx + label_radius * math.cos(angle_rad)
            label_y = cy + label_radius * math.sin(angle_rad)

            # Draw label
            fm = p.fontMetrics()
            text_width = fm.horizontalAdvance(label_text)
            text_height = fm.height()

            # Determine text color based on direction
            if label_text == 'N':
                p.setPen(QPen(QColor(255, 0, 0)))  # Red for north
            else:
                p.setPen(QPen(QColor(255, 255, 255)))  # White for others

            p.drawText(QPointF(label_x - text_width/2, label_y + text_height/4), label_text)

        p.end()

        # Set the pixmap to the label
        self.compass_label.setPixmap(canvas)

    def set_gps_data(self, gps_data, current_image_index, aoi_color=None):
        """
        Set GPS data and render the map.

        Args:
            gps_data: List of GPS data dictionaries
            current_image_index: Index in gps_data list of currently selected image (can be None)
            aoi_color: Color to use for highlighting current image
        """
        self.gps_data = gps_data
        self.current_image_index = current_image_index if current_image_index is not None else -1
        if aoi_color:
            self.aoi_color = aoi_color

        # Calculate bounds
        self.calculate_bounds()

        # Render map and points
        self.render_map()

    def calculate_bounds(self):
        """Calculate the geographic bounds of all GPS points."""
        if not self.gps_data:
            return

        lats = [d['latitude'] for d in self.gps_data]
        lons = [d['longitude'] for d in self.gps_data]

        self.min_lat = min(lats)
        self.max_lat = max(lats)
        self.min_lon = min(lons)
        self.max_lon = max(lons)

        # Add some padding (about 10%)
        lat_padding = (self.max_lat - self.min_lat) * 0.1
        lon_padding = (self.max_lon - self.min_lon) * 0.1

        self.min_lat -= lat_padding
        self.max_lat += lat_padding
        self.min_lon -= lon_padding
        self.max_lon += lon_padding

    def lat_lon_to_scene(self, lat, lon):
        """
        Convert GPS coordinates to scene coordinates using Web Mercator projection.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees

        Returns:
            QPointF with scene coordinates
        """
        # Web Mercator projection
        x = (lon + 180.0) / 360.0 * (256 * (2 ** self.current_zoom))

        lat_rad = math.radians(lat)
        mer_y = math.log(math.tan(lat_rad / 2 + math.pi / 4))
        y = (1 - mer_y / math.pi) / 2 * (256 * (2 ** self.current_zoom))

        return QPointF(x, y)

    def scene_to_lat_lon(self, x, y):
        """
        Convert scene coordinates back to GPS coordinates.

        Args:
            x: Scene x coordinate
            y: Scene y coordinate

        Returns:
            tuple: (lat, lon) in degrees
        """
        # Inverse Web Mercator projection
        world_size = 256 * (2 ** self.current_zoom)

        # Convert x to longitude
        lon = x / world_size * 360.0 - 180.0

        # Convert y to latitude
        mer_y = (1 - y * 2 / world_size) * math.pi

        # Clamp to prevent overflow
        mer_y = max(-10, min(10, mer_y))

        try:
            lat_rad = math.atan(math.sinh(mer_y))
            lat = math.degrees(lat_rad)
        except (OverflowError, ValueError):
            # Fallback for extreme values
            lat = 85 if mer_y > 0 else -85

        return lat, lon

    def render_map(self):
        """Render map tiles and GPS points."""
        # Store AOI data temporarily if present
        temp_aoi_data = self.aoi_data
        temp_aoi_color = None
        if self.aoi_marker and self.aoi_marker.brush():
            temp_aoi_color = self.aoi_marker.brush().color()

        # Clear existing items
        self.scene.clear()
        self.point_items = []
        self.aoi_marker = None  # Reset reference since scene.clear() removed it
        self.fov_box = None  # Reset reference since scene.clear() removed it
        # Don't clear tile_items here - keep them for caching

        if not self.gps_data:
            return

        # Calculate appropriate zoom level
        view_rect = self.viewport().rect()
        self.base_zoom = self.tile_loader.calculate_zoom_for_bounds(
            self.min_lat, self.max_lat, self.min_lon, self.max_lon,
            view_rect.width(), view_rect.height()
        )
        self.current_zoom = self.base_zoom

        # Set a large scene rect to allow panning beyond visible area
        # This prevents the hard edge panning issue
        world_size = 256 * (2 ** self.current_zoom)
        self.scene.setSceneRect(-world_size/2, -world_size/2, world_size * 2, world_size * 2)

        # Load initial tiles
        self.load_visible_tiles()

        # Draw GPS points and path
        self.draw_gps_points()

        # Restore AOI marker if it was present
        if temp_aoi_data and temp_aoi_color:
            color_rgb = [temp_aoi_color.red(), temp_aoi_color.green(), temp_aoi_color.blue()]
            self.set_aoi_marker(temp_aoi_data, color_rgb)

    def load_visible_tiles(self):
        """Load map tiles for the visible area."""
        if self.min_lat is None:
            return

        # Get visible bounds in scene coordinates with extra padding
        view_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        # Add significant padding to load tiles beyond immediate view
        padding = 512  # Load tiles well beyond the edges
        view_rect = view_rect.adjusted(-padding, -padding, padding, padding)

        # Convert visible scene bounds back to lat/lon
        top_left = view_rect.topLeft()
        bottom_right = view_rect.bottomRight()

        # Use our inverse projection method
        visible_max_lat, visible_min_lon = self.scene_to_lat_lon(top_left.x(), top_left.y())
        visible_min_lat, visible_max_lon = self.scene_to_lat_lon(bottom_right.x(), bottom_right.y())

        # Ensure valid ranges
        visible_min_lat = max(-85, min(85, visible_min_lat))
        visible_max_lat = max(-85, min(85, visible_max_lat))
        visible_min_lon = max(-180, min(180, visible_min_lon))
        visible_max_lon = max(-180, min(180, visible_max_lon))

        # Calculate tile range for visible area
        min_tile_x, max_tile_y = self.tile_loader.lat_lon_to_tile(
            visible_min_lat, visible_min_lon, self.current_zoom
        )
        max_tile_x, min_tile_y = self.tile_loader.lat_lon_to_tile(
            visible_max_lat, visible_max_lon, self.current_zoom
        )

        # Add buffer (2 tiles in each direction for smoother panning)
        buffer_tiles = 2
        min_tile_x = max(0, min_tile_x - buffer_tiles)
        min_tile_y = max(0, min_tile_y - buffer_tiles)
        max_tile_x = min(2 ** self.current_zoom - 1, max_tile_x + buffer_tiles)
        max_tile_y = min(2 ** self.current_zoom - 1, max_tile_y + buffer_tiles)

        # Limit number of tiles to load (max 49 tiles - 7x7 grid)
        tile_count = (max_tile_x - min_tile_x + 1) * (max_tile_y - min_tile_y + 1)
        if tile_count > 49:
            # Reduce range to fit within limit
            center_x = (min_tile_x + max_tile_x) // 2
            center_y = (min_tile_y + max_tile_y) // 2
            range_limit = 3  # 7x7 grid
            min_tile_x = max(0, center_x - range_limit)
            max_tile_x = min(2 ** self.current_zoom - 1, center_x + range_limit)
            min_tile_y = max(0, center_y - range_limit)
            max_tile_y = min(2 ** self.current_zoom - 1, center_y + range_limit)

        # Load tiles
        for x in range(min_tile_x, max_tile_x + 1):
            for y in range(min_tile_y, max_tile_y + 1):
                key = (x, y, self.current_zoom)
                if key not in self.tile_items:
                    # Check if we have it in cache first (include source type)
                    cache_key = (x, y, self.current_zoom, self.tile_loader.tile_source)
                    if cache_key in self.all_tile_items:
                        # Use cached tile
                        lat, lon = self.tile_loader.tile_to_lat_lon(x, y, self.current_zoom)
                        scene_pos = self.lat_lon_to_scene(lat, lon)

                        tile_item = QGraphicsPixmapItem(self.all_tile_items[cache_key])
                        tile_item.setPos(scene_pos)
                        tile_item.setZValue(-100)
                        self.scene.addItem(tile_item)
                        self.tile_items[key] = tile_item
                    else:
                        # Load from network/disk
                        self.tile_loader.load_tile(x, y, self.current_zoom)

        # After loading all visible tiles, maintain compass
        QTimer.singleShot(10, self._maintain_compass)

    def on_tile_loaded(self, x_tile, y_tile, zoom, pixmap):
        """
        Handle loaded tile.

        Args:
            x_tile, y_tile: Tile coordinates
            zoom: Zoom level
            pixmap: Tile image
        """
        key = (x_tile, y_tile, zoom)
        # Include source type in cache key
        cache_key = (x_tile, y_tile, zoom, self.tile_loader.tile_source)

        # Store in global cache with source-specific key
        if cache_key not in self.all_tile_items:
            self.all_tile_items[cache_key] = pixmap

        # Only add to scene if it's for current zoom level
        if zoom != self.current_zoom:
            return

        if key in self.tile_items:
            return  # Already in scene

        # Calculate position
        lat, lon = self.tile_loader.tile_to_lat_lon(x_tile, y_tile, zoom)
        scene_pos = self.lat_lon_to_scene(lat, lon)

        # Add tile to scene
        tile_item = QGraphicsPixmapItem(pixmap)
        tile_item.setPos(scene_pos)
        tile_item.setZValue(-100)  # Put tiles in background
        self.scene.addItem(tile_item)
        self.tile_items[key] = tile_item

        # Maintain compass after adding tiles
        QTimer.singleShot(10, self._maintain_compass)

    def draw_gps_points(self):
        """Draw GPS points and connection lines."""
        if not self.gps_data:
            return

        # Convert GPS coordinates to scene coordinates
        points = []
        for data in self.gps_data:
            scene_point = self.lat_lon_to_scene(data['latitude'], data['longitude'])
            points.append(scene_point)

        # Draw connection lines (path)
        if len(points) > 1:
            path = QPainterPath()
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)

            self.path_item = QGraphicsPathItem(path)
            # Use a thin line that won't scale with zoom
            pen = QPen(QColor(150, 150, 150, 120), 1, Qt.PenStyle.SolidLine)  # Semi-transparent grey
            pen.setCosmetic(True)  # Cosmetic pen doesn't scale with zoom
            self.path_item.setPen(pen)
            self.path_item.setZValue(5)  # Above tiles, below points
            self.scene.addItem(self.path_item)

        # Draw GPS points
        for i, (data, scene_point) in enumerate(zip(self.gps_data, points)):
            # Determine point size and color
            is_current = (i == self.current_image_index)
            is_hidden = data.get('hidden', False)
            aoi_count = data.get('aoi_count', 0)
            has_flagged = data.get('has_flagged', False)

            if is_current:
                # Current image - larger and in AOI color
                size = 12
                color = self.aoi_color
                border_color = QColor(0, 0, 0)
                border_width = 2
                z_value = 20  # Bring to front
            elif is_hidden:
                # Hidden image - light grey
                size = 6
                color = QColor(200, 200, 200)  # Light grey
                border_color = QColor(150, 150, 150)
                border_width = 1
                z_value = 8
            elif has_flagged:
                # Flagged AOI - red point
                size = 8
                color = QColor(255, 0, 0)  # Red
                border_color = QColor(0, 0, 0)  # Black
                border_width = 1
                z_value = 15  # Higher priority than regular points
            elif aoi_count > 0:
                # Has AOI - blue (original color)
                size = 8
                color = QColor(0, 100, 255)  # Blue
                border_color = QColor(0, 0, 0)
                border_width = 1
                z_value = 12
            else:
                # Regular point - green (original color)
                size = 6
                color = QColor(0, 255, 0)  # Green
                border_color = QColor(0, 0, 0)
                border_width = 1
                z_value = 10

            # Create point item centered at scene coordinates
            point_item = QGraphicsEllipseItem(
                -size/2,  # Center the item at origin
                -size/2,
                size, size
            )
            point_item.setPos(scene_point)  # Position at scene coordinates
            point_item.setBrush(QBrush(color))
            point_item.setPen(QPen(border_color, border_width))
            point_item.setZValue(z_value)

            # Make the item ignore transformations (maintain screen size)
            point_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

            # Store image index as data
            point_item.setData(0, data['index'])

            # Make clickable
            point_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
            point_item.setCursor(Qt.CursorShape.PointingHandCursor)

            # Add tooltip
            tooltip = f"{data['name']}\n"
            tooltip += f"Image {data['index'] + 1}\n"
            if is_hidden:
                tooltip += "Status: Hidden\n"
            if has_flagged:
                tooltip += "🚩 Has flagged AOIs\n"
            tooltip += f"AOIs: {aoi_count}\n"
            tooltip += f"Lat: {data['latitude']:.6f}\n"
            tooltip += f"Lon: {data['longitude']:.6f}"
            point_item.setToolTip(tooltip)

            self.scene.addItem(point_item)
            self.point_items.append(point_item)

    def set_current_image(self, gps_list_index):
        """
        Update the currently highlighted image.

        Args:
            gps_list_index: Index in the gps_data list of the image to highlight
        """
        old_bearing = self.current_bearing
        self.current_image_index = gps_list_index if gps_list_index is not None else -1

        # Update current bearing (load lazily if needed)
        if 0 <= self.current_image_index < len(self.gps_data):
            # Check if bearing needs to be loaded
            if self.gps_data[self.current_image_index].get('bearing') is None:
                # Load bearing on demand
                image_path = self.gps_data[self.current_image_index].get('image_path')
                if image_path:
                    bearing = self.get_image_bearing_lazy(image_path)
                    self.gps_data[self.current_image_index]['bearing'] = bearing
            self.current_bearing = self.gps_data[self.current_image_index].get('bearing', None)
        else:
            self.current_bearing = None

        # If map is rotated and bearing changed, update rotation
        if self.is_rotated and self.current_bearing != old_bearing:
            if self.current_bearing is not None:
                # Reset and apply new rotation
                self.resetTransform()
                self.rotate(-self.current_bearing)
                # Reapply the zoom scale (tracked separately)
                self.scale(self.zoom_scale, self.zoom_scale)
                # Update compass rose to show new rotation
                self._create_compass_rose()  # Ensure compass exists
                self._draw_compass_rose(self.current_bearing)

        # Update point appearances
        for i, item in enumerate(self.point_items):
            is_current = (i == self.current_image_index)
            if i < len(self.gps_data):
                data = self.gps_data[i]
                is_hidden = data.get('hidden', False)
                aoi_count = data.get('aoi_count', 0)
                has_flagged = data.get('has_flagged', False)
            else:
                is_hidden = False
                aoi_count = 0
                has_flagged = False

            if is_current:
                # Highlight current point
                size = 12
                color = self.aoi_color
                border_color = QColor(0, 0, 0)
                border_width = 2
                z_value = 20
            elif is_hidden:
                # Hidden image - light grey
                size = 6
                color = QColor(200, 200, 200)
                border_width = 1
                border_color = QColor(150, 150, 150)
                z_value = 8
            elif has_flagged:
                # Flagged AOI - red point
                size = 8
                color = QColor(255, 0, 0)  # Red
                border_color = QColor(0, 0, 0)  # Black
                border_width = 1
                z_value = 15
            elif aoi_count > 0:
                # Has AOI - blue
                size = 8
                color = QColor(0, 100, 255)  # Blue
                border_color = QColor(0, 0, 0)
                border_width = 1
                z_value = 12
            else:
                # Regular point - green
                size = 6
                color = QColor(0, 255, 0)  # Green
                border_color = QColor(0, 0, 0)
                border_width = 1
                z_value = 10

            # Update point appearance (items are centered at origin)
            item.setRect(-size/2, -size/2, size, size)
            item.setBrush(QBrush(color))
            item.setPen(QPen(border_color, border_width))
            item.setZValue(z_value)

            # Center view on current point
            if is_current:
                self.centerOn(item.pos())
                # Ensure compass stays visible and positioned after centering
                QTimer.singleShot(10, self._maintain_compass)

        # Update FOV box for current image
        self.update_fov_box(self.current_image_index)

    def get_image_bearing_lazy(self, image_path):
        """
        Extract bearing/yaw information from image (lazy loading).

        Args:
            image_path: Path to the image file

        Returns:
            float: Bearing in degrees (0-360), or None if not available
        """
        try:
            from core.services.ImageService import ImageService
            image_service = ImageService(image_path, '')
            # Use get_drone_orientation() to match the Drone Orientation displayed in viewer
            return image_service.get_drone_orientation()
        except Exception:
            return None

    def set_tile_source(self, source):
        """
        Switch between map and satellite tile sources.

        Args:
            source: 'map' or 'satellite'
        """
        # Set the source in the tile loader
        self.tile_loader.set_tile_source(source)

        # Clear all tiles from scene
        for item in list(self.tile_items.values()):
            if isinstance(item, QGraphicsPixmapItem):
                try:
                    if item.scene() == self.scene:
                        self.scene.removeItem(item)
                except RuntimeError:
                    pass
        self.tile_items = {}

        # Don't clear all_tile_items - keep memory cache for quick switching
        # Just reload tiles with new source
        self.load_visible_tiles()

    def fit_all_points(self):
        """Fit all GPS points in the view."""
        if not self.point_items:
            return

        # Get the actual positions of all points (not bounding rect which ignores transformations)
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for item in self.point_items:
            pos = item.pos()  # Get actual scene position
            min_x = min(min_x, pos.x())
            max_x = max(max_x, pos.x())
            min_y = min(min_y, pos.y())
            max_y = max(max_y, pos.y())

        # Create rect from actual positions
        if min_x < float('inf'):
            rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

            # Add 10% padding
            padding = max(rect.width(), rect.height()) * 0.1
            rect.adjust(-padding, -padding, padding, padding)

            # Fit to view
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

            # Schedule tile loading
            self.tile_timer.start(100)

            # Maintain compass after fitting view
            QTimer.singleShot(50, self._maintain_compass)

    def zoom_in(self):
        """Zoom in by a factor."""
        self.scale(1.25, 1.25)
        self.zoom_scale *= 1.25  # Track zoom scale
        self.update_tile_zoom_level()  # Check if we need higher resolution tiles
        self.tile_timer.start(300)  # Load new tiles after zoom
        QTimer.singleShot(10, self._maintain_compass)  # Maintain compass

    def zoom_out(self):
        """Zoom out by a factor."""
        self.scale(0.8, 0.8)
        self.zoom_scale *= 0.8  # Track zoom scale
        self.update_tile_zoom_level()  # Check if we need lower resolution tiles
        self.tile_timer.start(300)  # Load new tiles after zoom
        QTimer.singleShot(10, self._maintain_compass)  # Maintain compass

    def pan(self, dx, dy):
        """
        Pan the view by the given amount.

        Args:
            dx: Horizontal pan amount
            dy: Vertical pan amount
        """
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - dx)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - dy)
        self.tile_timer.start(500)  # Load new tiles after pan

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        # Get the zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 0.85

        # Calculate new zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self.zoom_scale *= zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            self.zoom_scale *= zoom_out_factor

        # Apply zoom (AnchorUnderMouse is already set in __init__)
        self.scale(zoom_factor, zoom_factor)

        # Load tiles immediately, then check if we need different resolution
        self.tile_timer.start(100)

        # Check if we need to change tile zoom level after a short delay
        QTimer.singleShot(200, self.update_tile_zoom_level)

        # Maintain compass after zoom
        QTimer.singleShot(10, self._maintain_compass)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on AOI marker first
            if self.aoi_marker:
                aoi_view_pos = self.mapFromScene(self.aoi_marker.pos())
                dx = event.pos().x() - aoi_view_pos.x()
                dy = event.pos().y() - aoi_view_pos.y()
                distance = math.sqrt(dx * dx + dy * dy)

                if distance <= 10:  # Click tolerance
                    # Show AOI popup with copy button
                    self.show_aoi_popup(event.globalPos())
                    return

            # Check if clicking on a point
            # Since points ignore transformations, we need to check differently
            # Look for points near the click position
            click_tolerance = 10  # Pixels

            for item in self.point_items:
                # Get the item's scene position
                item_pos = item.pos()

                # Convert both to view coordinates for accurate hit testing
                item_view_pos = self.mapFromScene(item_pos)

                # Check if click is within tolerance of the point
                dx = event.pos().x() - item_view_pos.x()
                dy = event.pos().y() - item_view_pos.y()
                distance = math.sqrt(dx * dx + dy * dy)

                if distance <= click_tolerance:
                    # Get the image index from the item data
                    image_index = item.data(0)
                    if image_index is not None:
                        self.point_clicked.emit(image_index)
                        return

        # Default behavior for panning
        super().mousePressEvent(event)

    def show_aoi_popup(self, global_pos):
        """
        Show a popup with AOI data and copy button.

        Args:
            global_pos: Global position for the popup
        """
        if not self.aoi_data:
            return

        from PySide6.QtWidgets import QMenu, QApplication

        # Create popup menu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
        """)

        # Add copy data action
        copy_action = menu.addAction("Copy Data")
        copy_action.triggered.connect(self.copy_aoi_data)

        # Show menu at cursor position
        menu.exec(global_pos)

    def copy_aoi_data(self):
        """Copy AOI data to clipboard."""
        if not self.aoi_data:
            return

        from PySide6.QtWidgets import QApplication

        # Format the data for clipboard (matching AOIController format)
        clipboard_text = (
            f"Image: {self.aoi_data['image_name']}\n"
            f"AOI Coordinates: X={self.aoi_data['center_pixels'][0]}, Y={self.aoi_data['center_pixels'][1]}\n"
            f"AOI Area: {self.aoi_data['pixel_area']:.0f} px\n"
        )

        # Add average info if available
        if self.aoi_data.get('avg_info'):
            clipboard_text += f"Average: {self.aoi_data['avg_info']}\n"

        # Add GPS coordinates
        clipboard_text += f"GPS Coordinates: {self.aoi_data['latitude']:.6f}, {self.aoi_data['longitude']:.6f}"

        # Copy to clipboard
        QApplication.clipboard().setText(clipboard_text)

    def keyPressEvent(self, event):
        """Handle key press events for navigation."""
        if event.key() == Qt.Key.Key_Home:
            self.fit_all_points()
        elif event.key() == Qt.Key.Key_R:
            # Toggle rotation based on current image bearing
            self.toggle_rotation()
        else:
            super().keyPressEvent(event)

    def toggle_rotation(self):
        """Toggle map rotation between north-up and bearing-aligned."""
        # Ensure compass is created
        self._create_compass_rose()

        # Store current center point
        center_point = None
        if self.current_image_index >= 0 and self.current_image_index < len(self.point_items):
            center_point = self.point_items[self.current_image_index].pos()

        if self.is_rotated:
            # Reset to north-up
            self.resetTransform()
            self.is_rotated = False
            # Reapply the zoom scale (not from transform which includes rotation)
            self.scale(self.zoom_scale, self.zoom_scale)
            # Update compass rose to north-up
            self._draw_compass_rose(0)
        else:
            # Rotate to current image bearing if available
            if self.current_bearing is not None:
                # Reset and apply rotation
                self.resetTransform()
                # Rotate negative bearing to align map with drone heading
                self.rotate(-self.current_bearing)
                # Reapply the zoom scale
                self.scale(self.zoom_scale, self.zoom_scale)
                self.is_rotated = True
                # Update compass rose to show rotation
                self._draw_compass_rose(self.current_bearing)

        # Re-center on the current GPS point
        if center_point is not None:
            self.centerOn(center_point)

    def update_tile_zoom_level(self):
        """Update tile zoom level based on current view scale for better resolution."""
        # Use the tracked zoom scale, not transform which includes rotation
        scale_factor = self.zoom_scale

        # Calculate the optimal tile zoom for current scale
        # We want higher res tiles when zoomed in, lower res when zoomed out
        if scale_factor > 1.5:
            # Zoomed in - need higher resolution tiles
            target_zoom = min(18, self.current_zoom + 1)
        elif scale_factor < 0.67:
            # Zoomed out - can use lower resolution tiles
            target_zoom = max(1, self.current_zoom - 1)
        else:
            # Scale is reasonable for current tiles
            return

        # If zoom level changed, reload tiles but maintain view scale
        if target_zoom != self.current_zoom:
            # Store the current view center
            view_center = self.mapToScene(self.viewport().rect().center())
            view_center_lat, view_center_lon = self.scene_to_lat_lon(view_center.x(), view_center.y())

            # Calculate zoom difference
            zoom_diff = target_zoom - self.current_zoom
            scale_adjustment = 2.0 ** zoom_diff

            self.current_zoom = target_zoom

            # Clear old tiles from scene only (keep in cache)
            for item in list(self.tile_items.values()):
                if isinstance(item, QGraphicsPixmapItem):
                    try:
                        if item.scene() == self.scene:
                            self.scene.removeItem(item)
                    except RuntimeError:
                        pass
            self.tile_items = {}

            # Update scene rect for new zoom
            world_size = 256 * (2 ** self.current_zoom)
            self.scene.setSceneRect(-world_size/2, -world_size/2, world_size * 2, world_size * 2)

            # Update GPS point positions for new zoom level
            for i, point_item in enumerate(self.point_items):
                if i < len(self.gps_data):
                    data = self.gps_data[i]
                    new_pos = self.lat_lon_to_scene(data['latitude'], data['longitude'])
                    point_item.setPos(new_pos)

            # Update AOI marker position if present
            if self.aoi_marker and self.aoi_data:
                aoi_new_pos = self.lat_lon_to_scene(
                    self.aoi_data['latitude'],
                    self.aoi_data['longitude']
                )
                self.aoi_marker.setPos(aoi_new_pos)

            # Update path
            if self.path_item:
                try:
                    if self.path_item.scene() == self.scene:
                        self.scene.removeItem(self.path_item)
                except RuntimeError:
                    pass
                self.draw_path_only()

            # Adjust zoom scale tracking
            self.zoom_scale = self.zoom_scale / scale_adjustment

            # Reset transform and reapply rotation and scale
            self.resetTransform()
            if self.is_rotated and self.current_bearing is not None:
                self.rotate(-self.current_bearing)
            self.scale(self.zoom_scale, self.zoom_scale)

            # Restore the view center to the same lat/lon position
            new_center = self.lat_lon_to_scene(view_center_lat, view_center_lon)
            self.centerOn(new_center)

            # Load new tiles (will use cache if available)
            self.load_visible_tiles()

            # Maintain compass after zoom level change
            QTimer.singleShot(50, self._maintain_compass)

    def draw_path_only(self):
        """Draw just the connection path between GPS points."""
        if not self.gps_data or len(self.gps_data) < 2:
            return

        points = []
        for data in self.gps_data:
            scene_point = self.lat_lon_to_scene(data['latitude'], data['longitude'])
            points.append(scene_point)

        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)

        self.path_item = QGraphicsPathItem(path)
        pen = QPen(QColor(255, 0, 0, 180), 1, Qt.PenStyle.SolidLine)
        pen.setCosmetic(True)
        self.path_item.setPen(pen)
        self.path_item.setZValue(5)
        self.scene.addItem(self.path_item)

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # Don't create compass here - let the dialog handle it

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        # Load tiles for new viewport
        self.tile_timer.start(500)
        # Maintain compass after resize
        self._maintain_compass()

    def set_aoi_marker(self, aoi_gps_data, identifier_color):
        """
        Display an AOI marker on the map.

        Args:
            aoi_gps_data: Dict with AOI GPS data including:
                - latitude: GPS latitude of the AOI
                - longitude: GPS longitude of the AOI
                - aoi_index: Index of the AOI
                - pixel_area: Area of the AOI in pixels
                - center_pixels: Pixel coordinates of AOI center
                - image_index: Index of the source image
                - image_name: Name of the source image
                - avg_info: Average color/temperature info (optional)
            identifier_color: List [r, g, b] for the marker color
        """
        # Remove existing AOI marker if present
        if self.aoi_marker and self.aoi_marker in self.scene.items():
            self.scene.removeItem(self.aoi_marker)
            self.aoi_marker = None

        if not aoi_gps_data:
            self.aoi_data = None
            return

        # Store AOI data for click handling
        self.aoi_data = aoi_gps_data

        # Convert GPS to scene coordinates
        scene_point = self.lat_lon_to_scene(
            aoi_gps_data['latitude'],
            aoi_gps_data['longitude']
        )

        # Create AOI marker - use a square to distinguish from image points
        size = 14  # Slightly larger than image points
        self.aoi_marker = QGraphicsRectItem(
            -size/2,  # Center the item at origin
            -size/2,
            size, size
        )
        self.aoi_marker.setPos(scene_point)

        # Set color from identifier_color
        color = QColor(identifier_color[0], identifier_color[1], identifier_color[2])
        self.aoi_marker.setBrush(QBrush(color))
        self.aoi_marker.setPen(QPen(QColor(0, 0, 0), 2))  # Black border
        self.aoi_marker.setZValue(25)  # Higher than all other points

        # Make the marker ignore transformations (maintain screen size)
        self.aoi_marker.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

        # Make clickable
        self.aoi_marker.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.aoi_marker.setCursor(Qt.CursorShape.PointingHandCursor)

        # Store type identifier for click detection
        self.aoi_marker.setData(0, 'aoi_marker')

        # Add tooltip
        tooltip = f"AOI from {aoi_gps_data['image_name']}\n"
        tooltip += f"Pixel Position: X={aoi_gps_data['center_pixels'][0]}, Y={aoi_gps_data['center_pixels'][1]}\n"
        tooltip += f"Area: {aoi_gps_data['pixel_area']:.0f} px\n"
        if aoi_gps_data.get('avg_info'):
            tooltip += f"{aoi_gps_data['avg_info']}\n"
        tooltip += f"GPS: {aoi_gps_data['latitude']:.6f}, {aoi_gps_data['longitude']:.6f}"
        self.aoi_marker.setToolTip(tooltip)

        self.scene.addItem(self.aoi_marker)

    def clear_aoi_marker(self):
        """Remove the AOI marker from the map."""
        if self.aoi_marker and self.aoi_marker in self.scene.items():
            self.scene.removeItem(self.aoi_marker)
            self.aoi_marker = None
        self.aoi_data = None

    def update_fov_box(self, image_index):
        """
        Update the Field of View box for the current image.

        Args:
            image_index: Index of the current image, or -1 to clear
        """
        # Clear existing FOV box
        if self.fov_box and self.fov_box in self.scene.items():
            self.scene.removeItem(self.fov_box)
            self.fov_box = None

        if image_index < 0 or image_index >= len(self.gps_data):
            return

        # Get current image data
        current_data = self.gps_data[image_index]
        image_lat = current_data['latitude']
        image_lon = current_data['longitude']
        image_path = current_data.get('image_path')

        if not image_path:
            return

        # Try to calculate FOV dimensions
        try:
            from core.services.ImageService import ImageService

            # Get the parent viewer's custom altitude if available
            custom_alt = None
            if hasattr(self, 'parent') and hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'custom_agl_altitude_ft'):
                custom_alt = self.parent().parent().custom_agl_altitude_ft
                if custom_alt and custom_alt <= 0:
                    custom_alt = None

            image_service = ImageService(image_path, '')

            # Get GSD
            gsd_cm = image_service.get_average_gsd(custom_altitude_ft=custom_alt)
            if gsd_cm is None or gsd_cm <= 0:
                return  # Can't calculate FOV without valid GSD

            # Get image dimensions
            img_array = image_service.img_array
            if img_array is None:
                return

            height, width = img_array.shape[:2]

            # Calculate image dimensions in meters
            gsd_m = gsd_cm / 100.0
            width_m = width * gsd_m
            height_m = height * gsd_m

            # Get drone orientation
            bearing = current_data.get('bearing')
            if bearing is None:
                # Try to load bearing
                bearing = self.get_image_bearing_lazy(image_path)
                if bearing is None:
                    bearing = 0

            # Calculate the four corners of the image in GPS coordinates
            # Corners in image space (centered at origin)
            corners_image = [
                (-width_m / 2, -height_m / 2),  # Top-left
                (width_m / 2, -height_m / 2),   # Top-right
                (width_m / 2, height_m / 2),    # Bottom-right
                (-width_m / 2, height_m / 2)    # Bottom-left
            ]

            # Rotate corners by bearing and convert to GPS
            bearing_rad = math.radians(-bearing)  # Negative for same rotation as map
            cos_b = math.cos(bearing_rad)
            sin_b = math.sin(bearing_rad)

            corners_gps = []
            earth_radius = 6371000  # meters

            for x, y in corners_image:
                # Rotate
                x_rot = x * cos_b - y * sin_b
                y_rot = x * sin_b + y * cos_b

                # Convert to lat/lon offset
                delta_lat = y_rot / earth_radius * (180 / math.pi)
                delta_lon = x_rot / (earth_radius * math.cos(math.radians(image_lat))) * (180 / math.pi)

                # Calculate corner GPS
                corner_lat = image_lat + delta_lat
                corner_lon = image_lon + delta_lon

                # Convert to scene coordinates
                scene_point = self.lat_lon_to_scene(corner_lat, corner_lon)
                corners_gps.append(scene_point)

            # Create polygon from corners
            polygon = QPolygonF(corners_gps)

            # Create FOV box
            self.fov_box = QGraphicsPolygonItem(polygon)

            # Style the FOV box
            pen = QPen(QColor(0, 150, 255), 2)  # Blue outline
            pen.setCosmetic(True)  # Keep line width constant regardless of zoom
            self.fov_box.setPen(pen)

            # Semi-transparent fill
            brush = QBrush(QColor(0, 150, 255, 30))
            self.fov_box.setBrush(brush)

            self.fov_box.setZValue(5)  # Below points but above tiles

            # Add tooltip
            tooltip = f"Image FOV\n"
            tooltip += f"Dimensions: {width}x{height} pixels\n"
            tooltip += f"Ground Coverage: {width_m:.1f}m x {height_m:.1f}m\n"
            tooltip += f"GSD: {gsd_cm:.2f} cm/px\n"
            tooltip += f"Bearing: {bearing:.1f}°"
            self.fov_box.setToolTip(tooltip)

            self.scene.addItem(self.fov_box)

        except Exception as e:
            # Silently fail if we can't draw the FOV box
            pass

    def clear_fov_box(self):
        """Remove the FOV box from the map."""
        if self.fov_box and self.fov_box in self.scene.items():
            self.scene.removeItem(self.fov_box)
            self.fov_box = None
