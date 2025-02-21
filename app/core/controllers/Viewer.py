import qimage2ndarray
import imghdr
import math
import traceback
from pathlib import Path
from collections import UserDict, OrderedDict

from PyQt5.QtGui import QImage, QIntValidator, QPixmap, QImageReader, QIcon, QMovie
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QMainWindow, QMessageBox, QListWidgetItem, QFileDialog, QPushButton, QFrame, QVBoxLayout, QLabel, QWidget
from qtwidgets import Toggle

from core.views.Viewer_ui import Ui_Viewer
from core.views.components.QtImageViewer import QtImageViewer

from core.services.LoggerService import LoggerService
from core.services.KMLService import KMLService
from core.services.XmlService import XmlService
from core.services.PdfGeneratorService import PdfGeneratorService
from core.services.ZipBundleService import ZipBundleService

from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper


class Viewer(QMainWindow, Ui_Viewer):
    """Controller for the Image Viewer (QMainWindow)."""

    def __init__(self, xml_path, position_format, temperature_unit, distance_unit, show_hidden):
        """Initializes the ADIAT Image Viewer.

        Args:
            xml_path (str): Path to XML file containing results data.
            position_format (str): The format in which GPS coordinates will be displayed.
            temperature_unit (str): The unit in which temperature values will be displayed.
            distance_unit (str): The unit in which distance values will be displayed.
            show_hidden (bool): Whether or not to show hidden images by default.
        """
        super().__init__()
        self.__threads = []
        self.mainImage = None
        self.logger = LoggerService()
        self.setupUi(self)
        self._add_hideImageToggle()
        self.xml_path = xml_path
        self.xmlService = XmlService(xml_path)
        self.images = self.xmlService.get_images()
        self.loaded_thumbnails = []
        self.hidden_image_count = sum(1 for image in self.images if image.get("hidden") is True)
        self.skipHidden.setText(f"Skip Hidden ({self.hidden_image_count}) ")
        settings, _ = self.xmlService.get_settings()
        self.is_thermal = (settings['thermal'] == 'True')
        self.position_format = position_format
        self.position = None
        self.temperature_data = None
        self.active_thumbnail = None
        self.temperature_unit = 'F' if temperature_unit == 'Fahrenheit' else 'C'
        self.distance_unit = 'ft' if distance_unit == 'Feet' else 'm'
        self.show_hidden = show_hidden
        self.skipHidden.setChecked(not self.show_hidden)
        self.skipHidden.clicked.connect(self._skip_hidden_clicked)
        self.thumbnail_limit = 30
        self.thumbnail_size = (122, 78)
        self.thumbnail_loader = None
        self.visible_thumbnails_range = (0, 0)
        self.messages = StatusDict(callback=self._message_listener, key_order=["GPS Coordinates", "Relative Altitude", "Temperature"])
        self._load_images()
        self._initialize_thumbnails()
        self._load_thumbnails_in_range(0, self.thumbnail_limit)
        self.showMaximized()
        self.setFocusPolicy(Qt.StrongFocus)
        self.hideImageToggle.setFocusPolicy(Qt.NoFocus)
        self.skipHidden.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("""
            QToolTip {
                background-color: lightblue;
                color: black;
                border: 1px solid blue;
            }
        """)

    def closeEvent(self, event):
        """Event triggered on window close; quits all thumbnail threads."""
        for thread, analyze in self.__threads:
            thread.quit()

    def _add_hideImageToggle(self):
        """Replaces the hide image checkbox with a toggle button."""
        self.hideImageToggle = Toggle()
        self.ButtonLayout.replaceWidget(self.hideImageCheckbox, self.hideImageToggle)
        self.hideImageCheckbox.deleteLater()
        self.hideImageToggle.clicked.connect(self._hide_image_change)

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
            if path.is_file() and imghdr.what(image['path']) is not None:
                valid_images.append(image)
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
            self.current_image = None
            for i in range(0, len(self.images)):
                if not self.show_hidden and self.images[i]['hidden']:
                    continue
                self.current_image = i
                break

            if self.current_image is None:
                self.current_image = 0

            self.messages['GPS Coordinates'] = self.messages['Relative Altitude'] = self.messages['Temperature'] = None
            image = self.images[self.current_image]
            self.placeholderImage.deleteLater()
            self.mainImage = QtImageViewer(self, self.centralwidget)
            self.mainImage.setMinimumSize(QSize(0, 650))
            self.mainImage.setObjectName("mainImage")
            self.mainImage.aspectRatioMode = Qt.KeepAspectRatio
            self.mainImage.canZoom = True
            self.mainImage.canPan = True
            img = QImage(image['path'])
            self.mainImage.setImage(img)
            self.ImageLayout.replaceWidget(self.placeholderImage, self.mainImage)
            self.fileNameLabel.setText(image['name'])
            self._load_areas_of_interest(image)

            gps_coords = LocationInfo.get_gps(image['path'])
            xmp_data = MetaDataHelper.get_xmp_data(image['path'], True)
            self.messages['Relative Altitude'] = self._find_relative_altitude(xmp_data)
            if gps_coords:
                self.position = self.get_position(gps_coords['latitude'], gps_coords['longitude'])
                self.messages['GPS Coordinates'] = self.position

            self.indexLabel.setText(f"Image {self.current_image + 1} of {len(self.images)}")

            if self.is_thermal:
                self.temperature_data = self._load_thermal_data(image['path'])
            self.mainImage.mousePositionOnImageChanged.connect(self._mainImage_mouse_pos)
            self.hideImageToggle.setChecked(image['hidden'])
        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(e)

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

    def _load_image(self):
        """Loads the image at the current index along with areas of interest and GPS data."""
        try:
            self.messages['GPS Coordinates'] = self.messages['Relative Altitude'] = self.messages['Temperature'] = None
            image = self.images[self.current_image]
            self._set_active_thumbnail(image['thumbnail'])
            img = QImage(image['path'])
            self.mainImage.setImage(img)
            self.fileNameLabel.setText(image['name'])
            self._load_areas_of_interest(image)
            self.mainImage.resetZoom()
            self.mainImage.setFocus()
            self.hideImageToggle.setChecked(image['hidden'])
            self.indexLabel.setText(f"Image {self.current_image + 1} of {len(self.images)}")

            gps_coords = LocationInfo.get_gps(image['path'])
            xmp_data = MetaDataHelper.get_xmp_data(image['path'], True)
            self.messages['Relative Altitude'] = self._find_relative_altitude(xmp_data)

            self.position = None
            if gps_coords:
                self.position = self.get_position(gps_coords['latitude'], gps_coords['longitude'])
                self.messages['GPS Coordinates'] = self.position

            if self.is_thermal:
                self.temperature_data = self._load_thermal_data(image['path'])
            self.mainImage.mousePositionOnImageChanged.connect(self._mainImage_mouse_pos)
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

    def _load_thermal_data(self, path):
        """Loads and converts thermal data based on the selected temperature unit.

        Args:
            path (str): Path to the thermal image file.

        Returns:
            np.ndarray: Temperature data array in the selected unit.
        """
        data = MetaDataHelper.get_temperature_data(path)
        return (data * 1.8) + 32 if self.temperature_unit == 'F' else data

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
            self._show_no_images_message()

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
            self._show_no_images_message()

    def _show_no_images_message(self):
        """Displays an error message when there are no available images."""
        self._show_error("No active images available.")

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
            self.xmlService.save_xml_file(self.xml_path)
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
        if self.mainImage is not None:
            self._load_image()

    def _area_of_interest_click(self, x, y, img):
        """Handles clicks on area of interest thumbnails.

        Args:
            x (int): X coordinate of the cursor.
            y (int): Y coordinate of the cursor.
            img (QtImageViewer): The clicked thumbnail image viewer.
        """
        self.mainImage.zoomToArea(img.center, 6)

    def _kmlButton_clicked(self):
        """Handles clicks on the Generate KML button to create a KML file."""
        fileName, _ = QFileDialog.getSaveFileName(self, "Save KML File", "", "KML files (*.kml)")
        if fileName:  # Only proceed if a filename was selected
            self.generate_kml(fileName)

    def generate_kml(self, output_path):
        """Generates a KML file from images' GPS data and saves it.

        Args:
            output_path (str): The file path to save the KML file.
        """
        kml = KMLService()
        kml_points = []
        for image in self.images:
            if image['hidden']:
                continue
            gps_coords = LocationInfo.get_gps(image['path'])
            if gps_coords:
                point = {"name": image['name'], "long": gps_coords['longitude'], "lat": gps_coords['latitude']}
                kml_points.append(point)
        kml.add_points(kml_points)
        kml.save_kml(output_path)

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

    def get_position(self, latitude, longitude):
        """Converts latitude and longitude to a formatted position string.

        Args:
            latitude (str): Latitude in degree, minute, second format.
            longitude (str): Longitude in degree, minute, second format.

        Returns:
            str: Formatted position string based on selected format.
        """
        if self.position_format == 'Lat/Long - Decimal Degrees':
            return f"{latitude}, {longitude}"
        elif self.position_format == 'Lat/Long - Degrees, Minutes, Seconds':
            dms = LocationInfo.convert_decimal_to_dms(latitude, longitude)
            return f"{dms['latitude']['degrees']}°{dms['latitude']['minutes']}'{dms['latitude']['seconds']}\"{dms['latitude']['reference']} " \
                   f"{dms['longitude']['degrees']}°{dms['longitude']['minutes']}'{dms['longitude']['seconds']}\"{dms['longitude']['reference']}"
        elif self.position_format == 'UTM':
            utm = LocationInfo.convert_degrees_to_utm(latitude, longitude)
            return f"{utm['zone_number']}{utm['zone_letter']} {utm['easting']} {utm['northing']}"

    def _pdfButton_clicked(self):
        """Handles clicks on the Generate PDF button."""
        fileName, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF files (*.pdf)")
        if fileName:
            try:
                pdf_generator = PdfGeneratorService(self)

                # Create and show the loading dialog
                self.loading_dialog = LoadingDialog(self)
                self.pdf_thread = PdfGenerationThread(pdf_generator, fileName)

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
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Zip File", "", "Zip files (*.zip)")
        if fileName:
            try:
                file_paths = [img['path'] for img in self.images if not img.get('hidden', False)]
                zip_generator = ZipBundleService()
                zip_generator.generate_zip_file(file_paths, fileName)
            except Exception as e:
                self.logger.error(f"Error generating Zip file: {str(e)}")
                self._show_error(f"Failed to generate Zip file: {str(e)}")

    def _message_listener(self, key, value):
        """Updates the status bar with all key-value pairs from self.messages, skipping None values."""
        status_text = " | ".join([f"{k}: {v}" for k, v in self.messages.items() if v is not None])
        self.statusbar.showMessage(status_text)

    def _find_relative_altitude(self, data):
        """
        Find the key-value pair where the key contains 'RelativeAltitude'.

        Args:
            data (dict): The dictionary to search.

        Returns:
            tuple: The key-value pair if found, otherwise None.
        """
        METERS_TO_FEET = 3.28084
        if data is None:
            return None
        for key, value in data.items():
            if "RelativeAltitude" in key:
                try:
                    altitude_meters = float(value)  # Convert to float
                    altitude = round(altitude_meters * METERS_TO_FEET, 2) if self.distance_unit == 'ft' else altitude_meters
                    return f"{altitude} {self.distance_unit}"
                except ValueError:
                    return None  # Handle cases where conversion fails
        return None


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
