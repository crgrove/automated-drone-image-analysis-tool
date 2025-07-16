import qimage2ndarray
from PIL import Image, UnidentifiedImageError

import math
import numpy as np
from pathlib import Path
from collections import UserDict, OrderedDict
from PyQt5.QtGui import QImage, QIntValidator, QPixmap, QImageReader, QIcon, QMovie, QPainter, QFont, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QPointF, QEvent
from PyQt5.QtWidgets import QDialog, QMainWindow, QMessageBox, QListWidgetItem, QFileDialog, QCheckBox
from PyQt5.QtWidgets import QPushButton, QFrame, QVBoxLayout, QLabel, QWidget, QAbstractButton, QHBoxLayout
from qtwidgets import Toggle

from core.views.Viewer_ui import Ui_Viewer
from core.views.components.QtImageViewer import QtImageViewer

from core.services.LoggerService import LoggerService
from core.services.KMLGeneratorService import KMLGeneratorService
from core.services.XmlService import XmlService
from core.services.PdfGeneratorService import PdfGeneratorService
from core.services.ZipBundleService import ZipBundleService
from core.services.ImageService import ImageService


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
        self.__threads = []
        self.main_image = None
        self.logger = LoggerService()
        self.setupUi(self)
        self._add_Toggles()

        # ---------------- settings / data ----------------
        self.xml_path = xml_path
        self.xml_service = XmlService(xml_path)
        self.images = self.xml_service.get_images()
        self.loaded_thumbnails = []
        self.hidden_image_count = sum(1 for image in self.images if image.get("hidden"))
        self.skipHidden.setText(f"Skip Hidden ({self.hidden_image_count}) ")
        settings, _ = self.xml_service.get_settings()
        self.is_thermal = (settings['thermal'] == 'True')
        self.position_format = position_format
        self.temperature_data = None
        self.active_thumbnail = None
        self.temperature_unit = 'F' if temperature_unit == 'Fahrenheit' else 'C'
        self.distance_unit = 'ft' if distance_unit == 'Feet' else 'm'
        self.show_hidden = show_hidden
        self.skipHidden.setChecked(not self.show_hidden)
        self.skipHidden.clicked.connect(self._skip_hidden_clicked)

        # thumbnail config
        self.thumbnail_limit = 30
        self.thumbnail_size = (122, 78)
        self.thumbnail_loader = None
        self.visible_thumbnails_range = (0, 0)

        # compass asset
        self.original_north_pix = QPixmap(f":/icons/{theme.lower()}/north.png")

        # status‑bar helper
        self.messages = StatusDict(callback=self._message_listener,
                                   key_order=["GPS Coordinates", "Relative Altitude",
                                              "Drone Orientation", "Estimated Average GSD",
                                              "Temperature"])
        self._reapply_icons(theme)

        # scale bar (re‑parented later into HUD overlay)
        self.scaleBar = ScaleBarWidget()

        # ---- load everything ----
        self._load_images()
        self._initialize_thumbnails()
        self._load_thumbnails_in_range(0, self.thumbnail_limit)

        # UI tweaks
        self.showMaximized()
        self.setFocusPolicy(Qt.StrongFocus)
        self.hideImageToggle.setFocusPolicy(Qt.NoFocus)
        self.skipHidden.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("QToolTip {background-color: lightblue; color:black; border:1px solid blue;}")

    def closeEvent(self, event):
        """Event triggered on window close; quits all thumbnail threads."""
        for thread, loader in self.__threads:
            if thread.isRunning():
                thread.requestInterruption()  # Optional: politely request interruption
                thread.quit()
                thread.wait()  # Wait until the thread has terminated
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

    def keyPressEvent(self, e):
        """Handles key press events for navigation and hiding images.

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

    def _load_images(self):
        """Loads and validates images from the XML file."""
        valid_images = []
        for index, image in enumerate(self.images[:]):
            path = Path(image['path'])
            image['name'] = path.name
            if path.is_file():
                try:
                    with Image.open(image['path']) as img:
                        img.verify()  # Checks if image is valid
                    valid_images.append(image)
                except (UnidentifiedImageError, OSError):
                    pass  # Not a valid image
        self.images = valid_images

        if len(self.images) == 0:
            self._show_no_images_message()
        else:
            self._load_initial_image()
            self.previousImageButton.clicked.connect(self._previousImageButton_clicked)
            self.nextImageButton.clicked.connect(self._nextImageButton_clicked)
            self.kmlButton.clicked.connect(self._kmlButton_clicked)
            self.pdfButton.clicked.connect(self._pdfButton_clicked)
            self.zipButton.clicked.connect(self._zipButton_clicked)
            self.jumpToLine.setValidator(QIntValidator(1, len(self.images), self))
            self.jumpToLine.editingFinished.connect(self._jumpToLine_changed)
            self.thumbnailScrollArea.horizontalScrollBar().valueChanged.connect(self._on_thumbnail_scroll)

    def _initialize_thumbnails(self):
        """Initializes the layout for thumbnails with default styling."""
        self.thumbnailLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.thumbnailLayout.setSpacing(5)
        for index, image in enumerate(self.images[:]):
            frame = QFrame()
            button = QPushButton()
            button.setFixedSize(QSize(100, 56))
            button.setProperty('imageIndex', index)
            button.setProperty('frame', frame)
            button.clicked.connect(self._on_thumbnail_clicked)
            layout = QVBoxLayout(frame)
            layout.addWidget(button)
            layout.setAlignment(Qt.AlignCenter)
            frame.setLayout(layout)
            frame.setFixedSize(QSize(*self.thumbnail_size))
            frame.setStyleSheet("border: 1px solid grey; border-radius: 3px;")
            overlay = QLabel(frame)
            overlay.setFixedSize(frame.width(), frame.height())
            overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
            overlay.move(0, 0)
            overlay.show()
            button.setProperty('overlay', overlay)
            self.thumbnailLayout.addWidget(frame)
            image['thumbnail'] = button
        # self.scrollAreaWidgetContents.setMinimumHeight(96)
        # self.thumbnailScrollArea.setMinimumHeight(116)

    def _load_thumbnails_in_range(self, start_index, end_index):
        """Loads thumbnails in the specified range asynchronously.

        Args:
            start_index (int): The starting index of thumbnails to load.
            end_index (int): The ending index of thumbnails to load.
        """
        self.thumbnail_loader = ThumbnailLoader(self.images, start_index, end_index, self.loaded_thumbnails)
        thread = QThread()
        self.__threads.append((thread, self.thumbnail_loader))
        self.thumbnail_loader.moveToThread(thread)
        self.thumbnail_loader.thumbnail_loaded.connect(self._on_thumbnail_loaded)
        self.thumbnail_loader.finished.connect(self._on_thumbnail_load_finished)
        thread.started.connect(self.thumbnail_loader.run)
        thread.start()

    def _on_thumbnail_loaded(self, index, icon):
        """Updates the thumbnail icon and overlay for the loaded thumbnail.

        Args:
            index (int): The index of the loaded thumbnail.
            icon (QIcon): The icon to display for the thumbnail.
        """
        button = self.images[index]['thumbnail']
        button.setIcon(icon)
        button.setIconSize(QSize(100, 56))
        if self.images[index].get('hidden'):
            overlay = button.property('overlay')
            overlay.setStyleSheet("background-color: rgba(128, 128, 128, 150);")

        self.loaded_thumbnails.append(index)

    def _on_thumbnail_load_finished(self):
        """Stops and quits all thumbnail threads after loading is complete."""
        for thread, analyze in self.__threads:
            thread.quit()

    def _on_thumbnail_scroll(self):
        """Loads thumbnails in the visible range when the user scrolls."""
        scrollbar = self.thumbnailScrollArea.horizontalScrollBar()
        max_scroll_value = scrollbar.maximum()
        current_scroll_value = scrollbar.value()
        total_images = len(self.images)
        visible_thumbnails = math.ceil(self.width()/self.thumbnail_size[0])
        if max_scroll_value == 0:
            current_index = 0
        else:
            current_index = math.ceil((current_scroll_value / max_scroll_value) * total_images)
        visible_start_index = max(0, current_index - int(self.thumbnail_limit))
        visible_end_index = min(current_index + visible_thumbnails + 4, total_images)
        if (int(visible_start_index), int(visible_end_index)) != self.visible_thumbnails_range:
            self._load_thumbnails_in_range(visible_start_index, visible_end_index)
            self.visible_thumbnails_range = (int(visible_start_index), int(visible_end_index))

    def _on_thumbnail_clicked(self):
        """Loads the image associated with the clicked thumbnail."""
        button = self.sender()
        self.current_image = button.property('imageIndex')
        self._load_image()

    def _scroll_thumbnail_int_view(self):
        """Ensures the active thumbnail is visible in the scroll area."""
        if self.active_thumbnail:
            self.thumbnailScrollArea.ensureWidgetVisible(self.active_thumbnail)
            self._on_thumbnail_scroll()

    def _set_active_thumbnail(self, button):
        """Sets the specified thumbnail as active.

        Args:
            button (QPushButton): The thumbnail button to set as active.
        """
        frame = button.property('frame')
        if self.active_thumbnail:
            self.active_thumbnail.setStyleSheet("border: 1px solid grey;")

        frame.setStyleSheet("QFrame { border: 1px solid blue; }")
        self.active_thumbnail = frame

    def _load_initial_image(self):
        """Loads the initial image and its areas of interest."""
        try:
            # (original logic unchanged up to constructing QtImageViewer)
            self.current_image = None
            for i in range(0, len(self.images)):
                if not self.show_hidden and self.images[i]['hidden']:
                    continue
                self.current_image = i
                break
            if self.current_image is None:
                self.current_image = 0

            self.placeholderImage.deleteLater()
            self.main_image = QtImageViewer(self, self.centralwidget)
            self.main_image.setMinimumSize(QSize(0, 0))
            self.main_image.setObjectName("mainImage")
            self.main_image.aspectRatioMode = Qt.KeepAspectRatio
            self.main_image.canZoom = True
            self.main_image.canPan = True
            self.ImageLayout.replaceWidget(self.placeholderImage, self.main_image)
            self.main_image.viewport().installEventFilter(self)

            self._load_image()

        except Exception as e:
            self.logger.error(e)

    def _load_image(self):
        """Loads the image at the current index along with areas of interest and GPS data."""
        try:
            # Clear previous status
            self.messages['GPS Coordinates'] = self.messages['Relative Altitude'] = self.messages['Drone Orientation'] = None
            self.messages['Estimated Average GSD'] = self.messages['Temperature'] = None

            image = self.images[self.current_image]
            if 'thumbnail' in image:
                self._set_active_thumbnail(image['thumbnail'])
            img = QImage(image['path'])
            self.main_image.setImage(img)
            self.fileNameLabel.setText(image['name'])
            self._load_areas_of_interest(image)
            self.main_image.resetZoom()
            self.main_image.setFocus()
            self.hideImageToggle.setChecked(image['hidden'])
            self.indexLabel.setText(f"Image {self.current_image + 1} of {len(self.images)}")

            image_service = ImageService(image['path'])
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
            if self.is_thermal:
                self.temperature_data = image_service.get_thermal_data(self.temperature_unit)
            self.main_image.mousePositionOnImageChanged.connect(self._mainImage_mouse_pos)
            self.main_image.zoomChanged.connect(self._update_scale_bar)
            self._update_scale_bar(self.main_image.getZoom())

            # move HUD to this viewport (in case of re‑parenting quirks)
            self._build_overlay()
            self._rotate_north_icon(direction)

            # HUD overlay visibility logic:
            # Show if either direction or avg_gsd is available; hide if both are missing
            if hasattr(self, "_hud"):
                if (direction is None) and (avg_gsd is None):
                    self._hud.hide()
                else:
                    if self.showOverlayToggle.isChecked():
                        self._hud.show()
                    else:
                        self._hud.hide()
            self._place_overlay()
        except Exception as e:
            self.logger.error(e)

    def _load_areas_of_interest(self, image):
        """Loads areas of interest thumbnails for a given image.

        Args:
            image (dict): Information about the image to load areas of interest for.
        """
        self.aoiListWidget.clear()
        img_arr = qimage2ndarray.imread(image['path'])
        count = 0
        self.highlights = []
        for area_of_interest in image['areas_of_interest']:
            # Create container widget for thumbnail and label
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setSpacing(2)
            layout.setContentsMargins(0, 0, 0, 0)

            center = area_of_interest['center']
            radius = area_of_interest['radius'] + 10
            crop_arr = self.crop_image(img_arr, center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)

            # Create the image viewer
            highlight = QtImageViewer(self, container, center, True)
            highlight.setObjectName(f"highlight{count}")
            highlight.setMinimumSize(QSize(190, 190))  # Reduced height to make room for label
            highlight.aspectRatioMode = Qt.KeepAspectRatio
            img = qimage2ndarray.array2qimage(crop_arr)
            highlight.setImage(img)
            highlight.canZoom = False
            highlight.canPan = False

            # Create coordinate label
            coord_label = QLabel(f"X: {center[0]}, Y: {center[1]}")
            coord_label.setAlignment(Qt.AlignCenter)
            coord_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 0, 0, 150);
                    color: white;
                    padding: 2px;
                    font-size: 10pt;
                    border-radius: 2px;
                }
            """)

            # Add widgets to layout
            layout.addWidget(highlight)
            layout.addWidget(coord_label)

            # Create list item
            listItem = QListWidgetItem()
            listItem.setSizeHint(QSize(190, 210))  # Increased height to accommodate label
            self.aoiListWidget.addItem(listItem)
            self.aoiListWidget.setItemWidget(listItem, container)
            self.aoiListWidget.setSpacing(5)
            self.highlights.append(highlight)
            highlight.leftMouseButtonPressed.connect(self._area_of_interest_click)
            count += 1

        self.areaCountLabel.setText(f"{count} {'Area' if count == 1 else 'Areas'} of Interest")

    def _previousImageButton_clicked(self):
        """Navigates to the previous image in the list, skipping hidden images if applicable."""
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
            self._scroll_thumbnail_int_view()
        else:
            self._show_additional_images_message()

    def _nextImageButton_clicked(self):
        """Navigates to the next image in the list, skipping hidden images if applicable."""
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
            self._scroll_thumbnail_int_view()
        else:
            self._show_additional_images_message()

    def _show_no_images_message(self):
        """Displays an error message when there are no available images."""
        self._show_error("No active images available.")

    def _show_additional_images_message(self):
        """Displays an error message when there are no available images."""
        self._show_error("No other images available.")

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
            overlay = image['thumbnail'].property('overlay')
            if state:
                overlay.setStyleSheet("background-color: rgba(128, 128, 128, 150);")
                if not image['hidden']:
                    self.hidden_image_count += 1
            else:
                overlay.setStyleSheet("background-color: none;")
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
            state (bool): True if the image should be hidden, False otherwise.
        """
        if self._hud is not None:
            if state:
                self._hud.show()
            else:
                self._hud.hide()

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
            self._scroll_thumbnail_int_view()
            self.jumpToLine.setText("")

    def resizeEvent(self, event):
        """Handles window resize events to adjust the main image.

        Args:
            event (QResizeEvent): Resize event.
        """
        super().resizeEvent(event)
        if self.main_image is not None:
            self._load_image()

    def _area_of_interest_click(self, x, y, img):
        """Handles clicks on area of interest thumbnails.

        Args:
            x (int): X coordinate of the cursor.
            y (int): Y coordinate of the cursor.
            img (QtImageViewer): The clicked thumbnail image viewer.
        """
        self.main_image.zoomToArea(img.center, 6)

    def _kmlButton_clicked(self):
        """Handles clicks on the Generate KML button to create a KML file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save KML File", "", "KML files (*.kml)")
        if file_name:  # Only proceed if a filename was selected
            kml_service = KMLGeneratorService()
            kml_service.generate_kml_export([img for img in self.images if not img.get("hidden", False)], file_name)

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

    def _show_error(self, text):
        """Displays an error message box.

        Args:
            text (str): Error message to display.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error Loading Images")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def _pdfButton_clicked(self):
        """Handles clicks on the Generate PDF button."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF files (*.pdf)")
        if file_name:
            try:
                pdf_generator = PdfGeneratorService(self)

                # Create and show the loading dialog
                self.loading_dialog = LoadingDialog(self)
                self.pdf_thread = PdfGenerationThread(pdf_generator, file_name)

                # Connect signals
                self.pdf_thread.finished.connect(self._on_pdf_generation_finished)
                self.pdf_thread.canceled.connect(self._on_pdf_generation_cancelled)
                self.pdf_thread.errorOccurred.connect(self._on_pdf_generation_error)

                self.pdf_thread.start()

                # Show the loading dialog and handle cancellation
                if self.loading_dialog.exec_() == QDialog.Rejected:
                    self.pdf_thread.cancel()

            except Exception as e:
                self.logger.error(f"Error generating PDF file: {str(e)}")
                self._show_error(f"Failed to generate PDF file: {str(e)}")

    def _on_pdf_generation_finished(self):
        """Handles successful completion of PDF generation."""
        self.loading_dialog.accept()
        QMessageBox.information(self, "Success", "PDF report generated successfully!")

    def _on_pdf_generation_cancelled(self):
        """Handles cancellation of PDF generation."""
        if self.pdf_thread and self.pdf_thread.isRunning():
            self.pdf_thread.terminate()  # Forcefully terminate the thread
            self.pdf_thread.wait()      # Wait for the thread to terminate completely
        # Close the loading dialog
        if hasattr(self, 'loading_dialog') and self.loading_dialog.isVisible():
            self.loading_dialog.reject()  # Close the dialog

    def _on_pdf_generation_error(self, error_message):
        """Handles errors during PDF generation."""
        if hasattr(self, 'loading_dialog') and self.loading_dialog.isVisible():
            self.loading_dialog.reject()  # Close the loading dialog
        self._show_error(f"PDF generation failed: {error_message}")

    def _zipButton_clicked(self):
        """Handles clicks on the Generate Zip Bundle."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Zip File", "", "Zip files (*.zip)")
        if file_name:
            try:
                file_paths = [img['path'] for img in self.images if not img.get('hidden', False)]
                zip_generator = ZipBundleService()
                zip_generator.generate_zip_file(file_paths, file_name)
            except Exception as e:
                self.logger.error(f"Error generating Zip file: {str(e)}")
                self._show_error(f"Failed to generate Zip file: {str(e)}")

    def _message_listener(self, key, value):
        """Updates the status bar with all key-value pairs from self.messages, skipping None values."""
        status_text = " | ".join([f"{k}: {v}" for k, v in self.messages.items() if v is not None])
        self.statusbar.showMessage(status_text)

    def _mainImage_mouse_pos(self, pos):
        """Displays temperature data or GPS coordinates at the mouse position.

        Args:
            pos (QPoint): The current mouse position on the image.
        """
        if self.temperature_data is not None:
            shape = self.temperature_data.shape
            if (0 <= pos.y() < shape[0]) and (0 <= pos.x() < shape[1]):
                temp_value = str(round(self.temperature_data[pos.y()][pos.x()], 2))
                temp_display = f"{temp_value}° {self.temperature_unit}"
                self.messages["Temperature"] = temp_display

    def _rotate_north_icon(self, direction):
        """
        Draws a north-facing arrow icon based on the given drone orientation.

        Args:
            direction (float | None): Yaw angle in degrees. If None, hides the arrow.
        """
        if direction is None:
            # Hide the icon by setting a fully transparent 1x1 pixmap
            transparent = QPixmap(1, 1)
            transparent.fill(Qt.transparent)
            self.northIcon.setPixmap(transparent)
            return

        angle = 360 - direction
        pm = self.original_north_pix
        w, h = pm.width(), pm.height()

        # Find the true tip: first non-transparent pixel from the top, center column
        img = pm.toImage().convertToFormat(QImage.Format_ARGB32)
        cx = w // 2
        for y in range(h):
            if QColor(img.pixel(cx, y)).alpha() > 0:
                tip_y = y
                break
        else:
            tip_y = 0  # fallback if arrow is fully transparent

        tip_offset_px = h / 2 - tip_y  # distance from center to true tip

        # final canvas size
        final_size = 50
        margin = 12
        spacing = 8  # spacing between arrow tip and label in final rendered px

        # scale so the arrow fits inside the canvas minus margin
        diag = math.hypot(w, h)
        scale = (final_size - 2 * margin) / diag

        canvas = QPixmap(final_size, final_size)
        canvas.fill(Qt.transparent)

        p = QPainter(canvas)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # --- draw arrow ---
        p.save()
        p.translate(final_size / 2, final_size / 2)
        p.rotate(angle)
        p.scale(scale, scale)
        p.drawPixmap(round(-w / 2), round(-h / 2), pm)
        p.restore()

        # --- draw 'N' label a fixed number of px past the visual tip ---
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        p.setFont(font)
        fm = p.fontMetrics()
        text = "N"
        tw = fm.horizontalAdvance(text)

        # scaled distance from center to arrow tip, plus spacing beyond tip
        tip_offset = tip_offset_px * scale + spacing

        p.save()
        p.translate(final_size / 2, final_size / 2)
        p.rotate(angle)
        p.translate(0, -tip_offset)  # move up to just past tip
        p.rotate(-angle)             # make text upright again

        default_text_color = self.palette().color(QPalette.Text)
        p.setPen(QPen(default_text_color))

        text_y = (fm.ascent() - fm.height() / 2)
        p.drawText(QPointF(-tw / 2, text_y), text)
        p.restore()

        p.end()
        self.northIcon.setPixmap(canvas)

    def _update_scale_bar(self, zoom: float):
        """
        Called from QtImageViewer.zoomChanged.
        Computes the real‑world length represented by `scaleBar._bar_px`
        at the current zoom and writes it into the label.
        """
        try:
            if not self.main_image or not self.main_image.hasImage():
                self.scaleBar.setVisible(False)
                return

            gsd_text = self.messages.get("Estimated Average GSD")  # e.g. '3.2cm/px'
            if not gsd_text:
                self.scaleBar.setVisible(False)
                return

            # -------- compute label --------
            gsd_cm = float(gsd_text.replace("cm/px", "").strip())   # cm / px
            zoomed_gsd = gsd_cm / zoom                                  # cm / px at current zoom
            bar_px = self.scaleBar._bar_px                          # fixed 120 px
            real_cm = bar_px * zoomed_gsd                            # cm represented by bar

            if self.distance_unit == 'ft':
                real_in = real_cm / 2.54
                if real_in >= 12:
                    label = f"{real_in / 12:.2f} ft"
                else:
                    label = f"{real_in:.1f} in"
            else:
                if real_cm >= 100:
                    label = f"{real_cm / 100:.1f} m"
                else:
                    label = f"{real_cm:.0f} cm"

            # -------- show --------
            self.scaleBar.setLabel(label)
            self.scaleBar.setVisible(True)

        except Exception as e:
            self.logger.error(f"scale‑bar update failed: {e}")

    def _build_overlay(self):
        """Create semi‑transparent HUD once per main_image."""
        if hasattr(self, "_hud"):
            return
        self._hud = QWidget(self.main_image.viewport())
        self._hud.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._hud.setObjectName("hud")
        self._hud.setStyleSheet("#hud{background:rgba(0,0,0,150); border-radius:6px;}")
        lay = QHBoxLayout(self._hud)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(10)
        self._compassLbl = QLabel(self._hud)
        self._compassLbl.setFixedSize(50, 50)
        lay.addWidget(self._compassLbl)
        self.scaleBar.setParent(self._hud)
        lay.addWidget(self.scaleBar)
        self.northIcon = self._compassLbl  # redirect for _rotate_north_icon
        # keep overlay positioned when user pans / zooms
        self.main_image.viewChanged.connect(self._place_overlay)

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

    def _place_overlay(self):
        """Anchor HUD to bottom‑right corner *of the image*, not viewport."""
        if not hasattr(self, "_hud"):
            return
        vp = self.main_image.viewport()
        # bottom‑right of the image (sceneRect) in viewport coords
        br_scene = self.main_image.sceneRect().bottomRight()
        br_view = self.main_image.mapFromScene(br_scene)
        margin = 12
        x = br_view.x() - self._hud.width() - margin
        y = br_view.y() - self._hud.height() - margin
        # clamp into viewport just in case
        x = max(margin, min(x, vp.width() - self._hud.width() - margin))
        y = max(margin, min(y, vp.height() - self._hud.height() - margin))
        self._hud.move(x, y)
        self._hud.raise_()

    # Qt event filter keeps HUD glued to corner on viewport resize
    def eventFilter(self, obj, ev):
        if hasattr(self, "main_image") and obj is self.main_image.viewport() and ev.type() == QEvent.Resize:
            self._place_overlay()
        return super().eventFilter(obj, ev)


class LoadingDialog(QDialog):
    """Custom dialog for showing a loading spinner and message."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generating Report")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(300, 200)

        # Layout and widgets
        layout = QVBoxLayout()

        # Add spinning loader
        self.spinner_label = QLabel(self)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_movie = QMovie(":/icons/loading.gif")  # Path to your GIF in the resource file
        self.spinner_movie.setScaledSize(QSize(50, 50))  # Adjust the size if needed
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_movie.start()  # Start the animation

        # Add message label
        self.message_label = QLabel("Report generation in progress...")
        self.message_label.setAlignment(Qt.AlignCenter)

        # Add cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        # Add widgets to layout
        layout.addWidget(self.spinner_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)


