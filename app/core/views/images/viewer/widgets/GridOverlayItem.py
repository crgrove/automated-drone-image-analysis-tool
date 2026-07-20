"""
GridOverlayItem - On-image grid decoration for grid review mode.

Draws the review grid on top of the main image: thin cell borders, a
translucent green tint over cells already reviewed, and a highlighted
border around the cell the reviewer is currently sweeping. Inside the
active cell it can also draw an N x N focus guide (3x3 by default) in
the grid-line color — a purely visual aid that breaks the cell into
sub-regions so the reviewer scans each in turn before advancing. The
item lives in the image scene in image-pixel coordinates, so it pans
and zooms with the photo for free; line widths are cosmetic (constant
on-screen thickness at any zoom).

Cell geometry comes from GridReviewService.cell_rects so the painted
grid always matches the persisted reviewed-cell indices.
"""

from PySide6.QtCore import Qt, QRectF, QLineF
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import QGraphicsItem

from core.services.GridReviewService import GridReviewService


# Painting constants. Colors are chosen to read over both dark forest and
# bright snow imagery without obscuring detail underneath.
_GRID_LINE_COLOR = QColor(255, 255, 255, 140)
_GRID_LINE_WIDTH = 1            # cosmetic px
_REVIEWED_FILL = QColor(0, 200, 83, 50)
_CURRENT_BORDER_COLOR = QColor(255, 179, 0)   # amber
_CURRENT_BORDER_WIDTH = 3       # cosmetic px

# Focus-guide subdivisions per side inside the active cell (3 -> nine
# sub-regions). 1 disables the guide.
_DEFAULT_SUBDIVISIONS = 3


class GridOverlayItem(QGraphicsItem):
    """QGraphicsItem that paints the review grid over the main image."""

    def __init__(self):
        super().__init__()
        self._image_w = 0
        self._image_h = 0
        self._rects = []            # (x, y, w, h) per cell, row-major
        self._reviewed = set()      # row-major indices
        self._current_index = None  # row-major index or None
        self._subdivisions = _DEFAULT_SUBDIVISIONS  # focus guide per side
        # Below the selected-AOI decoration (1000) but above the pixmap
        # and the AOI circles.
        self.setZValue(950)
        # The grid is purely visual; never block panning, region zoom or
        # AOI clicks underneath it.
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.hide()

    def configure(self, image_w, image_h, rows, cols, reviewed, current_index,
                  subdivisions=_DEFAULT_SUBDIVISIONS):
        """Set the grid to draw.

        Args:
            image_w: Image width in pixels.
            image_h: Image height in pixels.
            rows: Number of grid rows.
            cols: Number of grid columns.
            reviewed: Set of reviewed row-major cell indices.
            current_index: Row-major index of the active cell, or None.
            subdivisions: Focus-guide subdivisions per side inside the
                active cell (3 -> nine sub-regions; 1 disables the guide).
        """
        self.prepareGeometryChange()
        self._image_w = int(image_w or 0)
        self._image_h = int(image_h or 0)
        if self._image_w > 0 and self._image_h > 0:
            self._rects = GridReviewService.cell_rects(self._image_w, self._image_h, rows, cols)
        else:
            self._rects = []
        self._reviewed = set(reviewed or ())
        self._current_index = current_index
        self._subdivisions = max(1, int(subdivisions))
        self.update()

    def set_reviewed(self, reviewed):
        """Update only the reviewed-cell set."""
        self._reviewed = set(reviewed or ())
        self.update()

    def set_current_index(self, current_index):
        """Update only the active-cell highlight."""
        self._current_index = current_index
        self.update()

    def set_subdivisions(self, subdivisions):
        """Update only the focus-guide subdivision count (1 disables it)."""
        self._subdivisions = max(1, int(subdivisions))
        self.update()

    def cell_rect(self, index):
        """Return the (x, y, w, h) rect of a cell, or None when out of range."""
        if index is None or not (0 <= index < len(self._rects)):
            return None
        return self._rects[index]

    def boundingRect(self):
        return QRectF(0, 0, self._image_w, self._image_h)

    def paint(self, painter, option, widget=None):
        if not self._rects:
            return

        # Reviewed-cell tint first so the grid lines stay visible above it.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(_REVIEWED_FILL))
        for index in self._reviewed:
            rect = self.cell_rect(index)
            if rect is not None:
                painter.drawRect(QRectF(*rect))

        # Cell borders.
        grid_pen = QPen(_GRID_LINE_COLOR)
        grid_pen.setWidth(_GRID_LINE_WIDTH)
        grid_pen.setCosmetic(True)
        painter.setPen(grid_pen)
        painter.setBrush(Qt.NoBrush)
        for rect in self._rects:
            painter.drawRect(QRectF(*rect))

        # Active cell: optional focus guide, then the highlight border.
        current_rect = self.cell_rect(self._current_index)
        if current_rect is not None:
            x, y, w, h = current_rect

            # Focus guide: an N x N subdivision drawn inside the active cell
            # in the grid-line color. Purely a visual scan aid, no state.
            if self._subdivisions > 1:
                painter.setPen(grid_pen)
                for k in range(1, self._subdivisions):
                    gx = x + (w * k / self._subdivisions)
                    painter.drawLine(QLineF(gx, y, gx, y + h))
                    gy = y + (h * k / self._subdivisions)
                    painter.drawLine(QLineF(x, gy, x + w, gy))

            current_pen = QPen(_CURRENT_BORDER_COLOR)
            current_pen.setWidth(_CURRENT_BORDER_WIDTH)
            current_pen.setCosmetic(True)
            painter.setPen(current_pen)
            painter.drawRect(QRectF(*current_rect))
