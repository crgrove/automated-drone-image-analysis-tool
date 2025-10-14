# Set environment variable to avoid numpy._core issues - MUST be first
import os
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'

import qimage2ndarray
from PIL import UnidentifiedImageError
import traceback
import math
import re
import colorsys
import numpy as np
import tempfile
import cv2
import qtawesome as qta

from pathlib import Path
from urllib.parse import quote_plus

from PySide6.QtGui import QImage, QIntValidator, QPixmap, QIcon, QPainter, QFont, QPen, QPalette, QColor, QDesktopServices, QBrush, QCursor
from PySide6.QtCore import Qt, QSize, QThread, QPointF, QPoint, QEvent, QTimer, QUrl, QRectF, QObject
from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox, QListWidgetItem, QFileDialog, QApplication
from PySide6.QtWidgets import QPushButton, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QAbstractButton, QMenu, QInputDialog

from core.views.components.Toggle import Toggle
from core.views.viewer.ui.Viewer_ui import Ui_Viewer
from core.views.viewer.widgets.QtImageViewer import QtImageViewer

from core.controllers.viewer.status.StatusDict import StatusDict

from core.views.viewer.dialogs.ImageAdjustmentDialog import ImageAdjustmentDialog
from core.views.viewer.widgets.ScaleBarWidget import ScaleBarWidget
from core.views.viewer.dialogs.LoadingDialog import LoadingDialog
from core.views.viewer.dialogs.MeasureDialog import MeasureDialog
from core.controllers.viewer.MagnifyingGlass import MagnifyingGlass
from core.views.viewer.widgets.OverlayWidget import OverlayWidget
from core.views.viewer.dialogs.UpscaleDialog import UpscaleDialog
from core.views.viewer.dialogs.HelpDialog import HelpDialog

from core.controllers.viewer.UIStyleController import UIStyleController
from core.controllers.viewer.ThermalDataController import ThermalDataController
from core.controllers.viewer.PixelInfoController import PixelInfoController
from core.controllers.viewer.image.ImageLoadController import ImageLoadController
from core.controllers.viewer.AltitudeController import AltitudeController

from core.controllers.viewer.exports.PDFExportController import PDFExportController
from core.controllers.viewer.exports.ZipExportController import ZipExportController
from core.controllers.viewer.exports.CalTopoExportController import CalTopoExportController
from core.controllers.viewer.exports.CoverageExtentExportController import CoverageExtentExportController
from core.controllers.viewer.exports.UnifiedMapExportController import UnifiedMapExportController

from core.controllers.viewer.aoi.AOIController import AOIController
from core.controllers.viewer.thumbnails.ThumbnailController import ThumbnailController
from core.controllers.viewer.CoordinateController import CoordinateController
from core.controllers.viewer.status.StatusController import StatusController
from core.controllers.viewer.GPSMapController import GPSMapController

from core.services.LoggerService import LoggerService
from core.services.XmlService import XmlService
from core.services.ImageService import ImageService
from core.services.ThermalParserService import ThermalParserService
from helpers.LocationInfo import LocationInfo

from typing import List, Dict, Any, Optional