class ThumbnailLoader(QThread):
    """Threaded loader for generating and displaying image thumbnails."""

    thumbnail_loaded = pyqtSignal(int, QIcon)

    def __init__(self, images, start_index, end_index, existing_thumbnails, parent=None):
        """Initializes the thumbnail loader.

        Args:
            images (list): List of image data dictionaries.
            start_index (int): Starting index for thumbnail loading.
            end_index (int): Ending index for thumbnail loading.
            existing_thumbnails (list): Indices of already loaded thumbnails.
            parent (QObject, optional): Parent object for the loader.
        """
        super().__init__(parent)
        self.images = images
        self.start_index = max(start_index, 0)
        self.end_index = min(end_index, len(images))
        self.existing_thumbnails = existing_thumbnails

    def run(self):
        """Runs the thumbnail loading process."""
        for index in range(self.start_index, self.end_index):
            if index not in self.existing_thumbnails:
                image_path = self.images[index]['path']
                reader = QImageReader(image_path)
                reader.setScaledSize(QSize(100, 56))
                pixmap = QPixmap.fromImage(reader.read())
                icon = QIcon(pixmap)
                self.thumbnail_loaded.emit(index, icon)


class PdfGenerationThread(QThread):
    """Thread for generating the PDF report."""
    finished = pyqtSignal()
    canceled = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    def __init__(self, pdf_generator, output_path):
        """Initializes the PdfGenerationThread.

        Args:
            pdf_generator (PdfGeneratorService): The PDF generator instance responsible for creating the report.
            output_path (str): The file path where the generated PDF will be saved.
        """
        super().__init__()
        self.pdf_generator = pdf_generator
        self.output_path = output_path
        self._is_canceled = False

    def run(self):
        """Executes the PDF generation process.

        If the process is not canceled, it generates the PDF report and emits
        the `finished` signal upon successful completion.
        """
        try:
            if not self._is_canceled:
                error_message = self.pdf_generator.generate_report(self.output_path)
                if error_message:
                    self.errorOccurred.emit(error_message)  # Emit error if there's an error message
                else:
                    self.finished.emit()  # Emit finished if successful
        except Exception as e:
            self.errorOccurred.emit(str(e))  # Emit error if an exception occurs

    def cancel(self):
        """Cancels the PDF generation process.

        Sets the `_is_canceled` flag to True and emits the `canceled` signal.
        """
        self._is_canceled = True
        self.canceled.emit()


