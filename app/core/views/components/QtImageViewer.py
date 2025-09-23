"""
QtImageViewer.py ‑ QGraphicsView‑based image viewer with zoom / pan / ROI.

This version (2.1.0 custom) guarantees that the signal

    zoomChanged(float current_zoom)

is emitted exactly once whenever the effective zoom factor changes – whether
through the mouse wheel, rubber‑band zoom, double‑click reset, programmatic
calls to setZoom/zoomToArea, widget resize, etc.
"""

import os.path
from PySide6.QtCore import (
    Qt, QRectF, QPoint, QPointF, Signal, QEvent, QSize
)
from PySide6.QtGui import (
    QImage, QPixmap, QPainterPath, QMouseEvent, QPainter, QPen, QCursor
)
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QFileDialog, QSizePolicy,
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem,
    QGraphicsLineItem, QGraphicsPolygonItem, QApplication
)

# Optional deps
try:
    import numpy as np
except ImportError:
    np = None
try:
    import qimage2ndarray
except ImportError:
    qimage2ndarray = None

__author__ = "Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>"
__version__ = "2.1.1 (fixed-lockup)"

# Constants for zoom limits
MIN_ZOOM_RECT_SIZE = 10.0  # Minimum size in pixels to prevent degenerate rectangles
MAX_ZOOM_STACK_DEPTH = 50  # Maximum zoom stack depth to prevent memory issues
MIN_ZOOM_FACTOR = 0.01  # Minimum zoom factor (1% of original)
MAX_ZOOM_FACTOR = 100.0  # Maximum zoom factor (100x original)


