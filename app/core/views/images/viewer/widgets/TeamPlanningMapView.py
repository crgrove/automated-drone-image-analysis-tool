"""
TeamPlanningMapView - Map widget for team-based AOI assignment.

Extends the tile-map pattern from GPSMapView to display flagged AOI positions
with multi-selection (click and rubber-band) and team-color coding.
"""

import math
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsPixmapItem, QGraphicsRectItem, QApplication,
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QTimer
from PySide6.QtGui import (
    QPen, QBrush, QColor, QWheelEvent, QMouseEvent,
    QPainter, QFont,
)
from core.views.images.viewer.widgets.MapTileLoader import MapTileLoader
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin

# Unassigned marker colour
UNASSIGNED_COLOR = QColor(180, 180, 180)
SELECTION_HIGHLIGHT = QColor(255, 255, 255, 200)


class TeamPlanningMapView(TranslationMixin, QGraphicsView):
    """Interactive map for selecting and assigning AOIs to field teams.

    Signals:
        aoi_clicked(int): Emitted when a single AOI marker is clicked (aoi uid).
        selection_changed(list[int]): Emitted after rubber-band or ctrl-click
            changes the set of selected AOI uids.
    """

    aoi_clicked = Signal(int)
    selection_changed = Signal(list)

    # ------------------------------------------------------------------ init
    def __init__(self, parent=None, offline_only=False):
        super().__init__(parent)
        self.logger = LoggerService()
        self.offline_only = bool(offline_only)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tile_loader = MapTileLoader(offline_only=self.offline_only)
        self.tile_loader.tile_loaded.connect(self._on_tile_loaded)

        self.tile_items: dict = {}
        self.current_zoom = 15
        self.zoom_scale = 1.0
        self._min_zoom_scale = 0.0  # set after first fit

        self._aoi_data: list[dict] = []
        self._markers: list[QGraphicsEllipseItem] = []
        self._selected_uids: set[int] = set()

        self.min_lat = self.max_lat = self.min_lon = self.max_lon = None

        self._tile_timer = QTimer(self)
        self._tile_timer.setSingleShot(True)
        self._tile_timer.timeout.connect(self._load_visible_tiles)

        self._rubber_origin: QPointF | None = None
        self._rubber_rect_item: QGraphicsRectItem | None = None
        self._select_mode = False

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)

    # --------------------------------------------------------- public API
    def set_aoi_data(self, aoi_list: list[dict]):
        """Load AOI positions onto the map.

        Each dict must contain: uid (int), latitude, longitude,
        and optionally team_color (hex str).
        """
        self._aoi_data = list(aoi_list)
        self._selected_uids.clear()
        self._rebuild_map()

    def update_marker_colors(self, uid_to_color: dict[int, str]):
        """Repaint markers according to new team-color mapping."""
        for marker in self._markers:
            uid = marker.data(0)
            hex_color = uid_to_color.get(uid)
            color = QColor(hex_color) if hex_color else UNASSIGNED_COLOR
            marker.setBrush(QBrush(color))
        self._apply_selection_visuals()

    def highlight_team(self, team_name: str | None, aoi_data: list[dict]):
        """Visually emphasise AOIs belonging to *team_name*.

        Non-matching markers are drawn smaller; matching ones larger.
        Pass None to reset all to normal size.
        """
        for marker in self._markers:
            uid = marker.data(0)
            entry = next((a for a in aoi_data if a['uid'] == uid), None)
            if entry is None:
                continue
            belongs = (team_name is not None and entry.get('team') == team_name)
            size = 14 if belongs else (10 if team_name is not None else 10)
            marker.setRect(-size / 2, -size / 2, size, size)

    def get_selected_uids(self) -> list[int]:
        return list(self._selected_uids)

    def clear_selection(self):
        self._selected_uids.clear()
        self._apply_selection_visuals()
        self.selection_changed.emit([])

    def set_select_mode(self, enabled: bool):
        """Toggle rubber-band selection vs pan mode."""
        self._select_mode = enabled
        if enabled:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.unsetCursor()

    # --------------------------------------------------------- map building
    def _rebuild_map(self):
        self.scene.clear()
        self._markers.clear()
        self.tile_items.clear()
        self._current_tile_source = getattr(self.tile_loader, 'tile_source', 'map')

        if not self._aoi_data:
            return

        lats = [a['latitude'] for a in self._aoi_data]
        lons = [a['longitude'] for a in self._aoi_data]
        self.min_lat, self.max_lat = min(lats), max(lats)
        self.min_lon, self.max_lon = min(lons), max(lons)

        lat_range = self.max_lat - self.min_lat or 0.01
        lon_range = self.max_lon - self.min_lon or 0.01
        self.min_lat -= lat_range * 0.15
        self.max_lat += lat_range * 0.15
        self.min_lon -= lon_range * 0.15
        self.max_lon += lon_range * 0.15

        self.current_zoom = self._calc_zoom()

        # Unrestricted panning: set scene rect much larger than tile space
        n = 2.0 ** self.current_zoom
        full = n * 256
        self.scene.setSceneRect(-full, -full, full * 3, full * 3)

        self._draw_aoi_markers()
        self._load_visible_tiles()
        QTimer.singleShot(50, self.fit_all_points)

    MIN_TILE_ZOOM = 7

    def _calc_zoom(self) -> int:
        if self.min_lat is None:
            return 15
        lat_range = self.max_lat - self.min_lat
        lon_range = self.max_lon - self.min_lon
        for z in range(18, self.MIN_TILE_ZOOM - 1, -1):
            n = 2.0 ** z
            tile_lat = 360.0 / n
            tile_lon = 360.0 / n
            if lat_range < tile_lat * 4 and lon_range < tile_lon * 4:
                return z
        return self.MIN_TILE_ZOOM

    def _lat_lon_to_scene(self, lat: float, lon: float) -> QPointF:
        n = 2.0 ** self.current_zoom
        x = (lon + 180.0) / 360.0 * n * 256
        lat_rad = math.radians(lat)
        y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n * 256
        return QPointF(x, y)

    def _scene_to_lat_lon(self, sx: float, sy: float):
        n = 2.0 ** self.current_zoom
        lon = sx / (n * 256) * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * sy / (n * 256))))
        return math.degrees(lat_rad), lon

    def _draw_aoi_markers(self):
        for entry in self._aoi_data:
            pt = self._lat_lon_to_scene(entry['latitude'], entry['longitude'])
            hex_c = entry.get('team_color')
            color = QColor(hex_c) if hex_c else UNASSIGNED_COLOR
            size = 10
            marker = QGraphicsEllipseItem(-size / 2, -size / 2, size, size)
            marker.setPos(pt)
            marker.setBrush(QBrush(color))
            marker.setPen(QPen(QColor(0, 0, 0), 1.5))
            marker.setZValue(20)
            marker.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
            marker.setCursor(Qt.CursorShape.PointingHandCursor)
            marker.setData(0, entry['uid'])

            tooltip = f"{entry.get('image_name', '')}\n"
            tooltip += f"Lat: {entry['latitude']:.6f}\nLon: {entry['longitude']:.6f}"
            if entry.get('team'):
                tooltip += f"\nTeam: {entry['team']}"
            marker.setToolTip(tooltip)

            self.scene.addItem(marker)
            self._markers.append(marker)

    # ------------------------------------------------------ tile management
    def _load_visible_tiles(self):
        if self.min_lat is None:
            return
        vp = self.mapToScene(self.viewport().rect()).boundingRect()
        zoom = self.current_zoom
        n = 2.0 ** zoom
        current_src = getattr(self, '_current_tile_source', 'map')

        min_tx = max(0, int(vp.left() / 256))
        max_tx = min(int(n) - 1, int(vp.right() / 256))
        min_ty = max(0, int(vp.top() / 256))
        max_ty = min(int(n) - 1, int(vp.bottom() / 256))

        for tx in range(min_tx, max_tx + 1):
            for ty in range(min_ty, max_ty + 1):
                key = (tx, ty, zoom, current_src)
                if key not in self.tile_items:
                    self.tile_loader.load_tile(tx, ty, zoom)

    def _on_tile_loaded(self, x, y, zoom, pixmap):
        if zoom != self.current_zoom:
            return
        current_src = getattr(self, '_current_tile_source', 'map')
        if getattr(self.tile_loader, 'tile_source', 'map') != current_src:
            return
        key = (x, y, zoom, current_src)
        if key in self.tile_items:
            return
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(x * 256, y * 256)
        item.setZValue(0)
        self.scene.addItem(item)
        self.tile_items[key] = item

    # ------------------------------------------------------ interaction
    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            factor = 1.15
        else:
            factor = 0.85
            if self._min_zoom_scale > 0 and self.zoom_scale * factor < self._min_zoom_scale:
                event.accept()
                return
        self.zoom_scale *= factor
        self.scale(factor, factor)
        self._tile_timer.start(200)

    def mousePressEvent(self, event: QMouseEvent):
        if self._select_mode and event.button() == Qt.MouseButton.LeftButton:
            self._rubber_origin = self.mapToScene(event.pos())
            self._rubber_rect_item = QGraphicsRectItem()
            self._rubber_rect_item.setPen(QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine))
            self._rubber_rect_item.setBrush(QBrush(QColor(0, 120, 215, 40)))
            self._rubber_rect_item.setZValue(100)
            self.scene.addItem(self._rubber_rect_item)
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            click_pos = event.pos()
            for marker in self._markers:
                view_pos = self.mapFromScene(marker.pos())
                dx = click_pos.x() - view_pos.x()
                dy = click_pos.y() - view_pos.y()
                if math.sqrt(dx * dx + dy * dy) <= 12:
                    uid = marker.data(0)
                    ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
                    if ctrl:
                        if uid in self._selected_uids:
                            self._selected_uids.discard(uid)
                        else:
                            self._selected_uids.add(uid)
                    else:
                        self._selected_uids = {uid}
                    self._apply_selection_visuals()
                    self.selection_changed.emit(list(self._selected_uids))
                    self.aoi_clicked.emit(uid)
                    event.accept()
                    return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._select_mode and self._rubber_origin is not None:
            current = self.mapToScene(event.pos())
            rect = QRectF(self._rubber_origin, current).normalized()
            self._rubber_rect_item.setRect(rect)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._select_mode and self._rubber_origin is not None and event.button() == Qt.MouseButton.LeftButton:
            if self._rubber_rect_item:
                rect = self._rubber_rect_item.rect()
                self.scene.removeItem(self._rubber_rect_item)
                self._rubber_rect_item = None

                ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
                if not ctrl:
                    self._selected_uids.clear()

                for marker in self._markers:
                    if rect.contains(marker.pos()):
                        self._selected_uids.add(marker.data(0))

                self._apply_selection_visuals()
                self.selection_changed.emit(list(self._selected_uids))

            self._rubber_origin = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # -------------------------------------------------- selection visuals
    def _apply_selection_visuals(self):
        for marker in self._markers:
            uid = marker.data(0)
            pen_color = SELECTION_HIGHLIGHT if uid in self._selected_uids else QColor(0, 0, 0)
            pen_width = 3.0 if uid in self._selected_uids else 1.5
            marker.setPen(QPen(pen_color, pen_width))

    # -------------------------------------------------- fit helpers
    def fit_all_points(self):
        if not self._aoi_data:
            return
        pts = [self._lat_lon_to_scene(a['latitude'], a['longitude']) for a in self._aoi_data]
        xs = [p.x() for p in pts]
        ys = [p.y() for p in pts]
        margin = 50
        rect = QRectF(min(xs) - margin, min(ys) - margin,
                      max(xs) - min(xs) + margin * 2,
                      max(ys) - min(ys) + margin * 2)
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        self.zoom_scale = self.transform().m11()
        # The fit-all scale is the minimum allowed zoom-out
        if self._min_zoom_scale <= 0:
            self._min_zoom_scale = self.zoom_scale * 0.5
        self._tile_timer.start(100)

    def zoom_in(self):
        self.scale(1.3, 1.3)
        self.zoom_scale *= 1.3
        self._tile_timer.start(200)

    def zoom_out(self):
        if self._min_zoom_scale > 0 and self.zoom_scale * 0.7 < self._min_zoom_scale:
            return
        self.scale(0.7, 0.7)
        self.zoom_scale *= 0.7
        self._tile_timer.start(200)

    def set_offline_mode(self, offline_only: bool):
        self.offline_only = bool(offline_only)
        self.tile_loader.offline_only = self.offline_only

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self._tile_timer.start(100)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._tile_timer.start(100)

    def set_tile_source(self, source: str):
        # Disconnect so abort-triggered callbacks never reach us
        self.tile_loader.tile_loaded.disconnect(self._on_tile_loaded)

        for reply in list(self.tile_loader.active_downloads.values()):
            reply.abort()
        self.tile_loader.active_downloads.clear()

        # Flush any queued signals from the aborted replies
        QApplication.processEvents()

        self.tile_loader.tile_source = source
        self._current_tile_source = source

        # Remove all tile pixmaps from scene (markers have zValue > 0)
        for item in [i for i in self.scene.items()
                     if isinstance(i, QGraphicsPixmapItem)]:
            self.scene.removeItem(item)
        self.tile_items.clear()

        # Reconnect and load fresh tiles for the new source
        self.tile_loader.tile_loaded.connect(self._on_tile_loaded)
        self._load_visible_tiles()
