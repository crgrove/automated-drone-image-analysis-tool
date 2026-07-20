"""
GPSMapView - Custom QGraphicsView widget for GPS map visualization.

This widget renders map tiles, GPS points, connection lines, and handles user interaction.
"""

import math
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPathItem,
    QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPolygonItem, QWidget,
    QLabel, QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QTimer, QEvent
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QWheelEvent, QMouseEvent, QPainter, QPixmap, QFont, QPalette, QPolygonF, QTransform

# Half the Web Mercator world extent in meters (pi * 6378137); the scene is a
# slippy-map plane, so an EPSG:3857 raster maps onto it with a pure scale+shift.
WEB_MERCATOR_ORIGIN_SHIFT = 20037508.342789244
# z-value for the POD overlay: above basemap tiles (-100), below flight path (5).
POD_OVERLAY_Z = -50
from core.views.images.viewer.widgets.MapTileLoader import MapTileLoader
from core.services.image.ImageService import ImageService
from core.services.image.AOIService import AOIService, _get_terrain_service
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin
from helpers.PhotogrammetryHelper import FovHomography, validate_alignment


class GPSMapView(TranslationMixin, QGraphicsView):
    """
    Custom graphics view for displaying and interacting with GPS points on a map.

    Renders map tiles, GPS locations as points, connects them chronologically,
    and handles zoom/pan/click interactions.
    """

    # Signal emitted when a GPS point is clicked
    point_clicked = Signal(int)

    # Signal emitted when user right-clicks on the map (lat, lon)
    gps_right_clicked = Signal(float, float)

    def __init__(self, parent=None, offline_only=False):
        """Initialize the GPS map view."""
        super().__init__(parent)
        self.logger = LoggerService()
        self.offline_only = bool(offline_only)

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
        self.tile_loader = MapTileLoader(offline_only=self.offline_only)
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

        # Zoom FOV box for current visible viewport
        self.zoom_fov_box = None
        self._fov_cache = None  # Cached FOV params: gsd_m, width, height, bearing, lat, lon
        self._last_visible_rect = None  # Last visible rect for map zoom redraws

        # POD coverage overlay (a georeferenced EPSG:3857 raster as a pixmap item)
        self.pod_overlay_item = None
        self._pod_pixmap = None
        self._pod_transform6 = None   # (a, b, c, d, e, f) affine of the pixmap in EPSG:3857
        self._pod_opacity = 0.7
        self._pod_visible = False

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

    def set_offline_mode(self, offline_only: bool):
        """Toggle offline behavior for tile loading."""
        self.offline_only = bool(offline_only)
        if hasattr(self, "tile_loader"):
            self.tile_loader.set_offline_only(self.offline_only)

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
        rotation = -self.current_bearing if self.is_rotated and self.current_bearing else 0
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
        north_arrow.lineTo(-arrow_width / 2, 0)
        north_arrow.lineTo(arrow_width / 2, 0)
        north_arrow.closeSubpath()
        p.drawPath(north_arrow)

        # Draw south arrow (white)
        p.setPen(QPen(QColor(255, 255, 255), 2))
        p.setBrush(QBrush(QColor(255, 255, 255)))
        south_arrow = QPainterPath()
        south_arrow.moveTo(0, arrow_length)
        south_arrow.lineTo(-arrow_width / 2, 0)
        south_arrow.lineTo(arrow_width / 2, 0)
        south_arrow.closeSubpath()
        p.drawPath(south_arrow)

        # Draw east arrow (gray)
        p.setPen(QPen(QColor(180, 180, 180), 1))
        p.setBrush(QBrush(QColor(180, 180, 180)))
        east_arrow = QPainterPath()
        east_arrow.moveTo(arrow_length * 0.7, 0)
        east_arrow.lineTo(0, -arrow_width / 2 * 0.7)
        east_arrow.lineTo(0, arrow_width / 2 * 0.7)
        east_arrow.closeSubpath()
        p.drawPath(east_arrow)

        # Draw west arrow (gray)
        west_arrow = QPainterPath()
        west_arrow.moveTo(-arrow_length * 0.7, 0)
        west_arrow.lineTo(0, -arrow_width / 2 * 0.7)
        west_arrow.lineTo(0, arrow_width / 2 * 0.7)
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

            p.drawText(QPointF(label_x - text_width / 2, label_y + text_height / 3), label_text)

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

    # ---------------- POD coverage overlay ----------------

    def set_pod_overlay(self, pixmap, transform6):
        """Show a georeferenced POD raster on the map.

        Args:
            pixmap: a ready QPixmap (RGBA) built from the POD/look-count LUT.
            transform6: (a, b, c, d, e, f) affine coefficients of ``pixmap`` in
                EPSG:3857 (north-up, square pixels: b == d == 0, e < 0).
        """
        self._pod_pixmap = pixmap
        self._pod_transform6 = tuple(float(v) for v in transform6)
        self._pod_visible = True
        self._add_pod_overlay_item()

    def clear_pod_overlay(self):
        """Remove the POD overlay and forget its raster."""
        self._pod_visible = False
        self._pod_pixmap = None
        self._pod_transform6 = None
        self._remove_pod_overlay_item()

    def set_pod_overlay_visible(self, visible):
        self._pod_visible = bool(visible)
        if self._pod_visible:
            self._add_pod_overlay_item()
        else:
            self._remove_pod_overlay_item()

    def set_pod_overlay_opacity(self, opacity):
        self._pod_opacity = max(0.0, min(1.0, float(opacity)))
        if self.pod_overlay_item is not None:
            self.pod_overlay_item.setOpacity(self._pod_opacity)

    def _remove_pod_overlay_item(self):
        if self.pod_overlay_item is not None:
            try:
                if self.pod_overlay_item.scene() == self.scene:
                    self.scene.removeItem(self.pod_overlay_item)
            except RuntimeError:
                pass
            self.pod_overlay_item = None

    def _add_pod_overlay_item(self):
        if not self._pod_visible or self._pod_pixmap is None:
            return
        self._remove_pod_overlay_item()
        item = QGraphicsPixmapItem(self._pod_pixmap)
        item.setZValue(POD_OVERLAY_Z)
        item.setOpacity(self._pod_opacity)
        item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.scene.addItem(item)
        self.pod_overlay_item = item
        self._position_pod_overlay()

    def _position_pod_overlay(self):
        """Place the overlay so its EPSG:3857 affine lines up with the scene."""
        if self.pod_overlay_item is None or self._pod_transform6 is None:
            return
        a, b, c, d, e, f = self._pod_transform6
        world = 256 * (2 ** self.current_zoom)
        k = world / (2 * WEB_MERCATOR_ORIGIN_SHIFT)     # scene units per 3857 meter
        self.pod_overlay_item.setPos((c + WEB_MERCATOR_ORIGIN_SHIFT) * k,
                                     (WEB_MERCATOR_ORIGIN_SHIFT - f) * k)
        t = QTransform()
        t.scale(a * k, -e * k)                          # e < 0 for north-up -> positive y scale
        self.pod_overlay_item.setTransform(t)

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
        self.scene.setSceneRect(-world_size / 2, -world_size / 2, world_size * 2, world_size * 2)

        # Load tiles and draw points
        self.load_visible_tiles()
        self.draw_gps_points()

        # Re-add the POD overlay (scene.clear() dropped the item; state survives).
        self._add_pod_overlay_item()

        # Restore AOI marker if it was present
        if temp_aoi_data and temp_aoi_color:
            color_rgb = [temp_aoi_color.red(), temp_aoi_color.green(), temp_aoi_color.blue()]
            self.set_aoi_marker(temp_aoi_data, color_rgb)

        # Ensure compass is in correct position after map render
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

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
            is_source_only = data.get('is_source_only', False)

            if is_current:
                size, color, border_color, border_width, z_value = 12, self.aoi_color, QColor(0, 0, 0), 2, 20
            elif is_source_only:
                # Non-AOI source captures: small grey dots beneath AOI markers,
                # no border, no click target. Just enough to trace the flight path.
                size, color, border_color, border_width, z_value = 4, QColor(140, 140, 140), QColor(140, 140, 140), 0, 6
            elif is_hidden:
                size, color, border_color, border_width, z_value = 6, QColor(200, 200, 200), QColor(150, 150, 150), 1, 8
            elif has_flagged:
                size, color, border_color, border_width, z_value = 8, QColor(255, 0, 0), QColor(0, 0, 0), 1, 15
            elif aoi_count > 0:
                size, color, border_color, border_width, z_value = 8, QColor(0, 100, 255), QColor(0, 0, 0), 1, 12
            else:
                size, color, border_color, border_width, z_value = 6, QColor(0, 255, 0), QColor(0, 0, 0), 1, 10

            # Create point item
            point_item = QGraphicsEllipseItem(-size / 2, -size / 2, size, size)
            point_item.setPos(scene_point)
            point_item.setBrush(QBrush(color))
            point_item.setPen(QPen(border_color, border_width))
            point_item.setZValue(z_value)
            point_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
            # Source-only entries store None — mousePressEvent skips clicks with index=None.
            point_item.setData(0, data.get('index'))
            if not is_source_only:
                point_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
                point_item.setCursor(Qt.CursorShape.PointingHandCursor)

            # Tooltip
            if is_source_only:
                point_item.setToolTip(
                    f"{data['name']}\nLat: {data['latitude']:.6f}\nLon: {data['longitude']:.6f}"
                )
            else:
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

        # Clear zoom FOV box when switching images
        self._last_visible_rect = None
        self.clear_zoom_fov_box()

        # Ensure compass stays in correct position
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

    def _update_point_appearances(self):
        """Update the visual appearance of all GPS points."""
        for i, item in enumerate(self.point_items):
            is_current = (i == self.current_image_index)
            if i < len(self.gps_data):
                data = self.gps_data[i]
                is_hidden = data.get('hidden', False)
                aoi_count = data.get('aoi_count', 0)
                has_flagged = data.get('has_flagged', False)
                is_source_only = data.get('is_source_only', False)
            else:
                is_hidden = False
                aoi_count = 0
                has_flagged = False
                is_source_only = False

            if is_current and not is_source_only:
                size, color, border_color, border_width, z_value = 12, self.aoi_color, QColor(0, 0, 0), 2, 20
            elif is_source_only:
                size, color, border_color, border_width, z_value = 4, QColor(140, 140, 140), QColor(140, 140, 140), 0, 6
            elif is_hidden:
                size, color, border_color, border_width, z_value = 6, QColor(200, 200, 200), QColor(150, 150, 150), 1, 8
            elif has_flagged:
                size, color, border_color, border_width, z_value = 8, QColor(255, 0, 0), QColor(0, 0, 0), 1, 15
            elif aoi_count > 0:
                size, color, border_color, border_width, z_value = 8, QColor(0, 100, 255), QColor(0, 0, 0), 1, 12
            else:
                size, color, border_color, border_width, z_value = 6, QColor(0, 255, 0), QColor(0, 0, 0), 1, 10

            item.setRect(-size / 2, -size / 2, size, size)
            item.setBrush(QBrush(color))
            item.setPen(QPen(border_color, border_width))
            item.setZValue(z_value)

    def get_image_bearing_lazy(self, image_path, calculated_bearing=None):
        """
        Extract bearing/yaw information from image (lazy loading).

        Args:
            image_path: Path to the image file
            calculated_bearing: Optional pre-computed bearing (e.g. from Wingtra CSV)

        Returns:
            float: Bearing in degrees (0-360), or None if not available
        """
        try:
            image_service = ImageService(image_path, '', calculated_bearing=calculated_bearing)
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

        # Ensure compass is in correct position after tile source change
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

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

        # Ensure compass is in correct position after fitting
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

    def zoom_in(self):
        """Zoom in by a factor."""
        self.scale(1.25, 1.25)
        self.zoom_scale *= 1.25
        self._check_tile_zoom_level()
        self.load_visible_tiles()
        # Ensure compass stays in correct position
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

    def zoom_out(self):
        """Zoom out by a factor."""
        self.scale(0.8, 0.8)
        self.zoom_scale *= 0.8
        self._check_tile_zoom_level()
        self.load_visible_tiles()
        # Ensure compass stays in correct position
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

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
        # Ensure compass stays in correct position after pan
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 0.85
        self.zoom_scale *= zoom_factor
        self.scale(zoom_factor, zoom_factor)

        # Defer tile zoom level check to avoid performance hits during rapid scrolling
        if hasattr(self, '_tile_zoom_timer'):
            self._tile_zoom_timer.stop()
        else:
            self._tile_zoom_timer = QTimer(self)
            self._tile_zoom_timer.setSingleShot(True)
            self._tile_zoom_timer.timeout.connect(self._deferred_tile_check)

        # Start a short timer to check tile zoom after scrolling stops
        self._tile_zoom_timer.start(150)  # Wait 150ms after last scroll

        # Still load visible tiles immediately for smooth experience
        self.load_visible_tiles()

        # Ensure compass stays in correct position
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

    def _deferred_tile_check(self):
        """Deferred tile zoom level check after scrolling stops."""
        self._check_tile_zoom_level()
        # Ensure compass is in correct position after zoom level changes
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

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
        self.scene.setSceneRect(-world_size / 2, -world_size / 2, world_size * 2, world_size * 2)

        # Re-anchor the POD overlay to the new zoom scale.
        self._position_pod_overlay()

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

        # Redraw zoom FOV box with updated scene coordinates
        if self._last_visible_rect is not None:
            self.update_zoom_fov_box(self._last_visible_rect)

        # Load new tiles
        self.load_visible_tiles()

        # Ensure compass stays in correct position after zoom level change
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

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
        if event.button() == Qt.MouseButton.RightButton:
            scene_pos = self.mapToScene(event.pos())
            lat, lon = self.scene_to_lat_lon(scene_pos.x(), scene_pos.y())
            self.gps_right_clicked.emit(lat, lon)
            event.accept()
            return

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

        copy_action = menu.addAction(self.tr("Copy Data"))
        copy_action.triggered.connect(self.copy_aoi_data)
        menu.exec(global_pos)

    def copy_aoi_data(self):
        """Copy AOI data to clipboard."""
        if not self.aoi_data:
            return

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

        # Ensure compass stays in correct position after rotation
        self._ensure_compass_created()
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

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

    def scrollContentsBy(self, dx, dy):
        """Handle scroll events (called for ALL scrolling including drag-to-pan)."""
        super().scrollContentsBy(dx, dy)
        # Reposition compass after any scroll
        if self.compass_container:
            self._position_compass()
            self.compass_container.raise_()

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
        self.aoi_marker = QGraphicsRectItem(-size / 2, -size / 2, size, size)
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

        # Ensure compass stays on top after adding marker
        if self.compass_container:
            self.compass_container.raise_()

    def clear_aoi_marker(self):
        """Remove the AOI marker from the map."""
        if self.aoi_marker and self.aoi_marker in self.scene.items():
            self.scene.removeItem(self.aoi_marker)
            self.aoi_marker = None
        self.aoi_data = None

    def _fov_flat_corners(self, corners_m, bearing, image_lat, image_lon):
        """Convert corners in meters (relative to image center) to scene points using flat projection."""
        bearing_rad = math.radians(-bearing)
        cos_b = math.cos(bearing_rad)
        sin_b = math.sin(bearing_rad)
        earth_radius = 6371000
        corners_scene = []
        for x, y in corners_m:
            x_rot = x * cos_b - y * sin_b
            y_rot = x * sin_b + y * cos_b
            delta_lat = y_rot / earth_radius * (180 / math.pi)
            delta_lon = x_rot / (earth_radius * math.cos(math.radians(image_lat))) * (180 / math.pi)
            corner_lat = image_lat + delta_lat
            corner_lon = image_lon + delta_lon
            corners_scene.append(self.lat_lon_to_scene(corner_lat, corner_lon))
        return corners_scene

    def _generate_edge_pixels(self, corners_px, gsd_m, terrain_res_m=38.0):
        """Generate pixel coords along rect edges, spaced at terrain resolution.

        Args:
            corners_px: List of 4 corner tuples [(x,y), ...] in order: TL, TR, BR, BL
            gsd_m: Ground sampling distance in meters/pixel
            terrain_res_m: Terrain DEM resolution in meters

        Returns:
            List of (x, y) pixel coordinate tuples tracing all 4 edges
        """
        step_px = max(1.0, terrain_res_m / gsd_m) if gsd_m > 0 else 1.0
        edge_pixels = []
        for i in range(4):
            x0, y0 = corners_px[i]
            x1, y1 = corners_px[(i + 1) % 4]
            dx, dy = x1 - x0, y1 - y0
            edge_len = math.sqrt(dx * dx + dy * dy)
            num_steps = max(1, int(edge_len / step_px))
            for s in range(num_steps):
                t = s / num_steps
                edge_pixels.append((x0 + t * dx, y0 + t * dy))
        return edge_pixels

    def _use_terrain_enabled(self):
        """Read the viewer's terrain-elevation preference (default True).

        Walks the same parent chain used for custom_agl_altitude_ft so the
        FOV/zoom boxes honor the UseTerrainElevation setting like the AOI
        pipeline does.
        """
        try:
            parent_viewer = self.parent().parent()
            return bool(getattr(parent_viewer, 'use_terrain_elevation', True))
        except Exception:
            return True

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
            # Manually aligned image: draw the user-placed corners directly,
            # bypassing GSD / ray-cast / terrain entirely.
            refinement = current_data.get('fov_alignment')
            if (refinement and refinement.get('corners')
                    and validate_alignment(refinement['corners'])):
                corners_scene = [
                    self.lat_lon_to_scene(lat, lon)
                    for lat, lon in refinement['corners']
                ]
                self._fov_cache = {
                    'mode': 'refined',
                    'fov_alignment': refinement,
                    'width': current_data.get('width'),
                    'height': current_data.get('height'),
                }
                self._add_fov_polygon(corners_scene, "Image FOV\nProjection: User-aligned")
                return

            # Get custom altitude if available
            custom_alt = None
            if hasattr(self, 'parent') and hasattr(self.parent(), 'parent'):
                parent_viewer = self.parent().parent()
                if hasattr(parent_viewer, 'custom_agl_altitude_ft'):
                    custom_alt = parent_viewer.custom_agl_altitude_ft
                    if custom_alt and custom_alt <= 0:
                        custom_alt = None

            # Get bearing and per-image AGL from the image dict if available
            calculated_bearing = current_data.get('bearing')
            wingtra_agl_ft = current_data.get('wingtra_agl_ft')

            image_service = ImageService(image_path, '', calculated_bearing=calculated_bearing)

            # Get GSD - use per-image AGL (e.g. Wingtra) if available, else custom
            if wingtra_agl_ft is not None:
                custom_alt = wingtra_agl_ft
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

            # Attempt terrain-adjusted raycast for accurate FOV
            intrinsics = image_service.get_camera_intrinsics()
            pitch = image_service.get_camera_pitch()
            if pitch is None:
                pitch = -90  # Assume nadir
            yaw = image_service.get_camera_yaw()
            if yaw is None:
                yaw = bearing
            # Pull gimbal roll for fixed-wing rigs (WALDO ±22.5°). Skip the
            # DJI "inverted gimbal" >90° pattern; get_camera_yaw already
            # compensates that by flipping yaw 180°.
            roll = image_service.get_gimbal_roll() or 0.0
            if abs(roll) > 90.0:
                roll = 0.0

            # Match AOIService.estimate_aoi_gps altitude determination exactly
            if custom_alt and custom_alt > 0:
                reported_agl = custom_alt / 3.28084  # ft to m
            else:
                reported_agl = image_service.get_relative_altitude('m') or 0
            absolute_alt = image_service.get_asl_altitude('m')

            effective_agl = reported_agl
            terrain_elevation = None
            geoid_undulation = None
            drone_absolute_elev = None

            terrain_service = None
            if self._use_terrain_enabled():
                try:
                    terrain_service = _get_terrain_service()
                except Exception:
                    pass

            # AOIService special case: unreliable low RelativeAltitude
            if (reported_agl < 10 and absolute_alt and absolute_alt > 50
                    and terrain_service and terrain_service.enabled):
                geoid_undulation = terrain_service.get_geoid_undulation(image_lat, image_lon)
                drone_ortho = absolute_alt - (geoid_undulation or 0)
                drone_terrain = terrain_service.get_elevation(image_lat, image_lon)
                if drone_terrain.source == 'terrain' and drone_terrain.elevation_m is not None:
                    terrain_based_agl = drone_ortho - drone_terrain.elevation_m
                    if terrain_based_agl > 5:
                        effective_agl = terrain_based_agl
                        terrain_elevation = drone_terrain.elevation_m

            # Compute drone absolute elevation for per-corner terrain refinement
            if absolute_alt is not None and terrain_service and terrain_service.enabled:
                if geoid_undulation is None:
                    geoid_undulation = terrain_service.get_geoid_undulation(image_lat, image_lon)
                drone_absolute_elev = absolute_alt - (geoid_undulation or 0)

            if effective_agl <= 0:
                effective_agl = reported_agl if reported_agl > 0 else 1.0

            # Cache FOV parameters for zoom FOV reuse
            has_raycast = False
            cx = width / 2.0
            cy = height / 2.0
            self._fov_cache = {
                'gsd_m': gsd_m,
                'width': width,
                'height': height,
                'bearing': bearing,
                'image_lat': image_lat,
                'image_lon': image_lon,
                'has_raycast': False,
            }

            # Try raycast approach with camera intrinsics
            corners_scene = []
            terrain_res_m = 38.0
            if intrinsics and effective_agl > 0:
                focal_mm = intrinsics['focal_length_mm']
                sensor_w_mm = intrinsics['sensor_width_mm']
                sensor_h_mm = intrinsics['sensor_height_mm']

                # Sample along all edges at terrain DEM resolution
                rect_corners = [(0, 0), (width, 0), (width, height), (0, height)]
                edge_pixels = self._generate_edge_pixels(rect_corners, gsd_m, terrain_res_m)

                # Raycast all edge points with drone-position AGL
                edge_gps = []
                raycast_ok = True
                for u, v in edge_pixels:
                    result = AOIService._calculate_ground_position(
                        image_lat, image_lon, u, v, cx, cy,
                        width, height, focal_mm, sensor_w_mm, sensor_h_mm,
                        effective_agl, pitch, yaw, roll
                    )
                    if result is None:
                        raycast_ok = False
                        break
                    edge_gps.append(result)

                # Iterative per-point terrain refinement (matches AOIService convergence)
                if raycast_ok and terrain_service and terrain_service.enabled and drone_absolute_elev:
                    for i, (pt_lat, pt_lon) in enumerate(edge_gps):
                        try:
                            cur_lat, cur_lon = pt_lat, pt_lon
                            for _iteration in range(3):
                                pt_terrain = terrain_service.get_elevation(cur_lat, cur_lon)
                                if pt_terrain.source != 'terrain' or pt_terrain.elevation_m is None:
                                    break
                                if pt_terrain.resolution_m:
                                    terrain_res_m = pt_terrain.resolution_m
                                pt_agl = max(1.0, drone_absolute_elev - pt_terrain.elevation_m)
                                u, v = edge_pixels[i]
                                refined = AOIService._calculate_ground_position(
                                    image_lat, image_lon, u, v, cx, cy,
                                    width, height, focal_mm, sensor_w_mm, sensor_h_mm,
                                    pt_agl, pitch, yaw, roll
                                )
                                if refined is None:
                                    break
                                new_lat, new_lon = refined
                                dlat_m = (new_lat - cur_lat) * 111320
                                dlon_m = (new_lon - cur_lon) * 111320 * math.cos(math.radians(cur_lat))
                                displacement = math.sqrt(dlat_m * dlat_m + dlon_m * dlon_m)
                                cur_lat, cur_lon = new_lat, new_lon
                                if displacement < 1.0:
                                    break
                            edge_gps[i] = (cur_lat, cur_lon)
                        except Exception:
                            pass

                if raycast_ok:
                    corners_scene = [self.lat_lon_to_scene(lat, lon) for lat, lon in edge_gps]
                    has_raycast = True
                    self._fov_cache.update({
                        'has_raycast': True,
                        'focal_mm': focal_mm,
                        'sensor_w_mm': sensor_w_mm,
                        'sensor_h_mm': sensor_h_mm,
                        'cx': cx,
                        'cy': cy,
                        'pitch': pitch,
                        'yaw': yaw,
                        'roll': roll,
                        'effective_agl': effective_agl,
                        'drone_absolute_elev': drone_absolute_elev,
                        'terrain_res_m': terrain_res_m,
                    })

            # Fallback to flat GSD approach
            if not has_raycast:
                corners_scene = self._fov_flat_corners(
                    [(- width_m / 2, -height_m / 2),
                     (width_m / 2, -height_m / 2),
                     (width_m / 2, height_m / 2),
                     (-width_m / 2, height_m / 2)],
                    bearing, image_lat, image_lon
                )

            # Build the tooltip and create the FOV polygon.
            tooltip = "Image FOV\n"
            tooltip += f"Dimensions: {width}x{height} pixels\n"
            tooltip += f"Ground Coverage: {width_m:.1f}m x {height_m:.1f}m\n"
            tooltip += f"GSD: {gsd_cm:.2f} cm/px\n"
            tooltip += f"Bearing: {bearing:.1f}°"
            if terrain_elevation is not None:
                tooltip += f"\nTerrain: {terrain_elevation:.0f}m ASL"
                tooltip += f"\nEffective AGL: {effective_agl:.1f}m"
            if has_raycast:
                tooltip += "\nProjection: Raycast"

            self._add_fov_polygon(corners_scene, tooltip)

        except Exception as e:
            self.logger.error(f"update_fov_box failed: {e}")

    def clear_fov_box(self):
        """Remove the FOV box from the map."""
        if self.fov_box and self.fov_box in self.scene.items():
            self.scene.removeItem(self.fov_box)
            self.fov_box = None

    def _add_fov_polygon(self, corners_scene, tooltip):
        """Create the FOV box from scene-space corners and add it to the scene.

        Args:
            corners_scene: List of QPointF polygon corners in scene coordinates.
            tooltip: Tooltip text for the FOV box.
        """
        self.fov_box = QGraphicsPolygonItem(QPolygonF(corners_scene))
        pen = QPen(QColor(0, 150, 255), 2)
        pen.setCosmetic(True)
        self.fov_box.setPen(pen)
        self.fov_box.setBrush(QBrush(QColor(0, 150, 255, 30)))
        self.fov_box.setZValue(5)
        self.fov_box.setToolTip(tooltip)
        self.scene.addItem(self.fov_box)
        if self.compass_container:
            self.compass_container.raise_()

    def _add_zoom_fov_polygon(self, corners_scene, tooltip):
        """Create the zoom FOV box from scene-space corners and add it.

        Args:
            corners_scene: List of QPointF polygon corners in scene coordinates.
            tooltip: Tooltip text for the zoom FOV box.
        """
        self.zoom_fov_box = QGraphicsPolygonItem(QPolygonF(corners_scene))
        pen = QPen(QColor(255, 50, 50), 2)
        pen.setCosmetic(True)
        self.zoom_fov_box.setPen(pen)
        self.zoom_fov_box.setBrush(QBrush(QColor(255, 50, 50, 30)))
        self.zoom_fov_box.setZValue(6)
        self.zoom_fov_box.setToolTip(tooltip)
        self.scene.addItem(self.zoom_fov_box)
        if self.compass_container:
            self.compass_container.raise_()

    def update_zoom_fov_box(self, visible_rect):
        """
        Update the zoom Field of View box showing the visible portion of the image.

        Args:
            visible_rect: QRectF in image pixel coordinates of the currently visible area,
                          or None to clear.
        """
        self._last_visible_rect = visible_rect

        # Clear existing zoom FOV box
        if self.zoom_fov_box and self.zoom_fov_box in self.scene.items():
            self.scene.removeItem(self.zoom_fov_box)
            self.zoom_fov_box = None

        if visible_rect is None or self._fov_cache is None:
            return

        try:
            cache = self._fov_cache

            # Manually aligned image: map the visible rect through the homography.
            if cache.get('mode') == 'refined':
                refinement = cache.get('fov_alignment')
                width = cache.get('width')
                height = cache.get('height')
                if not (refinement and width and height):
                    return
                # Skip when the visible rect covers the whole image.
                if (visible_rect.left() <= 1 and visible_rect.top() <= 1
                        and visible_rect.right() >= width - 1
                        and visible_rect.bottom() >= height - 1):
                    return
                homography = FovHomography(
                    refinement['corners'], width, height,
                    refinement.get('tie_points')
                )
                # Clamp the visible rect to the image bounds. The zoom box
                # shows a portion of the image, so it can never extend past
                # the image edges (i.e. outside the FOV box).
                left = max(0.0, min(visible_rect.left(), float(width)))
                right = max(0.0, min(visible_rect.right(), float(width)))
                top = max(0.0, min(visible_rect.top(), float(height)))
                bottom = max(0.0, min(visible_rect.bottom(), float(height)))
                rect_px = [
                    (left, top), (right, top), (right, bottom), (left, bottom),
                ]
                corners_scene = [
                    self.lat_lon_to_scene(*homography.pixel_to_gps(u, v))
                    for u, v in rect_px
                ]
                self._add_zoom_fov_polygon(corners_scene, self.tr("Zoom FOV"))
                return

            gsd_m = cache['gsd_m']
            imgWidth = cache['width']
            imgHeight = cache['height']
            bearing = cache['bearing']
            image_lat = cache['image_lat']
            image_lon = cache['image_lon']

            # Don't draw if visible rect covers the full image
            if (visible_rect.left() <= 1 and visible_rect.top() <= 1
                    and visible_rect.right() >= imgWidth - 1
                    and visible_rect.bottom() >= imgHeight - 1):
                return

            rect_corners = [
                (visible_rect.left(), visible_rect.top()),
                (visible_rect.right(), visible_rect.top()),
                (visible_rect.right(), visible_rect.bottom()),
                (visible_rect.left(), visible_rect.bottom()),
            ]

            # Use raycast if available
            corners_scene = None
            if cache.get('has_raycast'):
                terrain_res = cache.get('terrain_res_m', 38.0)
                edge_pixels = self._generate_edge_pixels(rect_corners, gsd_m, terrain_res)

                edge_gps = []
                raycast_ok = True
                roll_cached = cache.get('roll', 0.0)
                for u, v in edge_pixels:
                    result = AOIService._calculate_ground_position(
                        image_lat, image_lon, u, v,
                        cache['cx'], cache['cy'],
                        imgWidth, imgHeight,
                        cache['focal_mm'], cache['sensor_w_mm'], cache['sensor_h_mm'],
                        cache['effective_agl'], cache['pitch'], cache['yaw'],
                        roll_cached
                    )
                    if result is None:
                        raycast_ok = False
                        break
                    edge_gps.append(result)

                # Iterative per-point terrain refinement (matches AOIService convergence)
                drone_abs = cache.get('drone_absolute_elev')
                if raycast_ok and drone_abs and self._use_terrain_enabled():
                    try:
                        terrain_service = _get_terrain_service()
                        if terrain_service and terrain_service.enabled:
                            for i, (pt_lat, pt_lon) in enumerate(edge_gps):
                                try:
                                    cur_lat, cur_lon = pt_lat, pt_lon
                                    for _iteration in range(3):
                                        # offline_only: this runs on the GUI thread for every
                                        # viewChanged (pan/zoom). A cache miss must fall back to
                                        # flat instantly rather than block on a network download
                                        # (10 s timeout x fallback URLs x edge points). Footprint
                                        # tiles are already prefetched by update_fov_box on load.
                                        pt_terrain = terrain_service.get_elevation(
                                            cur_lat, cur_lon, offline_only=True
                                        )
                                        if pt_terrain.source != 'terrain' or pt_terrain.elevation_m is None:
                                            break
                                        pt_agl = max(1.0, drone_abs - pt_terrain.elevation_m)
                                        u, v = edge_pixels[i]
                                        refined = AOIService._calculate_ground_position(
                                            image_lat, image_lon, u, v,
                                            cache['cx'], cache['cy'],
                                            imgWidth, imgHeight,
                                            cache['focal_mm'], cache['sensor_w_mm'], cache['sensor_h_mm'],
                                            pt_agl, cache['pitch'], cache['yaw'],
                                            roll_cached
                                        )
                                        if refined is None:
                                            break
                                        new_lat, new_lon = refined
                                        dlat_m = (new_lat - cur_lat) * 111320
                                        dlon_m = (new_lon - cur_lon) * 111320 * math.cos(math.radians(cur_lat))
                                        displacement = math.sqrt(dlat_m * dlat_m + dlon_m * dlon_m)
                                        cur_lat, cur_lon = new_lat, new_lon
                                        if displacement < 1.0:
                                            break
                                    edge_gps[i] = (cur_lat, cur_lon)
                                except Exception:
                                    pass
                    except Exception:
                        pass

                if raycast_ok:
                    corners_scene = [self.lat_lon_to_scene(lat, lon) for lat, lon in edge_gps]

            # Fallback to flat GSD projection
            if corners_scene is None:
                halfW = imgWidth / 2.0
                halfH = imgHeight / 2.0
                corners_m = []
                for px, py in rect_corners:
                    x_m = (px - halfW) * gsd_m
                    y_m = (halfH - py) * gsd_m  # Negate: image Y-down → ground Y-north
                    corners_m.append((x_m, y_m))
                corners_scene = self._fov_flat_corners(corners_m, bearing, image_lat, image_lon)

            # Create the zoom FOV polygon.
            visW_m = visible_rect.width() * gsd_m
            visH_m = visible_rect.height() * gsd_m
            tooltip = self.tr("Zoom FOV") + "\n"
            tooltip += f"{self.tr('Visible')}: {visible_rect.width():.0f}x{visible_rect.height():.0f} px\n"
            tooltip += f"{self.tr('Ground')}: {visW_m:.1f}m x {visH_m:.1f}m"
            self._add_zoom_fov_polygon(corners_scene, tooltip)

        except Exception:
            pass

    def clear_zoom_fov_box(self):
        """Remove the zoom FOV box from the map."""
        if self.zoom_fov_box and self.zoom_fov_box in self.scene.items():
            self.scene.removeItem(self.zoom_fov_box)
            self.zoom_fov_box = None
