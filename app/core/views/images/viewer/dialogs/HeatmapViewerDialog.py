# HeatmapViewerDialog.py
# Modal dialog for viewing the AOI detection density heatmap with interactive threshold.

import cv2
import numpy as np
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QGroupBox, QButtonGroup,
                               QRadioButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from helpers.TranslationMixin import TranslationMixin


class HeatmapViewerDialog(TranslationMixin, QDialog):
    """Modal dialog showing the AOI detection density heatmap with interactive threshold."""

    DISPLAY_SIZE = 700

    def __init__(self, parent, heatmapService, currentThreshold=75, currentGridSize=200):
        """Initialize the heatmap viewer dialog.

        Args:
                parent: Parent widget.
                heatmapService: HeatmapService instance with computed heatmap data.
                currentThreshold: Current percentile threshold (0-100).
                currentGridSize: Current grid resolution.
        """
        super().__init__(parent)
        self.heatmapService = heatmapService
        self.threshold = currentThreshold
        self.gridSize = currentGridSize

        self.setWindowTitle(self.tr("AOI Detection Heatmap"))
        self.setModal(True)
        self.setMinimumSize(850, 900)

        self._setupUi()
        self._apply_translations()
        self._renderHeatmap()

    def _setupUi(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()

        # Heatmap image display
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.imageLabel.setMinimumSize(self.DISPLAY_SIZE, self.DISPLAY_SIZE)
        layout.addWidget(self.imageLabel)

        # Stats label
        self.statsLabel = QLabel()
        self.statsLabel.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        layout.addWidget(self.statsLabel)

        # Threshold slider
        thresholdGroup = QGroupBox(self.tr("Threshold"))
        thresholdLayout = QHBoxLayout()

        thresholdLayout.addWidget(QLabel(self.tr("Percentile:")))

        self.thresholdSlider = QSlider(Qt.Horizontal)
        self.thresholdSlider.setMinimum(0)
        self.thresholdSlider.setMaximum(100)
        self.thresholdSlider.setValue(self.threshold)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(25)
        self.thresholdSlider.valueChanged.connect(self._onThresholdChanged)
        thresholdLayout.addWidget(self.thresholdSlider)

        self.thresholdLabel = QLabel(f"{self.threshold}%")
        self.thresholdLabel.setMinimumWidth(40)
        thresholdLayout.addWidget(self.thresholdLabel)

        thresholdGroup.setLayout(thresholdLayout)
        layout.addWidget(thresholdGroup)

        # Grid resolution presets
        resGroup = QGroupBox(self.tr("Grid Resolution"))
        resLayout = QHBoxLayout()

        self.resButtonGroup = QButtonGroup(self)

        self.lowRadio = QRadioButton(self.tr("Low (100)"))
        self.medRadio = QRadioButton(self.tr("Medium (200)"))
        self.highRadio = QRadioButton(self.tr("High (400)"))

        self.resButtonGroup.addButton(self.lowRadio, 100)
        self.resButtonGroup.addButton(self.medRadio, 200)
        self.resButtonGroup.addButton(self.highRadio, 400)

        # Set current selection
        if self.gridSize <= 100:
            self.lowRadio.setChecked(True)
        elif self.gridSize >= 400:
            self.highRadio.setChecked(True)
        else:
            self.medRadio.setChecked(True)

        self.resButtonGroup.idClicked.connect(self._onGridResolutionChanged)

        resLayout.addWidget(self.lowRadio)
        resLayout.addWidget(self.medRadio)
        resLayout.addWidget(self.highRadio)
        resLayout.addStretch()

        resGroup.setLayout(resLayout)
        layout.addWidget(resGroup)

        # Info label
        infoLabel = QLabel(self.tr(
            "Hot zones (colored) show high-density detection areas. "
            "Gray zones are below the threshold. "
            "Adjust the threshold to control what counts as a hot zone."
        ))
        infoLabel.setWordWrap(True)
        infoLabel.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        layout.addWidget(infoLabel)

        # Close button
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()

        closeButton = QPushButton(self.tr("Close"))
        closeButton.clicked.connect(self.accept)
        buttonLayout.addWidget(closeButton)

        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def _onThresholdChanged(self, value):
        """Handle threshold slider changes."""
        self.threshold = value
        self.thresholdLabel.setText(f"{value}%")
        self._renderHeatmap()

    def _onGridResolutionChanged(self, gridSize):
        """Handle grid resolution preset changes. Recomputes the heatmap."""
        self.gridSize = gridSize
        # Recompute with new grid size using the stored images
        if hasattr(self.heatmapService, '_lastImages') and self.heatmapService._lastImages is not None:
            self.heatmapService.compute_heatmap(self.heatmapService._lastImages, gridSize=gridSize)
        self._renderHeatmap()

    def _renderHeatmap(self):
        """Render the heatmap image with current threshold overlay."""
        if not self.heatmapService.is_valid():
            self.imageLabel.setText(self.tr("No heatmap data available"))
            return

        heatmapImg, stats = self.heatmapService.generate_heatmap_image(
            thresholdPercentile=self.threshold
        )

        # Scale up to display size
        displayImg = cv2.resize(heatmapImg, (self.DISPLAY_SIZE, self.DISPLAY_SIZE),
                                interpolation=cv2.INTER_LINEAR)

        # Add center crosshair
        center = self.DISPLAY_SIZE // 2
        crossColor = (200, 200, 200)
        cv2.line(displayImg, (center - 20, center), (center + 20, center), crossColor, 1)
        cv2.line(displayImg, (center, center - 20), (center, center + 20), crossColor, 1)

        # Add corner labels
        cv2.putText(displayImg, "Top-Left", (5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
        cv2.putText(displayImg, "Bottom-Right",
                    (self.DISPLAY_SIZE - 100, self.DISPLAY_SIZE - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        # Build color bar on the right
        barWidth = 30
        barHeight = self.DISPLAY_SIZE - 40
        barTop = 20
        gradient = np.linspace(255, 0, barHeight).astype(np.uint8)
        gradient = np.tile(gradient.reshape(-1, 1), (1, barWidth))
        colorBar = cv2.applyColorMap(gradient, cv2.COLORMAP_JET)

        # Apply threshold mask to color bar too
        if self.threshold > 0:
            thresholdRow = int(barHeight * (1.0 - self.threshold / 100.0))
            dimColor = np.array([40, 40, 40], dtype=np.uint8)
            colorBar[thresholdRow:] = dimColor
            # Draw threshold line
            cv2.line(colorBar, (0, thresholdRow), (barWidth, thresholdRow), (255, 255, 255), 2)

        # Compose final image with color bar
        padding = 10
        totalWidth = self.DISPLAY_SIZE + padding + barWidth + padding
        canvas = np.zeros((self.DISPLAY_SIZE, totalWidth, 3), dtype=np.uint8)
        canvas[:] = (40, 40, 40)

        # Place heatmap
        canvas[:, :self.DISPLAY_SIZE] = displayImg

        # Place color bar
        cbLeft = self.DISPLAY_SIZE + padding
        canvas[barTop:barTop + barHeight, cbLeft:cbLeft + barWidth] = colorBar

        # Color bar labels
        cv2.putText(canvas, "High", (cbLeft, barTop - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        cv2.putText(canvas, "Low", (cbLeft, barTop + barHeight + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        # Draw border around heatmap
        cv2.rectangle(canvas, (0, 0), (self.DISPLAY_SIZE - 1, self.DISPLAY_SIZE - 1),
                      (180, 180, 180), 1)

        # Convert BGR to RGB for Qt
        rgbImg = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImg.shape
        qImg = QImage(rgbImg.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)

        self.imageLabel.setPixmap(pixmap)

        # Update stats
        plottedAois = stats['totalAois'] - stats['skippedAois']
        self.statsLabel.setText(
            f"Images: {stats['totalImages']}  |  "
            f"AOIs: {plottedAois}/{stats['totalAois']}  |  "
            f"Grid: {stats['gridSize']}x{stats['gridSize']}"
        )

    def get_threshold(self):
        """Get the current threshold value.

        Returns:
                int: Threshold percentile (0-100).
        """
        return self.threshold

    def get_grid_size(self):
        """Get the current grid resolution.

        Returns:
                int: Grid resolution.
        """
        return self.gridSize