class Viewer(QMainWindow, Ui_Viewer):
    """
    Main application controller for the ADIAT Image Viewer.

    Handles UI initialization, thumbnail loading, metadata extraction,
    and interaction logic for navigating and analyzing drone images.
    """

    def __init__(self, xml_path, position_format, temperature_unit, distance_unit, show_hidden, theme):
        """Initializes the ADIAT Image Viewer.

        Args:
            xml_path (str): Path to XML file containing results data.
            position_format (str): The format in which GPS coordinates will be displayed.
            temperature_unit (str): The unit in which temperature values will be displayed.
            distance_unit (str): The unit in which distance values will be displayed.
            show_hidden (bool): Whether or not to show hidden images by default.
            theme (str): The current active theme.
        """
        super().__init__()
        self._threads = []
        self.main_image = None
        self.logger = LoggerService()
        self.theme = theme  # Store theme before calling _add_Toggles
        self.setupUi(self)
        self._add_Toggles()
        # ---------------- settings / data ----------------
        self.xml_path = xml_path
        self.xml_service = XmlService(xml_path)
        self.images = self.xml_service.get_images()
        self.loaded_thumbnails = []
        self.hidden_image_count = sum(1 for image in self.images if image.get("hidden"))
        self.skipHidden.setText(f"Skip Hidden ({self.hidden_image_count}) ")
        self.settings, _ = self.xml_service.get_settings()

        # Initialize controllers
        self.aoi_controller = AOIController(self)
        self.thumbnail_controller = ThumbnailController(self)
        self.coordinate_controller = CoordinateController(self)
        self.status_controller = StatusController(self)
        self.gps_map_controller = GPSMapController(self)
        
        self.ui_style_controller = UIStyleController(self, theme)
        self.thermal_controller = ThermalDataController(self)
        self.pixel_info_controller = PixelInfoController(self)
        self.image_load_controller = ImageLoadController(self)
        self.altitude_controller = AltitudeController(self)

        # Load flagged AOIs from XML
        self.aoi_controller.initialize_from_xml(self.images)
        self.is_thermal = (self.settings['thermal'] == 'True')
        self.position_format = position_format
        self.current_image_array = None  # Cache for the current image RGB array
        self.current_image_service = None  # Keep reference to ImageService

        self.temperature_unit = 'F' if temperature_unit == 'Fahrenheit' else 'C'
        self.distance_unit = 'ft' if distance_unit == 'Feet' else 'm'
        self.show_hidden = show_hidden
        self.skipHidden.setChecked(not self.show_hidden)
        self.skipHidden.clicked.connect(self._skip_hidden_clicked)

        # status‑bar helper
        self.messages = StatusDict(callback=self.status_controller.message_listener,
                                   key_order=["GPS Coordinates", "Relative Altitude",
                                              "Gimbal Orientation", "Estimated Average GSD",
                                              "Temperature", "Color Values"])
        
        # Apply icons
        self._apply_icons()
        self.statusBar.linkActivated.connect(self.coordinate_controller.on_coordinates_clicked)

        # toast (non intrusive) over statusBarWidget
        self._toastLabel = QLabel(self.statusBarWidget)
        self._toastLabel.setVisible(False)
        self._toastLabel.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._toastTimer = QTimer(self)
        self._toastTimer.setSingleShot(True)
        self._toastTimer.timeout.connect(lambda: self._toastLabel.setVisible(False))

        # coordinates for sharing
        self.current_decimal_coords = None

        # Track last mouse position for AOI selection
        self.last_mouse_pos = QPoint(-1, -1)

        # AOI creation mode state
        self.aoi_creation_mode = False  # Whether user is in AOI creation mode
        self.aoi_creation_start = None  # QPointF: Starting point of circle drag
        self.aoi_creation_current = None  # QPointF: Current mouse position during drag
        self.aoi_creation_preview_item = None  # QGraphicsEllipseItem: Preview circle being drawn

        # scale bar (will be used by overlay widget)
        self.scaleBar = ScaleBarWidget()

        # ---- load everything ----
        self._load_images()

        # Set up UI elements for controllers
        # Controllers get UI elements directly from parent

        # Defer thumbnail initialization to avoid blocking with large datasets
        # Only initialize visible thumbnails first
        self.thumbnail_controller.initialize_thumbnails_deferred()
        self._setupViewer()

        # UI tweaks
        self.setFocusPolicy(Qt.StrongFocus)
        self.hideImageToggle.setFocusPolicy(Qt.NoFocus)
        self.skipHidden.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("QToolTip {background-color: lightblue; color:black; border:1px solid blue;}")

        self.showMaximized()

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, '_initialized_once'):
            self._initial_fit_image()
            self._initialized_once = True

    def _initial_fit_image(self):
        if self.main_image is not None and not self.main_image._is_destroyed:
            # Ensure the widget is properly sized before resetting zoom
            self.main_image.updateGeometry()
            self.main_image.resetZoom()
            if hasattr(self, 'overlay'):
                self.overlay._place_overlay()

    def closeEvent(self, event):
        """Event triggered on window close; quits all thumbnail threads."""
        for thread, loader in self._threads:
            if thread.isRunning():
                thread.requestInterruption()  # Optional: politely request interruption
                thread.quit()
                thread.wait()  # Wait until the thread has terminated

        # Clean up magnifying glass controller
        if hasattr(self, 'magnifying_glass'):
            self.magnifying_glass.cleanup()
            # Reset button styling
            self.magnifying_glass_enabled = False
            self._update_magnify_button_style()

        # Clean up overlay widget
        if hasattr(self, 'overlay'):
            self.overlay.cleanup()

        # Clean up controllers
        if hasattr(self, 'thumbnail_controller'):
            self.thumbnail_controller.cleanup()

        # Close GPS map window if open
        if hasattr(self, 'gps_map_controller'):
            self.gps_map_controller.close_map()

        # Close north-oriented image window if open
        if hasattr(self, 'coordinate_controller'):
            self.coordinate_controller.cleanup()

        # Close help dialog if open
        if hasattr(self, 'help_dialog') and self.help_dialog:
            self.help_dialog.close()

        event.accept()

    def _add_Toggles(self):
        """Replaces checkboxs with a toggle button."""
        self.hideImageToggle = Toggle()
        self.hideImageToggle.setContentsMargins(4, 0, 4, 0)
        self.hideImageToggle.setFixedWidth(50)
        self.ButtonLayout.replaceWidget(self.hideImageCheckbox, self.hideImageToggle)
        self.hideImageCheckbox.deleteLater()
        self.hideImageToggle.clicked.connect(self._hide_image_change)
        
        # Get the main layout
        layout = self.mainHeaderWidget.layout()
        font = QFont()
        font.setPointSize(10)
        
        # Show Overlay toggle with label
        self.showOverlayToggle = Toggle()
        self.showOverlayToggle.setContentsMargins(4, 0, 4, 0)
        self.showOverlayToggle.setFixedWidth(50)
        self.showOverlayLabel = QLabel("Show Overlay")
        self.showOverlayLabel.setFont(font)
        
        # Create container widget for toggle + label
        showOverlayContainer = QWidget()
        showOverlayLayout = QHBoxLayout(showOverlayContainer)
        showOverlayLayout.setContentsMargins(0, 0, 0, 0)
        showOverlayLayout.setSpacing(1)
        showOverlayLayout.addWidget(self.showOverlayToggle)
        showOverlayLayout.addWidget(self.showOverlayLabel)
        
        layout.replaceWidget(self.showOverlayCheckBox, showOverlayContainer)
        self.showOverlayCheckBox.deleteLater()
        self.showOverlayToggle.setChecked(True)
        self.showOverlayToggle.clicked.connect(self._show_overlay_change)
        

    def _show_help_dialog(self):
        """Show the help dialog."""
        if self.help_dialog is None:
            self.help_dialog = HelpDialog(self)

        self.help_dialog.show()
        self.help_dialog.raise_()
        self.help_dialog.activateWindow()

    def keyPressEvent(self, e):
        """Handles key press events for navigation, hiding images, and adjustments.

        Args:
            e (QKeyEvent): Key event containing the key pressed.
        """
        if e.key() == Qt.Key_Right:
            self._nextImageButton_clicked()
        if e.key() == Qt.Key_Left:
            self._previousImageButton_clicked()
        if e.key() == Qt.Key_Down or e.key() == Qt.Key_P:
            self._hide_image_change(True)
        if e.key() == Qt.Key_Up or e.key() == Qt.Key_U:
            self._hide_image_change(False)
        if e.key() == Qt.Key_H and e.modifiers() == Qt.ControlModifier:
            self._open_image_adjustment_dialog()
        if e.key() == Qt.Key_M and e.modifiers() == Qt.ControlModifier:
            self._open_measure_dialog()
        if e.key() == Qt.Key_I and e.modifiers() == Qt.ControlModifier:
            self.showPOIsButton.setChecked(not self.showPOIsButton.isChecked())
            self._update_show_pois_button_style()
            self._highlight_pixels_change(self.showPOIsButton.isChecked())
        if e.key() == Qt.Key_H and e.modifiers() == Qt.NoModifier:
            # Toggle highlight pixels with 'H' key (no modifier)
            self.showPOIsButton.setChecked(not self.showPOIsButton.isChecked())
            self._update_show_pois_button_style()
            self._highlight_pixels_change(self.showPOIsButton.isChecked())
        if e.key() == Qt.Key_C and e.modifiers() == Qt.NoModifier:
            # Enter AOI creation mode with 'C' key (no modifier)
            self._enter_aoi_creation_mode()
        if e.key() == Qt.Key_R and e.modifiers() == Qt.NoModifier:
            # Show north-oriented image with 'R' key
            self.coordinate_controller.show_north_oriented_image()
        if e.key() == Qt.Key_F and e.modifiers() == Qt.ShiftModifier:
            # Check if cursor is within an AOI (Shift+F to select AOI at cursor)
            aoi_index, visible_index = self.aoi_controller.find_aoi_at_position(
                self.last_mouse_pos.x(), self.last_mouse_pos.y()
            )

            # If an AOI is found at the cursor, select it
            if aoi_index >= 0:
                self.aoi_controller.select_aoi(aoi_index, visible_index)
        if e.key() == Qt.Key_F and e.modifiers() == Qt.NoModifier:
            # Flag/unflag the currently selected AOI
            self.aoi_controller.toggle_aoi_flag()
        if e.key() == Qt.Key_M and e.modifiers() == Qt.NoModifier:
            # Show GPS map with 'M' key
            self.gps_map_controller.show_map()
        if e.key() == Qt.Key_O and e.modifiers() == Qt.ShiftModifier:
            # Manual altitude override with 'Shift+O' key
            self._manual_altitude_override()
        if e.key() == Qt.Key_E and e.modifiers() == Qt.ShiftModifier:
            # Export coverage extent KML with 'Shift+E' key
            self._export_coverage_extent_kml()
        if e.key() == Qt.Key_E and e.modifiers() == Qt.NoModifier:
            # Upscale currently visible portion with 'E' key
            self._open_upscale_dialog()

    def _load_images(self):
        """Loads and validates images from the XML file."""
        valid_images = []
        for index, image in enumerate(self.images[:]):
            path = Path(image['path'])
            image['name'] = path.name
            if path.is_file():
                try:
                    valid_images.append(image)
                except (UnidentifiedImageError, OSError):
                    pass  # Not a valid image
        self.images = valid_images

    def _setupViewer(self):
        if len(self.images) == 0:
            self._show_no_images_message()
        else:
            self._load_initial_image()
            self.helpButton.clicked.connect(self._show_help_dialog)
            self.previousImageButton.clicked.connect(self._previousImageButton_clicked)
            self.nextImageButton.clicked.connect(self._nextImageButton_clicked)

            self.aoiSortComboBox.currentTextChanged.connect(self.aoi_controller.on_sort_combo_changed)
            self.filterButton.clicked.connect(self.aoi_controller.open_filter_dialog)
        

            # Set the buttons in the AOI controller

            self.kmlButton.clicked.connect(self._kmlButton_clicked)
            self.pdfButton.clicked.connect(self._pdfButton_clicked)
            self.zipButton.clicked.connect(self._zipButton_clicked)
            self.measureButton.clicked.connect(self._open_measure_dialog)
            self.adjustmentsButton.clicked.connect(self._open_image_adjustment_dialog)
            self.magnifyButton.clicked.connect(self._magnifyButton_clicked)
            self.GPSMapButton.clicked.connect(self._gps_map_button_clicked)
            self.rotateImageButton.clicked.connect(self._rotate_image_button_clicked)
            # Initialize button styling
            self._update_magnify_button_style()
            self.ui_style_controller.update_adjustments_button_style()
            self.ui_style_controller.update_measure_button_style()
            self.ui_style_controller.update_gps_map_button_style()
            self.ui_style_controller.update_rotate_image_button_style()
            
            # Connect the POIs button
            if hasattr(self, 'showPOIsButton'):
                self.showPOIsButton.clicked.connect(self._on_show_pois_clicked)
                self.showPOIsButton.setToolTip("Show Pixels of Interest (H or Ctrl+I)")
                # Initialize button styling
                self._update_show_pois_button_style()
            
            # Connect the AOIs button
            if hasattr(self, 'showAOIsButton'):
                self.showAOIsButton.clicked.connect(self._on_show_aois_clicked)
                self.showAOIsButton.setToolTip("Toggle AOI Circles (C)")
                # Initialize button styling
                self._update_show_aois_button_style()
            
            self.jumpToLine.setValidator(QIntValidator(1, len(self.images), self))
            self.jumpToLine.editingFinished.connect(self._jumpToLine_changed)
            self.thumbnailScrollArea.horizontalScrollBar().valueChanged.connect(self.thumbnail_controller.on_thumbnail_scroll)

                    # Session variable to store GSD value
            self.current_gsd = None
            self.measure_dialog = None
            self.help_dialog = None
            
            # Dialog state tracking for button styling
            self.adjustments_dialog_open = False
            self.measure_dialog_open = False
            self.gps_map_open = False
            self.rotate_image_open = False

    def _load_initial_image(self):
        """Loads the initial image and its areas of interest."""
        try:
            # Find the first visible image
            self.current_image = None
            for i in range(0, len(self.images)):
                if not self.show_hidden and self.images[i]['hidden']:
                    continue
                self.current_image = i
                break
            if self.current_image is None:
                self.current_image = 0

            self.main_image = QtImageViewer(self, self.centralwidget)
            # Set a reasonable minimum size to prevent the widget from being too small
            self.main_image.setMinimumSize(QSize(400, 300))
            self.main_image.setObjectName("mainImage")
            self.main_image.aspectRatioMode = Qt.KeepAspectRatio
            self.main_image.canZoom = True
            self.main_image.canPan = True

            self.ImageLayout.replaceWidget(self.placeholderImage, self.main_image)
            # Now it's safe to delete the placeholder
            self.placeholderImage.deleteLater()
            self.main_image.viewport().installEventFilter(self)

            # Initialize magnifying glass controller
            self.magnifying_glass = MagnifyingGlass(self.main_image, self.logger, self)
            self.magnifying_glass_enabled = False

            # Initialize overlay widget
            self.overlay = OverlayWidget(self.main_image, self.scaleBar, self.theme, self.logger)
            
            # Connect signals
            self.main_image.zoomChanged.connect(self._update_scale_bar)
            self.main_image.mousePositionOnImageChanged.connect(self._mainImage_mouse_pos)

            # Initialize export controllers
            self.pdf_export = PDFExportController(self, self.logger)
            self.zip_export = ZipExportController(self, self.logger)
            self.caltopo_export = CalTopoExportController(self, self.logger)
            self.coverage_extent_export = CoverageExtentExportController(self, self.logger)
            self.unified_map_export = UnifiedMapExportController(self, self.logger)

            # Force the layout to update and ensure proper sizing
            self.ImageLayout.update()
            self.centralwidget.updateGeometry()
            QApplication.processEvents()

            # Load the image immediately - the widget should be properly sized now
            self.image_load_controller.load_image()

        except Exception as e:
            self.logger.error(e)

    def _load_image(self):
        """Loads the image at the current index along with areas of interest and GPS data."""
        # Delegate to ImageLoadController
        self.image_load_controller.load_image()

    def _previousImageButton_clicked(self):
        """Navigates to the previous image in the list, skipping hidden images if applicable."""
        # Prevent race conditions by checking if viewer is still valid
        if not hasattr(self, 'main_image') or self.main_image is None:
            return

        found = False
        for i in range(self.current_image - 1, -1, -1):
            if not self.show_hidden and self.images[i]['hidden']:
                continue
            found = True
            self.current_image = i
            break

        if not found:
            for i in range(len(self.images) - 1, self.current_image, -1):
                if not self.show_hidden and self.images[i]['hidden']:
                    continue
                self.current_image = i
                found = True
                break

        if found:
            self._load_image()
            if hasattr(self.thumbnail_controller, 'ui_component') and self.thumbnail_controller.ui_component:
                self.thumbnail_controller.ui_component.scroll_thumbnail_into_view()
        else:
            self._show_additional_images_message()

    def _nextImageButton_clicked(self):
        """Navigates to the next image in the list, skipping hidden images if applicable."""
        # Prevent race conditions by checking if viewer is still valid
        if not hasattr(self, 'main_image') or self.main_image is None:
            return

        found = False
        for i in range(self.current_image + 1, len(self.images)):
            if not self.show_hidden and self.images[i]['hidden']:
                continue
            found = True
            self.current_image = i
            break

        if not found:
            for i in range(0, self.current_image):
                if not self.show_hidden and self.images[i]['hidden']:
                    continue
                self.current_image = i
                found = True
                break

        if found:
            self._load_image()
            if hasattr(self.thumbnail_controller, 'ui_component') and self.thumbnail_controller.ui_component:
                self.thumbnail_controller.ui_component.scroll_thumbnail_into_view()
        else:
            self._show_additional_images_message()

    def _show_no_images_message(self):
        """Displays an error message when there are no available images."""
        self.status_controller.show_no_images_message()

    def _show_additional_images_message(self):
        """Displays an error message when there are no available images."""
        self.status_controller.show_additional_images_message()

    def _hide_image_change(self, state):
        """Toggles visibility of the current image and updates XML.

        Args:
            state (bool): True if the image should be hidden, False otherwise.
        """
        self.hideImageToggle.setChecked(state)
        image = self.images[self.current_image]
        image_element = image['xml']
        if image_element is not None:
            image_element.set('hidden', "True" if state else "False")
            self.xml_service.save_xml_file(self.xml_path)
            self.thumbnail_controller.update_thumbnail_overlay(self.current_image, state)
            if state:
                if not image['hidden']:
                    self.hidden_image_count += 1
            else:
                if image['hidden']:
                    self.hidden_image_count -= 1
            image['hidden'] = state
            self.skipHidden.setText(f"Skip Hidden ({self.hidden_image_count}) ")
            if state:
                self._nextImageButton_clicked()
        else:
            self.logger.error("Image XML element is None, cannot update 'hidden' attribute.")

    def _show_overlay_change(self, state):
        """Toggles visibility of the overlay.

        Args:
            state (bool): True if the overlay should be shown, False otherwise.
        """
        if hasattr(self, 'overlay'):
            # Get current direction and GSD to determine if overlay should be visible
            direction = None
            avg_gsd = None

            # Try to get current values from messages
            gsd_text = self.messages.get("Estimated Average GSD")
            if gsd_text:
                try:
                    avg_gsd = float(gsd_text.replace("cm/px", "").strip())
                except Exception:
                    pass

            direction_text = self.messages.get("Drone Orientation")
            if direction_text:
                try:
                    direction = float(direction_text.replace("°", "").strip())
                except Exception:
                    pass

            self.overlay.update_visibility(state, direction, avg_gsd)

    def _on_show_pois_clicked(self):
        """Handle Show POIs button click - update styling and toggle highlight."""
        self._update_show_pois_button_style()
        self._highlight_pixels_change(self.showPOIsButton.isChecked())

    def _on_show_aois_clicked(self):
        """Handle Show AOIs button click - update styling and toggle circles."""
        self._update_show_aois_button_style()
        self._draw_aoi_circle_change(self.showAOIsButton.isChecked())

    def _highlight_pixels_change(self, state):
        """Toggles highlighting of pixels of interest.

        Args:
            state (bool): True if pixels should be highlighted, False otherwise.
        """
        # Simply reload the image with current settings
        self._reload_current_image_preserving_view()

    def _draw_aoi_circle_change(self, state):
        """Toggles drawing of AOI circles in the main image.

        Args:
            state (bool): True if circles should be drawn, False otherwise.
        """
        # Simply reload the image with current settings
        self._reload_current_image_preserving_view()

    def _reload_current_image_preserving_view(self):
        """Reloads the current image while preserving zoom and pan state.

        This method respects both the draw AOI circle and highlight pixels toggles.
        """
        # Delegate to ImageLoadController
        self.image_load_controller.reload_image_preserving_view()

    def _open_image_adjustment_dialog(self):
        """Opens the image adjustment dialog for the current image."""
        if self.main_image is None:
            return

        # Get current pixmap from the image viewer
        current_pixmap = self.main_image.pixmap()
        if current_pixmap is None:
            return

        # Store original pixmap for restoration if cancelled
        self._original_pixmap = current_pixmap

        # Create and show the adjustment dialog
        dialog = ImageAdjustmentDialog(self, current_pixmap)

        # Connect the real-time adjustment signal
        dialog.imageAdjusted.connect(self._on_image_adjusted)

        # Update button state to show dialog is open
        self.adjustments_dialog_open = True
        self.ui_style_controller.update_adjustments_button_style()

        # Show dialog
        result = dialog.exec()

        # Update button state to show dialog is closed
        self.adjustments_dialog_open = False
        self.ui_style_controller.update_adjustments_button_style()

        # If user clicked Apply or OK, keep the adjustments
        if result == QDialog.Accepted:
            adjusted_pixmap = dialog.get_adjusted_pixmap()
            if adjusted_pixmap:
                self.main_image.setImage(adjusted_pixmap)
        # If user clicked Close/Cancel, restore original image
        else:
            self.main_image.setImage(self._original_pixmap)

    def _on_image_adjusted(self, adjusted_pixmap):
        """Handle real-time image adjustments from the dialog.

        Args:
            adjusted_pixmap (QPixmap): The adjusted image pixmap.
        """
        if self.main_image and adjusted_pixmap:
            self.main_image.setImage(adjusted_pixmap)

    def _open_upscale_dialog(self):
        """Extract visible portion of zoomed image and open upscale dialog."""
        if self.main_image is None or not self.main_image.hasImage():
            return

        try:
            # Get the currently visible viewport in scene coordinates
            visible_rect = self.main_image.mapToScene(
                self.main_image.viewport().rect()
            ).boundingRect()

            # Get the full image pixmap
            pixmap = self.main_image.pixmap()
            if pixmap is None:
                return

            # Convert QPixmap to QImage
            qimage = pixmap.toImage()
            width = qimage.width()
            height = qimage.height()

            # Convert to numpy array
            import qimage2ndarray
            full_image_array = qimage2ndarray.rgb_view(qimage)

            # Crop to visible portion (convert scene coords to image coords)
            # The scene coordinates should map directly to image pixels
            x1 = max(0, int(visible_rect.left()))
            y1 = max(0, int(visible_rect.top()))
            x2 = min(width, int(visible_rect.right()))
            y2 = min(height, int(visible_rect.bottom()))

            # Ensure we have a valid region
            if x2 <= x1 or y2 <= y1:
                return

            # Extract visible portion
            visible_portion = full_image_array[y1:y2, x1:x2].copy()

            # Open upscale dialog with the visible portion
            # Note: The dialog will perform the initial upscale, so we start at level 1
            # and it will immediately upscale to level 2 (or the specified factor)
            dialog = UpscaleDialog(self, visible_portion, upscale_factor=2, current_level=1, auto_upscale=True)
            dialog.show()

        except ImportError:
            QMessageBox.warning(
                self,
                "Missing Dependency",
                "The qimage2ndarray module is required for the upscale feature.\n"
                "Please install it using: pip install qimage2ndarray"
            )
        except Exception as e:
            import traceback
            print(f"Error opening upscale dialog: {e}")
            print(traceback.format_exc())
            QMessageBox.warning(
                self,
                "Upscale Error",
                f"An error occurred while opening the upscale dialog:\n{str(e)}"
            )

    def _skip_hidden_clicked(self, state):
        """Updates visibility setting for hidden images based on skipHidden checkbox.

        Args:
            state (bool): True if hidden images should be skipped, False otherwise.
        """
        self.show_hidden = not state

    def _jumpToLine_changed(self):
        """Jumps to the specified image index when changed in the jump line input."""
        if self.jumpToLine.text() != "":
            self.current_image = int(self.jumpToLine.text()) - 1
            self._load_image()
            if hasattr(self.thumbnail_controller, 'ui_component') and self.thumbnail_controller.ui_component:
                self.thumbnail_controller.ui_component.scroll_thumbnail_into_view()
            self.jumpToLine.setText("")

    def resizeEvent(self, event):
        """Handles window resize events to adjust the main image.

        Args:
            event (QResizeEvent): Resize event.
        """
        super().resizeEvent(event)
        if self.main_image is not None and not self.main_image._is_destroyed:
            if event.oldSize() != event.size():
                # Ensure image is properly resized to fit the new dimensions
                if self.main_image.hasImage():
                    self.main_image.resetZoom()
                else:
                    self.main_image.updateViewer()

    def _kmlButton_clicked(self):
        """Handles clicks on the Map Export button to show unified export options."""
        if hasattr(self, 'unified_map_export'):
            self.unified_map_export.show_export_dialog()

    def crop_image(self, img_arr, startx, starty, endx, endy):
        """Crops a portion of an image array.

        Args:
            img_arr (np.ndarray): The input image array.
            startx (int): Start x-coordinate.
            starty (int): Start y-coordinate.
            endx (int): End x-coordinate.
            endy (int): End y-coordinate.

        Returns:
            np.ndarray: The cropped image array.
        """
        sx, sy = max(0, startx), max(0, starty)
        ex, ey = min(img_arr.shape[1] - 1, endx), min(img_arr.shape[0] - 1, endy)
        return img_arr[sy:ey, sx:ex]

    def _pdfButton_clicked(self):
        """Handles clicks on the Generate PDF button."""
        if hasattr(self, 'pdf_export'):
            self.pdf_export.export_pdf(self.images, self.aoi_controller.flagged_aois)

    def _zipButton_clicked(self):
        """Handles clicks on the Generate Zip Bundle."""
        if hasattr(self, 'zip_export'):
            self.zip_export.export_zip(self.images)


    def _export_coverage_extent_kml(self):
        """Handles the export of coverage extent KML file for all images."""
        # Delegate to CoverageExtentExportController
        self.coverage_extent_export.export_coverage_extent_kml()

    def _magnifyButton_clicked(self):
        if self.main_image and self.main_image.hasImage():
            # Get center point of the image
            image_rect = self.main_image.sceneRect()
            center_x = image_rect.center().x()
            center_y = image_rect.center().y()
            self._toggle_magnifying_glass(center_x, center_y)
        else:
            self.logger.warning("No image available for magnifying glass")

    def _gps_map_button_clicked(self):
        """Handle GPS Map button click."""
        if hasattr(self, 'gps_map_controller'):
            self.gps_map_controller.show_map()

    def _rotate_image_button_clicked(self):
        """Handle Rotate Image button click."""
        if hasattr(self, 'coordinate_controller'):
            self.coordinate_controller.show_north_oriented_image()

    def _update_magnify_button_style(self):
        """Update the magnify button styling based on magnifying glass state."""
        # Delegate to UIStyleController
        self.ui_style_controller.update_magnify_button_style()

    def _update_show_pois_button_style(self):
        """Update the Show POIs button styling based on its checked state."""
        # Delegate to UIStyleController
        self.ui_style_controller.update_show_pois_button_style()

    def _update_show_aois_button_style(self):
        """Update the Show AOIs button styling based on its checked state."""
        # Delegate to UIStyleController
        self.ui_style_controller.update_show_aois_button_style()

    def _toggle_magnifying_glass(self, x, y):
        """Toggle the magnifying glass on/off when middle mouse button is pressed.

        Args:
            x (float): X coordinate where middle mouse was pressed
            y (float): Y coordinate where middle mouse was pressed
        """
        if hasattr(self, 'magnifying_glass'):
            self.magnifying_glass.toggle(x, y)
            # Update the enabled flag to match the magnifying glass state
            self.magnifying_glass_enabled = self.magnifying_glass.is_enabled()
            # Update button styling to reflect the state
            self._update_magnify_button_style()
        else:
            self.logger.warning("Magnifying glass not available")

    def _update_magnifying_glass(self, pos):
        """Update the magnifying glass position and content.

        Args:
            pos (QPoint): The current mouse position in image coordinates
        """
        if hasattr(self, 'magnifying_glass') and self.magnifying_glass.is_enabled():
            self.magnifying_glass.update_position(pos)

    def _update_scale_bar(self, zoom: float):
        """Update the scale bar through the overlay widget.

        Args:
            zoom: Current zoom level
        """
        if hasattr(self, 'overlay'):
            self.overlay.update_scale_bar(zoom, self.messages, self.distance_unit)

    def _mainImage_mouse_pos(self, pos):
        """Displays temperature data or color values at the mouse position.

        For thermal images: Shows temperature
        For HSV-based algorithms (HSVColorRange, RXAnomaly, MRMap): Shows H, S, V values
        For RGB-based algorithms (ColorRange, MatchedFilter): Shows R, G, B values

        The position is already in image coordinates, accounting for zoom/pan
        transformations handled by QtImageViewer's mapToScene method.

        Args:
            pos (QPoint): The current mouse position in image coordinates.
                         Will be (-1, -1) when cursor is outside the image.
        """
        # Store the current mouse position for AOI selection
        self.last_mouse_pos = pos

        # Delegate to PixelInfoController
        self.pixel_info_controller.update_cursor_info(pos)

        # Update magnifying glass if enabled
        if hasattr(self, 'magnifying_glass_enabled') and self.magnifying_glass_enabled and pos.x() >= 0 and pos.y() >= 0:
            self._update_magnifying_glass(pos)

    def _open_measure_dialog(self):
        """Opens the measure dialog for distance measurement."""
        if self.main_image is None or not self.main_image.hasImage():
            return

        # Try to get GSD from current image if we don't have a stored value
        if self.current_gsd is None:
            gsd_text = self.messages.get("Estimated Average GSD")  # e.g. '3.2cm/px'
            if gsd_text:
                try:
                    self.current_gsd = float(gsd_text.replace("cm/px", "").strip())
                except Exception:
                    pass

        if self.measure_dialog is None or not self.measure_dialog.isVisible():
            self.measure_dialog = MeasureDialog(self, self.main_image, self.current_gsd, self.distance_unit)
            self.measure_dialog.gsdChanged.connect(self._on_gsd_changed)
            
            # Connect to dialog close event to update button state
            self.measure_dialog.finished.connect(self._on_measure_dialog_closed)
            
            # Update button state to show dialog is open
            self.measure_dialog_open = True
            self.ui_style_controller.update_measure_button_style()
            
            self.measure_dialog.show()

    def _on_gsd_changed(self, gsd_value):
        """Updates the stored GSD value.

        Args:
            gsd_value (float): The new GSD value in cm/px.
        """
        self.current_gsd = gsd_value

    def _on_measure_dialog_closed(self):
        """Handle measure dialog close event."""
        self.measure_dialog_open = False
        self.ui_style_controller.update_measure_button_style()

    def _prompt_for_custom_agl_altitude(self):
        """Prompt user for custom AGL altitude when negative altitude is detected."""
        # Delegate to AltitudeController
        self.altitude_controller.prompt_for_custom_altitude(auto_triggered=True)

    def _manual_altitude_override(self):
        """Prompt user to manually override altitude for all images."""
        # Delegate to AltitudeController
        self.altitude_controller.manual_altitude_override()


    def _enter_aoi_creation_mode(self):
        """Enter AOI creation mode - user can click and drag to draw a circle."""
        # Delegate to AOIController
        self.aoi_controller.enter_creation_mode()

    def _exit_aoi_creation_mode(self):
        """Exit AOI creation mode and clean up."""
        # Delegate to AOIController
        self.aoi_controller.exit_creation_mode()

    def _apply_icons(self):
        """Apply themed icons to all buttons in the viewer."""
        from helpers.IconHelper import IconHelper
        
        self.magnifyButton.setIcon(IconHelper.create_icon('fa6s.magnifying-glass', self.theme))
        self.kmlButton.setIcon(IconHelper.create_icon('fa5s.map-marker-alt', self.theme))
        self.pdfButton.setIcon(IconHelper.create_icon('fa6s.file-pdf', self.theme))
        self.zipButton.setIcon(IconHelper.create_icon('fa5s.file-archive', self.theme))
        self.measureButton.setIcon(IconHelper.create_icon('fa6s.ruler', self.theme))
        self.adjustmentsButton.setIcon(IconHelper.create_icon('fa6s.sliders', self.theme))
        self.previousImageButton.setIcon(IconHelper.create_icon('fa6s.arrow-left', self.theme))
        self.nextImageButton.setIcon(IconHelper.create_icon('fa6s.arrow-right', self.theme))
        self.filterButton.setIcon(IconHelper.create_icon('fa6s.filter', self.theme))
        self.helpButton.setIcon(IconHelper.create_icon('fa6s.question', self.theme, options=[{'scale_factor': 1.5}]))
        self.showPOIsButton.setIcon(IconHelper.create_icon('mdi.scatter-plot', self.theme))
        self.showAOIsButton.setIcon(IconHelper.create_icon('fa6.circle', self.theme))
        self.GPSMapButton.setIcon(IconHelper.create_icon('fa6s.map-location-dot', self.theme))
        self.rotateImageButton.setIcon(IconHelper.create_icon('fa6s.compass', self.theme))

    # Qt event filter for viewport resize events and middle mouse button

    def eventFilter(self, obj, ev):
        """Event filter to handle middle mouse button clicks for magnifying glass."""
        # Check if this is a mouse button press event on the main image viewport
        if obj == self.main_image.viewport() and ev.type() == QEvent.MouseButtonPress:
            if ev.button() == Qt.MiddleButton:
                # Get mouse position in scene coordinates
                view_pos = ev.pos()
                scene_pos = self.main_image.mapToScene(view_pos)
                
                if self.main_image.hasImage():
                    # Toggle magnifying glass at the clicked position
                    self._toggle_magnifying_glass(scene_pos.x(), scene_pos.y())
                    return True  # Event handled
        
        # Overlay positioning is now handled automatically by the overlay widget
        return super().eventFilter(obj, ev)
