"""
AlignImageView - interactive canvas for the Align Image dialog.

Three layers share one scene:
- the drone image (back), geo-anchored at its estimated footprint, rotatable;
- map/satellite tiles (middle), semi-transparent;
- the FOV overlay quad with four draggable corner handles, plus optional
  draggable tie points (front).

Scene coordinates are local Web-Mercator pixels offset so the footprint sits
near the origin - this keeps every coordinate small and avoids the precision
problems of raw global Web-Mercator values. The tile detail level is chosen
dynamically from the view scale, so zooming in loads finer tiles. The base
layer can be toggled between satellite imagery and a street map.
"""

import math

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsPolygonItem,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem, QGraphicsItem, QMenu
)
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF, QPainter, QPixmap

from core.views.images.viewer.widgets.MapTileLoader import MapTileLoader
from core.services.LoggerService import LoggerService


class _AlignHandle(QGraphicsEllipseItem):
    """A draggable circular handle that reports moves through a callback.

    Handles ignore the view transform so they keep a constant screen size at
    any zoom; their scene position is the source of truth for a control point.
    An optional short text label is drawn as a tag above the circle so the two
    ends of a tie point can be told apart at a glance.
    """

    def __init__(self, radius, fill_color, outline_color, label=None):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        # Callback invoked (no args) whenever this handle is moved.
        self.on_move = None
        # Back-reference set when the handle belongs to a tie point.
        self.tie_point = None
        # Optional text tag drawn above the circle (e.g. "IMAGE" / "MAP").
        self.label = label
        self._label_bg = QColor(30, 30, 30, 235)
        self._label_fg = fill_color

        self.setBrush(QBrush(fill_color))
        self.setPen(QPen(outline_color, 2))
        self.setZValue(10)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.on_move is not None:
                self.on_move()
        return super().itemChange(change, value)

    def boundingRect(self):
        """Expand the bounds to include the text tag drawn above the circle."""
        rect = super().boundingRect()
        if self.label:
            return rect.adjusted(-44.0, -24.0, 44.0, 0.0)
        return rect

    def paint(self, painter, option, widget=None):
        """Draw the circle, then the label tag above it when one is set."""
        super().paint(painter, option, widget)
        if not self.label:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        font = painter.font()
        font.setPointSizeF(7.5)
        font.setBold(True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        tag_width = metrics.horizontalAdvance(self.label) + 8.0
        tag_height = metrics.height() + 3.0
        # The tag sits just above the circle, horizontally centred on it.
        tag = QRectF(-tag_width / 2.0,
                     self.rect().top() - tag_height - 3.0,
                     tag_width, tag_height)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._label_bg))
        painter.drawRoundedRect(tag, 3.0, 3.0)
        painter.setPen(QPen(self._label_fg))
        painter.drawText(tag, Qt.AlignmentFlag.AlignCenter, self.label)
        painter.restore()


class TiePoint:
    """A drone-pixel <-> map-GPS correspondence: two handles and a line.

    The source handle marks a feature in the drone image; the target handle
    marks the same feature on the map. The drone pixel is derived from the
    source handle's scene position via the drone image transform.
    """

    def __init__(self, source_handle, target_handle, line):
        self.source_handle = source_handle
        self.target_handle = target_handle
        self.line = line
        source_handle.tie_point = self
        target_handle.tie_point = self

    def update_line(self):
        """Redraw the dashed line connecting the two handles."""
        source = self.source_handle.pos()
        target = self.target_handle.pos()
        self.line.setLine(source.x(), source.y(), target.x(), target.y())

    def items(self):
        """Return all scene items owned by this tie point."""
        return (self.line, self.source_handle, self.target_handle)


