"""Aggregate Mission Gallery dock (plan §7).

Subscribes (via :class:`MissionGalleryController`) to every active feed
and renders detections from non-muted tiles in monotonic timestamp order.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDockWidget, QListWidget, QListWidgetItem, QWidget

from core.views.flight.mission_gallery_dock_ui import Ui_MissionGalleryContents
from core.views.flight.DetectionRowWidget import DetectionRowWidget
from helpers.TranslationMixin import TranslationMixin


class MissionGalleryDock(TranslationMixin, QDockWidget):
    """Right-hand dock that aggregates detections across feeds."""

    filtersChanged = Signal()
    exportRequested = Signal()
    detectionActivated = Signal(dict)  # emitted when a row is clicked / activated

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Mission Gallery"))
        # Required for QMainWindow.saveState() / restoreState() round-trip
        # (Qt warns and drops the dock from saved layouts otherwise).
        self.setObjectName("missionGalleryDock")
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )

        self.ui = Ui_MissionGalleryContents()
        contents = QWidget(self)
        self.ui.setupUi(contents)
        self.setWidget(contents)

        self.ui.minScoreSpin.setValue(0.0)

        # All three sources emit values we don't need; wrap to a no-arg slot
        # so `filtersChanged` (which carries no payload) is happy.
        self.ui.feedFilterCombo.currentIndexChanged.connect(lambda *_: self.filtersChanged.emit())
        self.ui.detectorFilterCombo.currentIndexChanged.connect(lambda *_: self.filtersChanged.emit())
        self.ui.minScoreSpin.valueChanged.connect(lambda *_: self.filtersChanged.emit())
        self.ui.exportButton.clicked.connect(self.exportRequested.emit)

        self.ui.feedFilterCombo.addItem(self.tr("All feeds"), "")
        # Filter rows by ``detector_id`` — class_name is detector-specific
        # (person, motion, dji-native, etc. have no shared class vocabulary),
        # so a "Class" filter forces operators to pick one detector's labels
        # and silently drops detections from every other detector. Detector
        # id is the universal axis.
        self.ui.detectorFilterCombo.addItem(self.tr("All detectors"), "")

        # Plan §15 M3 map widget: row activation re-centers the map dock.
        self.ui.missionList.itemActivated.connect(self._on_list_item_activated)
        self.ui.missionList.itemClicked.connect(self._on_list_item_activated)

    # ------------------------------------------------------------------
    # filter state
    # ------------------------------------------------------------------

    def selected_feed(self) -> str:
        return self.ui.feedFilterCombo.currentData() or ""

    def selected_detector(self) -> str:
        return self.ui.detectorFilterCombo.currentData() or ""

    def min_score(self) -> float:
        return float(self.ui.minScoreSpin.value())

    def register_feed(self, feed_id: str, label: str) -> None:
        if self._index_for_data(self.ui.feedFilterCombo, feed_id) is not None:
            return
        self.ui.feedFilterCombo.addItem(label, feed_id)

    def update_feed_label(self, feed_id: str, label: str) -> None:
        """Rename the feed's entry in the Feed filter dropdown.

        Used when a tile's ``displayNameChanged`` fires — e.g. the
        operator nicknamed the drone, or telemetry populated
        ``aircraft_name`` after the initial ``Tile-<code>`` registration.
        Idempotent: adds the entry if the feed wasn't registered yet.
        """
        idx = self._index_for_data(self.ui.feedFilterCombo, feed_id)
        if idx is None:
            self.ui.feedFilterCombo.addItem(label, feed_id)
        else:
            self.ui.feedFilterCombo.setItemText(idx, label)

    def deregister_feed(self, feed_id: str) -> None:
        idx = self._index_for_data(self.ui.feedFilterCombo, feed_id)
        if idx is not None:
            self.ui.feedFilterCombo.removeItem(idx)

    def register_detector(self, detector_id: str) -> None:
        if not detector_id:
            return
        if self._index_for_data(self.ui.detectorFilterCombo, detector_id) is not None:
            return
        self.ui.detectorFilterCombo.addItem(detector_id, detector_id)

    @staticmethod
    def _index_for_data(combo, data_value) -> Optional[int]:
        for i in range(combo.count()):
            if combo.itemData(i) == data_value:
                return i
        return None

    # ------------------------------------------------------------------
    # rows
    # ------------------------------------------------------------------

    @property
    def list_widget(self) -> QListWidget:
        return self.ui.missionList

    def clear(self) -> None:
        self.ui.missionList.clear()
        self.ui.rowCountLabel.setText(self.tr("0 detections"))

    def render_rows(self, detections: list) -> None:
        """Wholesale repaint with ``detections`` (a filtered, sorted list).

        Preserves the operator's scroll position across re-renders. The
        ``clear() + add`` pattern would otherwise snap the scrollbar back
        to the top every time a new detection arrives — annoying when the
        operator is reviewing earlier rows.
        """
        bar = self.ui.missionList.verticalScrollBar()
        prev_value = bar.value() if bar is not None else 0
        prev_at_top = (prev_value == 0)
        self.ui.missionList.clear()
        for detection in detections:
            row = DetectionRowWidget(detection, parent=self.ui.missionList)
            row.viewRequested.connect(self._on_row_view_requested)
            item = QListWidgetItem(self.ui.missionList)
            item.setSizeHint(row.sizeHint())
            # Stash the detection on the item itself so the activated
            # signal can recover it without fishing through the widget.
            item.setData(Qt.UserRole, detection)
            self.ui.missionList.addItem(item)
            self.ui.missionList.setItemWidget(item, row)
        self.ui.rowCountLabel.setText(
            self.tr("{n} detections").format(n=len(detections))
        )
        # Restore scroll. If the operator was pinned at the top
        # (newest-first ordering means top == latest), keep them there
        # so they see new detections arrive. Otherwise restore the
        # exact previous scroll value.
        if bar is not None:
            bar.setValue(0 if prev_at_top else min(prev_value, bar.maximum()))

    def _on_row_view_requested(self, detection: dict) -> None:
        """Bubble a ``viewRequested`` from a child row up to the dock.

        The dock re-emits ``detectionActivated`` so the
        :class:`FlightViewerController` can react (e.g. focus the map
        widget) just like the keyboard / list-click path.
        """
        if isinstance(detection, dict):
            self.detectionActivated.emit(detection)

    def _on_list_item_activated(self, item: QListWidgetItem) -> None:
        detection = item.data(Qt.UserRole) if item is not None else None
        if isinstance(detection, dict):
            self.detectionActivated.emit(detection)

    def highlight_track(self, track_key: str) -> None:
        """Scroll the row matching ``track_key`` into view and select it.

        Used by :class:`FlightViewerController` to surface the
        gallery-row counterpart of a map pin the operator clicked
        (plan §19.4.4 reverse direction).
        """
        if not track_key:
            return
        for i in range(self.ui.missionList.count()):
            item = self.ui.missionList.item(i)
            detection = item.data(Qt.UserRole) if item else None
            if isinstance(detection, dict) and detection.get("track_key") == track_key:
                self.ui.missionList.setCurrentItem(item)
                self.ui.missionList.scrollToItem(item)
                return
