"""ResultsFolderDialog - Dialog for displaying scanned results folders."""

import os
from typing import List, Callable
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QWidget, QProgressDialog
)
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QObject
from PySide6.QtGui import QDesktopServices, QBrush, QColor

from core.services.ResultsScannerService import ResultsScannerService, ResultsScanResult
from core.services.LoggerService import LoggerService
from helpers.IconHelper import IconHelper


class ScanWorker(QObject):
    """Worker for background folder scanning."""
    finished = Signal(list)  # Emits list of ResultsScanResult
    error = Signal(str)
    progress = Signal(int, int, str)  # current, total, current_directory

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self.scanner = ResultsScannerService()

    def run(self):
        """Execute the scan in background thread."""
        try:
            results = self.scanner.scan_folder(
                self.folder_path,
                progress_callback=self._on_progress
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, current: int, total: int, current_dir: str):
        """Handle progress updates from scanner."""
        self.progress.emit(current, total, current_dir)


class ScanProgressDialog(QProgressDialog):
    """Custom progress dialog for folder scanning."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scanning for Results")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumDuration(0)
        self.setMinimumWidth(500)
        self.setAutoClose(False)
        self.setAutoReset(False)
        self._results_found = 0

    def update_progress(self, current: int, total: int, current_dir: str):
        """Update the progress dialog with current scan status."""
        self.setMaximum(total)
        self.setValue(current)

        # Truncate long directory paths
        display_dir = current_dir
        if len(display_dir) > 60:
            display_dir = "..." + display_dir[-57:]

        self.setLabelText(
            f"Scanning folder {current} of {total}\n"
            f"Results found: {self._results_found}\n"
            f"{display_dir}"
        )

    def increment_results_found(self):
        """Increment the count of results found."""
        self._results_found += 1


class ResultsFolderDialog(QDialog):
    """Dialog for displaying and interacting with scanned result folders."""

    # Column indices
    COL_FOLDER = 0
    COL_ALGORITHM = 1
    COL_IMAGES = 2
    COL_MISSING = 3
    COL_AOIS = 4
    COL_MAP = 5
    COL_VIEW = 6

    def __init__(self, parent, results: List[ResultsScanResult], theme: str,
                 open_viewer_callback: Callable[[str], None]):
        """
        Initialize the results folder dialog.

        Args:
            parent: Parent widget
            results: List of scan results to display
            theme: Current theme ('Light' or 'Dark')
            open_viewer_callback: Function to call when opening Results Viewer
        """
        super().__init__(parent)
        self.results = results
        self.theme = theme
        self.open_viewer_callback = open_viewer_callback
        self.logger = LoggerService()

        self.setupUi()
        self.populate_table()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Load Results Folder")
        self.setModal(True)
        self.setMinimumSize(900, 500)
        self.resize(1000, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()

        # Header label
        header = QLabel(f"Found {len(self.results)} result(s)")
        header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Folder", "Algorithm", "Images", "Missing", "AOIs", "Map", "View"
        ])

        # Table configuration
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_FOLDER, QHeaderView.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_ALGORITHM, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_IMAGES, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_MISSING, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_AOIS, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_MAP, QHeaderView.Fixed
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_VIEW, QHeaderView.Fixed
        )
        self.table.setColumnWidth(self.COL_MAP, 60)
        self.table.setColumnWidth(self.COL_VIEW, 60)

        layout.addWidget(self.table)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_table(self):
        """Populate the table with scan results."""
        self.table.setRowCount(len(self.results))

        for row, result in enumerate(self.results):
            # Folder name
            folder_item = QTableWidgetItem(result.folder_name)
            folder_item.setToolTip(result.xml_path)
            self.table.setItem(row, self.COL_FOLDER, folder_item)

            # Algorithm
            self.table.setItem(row, self.COL_ALGORITHM,
                               QTableWidgetItem(result.algorithm))

            # Image count
            images_item = QTableWidgetItem(str(result.image_count))
            images_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, self.COL_IMAGES, images_item)

            # Missing images
            missing_item = QTableWidgetItem(str(result.missing_images))
            missing_item.setTextAlignment(Qt.AlignCenter)
            if result.missing_images > 0:
                missing_item.setForeground(QBrush(QColor(Qt.red)))
            self.table.setItem(row, self.COL_MISSING, missing_item)

            # AOI count
            aoi_item = QTableWidgetItem(str(result.aoi_count))
            aoi_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, self.COL_AOIS, aoi_item)

            # Map button - create a container widget for centering
            map_container = QWidget()
            map_layout = QHBoxLayout(map_container)
            map_layout.setContentsMargins(0, 0, 0, 0)
            map_layout.setAlignment(Qt.AlignCenter)

            map_button = QPushButton()
            map_button.setIcon(IconHelper.create_icon('fa6s.map-location-dot', self.theme))
            map_button.setToolTip("Open in Google Maps")
            map_button.setFixedSize(40, 28)

            # Disable if all images are missing (no GPS available)
            all_missing = (result.missing_images == result.image_count) or result.image_count == 0
            has_gps = result.gps_coordinates is not None
            map_button.setEnabled(not all_missing and has_gps)

            if not map_button.isEnabled():
                if all_missing:
                    map_button.setToolTip("No images available - cannot get GPS location")
                else:
                    map_button.setToolTip("No GPS coordinates found in images")

            if result.gps_coordinates:
                lat, lon = result.gps_coordinates
                # Use default argument to capture current values
                map_button.clicked.connect(
                    lambda checked, la=lat, lo=lon: self._open_google_maps(la, lo)
                )

            map_layout.addWidget(map_button)
            self.table.setCellWidget(row, self.COL_MAP, map_container)

            # View button - create a container widget for centering
            view_container = QWidget()
            view_layout = QHBoxLayout(view_container)
            view_layout.setContentsMargins(0, 0, 0, 0)
            view_layout.setAlignment(Qt.AlignCenter)

            view_button = QPushButton()
            view_button.setIcon(IconHelper.create_icon('fa6s.images', self.theme))
            view_button.setToolTip("Open in Results Viewer")
            view_button.setFixedSize(40, 28)
            # Use default argument to capture current value
            view_button.clicked.connect(
                lambda checked, path=result.xml_path: self._open_viewer(path)
            )

            view_layout.addWidget(view_button)
            self.table.setCellWidget(row, self.COL_VIEW, view_container)

        # Alternate row colors
        self.table.setAlternatingRowColors(True)

    def _open_google_maps(self, lat: float, lon: float):
        """Open Google Maps at the specified coordinates."""
        url = f"https://www.google.com/maps?q={lat},{lon}"
        QDesktopServices.openUrl(QUrl(url))

    def _open_viewer(self, xml_path: str):
        """Open the Results Viewer with the specified XML file."""
        self.open_viewer_callback(xml_path)
        self.accept()  # Close dialog after opening viewer