# --------------------------------------------------------------------------- #
#  QtImageViewer                                                              #
# --------------------------------------------------------------------------- #
class QtImageViewer(QGraphicsView):
    # -------------------------- public signals --------------------------- #
    leftMouseButtonPressed = Signal(float, float, object)
    leftMouseButtonReleased = Signal(float, float)
    middleMouseButtonPressed = Signal(float, float)
    middleMouseButtonReleased = Signal(float, float)
    rightMouseButtonPressed = Signal(float, float)
    rightMouseButtonReleased = Signal(float, float)
    leftMouseButtonDoubleClicked = Signal(float, float)
    rightMouseButtonDoubleClicked = Signal(float, float)

    viewChanged = Signal()          # any pan / zoom
    zoomChanged = Signal(float)     # **every** zoom change
    mousePositionOnImageChanged = Signal(QPoint)
    roiSelected = Signal(int)

    # ------------------------------ init --------------------------------- #
    def __init__(self, window, parent=None, center=None, thumbnail=False):
        super().__init__(parent)

        # ---- external reference (lets parent window hijack keyPressEvents)
        self.window = window

        # ---- scene / image
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self._image = None               # QGraphicsPixmapItem
        self._zoom = 1.0                # current view‑to‑scene scale
        self._recursion_guard = False   # Prevent infinite recursion
        self._is_destroyed = False      # Flag to prevent operations after destruction

        # ---- interaction state
        self.zoomStack = []          # list[QRectF] – manual zoom rectangles
        self._isZooming = False
        self._isPanning = False
        self._pixelPosition = QPoint()
        self._scenePosition = QPointF()

        # ---- config
        self.aspectRatioMode = Qt.KeepAspectRatio
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.regionZoomButton = Qt.LeftButton
        self.zoomOutButton = None
        self.panButton = Qt.RightButton
        self.wheelZoomFactor = 1.25

        self.canZoom = True
        self.canPan = True

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ---- misc
        self.center = center
        self.thumbnail = thumbnail

    def __del__(self):
        """Destructor to mark object as destroyed."""
        self._is_destroyed = True

    def closeEvent(self, event):
        """Handle close event to prevent operations after destruction."""
        self._is_destroyed = True
        super().closeEvent(event)

    def keyPressEvent(self, ev):
        plus_keys = {Qt.Key_Plus,  Qt.Key_Equal}
        minus_keys = {Qt.Key_Minus, Qt.Key_Underscore}

        # ---------------- zoom‑IN ----------------
        if ev.key() in plus_keys and not self.thumbnail:
            vp_pos = self.mapFromGlobal(QCursor.pos())
            scene_pos = (self.mapToScene(vp_pos)
                         if self.viewport().rect().contains(vp_pos)
                         else self.sceneRect().center())
            self._zoomInAtPos(scene_pos)
            ev.accept()
            return

        # ---------------- zoom‑OUT ---------------
        if ev.key() in minus_keys and not self.thumbnail:
            vp_pos = self.mapFromGlobal(QCursor.pos())
            scene_pos = (self.mapToScene(vp_pos)
                         if self.viewport().rect().contains(vp_pos)
                         else self.sceneRect().center())
            self._zoomOutAtPos(scene_pos)
            ev.accept()
            return

        # --------- fall back to original handling
        if self.window is not None:
            self.window.keyPressEvent(ev)
        else:
            super().keyPressEvent(ev)
    # ===================================================================== #
    #  Helpers                                                               #
    # ===================================================================== #

    def _emit_zoom_if_changed(self):
        """
        Re‑calculate effective zoom from the view’s transform matrix and
        emit zoomChanged(float) only if the value really changed.
        """
        if self._is_destroyed:
            return
        try:
            new_zoom = self.transform().m11()        # isotropic, so x==y
        except RuntimeError:
            self._is_destroyed = True
            return
        if abs(new_zoom - self._zoom) > 1e-6:
            self._zoom = new_zoom
            if not self._is_destroyed:
                self.zoomChanged.emit(self._zoom)

    def getZoom(self) -> float:
        """Current zoom factor (1.0 == image fits view in X)."""
        if self._is_destroyed:
            return 1.0
        return self._zoom

    def _safe_scene_rect(self):
        """Safely get scene rect, returning None if destroyed."""
        if self._is_destroyed:
            return None
        try:
            return self.sceneRect()
        except RuntimeError:
            self._is_destroyed = True
            return None

    def fitInView(self, rect, mode):
        """Override fitInView to emit viewChanged after the transformation completes."""
        if self._is_destroyed:
            return
            
        # Additional safety check before calling super()
        try:
            super().fitInView(rect, mode)
        except RuntimeError:
            # Widget was destroyed during the call
            self._is_destroyed = True
            return
            
        # Check again after super() call
        if self._is_destroyed:
            return
            
        # Now emit viewChanged after the view has been updated
        self._safe_emit_view_changed()

    def _safe_emit_view_changed(self):
        """Safely emit the viewChanged signal with proper error handling."""
        if not self._is_destroyed and hasattr(self, 'viewChanged') and self.viewChanged is not None:
            try:
                self.viewChanged.emit()
            except RuntimeError:
                # Widget was deleted during signal emission, ignore
                pass

    def _validate_zoom_rect(self, rect):
        """Validate and sanitize a zoom rectangle."""
        if self._is_destroyed or not rect or not rect.isValid():
            return None
            
        # Ensure minimum size
        if rect.width() < MIN_ZOOM_RECT_SIZE or rect.height() < MIN_ZOOM_RECT_SIZE:
            return None
            
        # Ensure it's within scene bounds
        scene_rect = self._safe_scene_rect()
        if not scene_rect or not scene_rect.isValid():
            return None
            
        # Intersect with scene
        rect = rect.intersected(scene_rect)
        
        # Check if intersection is still valid
        if not rect.isValid() or rect.width() < MIN_ZOOM_RECT_SIZE or rect.height() < MIN_ZOOM_RECT_SIZE:
            return None
            
        return rect

    def _cleanup_zoom_stack(self):
        """Clean up zoom stack by removing invalid entries."""
        if not self.zoomStack or self._is_destroyed:
            return
            
        # Remove invalid rectangles
        self.zoomStack = [r for r in self.zoomStack if self._validate_zoom_rect(r)]
        
        # Limit stack depth
        if len(self.zoomStack) > MAX_ZOOM_STACK_DEPTH:
            # Keep only the most recent entries
            self.zoomStack = self.zoomStack[-MAX_ZOOM_STACK_DEPTH:]

    # ===================================================================== #
    #  Image handling                                                        #
    # ===================================================================== #
    def hasImage(self):
        if self._is_destroyed:
            return False
        return self._image is not None

    def clearImage(self):
        if self._is_destroyed:
            return
        if self._image:
            self.scene.removeItem(self._image)
            self._image = None

    def pixmap(self):
        if self._is_destroyed:
            return None
        return self._image.pixmap() if self._image else None

    def image(self):
        if self._is_destroyed:
            return None
        return self._image.pixmap().toImage() if self._image else None

    def setImage(self, image):
        """Accept QPixmap, QImage or 2‑D numpy array."""
        if self._is_destroyed:
            return
        if isinstance(image, QPixmap):
            pixmap = image
        elif isinstance(image, QImage):
            pixmap = QPixmap.fromImage(image)
        elif (np is not None) and isinstance(image, np.ndarray):
            if qimage2ndarray is not None:
                qimg = qimage2ndarray.array2qimage(image, True)
            else:                           # manual 8‑bit grayscale fallback
                im = image.astype(np.float32)
                im -= im.min()
                im /= im.max() if im.max() else 1
                im *= 255
                im = im.clip(0, 255).astype(np.uint8)
                h, w = im.shape
                qimg = QImage(im.tobytes(), w, h, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimg)
        else:
            raise TypeError("setImage expects QPixmap / QImage / ndarray.")

        if self._image:
            self._image.setPixmap(pixmap)
        else:
            self._image = self.scene.addPixmap(pixmap)

        self.setSceneRect(QRectF(pixmap.rect()))
        if not self._is_destroyed:
            self.updateViewer()

    def open(self, path=None):
        if self._is_destroyed:
            return
        if path is None:
            path, _ = QFileDialog.getOpenFileName(self, "Open image")
        if path and os.path.isfile(path):
            self.setImage(QImage(path))

    # ===================================================================== #
    #  Core viewer logic                                                     #
    # ===================================================================== #
    def updateViewer(self):
        """Apply current zoom stack or fit whole image, then emit zoom."""
        if not self.hasImage() or self._recursion_guard or self._is_destroyed:
            return
            
        try:
            self._recursion_guard = True
            
            # Clean up zoom stack first
            self._cleanup_zoom_stack()
            
            # Check if still valid after cleanup
            if self._is_destroyed:
                return
            
            if self.zoomStack:
                last_rect = self.zoomStack[-1]
                if self._validate_zoom_rect(last_rect):
                    self.fitInView(last_rect, self.aspectRatioMode)
                else:
                    # Invalid rect, reset zoom
                    self.zoomStack.clear()
                    scene_rect = self._safe_scene_rect()
                    if scene_rect and not self._is_destroyed:
                        self.fitInView(scene_rect, self.aspectRatioMode)
            else:
                if self.thumbnail:
                    scene_rect = self._safe_scene_rect()
                    if scene_rect and not self._is_destroyed:
                        self.fitInView(scene_rect, self.aspectRatioMode)

            # Final check before emitting
            if not self._is_destroyed:
                self._emit_zoom_if_changed()
            
        finally:
            self._recursion_guard = False

    # --------------------- programmatic zoom helpers --------------------- #
    def setZoom(self, scale: float):
        """Zoom around the image centre to *scale*."""
        if scale <= 0 or not self.hasImage() or self._recursion_guard or self._is_destroyed:
            return
            
        # Clamp scale to reasonable limits
        scale = max(MIN_ZOOM_FACTOR, min(MAX_ZOOM_FACTOR, scale))
        
        self.clearZoom()
        scene_rect = self._safe_scene_rect()
        if not scene_rect:
            return
        self.zoomStack.append(scene_rect)
        zr = QRectF(self.zoomStack[-1])
        c = zr.center()
        new_width = zr.width() / scale
        new_height = zr.height() / scale
        
        # Check minimum size
        if new_width < MIN_ZOOM_RECT_SIZE or new_height < MIN_ZOOM_RECT_SIZE:
            self.zoomStack.clear()
            return
            
        zr.setWidth(new_width)
        zr.setHeight(new_height)
        zr.moveCenter(c)
        
        validated_rect = self._validate_zoom_rect(zr)
        if validated_rect:
            self.zoomStack[-1] = validated_rect
            self.updateViewer()
        else:
            self.zoomStack.clear()

    def zoomToArea(self, center_xy, scale):
        if not self.hasImage() or self._recursion_guard or self._is_destroyed:
            return
            
        # Clamp scale
        scale = max(MIN_ZOOM_FACTOR, min(MAX_ZOOM_FACTOR, scale))
        
        self.clearZoom()
        scene_rect = self._safe_scene_rect()
        if not scene_rect:
            return
        self.zoomStack.append(scene_rect)
        zr = QRectF(self.zoomStack[-1])
        new_width = zr.width() / scale
        new_height = zr.height() / scale
        
        # Check minimum size
        if new_width < MIN_ZOOM_RECT_SIZE or new_height < MIN_ZOOM_RECT_SIZE:
            self.zoomStack.clear()
            return
            
        zr.setWidth(new_width)
        zr.setHeight(new_height)
        zr.moveCenter(QPointF(*center_xy))
        
        validated_rect = self._validate_zoom_rect(zr)
        if validated_rect:
            self.zoomStack[-1] = validated_rect
            self.updateViewer()
        else:
            self.zoomStack.clear()

    def _zoomInAtPos(self, scene_pos, factor=None):
        """Zoom in so that *scene_pos* stays centred on screen."""
        if not self.canZoom or self.thumbnail or not self.hasImage() or self._is_destroyed:
            return
        factor = factor or self.wheelZoomFactor or 1.25

        # Start a fresh zoom‐stack level if necessary
        if not self.zoomStack:
            self.zoomStack.append(self.sceneRect())
        elif len(self.zoomStack) > 1:
            self.zoomStack[:] = self.zoomStack[-1:]

        zr = QRectF(self.zoomStack[-1])  # Make a copy of current zoom rect
        new_width = zr.width() / factor
        new_height = zr.height() / factor
        
        # Check minimum size
        if new_width < MIN_ZOOM_RECT_SIZE or new_height < MIN_ZOOM_RECT_SIZE:
            return
            
        zr.setWidth(new_width)
        zr.setHeight(new_height)
        zr.moveCenter(scene_pos)        # keep cursor position centred
        
        validated_rect = self._validate_zoom_rect(zr)
        if validated_rect:
            self.zoomStack[-1] = validated_rect
        else:
            return

        self.updateViewer()
        self._safe_emit_view_changed()

    # ------------------------------------------------------------- #
    #  zoom helper: zoom‑out while keeping scene_pos centred         #
    # ------------------------------------------------------------- #
    def _zoomOutAtPos(self, scene_pos, factor=None):
        """Zoom out so *scene_pos* stays centred on screen."""
        if not self.canZoom or self.thumbnail or not self.hasImage() or self._is_destroyed:
            return
        factor = factor or self.wheelZoomFactor or 1.25

        # Get scene_rect once at the start
        scene_rect = self._safe_scene_rect()
        if not scene_rect:
            return

        if not self.zoomStack:
            self.resetZoom()
            # Already at full‑view → nothing more to zoom out
            return

        if len(self.zoomStack) > 1:
            self.zoomStack[:] = self.zoomStack[-1:]        # keep only current

        zr = QRectF(self.zoomStack[-1])  # Make a copy
        zr.setWidth(zr.width() * factor)
        zr.setHeight(zr.height() * factor)
        zr.moveCenter(scene_pos)
        
        validated_rect = self._validate_zoom_rect(zr)
        
        if not validated_rect or validated_rect.contains(scene_rect):
            # We're back to full view
            self.zoomStack.clear()
        else:
            self.zoomStack[-1] = validated_rect

        self.updateViewer()
        if not self._is_destroyed:
            self._safe_emit_view_changed()

    def resetZoom(self):
        if self._is_destroyed:
            return
        self.clearZoom()
        if self.hasImage():
            # Ensure widget has a valid size before fitting
            if self.width() <= 0 or self.height() <= 0:
                return
            scene_rect = self._safe_scene_rect()
            if scene_rect:
                self.fitInView(scene_rect, self.aspectRatioMode)
                self._emit_zoom_if_changed()

    def clearZoom(self):
        if self._is_destroyed:
            return
        if self.zoomStack:
            self.zoomStack.clear()
            self.updateViewer()
            if not self._is_destroyed:
                self._safe_emit_view_changed()

    # ===================================================================== #
    #  Qt events that might change zoom                                      #
    # ===================================================================== #
    def resizeEvent(self, ev):
        try:
            super().resizeEvent(ev)
        except RuntimeError:
            self._is_destroyed = True
            return
        if not self._is_destroyed:
            self.updateViewer()                       # recompute & emit

    def showEvent(self, ev):
        try:
            super().showEvent(ev)
        except RuntimeError:
            self._is_destroyed = True
            return
        if not self._is_destroyed:
            self.resetZoom()

    # -------------------------- wheel zoom ------------------------------ #
    def wheelEvent(self, ev):
        if self.thumbnail or self.wheelZoomFactor in (None, 1) or not self.hasImage() or self._is_destroyed:
            return super().wheelEvent(ev)

        zoom_in = ev.angleDelta().y() > 0
        cursor_scene_pos = self.mapToScene(ev.position().toPoint())
        factor = self.wheelZoomFactor if zoom_in else 1 / self.wheelZoomFactor

        # Ensure zoom stack is initialized
        if not self.zoomStack:
            scene_rect = self._safe_scene_rect()
            if not scene_rect:
                return
            self.zoomStack.append(scene_rect)

        current_zr = self.zoomStack[-1]
        
        # Calculate cursor position ratios
        cursor_ratio_x = (cursor_scene_pos.x() - current_zr.left()) / current_zr.width()
        cursor_ratio_y = (cursor_scene_pos.y() - current_zr.top()) / current_zr.height()

        new_width = current_zr.width() / factor
        new_height = current_zr.height() / factor

        # Clamp new dimensions to prevent extremely small sizes
        new_width = max(new_width, MIN_ZOOM_RECT_SIZE)
        new_height = max(new_height, MIN_ZOOM_RECT_SIZE)

        new_left = cursor_scene_pos.x() - cursor_ratio_x * new_width
        new_top = cursor_scene_pos.y() - cursor_ratio_y * new_height

        scene_rect = self._safe_scene_rect()
        if not scene_rect:
            return
        new_zr = QRectF(new_left, new_top, new_width, new_height).intersected(scene_rect)

        # Check if zoom-out reaches original view
        if not zoom_in and (new_zr == scene_rect or new_zr.contains(scene_rect)):
            self.resetZoom()
            ev.accept()
            return

        # Ensure zoom rect is valid
        if new_zr.isValid():
            self.zoomStack[-1] = new_zr
            self.updateViewer()
            if not self._is_destroyed:
                self._safe_emit_view_changed()
        else:
            self.resetZoom()

        ev.accept()

    # -------------------------------------------------------------------- #
    #  Everything below (mousePressEvent, ROIs, etc.) is identical to the  #
    #  original file, only whitespace touched so it fits here.             #
    # -------------------------------------------------------------------- #
    # ------------------------- mousePressEvent -------------------------- #
    def mousePressEvent(self, ev):
        if self._is_destroyed:
            return
        dummyMods = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
        if ev.modifiers() & dummyMods:
            super().mousePressEvent(ev)
            ev.accept()
            return

        # ------------- region zoom start
        if (self.regionZoomButton and ev.button() == self.regionZoomButton and self.canZoom):
            self._pixelPosition = ev.position().toPoint()
            self.setDragMode(QGraphicsView.RubberBandDrag)
            super().mousePressEvent(ev)
            self._isZooming = True
            ev.accept()
            return

        # ------------- zoom‑out click
        if (self.zoomOutButton and ev.button() == self.zoomOutButton and self.canZoom):
            if self.zoomStack:
                self.zoomStack.pop()
                self.updateViewer()
                if not self._is_destroyed:
                    self._safe_emit_view_changed()
            ev.accept()
            return

        # ------------- pan start
        if (self.panButton and ev.button() == self.panButton and self.canPan):
            self._pixelPosition = ev.position().toPoint()
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            if self.panButton == Qt.LeftButton:
                super().mousePressEvent(ev)
            else:  # fake left‑button drag
                self.viewport().setCursor(Qt.ClosedHandCursor)
                fakeMods = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
                fakeEv = QMouseEvent(QEvent.MouseButtonPress, ev.position(),
                                     Qt.LeftButton, ev.buttons(), fakeMods)
                self.mousePressEvent(fakeEv)
            self._scenePosition = self.mapToScene(self.viewport().rect()).boundingRect().topLeft()
            self._isPanning = True
            ev.accept()
            return

        scenePos = self.mapToScene(ev.position().toPoint())
        if ev.button() == Qt.LeftButton:
            if not self._is_destroyed:
                self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y(), self)
        elif ev.button() == Qt.MiddleButton:
            if not self._is_destroyed:
                self.middleMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif ev.button() == Qt.RightButton:
            if not self._is_destroyed:
                self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())

        super().mousePressEvent(ev)

    # ----------------------- mouseReleaseEvent -------------------------- #
    def mouseReleaseEvent(self, ev):
        if self._is_destroyed:
            return
        dummyMods = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
        if ev.modifiers() & dummyMods:
            super().mouseReleaseEvent(ev)
            ev.accept()
            return

        # ---- finish region zoom
        if (self.regionZoomButton and ev.button() == self.regionZoomButton and self.canZoom):
            super().mouseReleaseEvent(ev)
            scene_rect = self._safe_scene_rect()
            if not scene_rect:
                return
            zoomRect = self.scene.selectionArea().boundingRect().intersected(scene_rect)
            self.scene.setSelectionArea(QPainterPath())
            self.setDragMode(QGraphicsView.NoDrag)

            # tiny rubber‑band → treat as click
            if max(abs(ev.position().x()-self._pixelPosition.x()),
                   abs(ev.position().y()-self._pixelPosition.y())) <= 3:
                pass
            else:
                validated_rect = self._validate_zoom_rect(zoomRect)
                if validated_rect and validated_rect != scene_rect:
                    self.zoomStack.append(validated_rect)
                    self._cleanup_zoom_stack()
                    self.updateViewer()
                    if not self._is_destroyed:
                        self._safe_emit_view_changed()
            self._isZooming = False
            ev.accept()
            return

        # ---- finish panning
        if (self.panButton and ev.button() == self.panButton and self.canPan):
            if self.panButton == Qt.LeftButton:
                super().mouseReleaseEvent(ev)
            else:
                self.viewport().setCursor(Qt.ArrowCursor)
                fakeMods = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
                fakeEv = QMouseEvent(QEvent.MouseButtonRelease, ev.position(),
                                     Qt.LeftButton, ev.buttons(), fakeMods)
                self.mouseReleaseEvent(fakeEv)
            self.setDragMode(QGraphicsView.NoDrag)
            if self.zoomStack:
                currentView = self.mapToScene(self.viewport().rect()).boundingRect()
                delta = currentView.topLeft() - self._scenePosition
                self.zoomStack[-1].translate(delta)
                validated_rect = self._validate_zoom_rect(self.zoomStack[-1])
                if validated_rect:
                    self.zoomStack[-1] = validated_rect
                else:
                    self.zoomStack.pop()
                self._cleanup_zoom_stack()
                if not self._is_destroyed:
                    self._safe_emit_view_changed()
            self._isPanning = False
            ev.accept()
            return

        scenePos = self.mapToScene(ev.position().toPoint())
        if ev.button() == Qt.LeftButton:
            if not self._is_destroyed:
                self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif ev.button() == Qt.MiddleButton:
            if not self._is_destroyed:
                self.middleMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif ev.button() == Qt.RightButton:
            if not self._is_destroyed:
                self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

        super().mouseReleaseEvent(ev)

    # ----------------------- mouseDoubleClickEvent ---------------------- #
    def mouseDoubleClickEvent(self, ev):
        if self._is_destroyed:
            return
        if (self.zoomOutButton and ev.button() == self.zoomOutButton and self.canZoom):
            self.resetZoom()
            ev.accept()
            return

        scenePos = self.mapToScene(ev.position().toPoint())
        if ev.button() == Qt.LeftButton:
            self.resetZoom()
            if not self._is_destroyed:
                self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif ev.button() == Qt.RightButton:
            if not self._is_destroyed:
                self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())

        super().mouseDoubleClickEvent(ev)

    # ------------------------- mouseMoveEvent --------------------------- #
    def mouseMoveEvent(self, ev):
        if self._is_destroyed:
            return
        if self._isPanning:
            super().mouseMoveEvent(ev)
            if self.zoomStack:
                currentView = self.mapToScene(self.viewport().rect()).boundingRect()
                delta = currentView.topLeft() - self._scenePosition
                self._scenePosition = currentView.topLeft()
                self.zoomStack[-1].translate(delta)
                scene_rect = self._safe_scene_rect()
                if scene_rect:
                    self.zoomStack[-1] = self.zoomStack[-1].intersected(scene_rect)
                    self.updateViewer()
                    if not self._is_destroyed:
                        self._safe_emit_view_changed()

        scenePos = self.mapToScene(ev.position().toPoint())
        scene_rect = self._safe_scene_rect()
        if scene_rect and scene_rect.contains(scenePos):
            x = int(round(scenePos.x() - 0.5))
            y = int(round(scenePos.y() - 0.5))
            if not self._is_destroyed:
                self.mousePositionOnImageChanged.emit(QPoint(x, y))
        else:
            if not self._is_destroyed:
                self.mousePositionOnImageChanged.emit(QPoint(-1, -1))

        super().mouseMoveEvent(ev)

    # ------------------------- cursor helpers --------------------------- #
    def enterEvent(self, ev):
        if self._is_destroyed:
            return
        if not self.thumbnail:
            self.setCursor(Qt.CrossCursor)

    def leaveEvent(self, ev):
        if self._is_destroyed:
            return
        self.setCursor(Qt.ArrowCursor)

    # ===================================================================== #
    #  ROI helpers                                                           #
    # ===================================================================== #
    def addROIs(self, rois):
        if self._is_destroyed:
            return
        for roi in rois:
            self.scene.addItem(roi)
            self.ROIs.append(roi)

    def deleteROIs(self, rois):
        if self._is_destroyed:
            return
        for roi in rois:
            self.scene.removeItem(roi)
            self.ROIs.remove(roi)
            del roi

    def clearROIs(self):
        if self._is_destroyed:
            return
        for roi in self.ROIs:
            self.scene.removeItem(roi)
        self.ROIs.clear()

    def roiClicked(self, roi):
        if self._is_destroyed:
            return
        try:
            idx = self.ROIs.index(roi)
            if not self._is_destroyed:
                self.roiSelected.emit(idx)
        except ValueError:
            pass

    def setROIsAreMovable(self, movable: bool):
        if self._is_destroyed:
            return
        flag = QGraphicsItem.ItemIsMovable
        for roi in self.ROIs:
            roi.setFlag(flag, movable)

    def addSpots(self, xy_iterable, radius):
        if self._is_destroyed:
            return
        for x, y in xy_iterable:
            spot = EllipseROI(self)
            spot.setRect(x - radius, y - radius, 2*radius, 2*radius)
            self.scene.addItem(spot)
            self.ROIs.append(spot)

    # -------------------------------------------------------------------- #
    #  ROI item classes (unchanged)                                         #
    # -------------------------------------------------------------------- #


class _BaseROIItem:
    def __init__(self, pen_color, viewer):
        super().__init__()
        self._viewer = viewer
        pen = QPen(pen_color)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if ev.button() == Qt.LeftButton and not getattr(self._viewer, '_is_destroyed', True):
            self._viewer.roiClicked(self)


class EllipseROI(QGraphicsEllipseItem, _BaseROIItem):
    def __init__(self, viewer):
        QGraphicsEllipseItem.__init__(self)
        _BaseROIItem.__init__(self, Qt.yellow, viewer)


class RectROI(QGraphicsRectItem, _BaseROIItem):
    def __init__(self, viewer):
        QGraphicsRectItem.__init__(self)
        _BaseROIItem.__init__(self, Qt.yellow, viewer)


class LineROI(QGraphicsLineItem, _BaseROIItem):
    def __init__(self, viewer):
        QGraphicsLineItem.__init__(self)
        _BaseROIItem.__init__(self, Qt.yellow, viewer)


class PolygonROI(QGraphicsPolygonItem, _BaseROIItem):
    def __init__(self, viewer):
        QGraphicsPolygonItem.__init__(self)
        _BaseROIItem.__init__(self, Qt.yellow, viewer)
