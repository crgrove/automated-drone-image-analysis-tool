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
from pathlib import Path
from urllib.parse import quote_plus

from PySide6.QtGui import QImage, QIntValidator, QPixmap, QIcon, QPainter, QFont, QPen, QPalette, QColor, QDesktopServices, QBrush, QCursor
from PySide6.QtCore import Qt, QSize, QThread, QPointF, QPoint, QEvent, QTimer, QUrl, QRectF, QObject
from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox, QListWidgetItem, QFileDialog, QApplication
from PySide6.QtWidgets import QPushButton, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QAbstractButton, QMenu

from core.views.components.Toggle import Toggle
from core.views.Viewer_ui import Ui_Viewer
from core.views.components.QtImageViewer import QtImageViewer

from core.controllers.viewer.status.StatusDict import StatusDict

from core.controllers.viewer.components.ImageAdjustmentDialog import ImageAdjustmentDialog
from core.controllers.viewer.components.ScaleBarWidget import ScaleBarWidget
from core.controllers.viewer.components.LoadingDialog import LoadingDialog
from core.controllers.viewer.components.MeasureDialog import MeasureDialog
from core.controllers.viewer.components.MagnifyingGlass import MagnifyingGlass
from core.controllers.viewer.components.OverlayWidget import OverlayWidget

from core.controllers.viewer.exports.KMLExportController import KMLExportController
from core.controllers.viewer.exports.PDFExportController import PDFExportController
from core.controllers.viewer.exports.ZipExportController import ZipExportController

from core.controllers.viewer.aoi.AOIController import AOIController
from core.controllers.viewer.thumbnails.ThumbnailController import ThumbnailController
from core.controllers.viewer.coordinates.CoordinateController import CoordinateController
from core.controllers.viewer.status.StatusController import StatusController