class StatusDict(UserDict):
    """
    Dictionary-like object that maintains a custom key order and supports
    callback execution when values are updated.

    Attributes:
        callback (Callable): Function to call when values are updated.
        key_order (list): Explicit order to maintain for dictionary keys.
    """
    def __init__(self, *args, callback=None, key_order=None, **kwargs):
        self.data = OrderedDict()  # Maintain explicit ordering
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.key_order = key_order or []  # Store explicit ordering

    def __setitem__(self, key, value):
        if key in self.data:
            del self.data[key]  # Remove existing entry to reinsert in correct order
        self.data[key] = value  # Insert the key-value pair

        self._enforce_order()  # Ensure keys are in correct order

        if self.callback:
            self.callback(key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        if self.callback:
            self.callback(f"Deleted {key}")

    def set_order(self, key_order):
        """Sets the explicit order of keys in the dictionary."""
        self.key_order = key_order
        self._enforce_order()  # Apply the new order immediately

    def _enforce_order(self):
        """Reorders the dictionary based on self.key_order."""
        new_data = OrderedDict()
        for key in self.key_order:
            if key in self.data:
                new_data[key] = self.data[key]
        self.data = new_data  # Replace existing dict with the ordered one

    def items(self):
        """Returns items in the explicitly set order."""
        return [(key, self.data[key]) for key in self.key_order if key in self.data]


class ScaleBarWidget(QWidget):
    """
    Draws a *fixed‑width* scale bar (default 120 px) and a text label that you
    can change at runtime with setLabel().
    """
    def __init__(self, parent=None, bar_px=120):
        super().__init__(parent)
        self._bar_px = bar_px
        self._label_text = ""
        self.setFixedSize(bar_px + 80, 30)          # +80 leaves room for text

    # ---------- public API ----------
    def setLabel(self, text: str):
        if text != self._label_text:
            self._label_text = text
            self.update()        # trigger paintEvent

    # ---------- paint ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.white, 2)
        painter.setPen(pen)

        mid_y = self.height() // 2
        start = 10                       # left margin
        end = start + self._bar_px

        # bar + end caps
        painter.drawLine(start, mid_y, end, mid_y)
        painter.drawLine(start, mid_y - 5, start, mid_y + 5)
        painter.drawLine(end,   mid_y - 5, end,   mid_y + 5)

        # label
        painter.setFont(QFont("Arial", 10))
        painter.drawText(end + 8, mid_y + 4, self._label_text)