class AlignImageView(QGraphicsView):
    """Interactive canvas hosting the drone image, map tiles and FOV overlay."""

    # Per-corner handle outline colours in TL, TR, BR, BL order.
    CORNER_COLORS = (
        QColor(255, 80, 80),    # TL
        QColor(80, 220, 80),    # TR
        QColor(80, 160, 255),   # BR
        QColor(255, 200, 50),   # BL
    )
    HANDLE_RADIUS = 8
    TIE_RADIUS = 7
    FOV_COLOR = QColor(0, 150, 255)
    TIE_SOURCE_COLOR = QColor(255, 0, 200)
    TIE_TARGET_COLOR = QColor(255, 230, 0)

    # Scene units are Web-Mercator pixels at this zoom, offset to the footprint
    # so coordinates stay small. Tiles load at a separate, dynamic detail level.
    REFERENCE_ZOOM = 20
    MIN_TILE_ZOOM = 3
    MAX_TILE_ZOOM_SATELLITE = 20
    MAX_TILE_ZOOM_MAP = 19

    def __init__(self, parent=None, offline_only=False):
        super().__init__(parent)
        self.logger = LoggerService()
        self.offline_only = bool(offline_only)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._tile_source = 'satellite'
        self._max_tile_zoom = self.MAX_TILE_ZOOM_SATELLITE
        self.tile_loader = MapTileLoader(offline_only=self.offline_only)
        self.tile_loader.set_tile_source(self._tile_source)
        self.tile_loader.tile_loaded.connect(self._on_tile_loaded)

        # Local-coordinate origin (absolute Web-Mercator pixels at REFERENCE_ZOOM
        # of the footprint centre); set in load().
        self._scene_origin = (0.0, 0.0)

        # Dynamic tile detail level; corrected from the view scale on first show.
        self.tile_zoom = 16
        self.tile_items = {}          # (x, y) -> QGraphicsPixmapItem (current zoom)
        self._pixmap_cache = {}       # (source, zoom, x, y) -> QPixmap
        self._tile_opacity = 1.0

        self.drone_item = None
        self.fov_polygon = None
        self.corner_handles = []      # four _AlignHandle, TL TR BR BL
        self.corner_markers = []      # four QGraphicsRectItem on the image corners
        self.tie_points = []          # list[TiePoint]

        self._footprint_rect = None   # QRectF of the estimated footprint
        self._fitted = False

        # Metadata estimate, remembered so Reset can restore it: the camera
        # heading orients the photo, the corners size and centre the footprint.
        self._estimated_corners = []
        self._estimate_rotation = 0.0

        # Debounced tile loading after pan.
        self._tile_timer = QTimer(self)
        self._tile_timer.setSingleShot(True)
        self._tile_timer.timeout.connect(self._load_visible_tiles)
        # Debounced tile-detail re-evaluation after zooming.
        self._zoom_timer = QTimer(self)
        self._zoom_timer.setSingleShot(True)
        self._zoom_timer.timeout.connect(self._update_tile_zoom)

        self.horizontalScrollBar().valueChanged.connect(self._request_tiles)
        self.verticalScrollBar().valueChanged.connect(self._request_tiles)

    # --- Local Web Mercator coordinate conversion ---

    def _abs_web_mercator(self, lat, lon):
        """Return absolute Web-Mercator pixel coordinates at REFERENCE_ZOOM."""
        world_size = 256 * (2 ** self.REFERENCE_ZOOM)
        x = (lon + 180.0) / 360.0 * world_size
        lat_rad = math.radians(lat)
        mer_y = math.log(math.tan(lat_rad / 2 + math.pi / 4))
        y = (1 - mer_y / math.pi) / 2 * world_size
        return x, y

    def lat_lon_to_scene(self, lat, lon):
        """Convert GPS coordinates to local scene coordinates."""
        x, y = self._abs_web_mercator(lat, lon)
        return QPointF(x - self._scene_origin[0], y - self._scene_origin[1])

    def scene_to_lat_lon(self, x, y):
        """Convert local scene coordinates back to GPS coordinates."""
        world_size = 256 * (2 ** self.REFERENCE_ZOOM)
        abs_x = x + self._scene_origin[0]
        abs_y = y + self._scene_origin[1]
        lon = abs_x / world_size * 360.0 - 180.0
        mer_y = (1 - abs_y * 2 / world_size) * math.pi
        mer_y = max(-10, min(10, mer_y))
        try:
            lat = math.degrees(math.atan(math.sinh(mer_y)))
        except (OverflowError, ValueError):
            lat = 85.0 if mer_y > 0 else -85.0
        return lat, lon

    # --- Scene construction ---

    def load(self, image_path, estimated_corners, bearing, saved_alignment=None):
        """Build the scene from a drone image and its starting alignment.

        Args:
            image_path (str): Path to the drone image.
            estimated_corners (list): Four (lat, lon) corner estimates, TL TR BR BL.
            bearing (float): Camera bearing in degrees (initial drone rotation).
            saved_alignment (dict): Optional previously saved alignment to resume.
        """
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.logger.error(f"AlignImageView: could not load image {image_path}")
            return
        img_w = pixmap.width()
        img_h = pixmap.height()

        if saved_alignment and saved_alignment.get('corners'):
            corners = list(saved_alignment['corners'])
            rotation = saved_alignment.get('rotation', 0.0)
            saved_ties = saved_alignment.get('tie_points') or []
            seed_from_image = False
        else:
            corners = list(estimated_corners)
            rotation = bearing or 0.0
            saved_ties = []
            seed_from_image = True

        # Remember the metadata estimate for Reset (see reset_to_estimate).
        self._estimated_corners = list(estimated_corners)
        self._estimate_rotation = bearing or 0.0

        # Local-coordinate origin: the footprint centre. Every scene coordinate
        # is then a small offset from it.
        center_lat = sum(c[0] for c in corners) / 4.0
        center_lon = sum(c[1] for c in corners) / 4.0
        self._scene_origin = self._abs_web_mercator(center_lat, center_lon)

        corner_scene = [self.lat_lon_to_scene(lat, lon) for lat, lon in corners]
        center = QPointF(
            sum(p.x() for p in corner_scene) / 4.0,
            sum(p.y() for p in corner_scene) / 4.0,
        )
        footprint_w = math.hypot(
            corner_scene[1].x() - corner_scene[0].x(),
            corner_scene[1].y() - corner_scene[0].y(),
        )

        # Drone image: scale to the footprint width, rotate, centre on the footprint.
        self.drone_item = QGraphicsPixmapItem(pixmap)
        self.drone_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.drone_item.setTransformOriginPoint(img_w / 2.0, img_h / 2.0)
        self.drone_item.setZValue(-200)
        self.scene.addItem(self.drone_item)
        self._layout_drone_image(center, footprint_w, rotation)

        # FOV overlay quad.
        self.fov_polygon = QGraphicsPolygonItem(QPolygonF(corner_scene))
        fov_pen = QPen(self.FOV_COLOR, 2)
        fov_pen.setCosmetic(True)
        self.fov_polygon.setPen(fov_pen)
        self.fov_polygon.setBrush(QBrush(QColor(0, 150, 255, 40)))
        self.fov_polygon.setZValue(5)
        self.scene.addItem(self.fov_polygon)

        # Corner handles.
        for index, scene_point in enumerate(corner_scene):
            handle = _AlignHandle(self.HANDLE_RADIUS, QColor(255, 255, 255),
                                  self.CORNER_COLORS[index])
            handle.on_move = self._rebuild_fov_polygon
            handle.setPos(scene_point)
            self.scene.addItem(handle)
            self.corner_handles.append(handle)

        # Colour-matched markers on the drone image's own pixel corners, so the
        # user can see which corner of the photo each corner handle belongs to.
        self._create_corner_markers(img_w, img_h)

        # For a fresh estimate, seed the handles on the photo's own pixel corners
        # so the quad starts as the photo outline with each handle sitting on its
        # colour-matched corner square. (The metadata corner estimate uses a
        # different corner/winding convention, so seeding straight from it would
        # start the quad mirrored and rotated away from the photo.) A resumed
        # alignment keeps its saved corners exactly as placed.
        if seed_from_image:
            self._seed_handles_from_image()

        # Restore saved tie points.
        for tie in saved_ties:
            u, v, lat, lon = tie
            self._create_tie_point(
                self.drone_item.mapToScene(QPointF(u, v)),
                self.lat_lon_to_scene(lat, lon),
            )

        self._footprint_rect = QPolygonF(corner_scene).boundingRect()
        # Generous scrolling room around the footprint (coordinates stay small).
        margin = 100000.0
        self.scene.setSceneRect(
            self._footprint_rect.adjusted(-margin, -margin, margin, margin)
        )

    def _rebuild_fov_polygon(self):
        """Redraw the FOV quad from the current corner handle positions."""
        if self.fov_polygon and len(self.corner_handles) == 4:
            self.fov_polygon.setPolygon(
                QPolygonF([handle.pos() for handle in self.corner_handles])
            )

    def _layout_drone_image(self, center, footprint_w, rotation):
        """Scale, rotate and centre the drone image to fill a footprint.

        Args:
            center (QPointF): Footprint centre in scene coordinates.
            footprint_w (float): Footprint top-edge width in scene units; the
                image is scaled uniformly so its width matches it.
            rotation (float): Image rotation in degrees (the camera heading).
        """
        if self.drone_item is None:
            return
        pixmap = self.drone_item.pixmap()
        img_w = pixmap.width()
        img_h = pixmap.height()
        scale = footprint_w / img_w if img_w else 1.0
        self.drone_item.setScale(scale)
        self.drone_item.setRotation(rotation)
        self.drone_item.setPos(center.x() - img_w / 2.0, center.y() - img_h / 2.0)

    def _seed_handles_from_image(self):
        """Place the four corner handles on the drone image's own pixel corners.

        This makes the FOV quad start as the photo's outline, with each handle
        sitting exactly on its colour-matched corner square, so aligning is a
        matter of nudging corners rather than untangling a mirrored estimate.
        """
        if self.drone_item is None or len(self.corner_handles) != 4:
            return
        pixmap = self.drone_item.pixmap()
        w = float(pixmap.width())
        h = float(pixmap.height())
        pixel_corners = [(0.0, 0.0), (w, 0.0), (w, h), (0.0, h)]
        for handle, (px, py) in zip(self.corner_handles, pixel_corners):
            handle.setPos(self.drone_item.mapToScene(QPointF(px, py)))
        self._rebuild_fov_polygon()

    def _create_corner_markers(self, img_w, img_h):
        """Mark the drone image's four pixel corners with the handle colours.

        These small squares are pinned to the drone image (they rotate with
        it), so the user can tell which corner of the photo each colour-matched
        corner handle belongs to - the red handle goes where the red marked
        corner of the photo belongs, and so on.
        """
        pixel_corners = [(0.0, 0.0), (float(img_w), 0.0),
                         (float(img_w), float(img_h)), (0.0, float(img_h))]
        for index, (px, py) in enumerate(pixel_corners):
            half = 5.0
            marker = QGraphicsRectItem(-half, -half, 2 * half, 2 * half)
            marker.setBrush(QBrush(self.CORNER_COLORS[index]))
            marker.setPen(QPen(QColor(20, 20, 20), 1.5))
            marker.setZValue(8)
            marker.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
            marker.setPos(self.drone_item.mapToScene(QPointF(px, py)))
            self.scene.addItem(marker)
            self.corner_markers.append(marker)

    def _update_corner_markers(self):
        """Re-pin the corner markers to the drone image's pixel corners."""
        if self.drone_item is None or not self.corner_markers:
            return
        pixmap = self.drone_item.pixmap()
        pixel_corners = [
            (0.0, 0.0), (float(pixmap.width()), 0.0),
            (float(pixmap.width()), float(pixmap.height())),
            (0.0, float(pixmap.height())),
        ]
        for marker, (px, py) in zip(self.corner_markers, pixel_corners):
            marker.setPos(self.drone_item.mapToScene(QPointF(px, py)))

    # --- Tie points ---

    def _create_tie_point(self, source_scene_pos, target_scene_pos):
        """Create a tie point with handles at the given scene positions."""
        line = QGraphicsLineItem()
        line_pen = QPen(self.TIE_SOURCE_COLOR, 1, Qt.PenStyle.DashLine)
        line_pen.setCosmetic(True)
        line.setPen(line_pen)
        line.setZValue(9)
        self.scene.addItem(line)

        source = _AlignHandle(self.TIE_RADIUS, self.TIE_SOURCE_COLOR,
                              QColor(255, 255, 255), label=self.tr("IMAGE"))
        target = _AlignHandle(self.TIE_RADIUS, self.TIE_TARGET_COLOR,
                              QColor(60, 60, 60), label=self.tr("MAP"))
        self.scene.addItem(source)
        self.scene.addItem(target)
        source.setPos(source_scene_pos)
        target.setPos(target_scene_pos)

        tie = TiePoint(source, target, line)
        source.on_move = tie.update_line
        target.on_move = tie.update_line
        tie.update_line()
        self.tie_points.append(tie)
        return tie

    def add_tie_point(self):
        """Add a new tie point near the centre of the current view."""
        if self.drone_item is None:
            return
        center = self.mapToScene(self.viewport().rect().center())
        offset = 40.0 / max(self.transform().m11(), 1e-6)
        self._create_tie_point(
            QPointF(center.x() - offset, center.y()),
            QPointF(center.x() + offset, center.y()),
        )

    def remove_tie_point(self, tie):
        """Remove a tie point and its scene items."""
        if tie in self.tie_points:
            for item in tie.items():
                self.scene.removeItem(item)
            self.tie_points.remove(tie)

    # --- Public controls ---

    def set_tile_opacity(self, percent):
        """Set the map/satellite tile layer opacity (0-100)."""
        self._tile_opacity = max(0.0, min(1.0, percent / 100.0))
        for item in self.tile_items.values():
            item.setOpacity(self._tile_opacity)

    def set_fov_opacity(self, percent):
        """Set the FOV overlay opacity (0-100)."""
        if self.fov_polygon:
            self.fov_polygon.setOpacity(max(0.0, min(1.0, percent / 100.0)))

    def set_image_rotation(self, degrees):
        """Rotate the drone image; the FOV overlay rotates rigidly with it.

        The four corner handles and every tie-point source are pinned to their
        drone-image pixels, so rotating the image carries the whole overlay
        with it instead of leaving it behind.
        """
        if self.drone_item is None:
            return
        # Capture every overlay handle's drone-image pixel under the current transform.
        corner_pixels = [self.drone_item.mapFromScene(h.pos())
                         for h in self.corner_handles]
        tie_pixels = [self.drone_item.mapFromScene(t.source_handle.pos())
                      for t in self.tie_points]
        self.drone_item.setRotation(degrees)
        # Restore them to the same pixels under the new transform.
        for handle, pixel in zip(self.corner_handles, corner_pixels):
            handle.setPos(self.drone_item.mapToScene(pixel))
        for tie, pixel in zip(self.tie_points, tie_pixels):
            tie.source_handle.setPos(self.drone_item.mapToScene(pixel))
            tie.update_line()
        self._rebuild_fov_polygon()
        self._update_corner_markers()

    def set_tile_source(self, source):
        """Switch the base layer between 'satellite' and 'map' (street map)."""
        if source not in ('satellite', 'map') or source == self._tile_source:
            return
        self._tile_source = source
        self.tile_loader.set_tile_source(source)
        self._max_tile_zoom = (self.MAX_TILE_ZOOM_SATELLITE if source == 'satellite'
                               else self.MAX_TILE_ZOOM_MAP)
        self.tile_zoom = min(self.tile_zoom, self._max_tile_zoom)
        self._clear_tiles()
        self._load_visible_tiles()

    def get_rotation(self):
        """Return the current drone image rotation in degrees."""
        return self.drone_item.rotation() if self.drone_item else 0.0

    def get_corner_gps(self):
        """Return the four corner GPS coordinates (TL, TR, BR, BL)."""
        return [self.scene_to_lat_lon(h.pos().x(), h.pos().y())
                for h in self.corner_handles]

    def get_tie_points(self):
        """Return tie points as (u, v, lat, lon) tuples."""
        result = []
        for tie in self.tie_points:
            pixel = self.drone_item.mapFromScene(tie.source_handle.pos())
            lat, lon = self.scene_to_lat_lon(tie.target_handle.pos().x(),
                                             tie.target_handle.pos().y())
            result.append((pixel.x(), pixel.y(), lat, lon))
        return result

    def reset_to_estimate(self):
        """Restore the drone image and corners to the metadata estimate.

        Re-lays the photo on the estimated footprint at the camera heading,
        re-seeds the corner handles on the photo's pixel corners, and clears any
        tie points - the same starting state as a fresh (unsaved) alignment.
        """
        if self.drone_item is None or len(self._estimated_corners) != 4:
            return
        for tie in list(self.tie_points):
            self.remove_tie_point(tie)
        corner_scene = [self.lat_lon_to_scene(lat, lon)
                        for lat, lon in self._estimated_corners]
        center = QPointF(
            sum(p.x() for p in corner_scene) / 4.0,
            sum(p.y() for p in corner_scene) / 4.0,
        )
        footprint_w = math.hypot(
            corner_scene[1].x() - corner_scene[0].x(),
            corner_scene[1].y() - corner_scene[0].y(),
        )
        self._layout_drone_image(center, footprint_w, self._estimate_rotation)
        self._update_corner_markers()
        self._seed_handles_from_image()

    # --- Tile loading ---

    def _request_tiles(self):
        """Schedule a debounced tile refresh for the visible area."""
        self._tile_timer.start(80)

    def _clear_tiles(self):
        """Remove every tile item from the scene (pixmaps stay cached)."""
        for item in self.tile_items.values():
            self.scene.removeItem(item)
        self.tile_items.clear()

    def _update_tile_zoom(self):
        """Pick the tile detail level that matches the current view scale."""
        try:
            view_scale = self.transform().m11()
            if view_scale <= 0:
                return
            desired = round(self.REFERENCE_ZOOM + math.log2(view_scale))
            desired = max(self.MIN_TILE_ZOOM, min(self._max_tile_zoom, desired))
            if desired != self.tile_zoom:
                self.tile_zoom = desired
                self._clear_tiles()
            self._load_visible_tiles()
        except Exception as e:
            self.logger.error(f"AlignImageView: tile zoom update failed - {e}")

    def _place_tile(self, x_tile, y_tile, zoom, pixmap):
        """Create and position a tile item in the scene."""
        lat, lon = self.tile_loader.tile_to_lat_lon(x_tile, y_tile, zoom)
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(self.lat_lon_to_scene(lat, lon))
        item.setScale(2 ** (self.REFERENCE_ZOOM - zoom))
        item.setZValue(-100)
        item.setOpacity(self._tile_opacity)
        existing = self.tile_items.get((x_tile, y_tile))
        if existing is not None:
            self.scene.removeItem(existing)
        self.scene.addItem(item)
        self.tile_items[(x_tile, y_tile)] = item

    def _load_visible_tiles(self):
        """Load tiles at the current detail level covering the visible viewport."""
        if self._footprint_rect is None:
            return
        try:
            tile_span = 256 * (2 ** (self.REFERENCE_ZOOM - self.tile_zoom))
            view_rect = self.mapToScene(self.viewport().rect()).boundingRect()
            view_rect = view_rect.adjusted(-tile_span, -tile_span, tile_span, tile_span)

            max_lat, min_lon = self.scene_to_lat_lon(view_rect.left(), view_rect.top())
            min_lat, max_lon = self.scene_to_lat_lon(view_rect.right(), view_rect.bottom())

            min_x, max_y = self.tile_loader.lat_lon_to_tile(min_lat, min_lon, self.tile_zoom)
            max_x, min_y = self.tile_loader.lat_lon_to_tile(max_lat, max_lon, self.tile_zoom)

            limit = 2 ** self.tile_zoom - 1
            min_x = max(0, min_x)
            min_y = max(0, min_y)
            max_x = min(limit, max_x)
            max_y = min(limit, max_y)

            # Guard against requesting an unreasonable number of tiles.
            if (max_x - min_x + 1) * (max_y - min_y + 1) > 160:
                return

            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    if (x, y) in self.tile_items:
                        continue
                    cached = self._pixmap_cache.get((self._tile_source, self.tile_zoom, x, y))
                    if cached is not None:
                        self._place_tile(x, y, self.tile_zoom, cached)
                    else:
                        try:
                            self.tile_loader.load_tile(x, y, self.tile_zoom)
                        except Exception as e:
                            self.logger.error(f"AlignImageView: tile request failed - {e}")
        except Exception as e:
            self.logger.error(f"AlignImageView: loading visible tiles failed - {e}")

    def _on_tile_loaded(self, x_tile, y_tile, zoom, pixmap):
        """Cache a loaded tile and place it if it is for the current detail level."""
        try:
            self._pixmap_cache[(self._tile_source, zoom, x_tile, y_tile)] = pixmap
            if zoom == self.tile_zoom:
                self._place_tile(x_tile, y_tile, zoom, pixmap)
        except Exception as e:
            self.logger.error(f"AlignImageView: placing tile failed - {e}")

    # --- Events ---

    def wheelEvent(self, event):
        """Zoom the whole scene with the mouse wheel."""
        try:
            factor = 1.2 if event.angleDelta().y() > 0 else 1.0 / 1.2
            self.scale(factor, factor)
            # Re-evaluate the tile detail level once zooming settles.
            self._zoom_timer.start(150)
        except Exception as e:
            self.logger.error(f"AlignImageView: wheel zoom failed - {e}")

    def showEvent(self, event):
        """Fit the footprint into the viewport the first time the view shows."""
        super().showEvent(event)
        if not self._fitted and self._footprint_rect is not None:
            self._fitted = True
            margin = max(self._footprint_rect.width(),
                         self._footprint_rect.height()) * 0.4
            self.fitInView(
                self._footprint_rect.adjusted(-margin, -margin, margin, margin),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            self._update_tile_zoom()

    def contextMenuEvent(self, event):
        """Offer to remove a tie point when right-clicked on one of its handles."""
        item = self.itemAt(event.pos())
        tie = getattr(item, 'tie_point', None)
        if tie is not None:
            menu = QMenu(self)
            remove_action = menu.addAction(self.tr("Remove Tie Point"))
            if menu.exec(event.globalPos()) == remove_action:
                self.remove_tie_point(tie)
            event.accept()
            return
        super().contextMenuEvent(event)