from core.services.LoggerService import LoggerService
from core.services.XmlService import XmlService
from core.services.ImageService import ImageService
from core.services.ThermalParserService import ThermalParserService
from helpers.LocationInfo import LocationInfo


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
        self.aoi_controller = AOIController(self, self.logger)
        self.thumbnail_controller = ThumbnailController(self, self.logger)
        self.coordinate_controller = CoordinateController(self, self.logger)
        self.status_controller = StatusController(self, self.logger)

        # Initialize GPS map controller
        from core.controllers.viewer.gps import GPSMapController
        self.gps_map_controller = GPSMapController(self, self.logger)

        # Load flagged AOIs from XML
        self.aoi_controller.initialize_from_xml(self.images)
        self.is_thermal = (self.settings['thermal'] == 'True')
        self.position_format = position_format
        self.temperature_data = None
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
                                              "Drone Orientation", "Estimated Average GSD",
                                              "Temperature", "Color Values"])
        self._reapply_icons(self.theme)
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

        # scale bar (will be used by overlay widget)
        self.scaleBar = ScaleBarWidget()

        # ---- load everything ----
        self._load_images()

        # Set up UI elements for controllers
        self.aoi_controller.set_ui_elements(self.aoiListWidget, self.areaCountLabel, None)  # flag button will be set later
        self.thumbnail_controller.set_ui_elements(self.thumbnailLayout, self.thumbnailScrollArea)
        self.status_controller.set_ui_elements(self.statusBar, self._toastLabel, self._toastTimer, self.messages)

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

        event.accept()

    def _add_Toggles(self):
        """Replaces checkboxs with a toggle button."""
        self.hideImageToggle = Toggle()
        self.ButtonLayout.replaceWidget(self.hideImageCheckbox, self.hideImageToggle)
        self.hideImageCheckbox.deleteLater()
        self.hideImageToggle.clicked.connect(self._hide_image_change)
        self.showOverlayToggle = Toggle()
        layout = self.TitleWidget.layout()
        layout.replaceWidget(self.showOverlayCheckBox, self.showOverlayToggle)
        self.showOverlayCheckBox.deleteLater()
        self.showOverlayLabel = QLabel("Show Overlay")
        font = QFont()
        font.setPointSize(10)
        self.showOverlayLabel.setFont(font)
        layout.insertWidget(layout.indexOf(self.showOverlayToggle) + 1, self.showOverlayLabel)
        self.showOverlayToggle.setChecked(True)
        self.showOverlayToggle.clicked.connect(self._show_overlay_change)

        # Add highlight pixels of interest toggle
        self.highlightPixelsToggle = Toggle()
        layout.replaceWidget(self.highlightPixelsOfInterestCheckBox, self.highlightPixelsToggle)
        self.highlightPixelsOfInterestCheckBox.deleteLater()

        layout.insertWidget(layout.indexOf(self.showOverlayLabel) + 1, self.highlightPixelsToggle)
        self.highlightPixelsLabel = QLabel("Highlight Pixels of Interest")
        self.highlightPixelsLabel.setFont(font)
        layout.insertWidget(layout.indexOf(self.highlightPixelsToggle) + 1, self.highlightPixelsLabel)
        self.highlightPixelsToggle.setChecked(False)
        self.highlightPixelsToggle.clicked.connect(self._highlight_pixels_change)
        self.highlightPixelsToggle.setToolTip("Highlight Pixels of Interest (H or Ctrl+I)")

        # Add draw AOI circle toggle
        self.showAOIsToggle = Toggle()
        layout.replaceWidget(self.showAOIsCheckBox, self.showAOIsToggle)
        self.showAOIsCheckBox.deleteLater()

        layout.insertWidget(layout.indexOf(self.highlightPixelsLabel) + 1, self.showAOIsToggle)
        self.drawAOICircleLabel = QLabel("Show AOIs")
        self.drawAOICircleLabel.setFont(font)
        layout.insertWidget(layout.indexOf(self.showAOIsToggle) + 1, self.drawAOICircleLabel)
        self.showAOIsToggle.setChecked(True)  # Default to showing circles
        self.showAOIsToggle.clicked.connect(self._draw_aoi_circle_change)
        self.showAOIsToggle.setToolTip("Toggle AOI Circles (C)")

        # Add measure button to toolbar

        # Session variable to store GSD value
        self.current_gsd = None
        self.measure_dialog = None

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
            self._highlight_pixels_change(not self.highlightPixelsToggle.isChecked())
        if e.key() == Qt.Key_H and e.modifiers() == Qt.NoModifier:
            # Toggle highlight pixels with 'H' key (no modifier)
            self.highlightPixelsToggle.setChecked(not self.highlightPixelsToggle.isChecked())
            self._highlight_pixels_change(self.highlightPixelsToggle.isChecked())
        if e.key() == Qt.Key_C and e.modifiers() == Qt.NoModifier:
            # Toggle AOI circle drawing with 'C' key (no modifier)
            self.showAOIsToggle.setChecked(not self.showAOIsToggle.isChecked())
            self._draw_aoi_circle_change(self.showAOIsToggle.isChecked())
        if e.key() == Qt.Key_R and e.modifiers() == Qt.NoModifier:
            # Show north-oriented image with 'R' key
            self.coordinate_controller.show_north_oriented_image()
        if e.key() == Qt.Key_F and e.modifiers() == Qt.NoModifier:
            # Flag/unflag the currently selected AOI
            self.aoi_controller.toggle_aoi_flag()
        if e.key() == Qt.Key_M and e.modifiers() == Qt.NoModifier:
            # Show GPS map with 'M' key
            self.gps_map_controller.show_map()

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
            self.previousImageButton.clicked.connect(self._previousImageButton_clicked)
            self.nextImageButton.clicked.connect(self._nextImageButton_clicked)

            # Create flag filter button and add it immediately
            self.flagFilterButton = QPushButton("🚩 Filter")
            self.flagFilterButton.setToolTip("Toggle filter to show only flagged AOIs")
            self.flagFilterButton.setFixedSize(80, 30)
            self.flagFilterButton.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QPushButton:checked {
                    background-color: #ff4444;
                    border: 2px solid #ff0000;
                    color: white;
                    font-weight: bold;
                }
            """)
            self.flagFilterButton.setCheckable(True)
            self.flagFilterButton.clicked.connect(self.aoi_controller.toggle_flag_filter)

            # Set the flag button in the AOI controller
            self.aoi_controller.set_ui_elements(self.aoiListWidget, self.areaCountLabel, self.flagFilterButton)

            # Try multiple approaches to add the button
            # Approach 1: Add next to measureButton (which is visible in your screenshot)
            if hasattr(self, 'measureButton'):
                parent = self.measureButton.parent()
                if parent and parent.layout():
                    layout = parent.layout()
                    for i in range(layout.count()):
                        if layout.itemAt(i).widget() == self.measureButton:
                            layout.insertWidget(i + 1, self.flagFilterButton)
                            self.flagFilterButton.show()
                            break

            # Approach 2: Also try adding after nextImageButton
            self.aoi_controller.add_flag_button_to_layout()

            self.kmlButton.clicked.connect(self._kmlButton_clicked)
            self.pdfButton.clicked.connect(self._pdfButton_clicked)
            self.zipButton.clicked.connect(self._zipButton_clicked)
            self.measureButton.clicked.connect(self._open_measure_dialog)
            self.adjustmentsButton.clicked.connect(self._open_image_adjustment_dialog)
            self.magnifyButton.clicked.connect(self._magnifyButton_clicked)
            # Initialize magnify button styling
            self._update_magnify_button_style()
            self.jumpToLine.setValidator(QIntValidator(1, len(self.images), self))
            self.jumpToLine.editingFinished.connect(self._jumpToLine_changed)
            self.thumbnailScrollArea.horizontalScrollBar().valueChanged.connect(self.thumbnail_controller.on_thumbnail_scroll)

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

            # Initialize export controllers
            self.kml_export = KMLExportController(self, self.logger)
            self.pdf_export = PDFExportController(self, self.logger)
            self.zip_export = ZipExportController(self, self.logger)

            # Force the layout to update and ensure proper sizing
            self.ImageLayout.update()
            self.centralwidget.updateGeometry()
            QApplication.processEvents()

            # Load the image immediately - the widget should be properly sized now
            self._load_image()

        except Exception as e:
            self.logger.error(e)

    def _load_image(self):
        """Loads the image at the current index along with areas of interest and GPS data."""
        try:
            # Prevent race conditions by checking if main_image is still valid
            if not hasattr(self, 'main_image') or self.main_image is None or self.main_image._is_destroyed:
                return

            # Clear previous status
            self.messages['GPS Coordinates'] = self.messages['Relative Altitude'] = self.messages['Drone Orientation'] = None
            self.messages['Estimated Average GSD'] = self.messages['Temperature'] = None

            # Hide magnifying glass when loading new image
            if hasattr(self, 'magnifying_glass'):
                self.magnifying_glass._hide()
                # Update the enabled flag and button styling
                self.magnifying_glass_enabled = self.magnifying_glass.is_enabled()
                self._update_magnify_button_style()

            image = self.images[self.current_image]

            # Always sync the active thumbnail/index, even if widget not built yet
            if 'thumbnail' in image:
                self.thumbnail_controller.set_active_thumbnail(image['thumbnail'])
            else:
                self.thumbnail_controller.set_active_index(self.current_image)

            # Update GPS map if it's open
            self.gps_map_controller.update_current_image(self.current_image)

            # Use original image path if available (mask-based approach)
            # Fall back to path for legacy support
            image_path = image.get('path', '')
            mask_path = image.get('mask_path', '')

            # Load the original image
            # Note: When using mask-based storage, image_path should already point to the original source image

            # Check if file exists
            if not os.path.exists(image_path):
                self.logger.error(f"Image file does not exist: {image_path}")
                return

            try:
                image_service = ImageService(image_path, mask_path)
            except Exception:
                raise

            # Store reference to ImageService for later use
            self.current_image_service = image_service

            # Cache the image array for pixel value display - with better memory handling

            has_img_array = hasattr(image_service, 'img_array')

            if has_img_array:
                try:
                    img_arr = image_service.img_array
                    if img_arr is not None:
                        # Just store the reference, skip all the shape checking for now
                        self.current_image_array = img_arr
                    else:
                        self.current_image_array = None
                except Exception:
                    self.current_image_array = None
            else:
                self.current_image_array = None

            # Draw AOI boundaries (circles or contours) if toggle is enabled
            if hasattr(self, 'showAOIsToggle') and self.showAOIsToggle.isChecked():
                augmented_image = image_service.circle_areas_of_interest(self.settings['identifier_color'], image['areas_of_interest'])
            else:
                # Get the original image without circles
                # Use reference instead of copy to avoid crash
                augmented_image = image_service.img_array

            # Highlight pixels of interest if toggle is enabled
            if hasattr(self, 'highlightPixelsToggle') and self.highlightPixelsToggle.isChecked():
                if mask_path:
                    # Use mask-based highlighting (new efficient approach)
                    # Pass the identifier color from settings to match AOI circle color
                    augmented_image = image_service.apply_mask_highlight(
                        augmented_image,
                        mask_path,
                        self.settings['identifier_color'],
                        image['areas_of_interest']
                    )
                else:
                    # Fall back to old method for backward compatibility
                    augmented_image = image_service.highlight_aoi_pixels(augmented_image, image['areas_of_interest'])

            img = QImage(qimage2ndarray.array2qimage(augmented_image))

            # Critical section: check if widget is still valid before setting image
            if not hasattr(self, 'main_image') or self.main_image is None or self.main_image._is_destroyed:
                return

            self.main_image.setImage(img)
            self.fileNameLabel.setText(image['name'])

            # For AOI thumbnails, we don't need to draw circles on the full image
            # Just pass the base image array - circles can be drawn on individual crops if needed
            # Use the base image array for AOI thumbnails (no need to process full image)
            self.aoi_controller.load_areas_of_interest(image_service.img_array, image['areas_of_interest'], self.current_image)

            # Check again before resetting zoom
            if not hasattr(self, 'main_image') or self.main_image is None or getattr(self.main_image, '_is_destroyed', True):
                return

            # Ensure the image is properly loaded before resetting zoom
            if not self.main_image.hasImage():
                return

            # Reset zoom to fit image properly
            # Guard resetZoom against deleted C++ object
            try:
                self.main_image.resetZoom()
            except RuntimeError:
                return
            self.main_image.setFocus()
            self.hideImageToggle.setChecked(image['hidden'])
            self.indexLabel.setText(f"Image {self.current_image + 1} of {len(self.images)}")

            altitude = image_service.get_relative_altitude(self.distance_unit)
            if altitude:
                self.messages['Relative Altitude'] = f"{altitude} {self.distance_unit}"
            direction = image_service.get_drone_orientation()
            if direction is not None:
                self.messages['Drone Orientation'] = f"{direction}°"
            else:
                self.messages['Drone Orientation'] = None
            avg_gsd = image_service.get_average_gsd()
            if avg_gsd is not None:
                self.messages['Estimated Average GSD'] = f"{avg_gsd}cm/px"
            else:
                self.messages['Estimated Average GSD'] = None
            position = image_service.get_position(self.position_format)
            if position:
                self.messages['GPS Coordinates'] = position
            # also keep decimal coords for sharing/opening links
            try:
                gps = LocationInfo.get_gps(exif_data=image_service.exif_data)
                if gps and 'latitude' in gps and 'longitude' in gps:
                    self.coordinate_controller.update_current_coordinates((gps['latitude'], gps['longitude']))
                else:
                    self.coordinate_controller.update_current_coordinates(None)
            except Exception:
                self.coordinate_controller.update_current_coordinates(None)
            if self.is_thermal:
                # First try to get thermal data from XMP metadata
                self.temperature_data = image_service.get_thermal_data(self.temperature_unit)

                # If no thermal data in XMP, try to parse it directly from the thermal image
                if self.temperature_data is None:
                    try:
                        # Check if this is a thermal image file
                        if image_path.lower().endswith(('.jpg', '.jpeg', '.rjpeg')):
                            thermal_parser = ThermalParserService(dtype=np.float32)
                            temperature_c, _ = thermal_parser.parse_file(image_path)

                            # Convert to the desired unit
                            if self.temperature_unit == 'F' and temperature_c is not None:
                                self.temperature_data = temperature_c * 1.8 + 32.0
                            else:
                                self.temperature_data = temperature_c
                    except Exception as e:
                        self.logger.error(f"Failed to parse thermal data from image: {e}")
                        self.temperature_data = None
            # Connect signals only once
            if not hasattr(self, '_signals_connected'):
                self.main_image.mousePositionOnImageChanged.connect(self._mainImage_mouse_pos)
                self.main_image.middleMouseButtonPressed.connect(self._toggle_magnifying_glass)
                self.main_image.zoomChanged.connect(self._update_scale_bar)
                self._signals_connected = True

            self._update_scale_bar(self.main_image.getZoom())

            # Update overlay with new image data - AFTER zoom reset so scene is properly set up
            if hasattr(self, 'overlay'):
                self.overlay.rotate_north_icon(direction)
                self.overlay.update_visibility(
                    self.showOverlayToggle.isChecked(),
                    direction,
                    avg_gsd
                )
                # Position the overlay after image is loaded and zoomed
                self.overlay._place_overlay()
        except Exception as e:
            error_msg = f"Error loading image {self.current_image + 1}: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(f"Traceback:\n{traceback.format_exc()}")
            print(f"\n{'='*60}")
            print("ERROR IN VIEWER - _load_image()")
            print(f"Image index: {self.current_image}")
            if image:
                print(f"Image path: {image.get('path', 'N/A')}")
                print(f"Mask path: {image.get('mask_path', 'N/A')}")
            print(f"Error: {str(e)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            print(f"{'='*60}\n")
            # Show error to user
            QMessageBox.critical(self, "Error Loading Image", error_msg)

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
            self.thumbnail_controller.scroll_thumbnail_into_view()
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
            self.thumbnail_controller.scroll_thumbnail_into_view()
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
        if not hasattr(self, 'main_image') or self.main_image is None:
            return

        # Save the current zoom stack and viewport to preserve state
        saved_zoom_stack = self.main_image.zoomStack.copy() if self.main_image.zoomStack else []
        saved_transform = self.main_image.transform()

        # Save AOI list scroll position
        aoi_scroll_pos = self.aoiListWidget.verticalScrollBar().value() if hasattr(self, 'aoiListWidget') else 0

        # Reload just the image content without resetting view
        image = self.images[self.current_image]
        image_path = image.get('path', '')
        mask_path = image.get('mask_path', '')

        # Load and process the image
        image_service = ImageService(image_path, mask_path)

        # Update the cached image array - using reference to avoid crash
        # Store the service reference to keep data alive
        self.current_image_service = image_service
        self.current_image_array = image_service.img_array

        # Start with the base image or with circles based on toggle
        if hasattr(self, 'showAOIsToggle') and self.showAOIsToggle.isChecked():
            augmented_image = image_service.circle_areas_of_interest(self.settings['identifier_color'], image['areas_of_interest'])
        else:
            # Use reference instead of copy to avoid crash
            augmented_image = image_service.img_array

        # Apply highlight if enabled (independent of circle drawing)
        if hasattr(self, 'highlightPixelsToggle') and self.highlightPixelsToggle.isChecked():
            if mask_path:
                augmented_image = image_service.apply_mask_highlight(
                    augmented_image,
                    self.settings['identifier_color'],
                    image['areas_of_interest']
                )
            else:
                augmented_image = image_service.highlight_aoi_pixels(augmented_image, image['areas_of_interest'])

        # Update the image without resetting the view
        img = QImage(qimage2ndarray.array2qimage(augmented_image))

        # Temporarily block zoom stack updates
        self.main_image.zoomStack = saved_zoom_stack

        # Set the new image
        self.main_image.setImage(img)

        # Restore the transform exactly
        self.main_image.setTransform(saved_transform)

        # Restore zoom stack
        self.main_image.zoomStack = saved_zoom_stack

        # Force emit zoom to update any UI elements
        self.main_image._emit_zoom_if_changed()

        # Restore AOI list scroll position
        if hasattr(self, 'aoiListWidget') and aoi_scroll_pos > 0:
            self.aoiListWidget.verticalScrollBar().setValue(aoi_scroll_pos)

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

        # Show dialog
        result = dialog.exec()

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
            self.thumbnail_controller.scroll_thumbnail_into_view()
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
        """Handles clicks on the Generate KML button to create a KML file."""
        if hasattr(self, 'kml_export'):
            self.kml_export.export_kml(self.images, self.aoi_controller.flagged_aois)

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

    # ---------- coordinates popup ----------

    def _show_aoi_context_menu(self, pos, label_widget, center, pixel_area, avg_info=None):
        """Show context menu for AOI coordinate label with copy option.

        Args:
            pos: Position where the context menu was requested (relative to label_widget)
            label_widget: The QLabel widget that was right-clicked
            center: Tuple of (x, y) coordinates of the AOI center
            pixel_area: The area of the AOI in pixels
            avg_info: Average color/temperature information string
        """
        menu = QMenu(label_widget)

        # Style the menu to match the application theme
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                color: white;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
        """)

        # Add copy action
        copy_action = menu.addAction("Copy Data")
        copy_action.triggered.connect(lambda: self._copy_aoi_data(center, pixel_area, avg_info))

        # Get the current cursor position (global coordinates)
        global_pos = QCursor.pos()

        # Show menu at cursor position
        menu.exec(global_pos)

    def _copy_aoi_data(self, center, pixel_area, avg_info=None):
        """Copy AOI data to clipboard including image name, coordinates, and GPS.

        Args:
            center: Tuple of (x, y) coordinates of the AOI center
            pixel_area: The area of the AOI in pixels
            avg_info: Average color/temperature information string
        """
        # Get current image information
        image = self.images[self.current_image]
        image_name = image.get('name', 'Unknown')

        # Get GPS coordinates if available
        gps_coords = self.messages.get('GPS Coordinates', 'N/A')

        # Format the data for clipboard
        clipboard_text = (
            f"Image: {image_name}\n"
            f"AOI Coordinates: X={center[0]}, Y={center[1]}\n"
            f"AOI Area: {pixel_area:.0f} px\n"
        )

        # Add average info if available
        if avg_info:
            clipboard_text += f"Average: {avg_info}\n"

        clipboard_text += f"GPS Coordinates: {gps_coords}"

        # Copy to clipboard
        QApplication.clipboard().setText(clipboard_text)

        # Show confirmation toast
        self.status_controller.show_toast("AOI data copied", 2000, color="#00C853")

    def _magnifyButton_clicked(self):
        if self.main_image and self.main_image.hasImage():
            # Get center point of the image
            image_rect = self.main_image.sceneRect()
            center_x = image_rect.center().x()
            center_y = image_rect.center().y()
            self._toggle_magnifying_glass(center_x, center_y)
        else:
            self.logger.warning("No image available for magnifying glass")

    def _update_magnify_button_style(self):
        """Update the magnify button styling based on magnifying glass state."""
        if hasattr(self, 'magnifyButton') and hasattr(self, 'magnifying_glass_enabled'):
            # Set a property to track the active state
            self.magnifyButton.setProperty("magnifyActive", self.magnifying_glass_enabled)

            if self.magnifying_glass_enabled:
                # Active state - highlight the button with theme-aware colors
                # Use a blue highlight similar to other active elements in the app
                if hasattr(self, 'theme') and self.theme.lower() == 'light':
                    # Light theme colors
                    style = """
                        QToolButton[magnifyActive="true"] {
                            background-color: #4A90E2;
                            border: 2px solid #357ABD;
                            border-radius: 4px;
                        }
                        QToolButton[magnifyActive="true"]:hover {
                            background-color: #5BA0F2;
                            border: 2px solid #4A90E2;
                        }
                        QToolButton[magnifyActive="false"] {
                            background-color: transparent;
                            border: none;
                        }
                    """
                else:
                    # Dark theme colors (more muted but still visible)
                    style = """
                        QToolButton[magnifyActive="true"] {
                            background-color: #5A7FB8;
                            border: 2px solid #4A6B9A;
                            border-radius: 4px;
                        }
                        QToolButton[magnifyActive="true"]:hover {
                            background-color: #6A8FC8;
                            border: 2px solid #5A7FB8;
                        }
                        QToolButton[magnifyActive="false"] {
                            background-color: transparent;
                            border: none;
                        }
                    """
                self.magnifyButton.setStyleSheet(style)
            else:
                # Inactive state - use the same stylesheet but the property will make it use the inactive rules
                if hasattr(self, 'theme') and self.theme.lower() == 'light':
                    style = """
                        QToolButton[magnifyActive="true"] {
                            background-color: #4A90E2;
                            border: 2px solid #357ABD;
                            border-radius: 4px;
                        }
                        QToolButton[magnifyActive="true"]:hover {
                            background-color: #5BA0F2;
                            border: 2px solid #4A90E2;
                        }
                        QToolButton[magnifyActive="false"] {
                            background-color: transparent;
                            border: none;
                        }
                    """
                else:
                    style = """
                        QToolButton[magnifyActive="true"] {
                            background-color: #5A7FB8;
                            border: 2px solid #4A6B9A;
                            border-radius: 4px;
                        }
                        QToolButton[magnifyActive="true"]:hover {
                            background-color: #6A8FC8;
                            border: 2px solid #5A7FB8;
                        }
                        QToolButton[magnifyActive="false"] {
                            background-color: transparent;
                            border: none;
                        }
                    """
                self.magnifyButton.setStyleSheet(style)

            # Force the style to be reapplied
            self.magnifyButton.style().unpolish(self.magnifyButton)
            self.magnifyButton.style().polish(self.magnifyButton)
            self.magnifyButton.update()
        else:
            self.logger.warning(
                f"Cannot update magnify button style: magnifyButton={hasattr(self, 'magnifyButton')}, "
                f"enabled={hasattr(self, 'magnifying_glass_enabled')}"
            )

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
        # Clear previous cursor position message
        if "Cursor Position" in self.messages:
            self.messages["Cursor Position"] = None
        # Clear previous color values message
        if "Color Values" in self.messages:
            self.messages["Color Values"] = None

        if self.temperature_data is not None:
            # Check if cursor is within valid image bounds
            if pos.x() >= 0 and pos.y() >= 0:
                shape = self.temperature_data.shape
                # Ensure position is within temperature data array bounds
                if (0 <= pos.y() < shape[0]) and (0 <= pos.x() < shape[1]):
                    temp_value = self.temperature_data[pos.y()][pos.x()]
                    # Format temperature with 1 decimal place for cleaner display
                    temp_display = f"{temp_value:.1f}° {self.temperature_unit} at ({pos.x()}, {pos.y()})"
                    self.messages["Temperature"] = temp_display
                else:
                    # Cursor is on image but outside temperature data bounds
                    self.messages["Temperature"] = None
            else:
                # Cursor is outside the image
                self.messages["Temperature"] = None
        else:
            # No temperature data available (non-thermal image)
            self.messages["Temperature"] = None

            # Display color values for non-thermal images only
            # Check if this is actually a non-thermal algorithm
            algorithm_name = self.settings.get('algorithm', '')
            if algorithm_name not in ['ThermalRange', 'ThermalAnomaly']:
                if pos.x() >= 0 and pos.y() >= 0:
                    # Only show color values if cursor is on the image
                    if hasattr(self, 'main_image') and self.main_image and self.main_image.hasImage():
                        try:
                            # Use cached image array if available
                            if self.current_image_array is not None:
                                img_array = self.current_image_array
                            elif self.current_image_service is not None and hasattr(self.current_image_service, 'img_array'):
                                # Use the stored ImageService reference
                                img_array = self.current_image_service.img_array
                            else:
                                # Fallback: load image if both cache and service are missing
                                image = self.images[self.current_image]
                                image_path = image.get('path', '')
                                mask_path = image.get('mask_path', '')
                                image_service = ImageService(image_path, mask_path)
                                img_array = image_service.img_array
                                # Store reference instead of copying
                                self.current_image_service = image_service
                                self.current_image_array = img_array

                            # Check bounds
                            if (0 <= pos.y() < img_array.shape[0]) and (0 <= pos.x() < img_array.shape[1]):
                                # Get RGB values at cursor position
                                r, g, b = img_array[pos.y(), pos.x()]

                                # Determine which values to display based on algorithm
                                if algorithm_name in ['HSVColorRange', 'RXAnomaly', 'MRMap']:
                                    # Display HSV values
                                    # Convert RGB to HSV
                                    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
                                    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)

                                    # Convert to standard ranges: H (0-360), S (0-100), V (0-100)
                                    h_deg = int(h * 360)
                                    s_pct = int(s * 100)
                                    v_pct = int(v * 100)

                                    color_display = f"H: {h_deg}°, S: {s_pct}%, V: {v_pct}% at ({pos.x()}, {pos.y()})"
                                    self.messages["Color Values"] = color_display
                                elif algorithm_name in ['ColorRange', 'MatchedFilter', 'AIPersonDetector']:
                                    # Display RGB values
                                    color_display = f"R: {r}, G: {g}, B: {b} at ({pos.x()}, {pos.y()})"
                                    self.messages["Color Values"] = color_display
                                else:
                                    # Default to RGB for unknown algorithms
                                    color_display = f"R: {r}, G: {g}, B: {b} at ({pos.x()}, {pos.y()})"
                                    self.messages["Color Values"] = color_display
                        except Exception as e:
                            # Log error but don't show to user
                            self.logger.error(f"Error getting pixel values: {e}")

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
            self.measure_dialog.show()

    def _on_gsd_changed(self, gsd_value):
        """Updates the stored GSD value.

        Args:
            gsd_value (float): The new GSD value in cm/px.
        """
        self.current_gsd = gsd_value

    def _reapply_icons(self, theme):
        """
        Reloads icon assets based on the currently selected theme.

        Args:
            theme (str): Name of the active theme used to resolve icon paths.
        """
        # decide which sub‑folder of your resources to use:
        for btn in self.findChildren(QAbstractButton):
            name = btn.property("iconName")
            if name:
                # set the icon from the correct prefix
                btn.setIcon(QIcon(f":/icons/{theme.lower()}/{name}"))
                btn.repaint()

    # Qt event filter for viewport resize events

    def eventFilter(self, obj, ev):
        # Overlay positioning is now handled automatically by the overlay widget
        return super().eventFilter(obj, ev)
