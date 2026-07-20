"""
ThermalHistogramChart - Interactive thermal histogram bar chart widget.
"""

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class ThermalHistogramChart(QWidget):
    """Draw an interactive thermal bar chart with anomaly overlays and hover tracking."""

    hoveredRangeChanged = Signal(object)
    zoomRangeSelected = Signal(float, float)
    zoomResetRequested = Signal()

    MIN_ZOOM_DRAG_PIXELS = 12
    WHEEL_ZOOM_FACTOR = 1.2
    MIN_AOI_BAR_HEIGHT = 3.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumHeight(240)

        self._histogram_data = None
        self._selection_min = None
        self._selection_max = None
        self._selection_wrap = False
        self._hovered_index = None
        self._view_min = None
        self._view_max = None
        self._zoom_drag_start_x = None
        self._zoom_drag_current_x = None
        self._show_aoi_only = False
        self._empty_state_text = None

    def set_histogram_data(self, histogram_data):
        """Load histogram data and reset transient state."""
        self._histogram_data = histogram_data
        self._hovered_index = None

        if histogram_data:
            self._selection_min = float(histogram_data['min_temperature'])
            self._selection_max = float(histogram_data['max_temperature'])
            self._view_min = float(histogram_data['min_temperature'])
            self._view_max = float(histogram_data['max_temperature'])
        else:
            self._selection_min = None
            self._selection_max = None
            self._view_min = None
            self._view_max = None

        self.update()

    def set_selection_range(self, minimum, maximum, emit_signal=False):
        """Update the selected thermal range."""
        if not self._histogram_data:
            return

        full_min = float(self._histogram_data['min_temperature'])
        full_max = float(self._histogram_data['max_temperature'])

        minimum = max(full_min, min(float(minimum), full_max))
        maximum = max(full_min, min(float(maximum), full_max))
        if minimum > maximum:
            minimum, maximum = maximum, minimum

        self._selection_min = minimum
        self._selection_max = maximum
        self.update()

    def selection_range(self):
        """Return the currently selected range."""
        return self._selection_min, self._selection_max

    def set_selection_wrap(self, wrap_enabled):
        """Set whether the selected range wraps around the axis origin."""
        self._selection_wrap = bool(wrap_enabled)
        self.update()

    def set_show_aoi_only(self, show_aoi_only):
        """Set whether only AOI/anomaly bars should be displayed."""
        self._show_aoi_only = bool(show_aoi_only)
        self.update()

    def show_aoi_only(self):
        """Return True when only AOI/anomaly bars are shown."""
        return self._show_aoi_only

    def set_empty_state_text(self, text):
        """Set the message displayed when no histogram data is loaded."""
        self._empty_state_text = str(text or "")
        self.update()

    def empty_state_text(self):
        """Return the message displayed when no histogram data is loaded."""
        return self._empty_state_text or self.tr("No histogram data available")

    def set_view_range(self, minimum, maximum):
        """Zoom the histogram to a specific x-axis temperature range."""
        if not self._histogram_data:
            return

        full_min = float(self._histogram_data['min_temperature'])
        full_max = float(self._histogram_data['max_temperature'])

        minimum = max(full_min, min(float(minimum), full_max))
        maximum = max(full_min, min(float(maximum), full_max))
        if minimum > maximum:
            minimum, maximum = maximum, minimum

        if abs(maximum - minimum) < 1e-6:
            return

        self._view_min = minimum
        self._view_max = maximum
        self._hovered_index = None
        self.hoveredRangeChanged.emit(None)
        self.update()

    def reset_view_range(self):
        """Reset the histogram zoom to the full range."""
        if not self._histogram_data:
            return

        self._view_min = float(self._histogram_data['min_temperature'])
        self._view_max = float(self._histogram_data['max_temperature'])
        self._hovered_index = None
        self.hoveredRangeChanged.emit(None)
        self.update()

    def view_range(self):
        """Return the current histogram zoom range."""
        return self._view_min, self._view_max

    def zoom_around_temperature(self, anchor_temperature, zoom_in=True):
        """Zoom the histogram x-axis around a specific temperature anchor."""
        if not self._histogram_data or self._view_min is None or self._view_max is None:
            return

        full_min = float(self._histogram_data['min_temperature'])
        full_max = float(self._histogram_data['max_temperature'])
        current_min = float(self._view_min)
        current_max = float(self._view_max)
        current_span = max(1e-6, current_max - current_min)
        full_span = max(1e-6, full_max - full_min)

        factor = self.WHEEL_ZOOM_FACTOR if zoom_in else (1.0 / self.WHEEL_ZOOM_FACTOR)
        new_span = current_span / factor

        min_span = max(full_span / 500.0, 0.1)
        max_span = full_span
        new_span = max(min_span, min(max_span, new_span))

        if abs(new_span - full_span) <= 1e-6:
            self.reset_view_range()
            return

        anchor_temperature = max(full_min, min(float(anchor_temperature), full_max))
        anchor_ratio = (anchor_temperature - current_min) / current_span
        anchor_ratio = max(0.0, min(1.0, anchor_ratio))

        new_min = anchor_temperature - (new_span * anchor_ratio)
        new_max = new_min + new_span

        if new_min < full_min:
            new_min = full_min
            new_max = new_min + new_span
        if new_max > full_max:
            new_max = full_max
            new_min = new_max - new_span

        self.set_view_range(new_min, new_max)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), self.palette().window())

        if not self._histogram_data:
            painter.setPen(self.palette().text().color())
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                self.empty_state_text()
            )
            return

        plot_rect = self._plot_rect()
        self._draw_selection_shading(painter, plot_rect)
        self._draw_grid(painter, plot_rect)
        if self._show_aoi_only:
            self._draw_bar_series(
                painter,
                plot_rect,
                self._histogram_data['anomaly_counts'],
                QColor(255, 120, 80, 235),
            )
        else:
            self._draw_bar_series(
                painter,
                plot_rect,
                self._histogram_data['counts'],
                QColor(135, 150, 178, 190),
            )
            if not self._is_hue_histogram():
                self._draw_anomaly_overlay(
                    painter,
                    plot_rect,
                    self._histogram_data['counts'],
                    self._histogram_data['anomaly_counts'],
                )
        self._draw_hover_marker(painter, plot_rect)
        self._draw_legend(painter, plot_rect)
        self._draw_axis_labels(painter, plot_rect)
        self._draw_zoom_drag_overlay(painter, plot_rect)

    def mousePressEvent(self, event):
        if not self._histogram_data or event.button() != Qt.LeftButton:
            return

        plot_rect = self._plot_rect()
        if not plot_rect.contains(event.position()):
            return

        self._zoom_drag_start_x = event.position().x()
        self._zoom_drag_current_x = event.position().x()
        self.update()

    def mouseMoveEvent(self, event):
        if not self._histogram_data:
            return

        plot_rect = self._plot_rect()
        if self._zoom_drag_start_x is not None:
            self._zoom_drag_current_x = max(plot_rect.left(), min(event.position().x(), plot_rect.right()))
            self.update()
            return

        hovered_index = self._bin_index_at_position(event.position().x(), plot_rect)
        if hovered_index != self._hovered_index:
            self._hovered_index = hovered_index
            self.update()
            if hovered_index is None:
                self.hoveredRangeChanged.emit(None)
            else:
                edges = self._histogram_data['bin_edges']
                self.hoveredRangeChanged.emit((float(edges[hovered_index]), float(edges[hovered_index + 1])))

    def mouseReleaseEvent(self, event):
        if self._zoom_drag_start_x is None or event.button() != Qt.LeftButton:
            return

        plot_rect = self._plot_rect()
        end_x = max(plot_rect.left(), min(event.position().x(), plot_rect.right()))
        start_x = self._zoom_drag_start_x
        self._zoom_drag_start_x = None
        self._zoom_drag_current_x = None
        self.update()

        if abs(end_x - start_x) < self.MIN_ZOOM_DRAG_PIXELS:
            return

        minimum = self._x_to_temperature(min(start_x, end_x), plot_rect)
        maximum = self._x_to_temperature(max(start_x, end_x), plot_rect)
        self.zoomRangeSelected.emit(minimum, maximum)

    def mouseDoubleClickEvent(self, event):
        if self._histogram_data and event.button() == Qt.LeftButton:
            self.zoomResetRequested.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        if not self._histogram_data:
            return super().wheelEvent(event)

        plot_rect = self._plot_rect()
        if not plot_rect.contains(event.position()):
            return super().wheelEvent(event)

        anchor_temperature = self._x_to_temperature(event.position().x(), plot_rect)
        zoom_in = event.angleDelta().y() > 0
        self.zoom_around_temperature(anchor_temperature, zoom_in=zoom_in)
        event.accept()

    def leaveEvent(self, event):
        if self._hovered_index is not None:
            self._hovered_index = None
            self.hoveredRangeChanged.emit(None)
            self.update()
        super().leaveEvent(event)

    def _plot_rect(self):
        """Return the drawing rect for the chart area."""
        return QRectF(48, 18, max(40, self.width() - 66), max(80, self.height() - 54))

    def _draw_grid(self, painter, plot_rect):
        axis_pen = QPen(self.palette().mid().color(), 1)
        painter.setPen(axis_pen)
        painter.drawLine(plot_rect.bottomLeft(), plot_rect.bottomRight())
        painter.drawLine(plot_rect.bottomLeft(), plot_rect.topLeft())

        grid_pen = QPen(self.palette().mid().color(), 1, Qt.DotLine)
        painter.setPen(grid_pen)
        for ratio in (0.25, 0.5, 0.75):
            y = plot_rect.bottom() - (plot_rect.height() * ratio)
            painter.drawLine(QPointF(plot_rect.left(), y), QPointF(plot_rect.right(), y))

    def _draw_bar_series(self, painter, plot_rect, counts, color):
        if counts is None or len(counts) == 0:
            return

        max_count = self._max_visible_count()
        use_hue_colors = self._is_hue_histogram()
        painter.save()
        painter.setPen(Qt.NoPen)

        for index, count in self._visible_counts(counts):
            bar_rect = self._bar_rect_for_index(index, float(count), max_count, plot_rect)
            if bar_rect.isEmpty():
                continue
            if use_hue_colors:
                hue_deg = float(self._histogram_data['bin_centers'][index])
                painter.setBrush(self._hue_bar_color(hue_deg))
            else:
                painter.setBrush(color)
            painter.drawRect(bar_rect)

        painter.restore()

    def _draw_anomaly_overlay(self, painter, plot_rect, counts, anomaly_counts):
        """Overlay anomaly bins as highlighted orange bars."""
        if counts is None or anomaly_counts is None or len(counts) == 0:
            return

        max_count = self._max_visible_count()
        overlay_mode = self._histogram_data.get('anomaly_overlay_mode', 'full_bin')
        active_indices = [
            idx for idx, value in self._visible_counts(anomaly_counts)
            if value > 0
        ]
        if not active_indices:
            return

        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 120, 80, 235))
        for histogram_index in active_indices:
            overlay_count = self._overlay_count_for_index(
                histogram_index,
                counts,
                anomaly_counts,
                overlay_mode
            )
            # AOI bins must stay visible even in sparse bins dwarfed by the
            # image's peak bin — clamp to a minimum height instead of skipping.
            bar_rect = self._bar_rect_for_index(
                histogram_index,
                overlay_count,
                max_count,
                plot_rect,
                min_height=self.MIN_AOI_BAR_HEIGHT
            )
            if bar_rect.isEmpty():
                continue
            painter.drawRect(bar_rect)
        painter.restore()

    @staticmethod
    def _overlay_count_for_index(index, counts, anomaly_counts, overlay_mode):
        """Return the effective overlay count for a histogram bin."""
        if overlay_mode == 'anomaly_count':
            return float(anomaly_counts[index])
        return float(counts[index])

    def _draw_selection_shading(self, painter, plot_rect):
        painter.save()
        shade = QColor(0, 0, 0, 70)

        min_x = self._temperature_to_x(self._selection_min, plot_rect)
        max_x = self._temperature_to_x(self._selection_max, plot_rect)

        if self._selection_wrap:
            painter.fillRect(
                QRectF(min_x, plot_rect.top(), max(0.0, max_x - min_x), plot_rect.height()),
                shade
            )
        else:
            left_w = max(0.0, min_x - plot_rect.left())
            painter.fillRect(
                QRectF(plot_rect.left(), plot_rect.top(), left_w, plot_rect.height()),
                shade
            )
            right_w = max(0.0, plot_rect.right() - max_x)
            painter.fillRect(
                QRectF(max_x, plot_rect.top(), right_w, plot_rect.height()),
                shade
            )
        painter.restore()

    def _draw_hover_marker(self, painter, plot_rect):
        if self._hovered_index is None:
            return

        display_counts = self._display_counts()
        max_count = self._max_visible_count()
        hover_count = float(display_counts[self._hovered_index])
        hover_rect = self._bar_rect_for_index(self._hovered_index, hover_count, max_count, plot_rect, width_ratio=0.92)

        painter.save()
        painter.setPen(QPen(QColor(255, 220, 100), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(hover_rect)
        painter.restore()

    def _draw_legend(self, painter, plot_rect):
        """Draw a compact legend for the chart series."""
        painter.save()
        legend_y = max(0.0, plot_rect.top() - 14.0)
        is_hue = self._is_hue_histogram()

        if not self._show_aoi_only and not is_hue:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(135, 150, 178, 190))
            painter.drawRect(
                QRectF(plot_rect.right() - 180, legend_y, 12, 12)
            )
            painter.setPen(self.palette().text().color())
            painter.drawText(
                QRectF(plot_rect.right() - 162, legend_y - 2, 70, 18),
                self.tr("All Pixels")
            )

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 120, 80, 235))
            painter.drawRect(
                QRectF(plot_rect.right() - 90, legend_y, 12, 12)
            )
            painter.setPen(self.palette().text().color())
            painter.drawText(
                QRectF(plot_rect.right() - 72, legend_y - 2, 80, 18),
                self.tr("AOI Pixels")
            )
        elif self._show_aoi_only and not is_hue:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 120, 80, 235))
            painter.drawRect(
                QRectF(plot_rect.right() - 180, legend_y, 12, 12)
            )
            painter.setPen(self.palette().text().color())
            painter.drawText(
                QRectF(plot_rect.right() - 162, legend_y - 2, 80, 18),
                self.tr("AOI Pixels")
            )

        painter.restore()

    def _draw_axis_labels(self, painter, plot_rect):
        painter.setPen(self.palette().text().color())

        minimum = self._view_min
        maximum = self._view_max
        midpoint = (minimum + maximum) / 2.0

        y = plot_rect.bottom() + 4
        painter.drawText(
            QRectF(plot_rect.left() - 8, y, 70, 18),
            self._format_axis_value(minimum)
        )
        painter.drawText(
            QRectF(plot_rect.center().x() - 25, y, 50, 18),
            Qt.AlignCenter,
            self._format_axis_value(midpoint)
        )
        painter.drawText(
            QRectF(plot_rect.right() - 62, y, 70, 18),
            Qt.AlignRight,
            self._format_axis_value(maximum)
        )

    def _draw_zoom_drag_overlay(self, painter, plot_rect):
        """Draw the current drag-to-zoom selection."""
        if self._zoom_drag_start_x is None or self._zoom_drag_current_x is None:
            return

        left = min(self._zoom_drag_start_x, self._zoom_drag_current_x)
        right = max(self._zoom_drag_start_x, self._zoom_drag_current_x)
        drag_rect = QRectF(left, plot_rect.top(), max(1.0, right - left), plot_rect.height())

        painter.save()
        painter.setPen(QPen(QColor(100, 190, 255), 1, Qt.DashLine))
        painter.setBrush(QColor(100, 190, 255, 50))
        painter.drawRect(drag_rect)
        painter.restore()

    def _temperature_to_x(self, temperature, plot_rect):
        minimum = float(self._view_min)
        maximum = float(self._view_max)
        span = max(1e-6, maximum - minimum)
        ratio = (float(temperature) - minimum) / span
        return plot_rect.left() + (ratio * plot_rect.width())

    def _x_to_temperature(self, x_position, plot_rect):
        minimum = float(self._view_min)
        maximum = float(self._view_max)
        width = max(1.0, plot_rect.width())
        ratio = (x_position - plot_rect.left()) / width
        ratio = max(0.0, min(1.0, ratio))
        return minimum + ((maximum - minimum) * ratio)

    def _count_to_y(self, count, max_count, plot_rect):
        ratio = 0.0 if max_count <= 0 else float(count) / float(max_count)
        return plot_rect.bottom() - (ratio * plot_rect.height())

    def _bin_index_to_x(self, index, plot_rect):
        centers = self._histogram_data['bin_centers']
        return self._temperature_to_x(float(centers[index]), plot_rect)

    def _bar_rect_for_index(self, index, count, max_count, plot_rect, width_ratio=0.8, min_height=None):
        """Return a vertical bar rect for a histogram bin."""
        edges = self._histogram_data['bin_edges']
        left_temp = max(float(edges[index]), float(self._view_min))
        right_temp = min(float(edges[index + 1]), float(self._view_max))
        if right_temp <= left_temp:
            return QRectF()

        left_x = self._temperature_to_x(left_temp, plot_rect)
        right_x = self._temperature_to_x(right_temp, plot_rect)
        available_width = max(2.0, right_x - left_x)
        bar_width = max(2.0, available_width * width_ratio)
        x = left_x + ((available_width - bar_width) / 2.0)
        top = self._count_to_y(count, max_count, plot_rect)
        height = plot_rect.bottom() - top
        if min_height is not None and height < min_height:
            height = min_height
            top = plot_rect.bottom() - height
        if height < 0.5:
            return QRectF()
        return QRectF(x, top, bar_width, height)

    def _bin_index_at_position(self, x_position, plot_rect):
        if not plot_rect.left() <= x_position <= plot_rect.right():
            return None

        visible = self._visible_indices()
        if not visible:
            return None

        centers = self._histogram_data['bin_centers']
        nearest_index = min(
            visible,
            key=lambda idx: abs(
                self._temperature_to_x(float(centers[idx]), plot_rect)
                - x_position
            )
        )
        return int(nearest_index)

    def _visible_indices(self):
        """Return histogram bin indices overlapping the current zoom range."""
        if not self._histogram_data:
            return []

        edges = self._histogram_data['bin_edges']
        visible = []
        for index in range(len(edges) - 1):
            left_temp = float(edges[index])
            right_temp = float(edges[index + 1])
            if right_temp < self._view_min or left_temp > self._view_max:
                continue
            visible.append(index)
        return visible

    def _visible_counts(self, counts):
        """Yield visible histogram bins and their counts."""
        for index in self._visible_indices():
            yield index, counts[index]

    def _max_visible_count(self):
        """Return the maximum count within the current zoom range."""
        display_counts = self._display_counts()
        visible = [int(display_counts[idx]) for idx in self._visible_indices()]
        return max(1, max(visible) if visible else 1)

    def _display_counts(self):
        """Return the count series currently displayed in the chart."""
        if self._show_aoi_only:
            return self._histogram_data['anomaly_counts']
        return self._histogram_data['counts']

    def _is_hue_histogram(self):
        """Return True when the histogram represents HSV Hue."""
        if not self._histogram_data:
            return False
        return (
            self._histogram_data.get('color_space') == 'HSV'
            and self._histogram_data.get('component') == 'H'
        )

    @staticmethod
    def _hue_bar_color(hue_degrees):
        """Return a saturated QColor for a given hue in degrees."""
        qt_hue = int(round(hue_degrees)) % 360
        return QColor.fromHsv(qt_hue, 220, 200, 210)

    def _format_axis_value(self, value):
        """Format an axis value using the histogram's preferred precision."""
        precision = int(self._histogram_data.get('value_precision', 1))
        if precision == 0:
            return str(int(round(float(value))))
        return f"{float(value):.{precision}f}"
