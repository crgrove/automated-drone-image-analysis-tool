"""
GPSMapView - Custom QGraphicsView widget for GPS map visualization.

This widget renders map tiles, GPS points, connection lines, and handles user interaction.
"""

import math
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPolygonItem, QWidget, QLabel
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QTimer, QEvent
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QWheelEvent, QMouseEvent, QPainter, QPixmap, QFont, QPalette, QPolygonF
from core.views.viewer.widgets.MapTileLoader import MapTileLoader


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

        # Tile loading timer - proper debouncing
        self.tile_timer = QTimer()
        self.tile_timer.timeout.connect(self._load_visible_tiles_debounced)
        self.tile_timer.setSingleShot(True)

        # Performance optimization
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)

        # Compass rose overlay (created once, managed properly)
        self.compass_container = None
        self.compass_label = None
        self._compass_needs_update = False

        # Install event filter on viewport to handle paint events
        if self.viewport():
            self.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        """Filter events from the viewport to manage compass overlay."""
        if obj == self.viewport():
            if event.type() == QEvent.Type.Paint:
                # After viewport paints, ensure compass is on top
                if self.compass_container and self.compass_container.isVisible():
                    self.compass_container.raise_()
                return False
            elif event.type() == QEvent.Type.Show:
                # Viewport is being shown, ensure compass is created
                self._ensure_compass_created()
                return False
        return super().eventFilter(obj, event)

    def _ensure_compass_created(self):
        """Ensure the compass rose is created and properly positioned."""
        if self.compass_container is not None:
            # Already created, just make sure it's visible and positioned
            if not self.compass_container.isVisible():
                self.compass_container.setVisible(True)
            self._position_compass()
            self.compass_container.raise_()
            return

        vp = self.viewport()
        if not vp or vp.width() <= 0 or vp.height() <= 0:
            return  # Viewport not ready - will be created in resizeEvent

        try:
            # Create compass rose container widget (increased size for labels)
            self.compass_container = QWidget(vp)
            self.compass_container.setFixedSize(80, 80)
            self.compass_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.compass_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.compass_container.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 120);
                    border-radius: 6px;
                    border: 1px solid rgba(255, 255, 255, 50);
                }
            """)

            # Create compass label (increased size to fit labels)
            self.compass_label = QLabel(self.compass_container)
            self.compass_label.setFixedSize(70, 70)
            self.compass_label.move(5, 5)
            self.compass_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Position and show
            self._position_compass()
            self._update_compass_rotation()
            self.compass_container.setVisible(True)
            self.compass_container.show()
            self.compass_container.raise_()
        except Exception:
            # Silently fail - will retry in next resize/paint event
            self.compass_container = None
            self.compass_label = None

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

    def _update_compass_rotation(self):
        """Update the compass rose to show current rotation."""
        rotation = self.current_bearing if self.is_rotated and self.current_bearing else 0
        self._draw_compass_rose(rotation)

    def _draw_compass_rose(self, rotation_angle):
        """
        Draw the compass rose with the given rotation.

        Args:
            rotation_angle: Rotation angle in degrees (0 = north up)
        """
        if not self.compass_label:
            return

        # Create a 70x70 pixmap for the compass (increased from 60)
        size = 70
        canvas = QPixmap(size, size)
        canvas.fill(Qt.GlobalColor.transparent)

        p = QPainter(canvas)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Center point
        cx = size / 2
        cy = size / 2

        # Draw compass rose
        arrow_length = 22
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
        font.setPointSize(9)  # Slightly smaller for better fit
        font.setBold(True)
        p.setFont(font)

        # Calculate label positions based on rotation (increased radius)
        label_radius = 28
        labels = [
            ('N', 0),    # North
            ('E', 90),   # East
            ('S', 180),  # South
            ('W', 270)   # West
        ]

        for label_text, base_angle in labels:
            # Apply rotation to label position
            angle_rad = math.radians(base_angle + rotation_angle - 90)
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

            p.drawText(QPointF(label_x - text_width/2, label_y + text_height/3), label_text)

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

        # Initialize current image state (bearing, FOV, etc.)
        if self.current_image_index >= 0:
            self.set_current_image(self.current_image_index)
        
        # Ensure compass is created after data is loaded
        self._ensure_compass_created()

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
        self.aoi_marker = None
        self.fov_box = None
        self.tile_items = {}

        if not self.gps_data:
            return

        # Calculate appropriate zoom level
        view_rect = self.viewport().rect()
        self.base_zoom = self.tile_loader.calculate_zoom_for_bounds(
            self.min_lat, self.max_lat, self.min_lon, self.max_lon,
            view_rect.width(), view_rect.height()
        )
        self.current_zoom = self.base_zoom

        # Set scene rect
        world_size = 256 * (2 ** self.current_zoom)
        self.scene.setSceneRect(-world_size/2, -world_size/2, world_size * 2, world_size * 2)

        # Load tiles and draw points
        self.load_visible_tiles()
        self.draw_gps_points()

        # Restore AOI marker if it was present
        if temp_aoi_data and temp_aoi_color:
            color_rgb = [temp_aoi_color.red(), temp_aoi_color.green(), temp_aoi_color.blue()]
            self.set_aoi_marker(temp_aoi_data, color_rgb)

    def load_visible_tiles(self):
        """Request tile loading with debouncing."""
        self.tile_timer.start(100)

    def _load_visible_tiles_debounced(self):
        """Actually load map tiles for the visible area (debounced)."""
        if self.min_lat is None:
            return

        # Get visible bounds with padding
        view_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        padding = 512
        view_rect = view_rect.adjusted(-padding, -padding, padding, padding)

        # Convert to lat/lon
        top_left = view_rect.topLeft()
        bottom_right = view_rect.bottomRight()

        visible_max_lat, visible_min_lon = self.scene_to_lat_lon(top_left.x(), top_left.y())
        visible_min_lat, visible_max_lon = self.scene_to_lat_lon(bottom_right.x(), bottom_right.y())

        # Clamp to valid ranges
        visible_min_lat = max(-85, min(85, visible_min_lat))
        visible_max_lat = max(-85, min(85, visible_max_lat))
        visible_min_lon = max(-180, min(180, visible_min_lon))
        visible_max_lon = max(-180, min(180, visible_max_lon))

        # Calculate tile range
        min_tile_x, max_tile_y = self.tile_loader.lat_lon_to_tile(
            visible_min_lat, visible_min_lon, self.current_zoom
        )
        max_tile_x, min_tile_y = self.tile_loader.lat_lon_to_tile(
            visible_max_lat, visible_max_lon, self.current_zoom
        )

        # Add buffer and limit tile count
        buffer_tiles = 2
        min_tile_x = max(0, min_tile_x - buffer_tiles)
        min_tile_y = max(0, min_tile_y - buffer_tiles)
        max_tile_x = min(2 ** self.current_zoom - 1, max_tile_x + buffer_tiles)
        max_tile_y = min(2 ** self.current_zoom - 1, max_tile_y + buffer_tiles)

        # Limit to 7x7 grid (49 tiles)
        tile_count = (max_tile_x - min_tile_x + 1) * (max_tile_y - min_tile_y + 1)
        if tile_count > 49:
            center_x = (min_tile_x + max_tile_x) // 2
            center_y = (min_tile_y + max_tile_y) // 2
            range_limit = 3
            min_tile_x = max(0, center_x - range_limit)
            max_tile_x = min(2 ** self.current_zoom - 1, center_x + range_limit)
            min_tile_y = max(0, center_y - range_limit)
            max_tile_y = min(2 ** self.current_zoom - 1, center_y + range_limit)

        # Load tiles
        for x in range(min_tile_x, max_tile_x + 1):
            for y in range(min_tile_y, max_tile_y + 1):
                key = (x, y, self.current_zoom)
                if key not in self.tile_items:
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

    def on_tile_loaded(self, x_tile, y_tile, zoom, pixmap):
        """
        Handle loaded tile.

        Args:
            x_tile, y_tile: Tile coordinates
            zoom: Zoom level
            pixmap: Tile image
        """
        key = (x_tile, y_tile, zoom)
        cache_key = (x_tile, y_tile, zoom, self.tile_loader.tile_source)

        # Store in global cache
        if cache_key not in self.all_tile_items:
            self.all_tile_items[cache_key] = pixmap

        # Only add to scene if it's for current zoom level
        if zoom != self.current_zoom or key in self.tile_items:
            return

        # Calculate position and add to scene
        lat, lon = self.tile_loader.tile_to_lat_lon(x_tile, y_tile, zoom)
        scene_pos = self.lat_lon_to_scene(lat, lon)

        tile_item = QGraphicsPixmapItem(pixmap)
        tile_item.setPos(scene_pos)
        tile_item.setZValue(-100)
        self.scene.addItem(tile_item)
        self.tile_items[key] = tile_item

    def draw_gps_points(self):
        """Draw GPS points and connection lines."""
        if not self.gps_data:
            return

        # Convert GPS coordinates to scene coordinates
        points = []
        for data in self.gps_data:
            scene_point = self.lat_lon_to_scene(data['latitude'], data['longitude'])
            points.append(scene_point)

        # Draw connection lines
        if len(points) > 1:
            path = QPainterPath()
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)

            self.path_item = QGraphicsPathItem(path)
            pen = QPen(QColor(150, 150, 150, 120), 1, Qt.PenStyle.SolidLine)
            pen.setCosmetic(True)
            self.path_item.setPen(pen)
            self.path_item.setZValue(5)
            self.scene.addItem(self.path_item)

        # Draw GPS points
        for i, (data, scene_point) in enumerate(zip(self.gps_data, points)):
            # Determine point appearance
            is_current = (i == self.current_image_index)
            is_hidden = data.get('hidden', False)
            aoi_count = data.get('aoi_count', 0)
            has_flagged = data.get('has_flagged', False)

            if is_current:
                size, color, border_color, border_width, z_value = 12, self.aoi_color, QColor(0, 0, 0), 2, 20
            elif is_hidden:
                size, color, border_color, border_width, z_value = 6, QColor(200, 200, 200), QColor(150, 150, 150), 1, 8
            elif has_flagged:
                size, color, border_color, border_width, z_value = 8, QColor(255, 0, 0), QColor(0, 0, 0), 1, 15
            elif aoi_count > 0:
                size, color, border_color, border_width, z_value = 8, QColor(0, 100, 255), QColor(0, 0, 0), 1, 12
            else:
                size, color, border_color, border_width, z_value = 6, QColor(0, 255, 0), QColor(0, 0, 0), 1, 10

            # Create point item
            point_item = QGraphicsEllipseItem(-size/2, -size/2, size, size)
            point_item.setPos(scene_point)
            point_item.setBrush(QBrush(color))
            point_item.setPen(QPen(border_color, border_width))
            point_item.setZValue(z_value)
            point_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
            point_item.setData(0, data['index'])
            point_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
            point_item.setCursor(Qt.CursorShape.PointingHandCursor)

            # Tooltip
            tooltip = f"{data['name']}\nImage {data['index'] + 1}\n"
            if is_hidden:
                tooltip += "Status: Hidden\n"
            if has_flagged:
                tooltip += "🚩 Has flagged AOIs\n"
            tooltip += f"AOIs: {aoi_count}\nLat: {data['latitude']:.6f}\nLon: {data['longitude']:.6f}"
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

        # Update current bearing
        if 0 <= self.current_image_index < len(self.gps_data):
            if self.gps_data[self.current_image_index].get('bearing') is None:
                image_path = self.gps_data[self.current_image_index].get('image_path')
                if image_path:
                    bearing = self.get_image_bearing_lazy(image_path)
                    self.gps_data[self.current_image_index]['bearing'] = bearing
            self.current_bearing = self.gps_data[self.current_image_index].get('bearing', None)
        else:
            self.current_bearing = None

        # Update rotation if bearing changed
        if self.is_rotated and self.current_bearing != old_bearing and self.current_bearing is not None:
            self.resetTransform()
            self.rotate(-self.current_bearing)
            self.scale(self.zoom_scale, self.zoom_scale)
            self._update_compass_rotation()

        # Update point appearances
        self._update_point_appearances()

        # Center on current point
        if 0 <= self.current_image_index < len(self.point_items):
            self.centerOn(self.point_items[self.current_image_index].pos())

        # Update FOV box
        self.update_fov_box(self.current_image_index)

    def _update_point_appearances(self):
        """Update the visual appearance of all GPS points."""
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
                size, color, border_color, border_width, z_value = 12, self.aoi_color, QColor(0, 0, 0), 2, 20
            elif is_hidden:
                size, color, border_color, border_width, z_value = 6, QColor(200, 200, 200), QColor(150, 150, 150), 1, 8
            elif has_flagged:
                size, color, border_color, border_width, z_value = 8, QColor(255, 0, 0), QColor(0, 0, 0), 1, 15
            elif aoi_count > 0:
                size, color, border_color, border_width, z_value = 8, QColor(0, 100, 255), QColor(0, 0, 0), 1, 12
            else:
                size, color, border_color, border_width, z_value = 6, QColor(0, 255, 0), QColor(0, 0, 0), 1, 10

            item.setRect(-size/2, -size/2, size, size)
            item.setBrush(QBrush(color))
            item.setPen(QPen(border_color, border_width))
            item.setZValue(z_value)

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
            return image_service.get_camera_yaw()
        except Exception:
            return None

    def set_tile_source(self, source):
        """
        Switch between map and satellite tile sources.

        Args:
            source: 'map' or 'satellite'
        """
        self.tile_loader.set_tile_source(source)

        # Clear tiles from scene
        for item in list(self.tile_items.values()):
            if isinstance(item, QGraphicsPixmapItem):
                try:
                    if item.scene() == self.scene:
                        self.scene.removeItem(item)
                except RuntimeError:
                    pass
        self.tile_items = {}

        # Reload with new source
        self.load_visible_tiles()

    def fit_all_points(self):
        """Fit all GPS points in the view."""
        if not self.point_items or not self.gps_data:
            return

        # Calculate bounds
        lats = [d['latitude'] for d in self.gps_data]
        lons = [d['longitude'] for d in self.gps_data]

        min_lat = min(lats)
        max_lat = max(lats)
        min_lon = min(lons)
        max_lon = max(lons)

        # Add padding
        lat_padding = (max_lat - min_lat) * 0.1 or 0.001
        lon_padding = (max_lon - min_lon) * 0.1 or 0.001

        min_lat -= lat_padding
        max_lat += lat_padding
        min_lon -= lon_padding
        max_lon += lon_padding

        # Get viewport dimensions
        viewport_rect = self.viewport().rect()
        view_width = viewport_rect.width()
        view_height = viewport_rect.height()

        if view_width <= 0 or view_height <= 0:
            return

        # Calculate optimal zoom
        target_tile_zoom = self.tile_loader.calculate_zoom_for_bounds(
            min_lat, max_lat, min_lon, max_lon,
            view_width, view_height
        )

        # Update zoom level if changed
        if target_tile_zoom != self.current_zoom:
            self._change_tile_zoom_level(target_tile_zoom)

        # Calculate scene bounds
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for item in self.point_items:
            pos = item.pos()
            min_x = min(min_x, pos.x())
            max_x = max(max_x, pos.x())
            min_y = min(min_y, pos.y())
            max_y = max(max_y, pos.y())

        if min_x >= float('inf'):
            return

        # Calculate center and dimensions
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        scene_width = max_x - min_x
        scene_height = max_y - min_y

        if scene_width <= 0 or scene_height <= 0:
            # All points at same location
            self.resetTransform()
            if self.is_rotated and self.current_bearing is not None:
                self.rotate(-self.current_bearing)
            self.zoom_scale = 1.0
            self.scale(self.zoom_scale, self.zoom_scale)
            self.centerOn(center_x, center_y)
        else:
            # Calculate scale to fit
            scale_x = view_width / (scene_width * 1.2)
            scale_y = view_height / (scene_height * 1.2)
            target_scale = min(scale_x, scale_y)

            self.resetTransform()
            if self.is_rotated and self.current_bearing is not None:
                self.rotate(-self.current_bearing)

            self.zoom_scale = target_scale
            self.scale(self.zoom_scale, self.zoom_scale)
            self.centerOn(center_x, center_y)

        # Schedule tile loading
        self.load_visible_tiles()
        
        # Ensure compass is created after fitting
        self._ensure_compass_created()

    def zoom_in(self):
        """Zoom in by a factor."""
        self.scale(1.25, 1.25)
        self.zoom_scale *= 1.25
        self._check_tile_zoom_level()
        self.load_visible_tiles()

    def zoom_out(self):
        """Zoom out by a factor."""
        self.scale(0.8, 0.8)
        self.zoom_scale *= 0.8
        self._check_tile_zoom_level()
        self.load_visible_tiles()

    def pan(self, dx, dy):
        """
        Pan the view by the given amount.

        Args:
            dx: Horizontal pan amount
            dy: Vertical pan amount
        """
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - dx)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - dy)
        self.load_visible_tiles()

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        self.zoom_scale *= zoom_factor
        self.scale(zoom_factor, zoom_factor)
        
        # Check tile zoom level after zoom completes
        self._check_tile_zoom_level()
        self.load_visible_tiles()

    def _check_tile_zoom_level(self):
        """Check if we need to change tile zoom level based on current scale."""
        if self.zoom_scale > 1.5:
            target_zoom = min(18, self.current_zoom + 1)
        elif self.zoom_scale < 0.67:
            target_zoom = max(1, self.current_zoom - 1)
        else:
            return  # Current tiles are fine

        if target_zoom != self.current_zoom:
            self._change_tile_zoom_level(target_zoom)

    def _change_tile_zoom_level(self, target_zoom):
        """
        Change the tile zoom level and update all positions.

        Args:
            target_zoom: New tile zoom level
        """
        # Store current view center
        view_center = self.mapToScene(self.viewport().rect().center())
        view_center_lat, view_center_lon = self.scene_to_lat_lon(view_center.x(), view_center.y())

        # Calculate adjustment
        zoom_diff = target_zoom - self.current_zoom
        scale_adjustment = 2.0 ** zoom_diff

        self.current_zoom = target_zoom

        # Clear old tiles
        for item in list(self.tile_items.values()):
            if isinstance(item, QGraphicsPixmapItem):
                try:
                    if item.scene() == self.scene:
                        self.scene.removeItem(item)
                except RuntimeError:
                    pass
        self.tile_items = {}

        # Update scene rect
        world_size = 256 * (2 ** self.current_zoom)
        self.scene.setSceneRect(-world_size/2, -world_size/2, world_size * 2, world_size * 2)

        # Update GPS point positions
        for i, point_item in enumerate(self.point_items):
            if i < len(self.gps_data):
                data = self.gps_data[i]
                new_pos = self.lat_lon_to_scene(data['latitude'], data['longitude'])
                point_item.setPos(new_pos)

        # Update AOI marker position
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

        # Adjust zoom scale
        self.zoom_scale = self.zoom_scale / scale_adjustment

        # Reset transform
        self.resetTransform()
        if self.is_rotated and self.current_bearing is not None:
            self.rotate(-self.current_bearing)
        self.scale(self.zoom_scale, self.zoom_scale)

        # Restore view center
        new_center = self.lat_lon_to_scene(view_center_lat, view_center_lon)
        self.centerOn(new_center)

        # Update FOV box
        if 0 <= self.current_image_index < len(self.gps_data):
            self.update_fov_box(self.current_image_index)

        # Load new tiles
        self.load_visible_tiles()

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
        pen = QPen(QColor(150, 150, 150, 120), 1, Qt.PenStyle.SolidLine)
        pen.setCosmetic(True)
        self.path_item.setPen(pen)
        self.path_item.setZValue(5)
        self.scene.addItem(self.path_item)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check AOI marker click
            if self.aoi_marker:
                aoi_view_pos = self.mapFromScene(self.aoi_marker.pos())
                dx = event.pos().x() - aoi_view_pos.x()
                dy = event.pos().y() - aoi_view_pos.y()
                if math.sqrt(dx * dx + dy * dy) <= 10:
                    self.show_aoi_popup(event.globalPos())
                    return

            # Check point click
            click_tolerance = 10
            for item in self.point_items:
                item_view_pos = self.mapFromScene(item.pos())
                dx = event.pos().x() - item_view_pos.x()
                dy = event.pos().y() - item_view_pos.y()
                if math.sqrt(dx * dx + dy * dy) <= click_tolerance:
                    image_index = item.data(0)
                    if image_index is not None:
                        self.point_clicked.emit(image_index)
                        return

        super().mousePressEvent(event)

    def show_aoi_popup(self, global_pos):
        """
        Show a popup with AOI data and copy button.

        Args:
            global_pos: Global position for the popup
        """
        if not self.aoi_data:
            return

        from PySide6.QtWidgets import QMenu

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

        copy_action = menu.addAction("Copy Data")
        copy_action.triggered.connect(self.copy_aoi_data)
        menu.exec(global_pos)

    def copy_aoi_data(self):
        """Copy AOI data to clipboard."""
        if not self.aoi_data:
            return

        from PySide6.QtWidgets import QApplication

        clipboard_text = (
            f"Image: {self.aoi_data['image_name']}\n"
            f"AOI Coordinates: X={self.aoi_data['center_pixels'][0]}, Y={self.aoi_data['center_pixels'][1]}\n"
            f"AOI Area: {self.aoi_data['pixel_area']:.0f} px\n"
        )

        if self.aoi_data.get('avg_info'):
            clipboard_text += f"Average: {self.aoi_data['avg_info']}\n"

        clipboard_text += f"GPS Coordinates: {self.aoi_data['latitude']:.6f}, {self.aoi_data['longitude']:.6f}"

        QApplication.clipboard().setText(clipboard_text)

    def keyPressEvent(self, event):
        """Handle key press events for navigation."""
        if event.key() == Qt.Key.Key_Home:
            self.fit_all_points()
        elif event.key() == Qt.Key.Key_R:
            self.toggle_rotation()
        else:
            super().keyPressEvent(event)

    def toggle_rotation(self):
        """Toggle map rotation between north-up and bearing-aligned."""
        # Store current center
        center_point = None
        if 0 <= self.current_image_index < len(self.point_items):
            center_point = self.point_items[self.current_image_index].pos()

        if self.is_rotated:
            # Reset to north-up
            self.resetTransform()
            self.is_rotated = False
            self.scale(self.zoom_scale, self.zoom_scale)
            self._update_compass_rotation()
        else:
            # Rotate to bearing
            if self.current_bearing is not None:
                self.resetTransform()
                self.rotate(-self.current_bearing)
                self.scale(self.zoom_scale, self.zoom_scale)
                self.is_rotated = True
                self._update_compass_rotation()

        # Re-center
        if center_point is not None:
            self.centerOn(center_point)

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # Try to create compass - will work if viewport is ready
        self._ensure_compass_created()

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        # Try to create compass if not exists (viewport now has valid size)
        self._ensure_compass_created()
        # Position it if it exists
        self._position_compass()
        self.load_visible_tiles()

    def paintEvent(self, event):
        """Handle paint events."""
        super().paintEvent(event)
        # Ensure compass stays on top after repaints
        if self.compass_container and self.compass_container.isVisible():
            self.compass_container.raise_()

    def set_aoi_marker(self, aoi_gps_data, identifier_color):
        """
        Display an AOI marker on the map.

        Args:
            aoi_gps_data: Dict with AOI GPS data
            identifier_color: List [r, g, b] for the marker color
        """
        # Remove existing marker
        if self.aoi_marker and self.aoi_marker in self.scene.items():
            self.scene.removeItem(self.aoi_marker)
            self.aoi_marker = None

        if not aoi_gps_data:
            self.aoi_data = None
            return

        self.aoi_data = aoi_gps_data

        # Convert GPS to scene
        scene_point = self.lat_lon_to_scene(
            aoi_gps_data['latitude'],
            aoi_gps_data['longitude']
        )

        # Create marker
        size = 14
        self.aoi_marker = QGraphicsRectItem(-size/2, -size/2, size, size)
        self.aoi_marker.setPos(scene_point)

        color = QColor(identifier_color[0], identifier_color[1], identifier_color[2])
        self.aoi_marker.setBrush(QBrush(color))
        self.aoi_marker.setPen(QPen(QColor(0, 0, 0), 2))
        self.aoi_marker.setZValue(25)
        self.aoi_marker.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.aoi_marker.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.aoi_marker.setCursor(Qt.CursorShape.PointingHandCursor)
        self.aoi_marker.setData(0, 'aoi_marker')

        # Tooltip
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

        # Calculate FOV dimensions
        try:
            from core.services.ImageService import ImageService

            # Get custom altitude if available
            custom_alt = None
            if hasattr(self, 'parent') and hasattr(self.parent(), 'parent'):
                parent_viewer = self.parent().parent()
                if hasattr(parent_viewer, 'custom_agl_altitude_ft'):
                    custom_alt = parent_viewer.custom_agl_altitude_ft
                    if custom_alt and custom_alt <= 0:
                        custom_alt = None

            image_service = ImageService(image_path, '')

            # Get GSD and dimensions
            gsd_cm = image_service.get_average_gsd(custom_altitude_ft=custom_alt)
            if gsd_cm is None or gsd_cm <= 0:
                return

            img_array = image_service.img_array
            if img_array is None:
                return

            height, width = img_array.shape[:2]

            # Calculate dimensions in meters
            gsd_m = gsd_cm / 100.0
            width_m = width * gsd_m
            height_m = height * gsd_m

            # Get bearing
            bearing = current_data.get('bearing')
            if bearing is None:
                bearing = self.get_image_bearing_lazy(image_path) or 0

            # Calculate corners
            corners_image = [
                (-width_m / 2, -height_m / 2),
                (width_m / 2, -height_m / 2),
                (width_m / 2, height_m / 2),
                (-width_m / 2, height_m / 2)
            ]

            # Rotate and convert to GPS
            bearing_rad = math.radians(-bearing)
            cos_b = math.cos(bearing_rad)
            sin_b = math.sin(bearing_rad)

            corners_gps = []
            earth_radius = 6371000

            for x, y in corners_image:
                x_rot = x * cos_b - y * sin_b
                y_rot = x * sin_b + y * cos_b

                delta_lat = y_rot / earth_radius * (180 / math.pi)
                delta_lon = x_rot / (earth_radius * math.cos(math.radians(image_lat))) * (180 / math.pi)

                corner_lat = image_lat + delta_lat
                corner_lon = image_lon + delta_lon

                scene_point = self.lat_lon_to_scene(corner_lat, corner_lon)
                corners_gps.append(scene_point)

            # Create FOV polygon
            polygon = QPolygonF(corners_gps)
            self.fov_box = QGraphicsPolygonItem(polygon)

            pen = QPen(QColor(0, 150, 255), 2)
            pen.setCosmetic(True)
            self.fov_box.setPen(pen)

            brush = QBrush(QColor(0, 150, 255, 30))
            self.fov_box.setBrush(brush)
            self.fov_box.setZValue(5)

            tooltip = f"Image FOV\n"
            tooltip += f"Dimensions: {width}x{height} pixels\n"
            tooltip += f"Ground Coverage: {width_m:.1f}m x {height_m:.1f}m\n"
            tooltip += f"GSD: {gsd_cm:.2f} cm/px\n"
            tooltip += f"Bearing: {bearing:.1f}°"
            self.fov_box.setToolTip(tooltip)

            self.scene.addItem(self.fov_box)

        except Exception:
            pass

    def clear_fov_box(self):
        """Remove the FOV box from the map."""
        if self.fov_box and self.fov_box in self.scene.items():
            self.scene.removeItem(self.fov_box)
            self.fov_box = None
