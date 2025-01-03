import qimage2ndarray
import imghdr
from pathlib import Path
from PyQt5.QtGui import QImage, QIntValidator, QPixmap, QImageReader, QIcon
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QFileDialog, QPushButton, QFrame, QVBoxLayout, QLabel, QWidget
from qtwidgets import Toggle

from core.views.Viewer_ui import Ui_Viewer
from core.views.components.QtImageViewer import QtImageViewer
from core.services.KMLService import KMLService
from core.services.XmlService import XmlService
from helpers.LocationInfo import LocationInfo
from core.services.LoggerService import LoggerService
from helpers.MetaDataHelper import MetaDataHelper


class Viewer(QMainWindow, Ui_Viewer):
    """Controller for the Image Viewer (QMainWindow)."""

    def __init__(self, xml_path, position_format, temperature_unit, show_hidden):
        """Initializes the ADIAT Image Viewer.

        Args:
            xml_path (str): Path to XML file containing results data.
            position_format (str): The format in which GPS coordinates will be displayed.
            temperature_unit (str): The unit in which temperature values will be displayed.
            show_hidden (bool): Whether or not to show hidden images by default.
        """
        super().__init__()
        self.__threads = []
        self.mainImage = None
        self.logger = LoggerService()
        self.setupUi(self)
        self.addHideImageToggle()
        self.xml_path = xml_path
        self.xmlService = XmlService(xml_path)
        self.images = self.xmlService.getImages()
        self.loaded_thumbnails = []
        self.hidden_image_count = sum(1 for image in self.images if image.get("hidden") is True)
        self.skipHidden.setText(f"Skip Hidden ({self.hidden_image_count}) ")
        settings, _ = self.xmlService.getSettings()
        self.is_thermal = (settings['thermal'] == 'True')
        self.position_format = position_format
        self.position = None
        self.temperature_data = None
        self.active_thumbnail = None
        self.temperature_unit = 'F' if temperature_unit == 'Fahrenheit' else 'C'
        self.show_hidden = show_hidden
        self.skipHidden.setChecked(not self.show_hidden)
        self.skipHidden.clicked.connect(self.skipHiddenClicked)
        self.thumbnail_limit = 30
        self.thumbnail_loader = None
        self.visible_thumbnails_range = (0, 0)
        self.loadImages()
        self.initializeThumbnails()
        self.loadThumbnailsInRange(0, self.thumbnail_limit)
        self.showMaximized()
        self.setFocusPolicy(Qt.StrongFocus)
        self.hideImageToggle.setFocusPolicy(Qt.NoFocus)
        self.skipHidden.setFocusPolicy(Qt.NoFocus)

    def closeEvent(self, event):
        """Event triggered on window close; quits all thumbnail threads."""
        for thread, analyze in self.__threads:
            thread.quit()

    def addHideImageToggle(self):
        """Replaces the hide image checkbox with a toggle button."""
        self.hideImageToggle = Toggle()
        self.ButtonLayout.replaceWidget(self.hideImageCheckbox, self.hideImageToggle)
        self.hideImageCheckbox.deleteLater()
        self.hideImageToggle.clicked.connect(self.hideImageChange)

    def keyPressEvent(self, e):
        """Handles key press events for navigation and hiding images.

        Args:
            e (QKeyEvent): Key event containing the key pressed.
        """
        if e.key() == Qt.Key_Right:
            self.nextImageButtonClicked()
        if e.key() == Qt.Key_Left:
            self.previousImageButtonClicked()
        if e.key() == Qt.Key_Down or e.key() == Qt.Key_P:
            self.hideImageChange(True)
        if e.key() == Qt.Key_Up or e.key() == Qt.Key_U:
            self.hideImageChange(False)

    def loadImages(self):
        """Loads and validates images from the XML file."""
        valid_images = []
        for index, image in enumerate(self.images[:]):
            path = Path(image['path'])
            image['name'] = path.name
            if path.is_file() and imghdr.what(image['path']) is not None:
                valid_images.append(image)
        self.images = valid_images

        if len(self.images) == 0:
            self.showNoImagesMessage()
        else:
            self.loadInitialImage()
            self.previousImageButton.clicked.connect(self.previousImageButtonClicked)
            self.nextImageButton.clicked.connect(self.nextImageButtonClicked)
            self.KmlButton.clicked.connect(self.KmlButtonClicked)
            self.jumpToLine.setValidator(QIntValidator(1, len(self.images), self))
            self.jumpToLine.editingFinished.connect(self.jumpToLineChanged)
            self.thumbnailScrollArea.horizontalScrollBar().valueChanged.connect(self.onThumbnailScroll)

    def initializeThumbnails(self):
        """Initializes the layout for thumbnails with default styling."""
        self.thumbnailLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.thumbnailLayout.setSpacing(5)
        for index, image in enumerate(self.images[:]):
            frame = QFrame()
            button = QPushButton()
            button.setFixedSize(QSize(100, 56))
            button.setProperty('imageIndex', index)
            button.setProperty('frame', frame)
            button.clicked.connect(self.onThumbnailClicked)
            layout = QVBoxLayout(frame)
            layout.addWidget(button)
            layout.setAlignment(Qt.AlignCenter)
            frame.setLayout(layout)
            frame.setFixedSize(QSize(122, 78))
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

    def loadThumbnailsInRange(self, start_index, end_index):
        """Loads thumbnails in the specified range asynchronously.

        Args:
            start_index (int): The starting index of thumbnails to load.
            end_index (int): The ending index of thumbnails to load.
        """
        self.thumbnail_loader = ThumbnailLoader(self.images, start_index, end_index, self.loaded_thumbnails)
        thread = QThread()
        self.__threads.append((thread, self.thumbnail_loader))
        self.thumbnail_loader.moveToThread(thread)
        self.thumbnail_loader.thumbnailLoaded.connect(self.onThumbnailLoaded)
        self.thumbnail_loader.finished.connect(self.onThumbnailLoadFinished)
        thread.started.connect(self.thumbnail_loader.run)
        thread.start()

    def onThumbnailLoaded(self, index, icon):
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

    def onThumbnailLoadFinished(self):
        """Stops and quits all thumbnail threads after loading is complete."""
        for thread, analyze in self.__threads:
            thread.quit()

    def onThumbnailScroll(self):
        """Loads thumbnails in the visible range when the user scrolls."""
        scrollbar = self.thumbnailScrollArea.horizontalScrollBar()
        max_scroll_value = scrollbar.maximum()
        current_scroll_value = scrollbar.value()
        total_images = len(self.images)

        visible_start_index = int((current_scroll_value / max_scroll_value) * total_images)
        visible_start_index = max(0, visible_start_index - int(self.thumbnail_limit))
        visible_end_index = min(visible_start_index + self.thumbnail_limit + 10, total_images)

        if (int(visible_start_index), int(visible_end_index)) != self.visible_thumbnails_range:
            self.loadThumbnailsInRange(visible_start_index, visible_end_index)
            self.visible_thumbnails_range = (int(visible_start_index), int(visible_end_index))

    def onThumbnailClicked(self):
        """Loads the image associated with the clicked thumbnail."""
        button = self.sender()
        self.current_image = button.property('imageIndex')
        self.loadImage()

    def scrollThumbnailIntoView(self):
        """Ensures the active thumbnail is visible in the scroll area."""
        if self.active_thumbnail:
            self.thumbnailScrollArea.ensureWidgetVisible(self.active_thumbnail)

    def setActiveThumbnail(self, button):
        """Sets the specified thumbnail as active.

        Args:
            button (QPushButton): The thumbnail button to set as active.
        """
        frame = button.property('frame')
        if self.active_thumbnail:
            self.active_thumbnail.setStyleSheet("border: 1px solid grey;")

        frame.setStyleSheet("QFrame { border: 1px solid blue; }")
        self.active_thumbnail = frame

    def loadInitialImage(self):
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
            self.loadAreasofInterest(image)

            gps_coords = LocationInfo.getGPS(image['path'])
            if gps_coords:
                self.position = self.getPosition(gps_coords['latitude'], gps_coords['longitude'])
                self.statusbar.showMessage("GPS Coordinates: " + self.position)
            else:
                self.statusbar.showMessage("")
            self.indexLabel.setText(f"Image {self.current_image + 1} of {len(self.images)}")

            if self.is_thermal:
                self.temperature_data = self.loadThermalData(image['path'])
            self.mainImage.mousePositionOnImageChanged.connect(self.mainImageMousePos)
            self.hideImageToggle.setChecked(image['hidden'])
        except Exception as e:
            self.logger.error(e)

    def mainImageMousePos(self, pos):
        """Displays temperature data or GPS coordinates at the mouse position.

        Args:
            pos (QPoint): The current mouse position on the image.
        """
        if self.temperature_data is not None:
            shape = self.temperature_data.shape
            if (0 <= pos.y() < shape[0]) and (0 <= pos.x() < shape[1]):
                temp_value = str(round(self.temperature_data[pos.y()][pos.x()], 2))
                temp_display = f"{temp_value}° {self.temperature_unit}"
                if self.position:
                    new_message = f"GPS Coordinates: {self.position}    Temperature: {temp_display}"
                else:
                    new_message = f"Temperature: {temp_display}"
                self.statusbar.showMessage(new_message)

    def loadImage(self):
        """Loads the image at the current index along with areas of interest and GPS data."""
        try:
            image = self.images[self.current_image]
            self.setActiveThumbnail(image['thumbnail'])
            img = QImage(image['path'])
            self.mainImage.setImage(img)
            self.fileNameLabel.setText(image['name'])
            self.loadAreasofInterest(image)
            self.mainImage.resetZoom()
            self.mainImage.setFocus()
            self.hideImageToggle.setChecked(image['hidden'])
            self.indexLabel.setText(f"Image {self.current_image + 1} of {len(self.images)}")

            gps_coords = LocationInfo.getGPS(image['path'])
            self.position = None
            if gps_coords:
                self.position = self.getPosition(gps_coords['latitude'], gps_coords['longitude'])
                self.statusbar.showMessage("GPS Coordinates: " + self.position)
            else:
                self.statusbar.showMessage("")

            if self.is_thermal:
                self.temperature_data = self.loadThermalData(image['path'])
            self.mainImage.mousePositionOnImageChanged.connect(self.mainImageMousePos)
        except Exception as e:
            self.logger.error(e)

    def loadAreasofInterest(self, image):
        """Loads areas of interest thumbnails for a given image.

        Args:
            image (dict): Information about the image to load areas of interest for.
        """
        self.aoiListWidget.clear()
        img_arr = qimage2ndarray.imread(image['path'])
        count = 0
        self.highlights = []
        for area_of_interest in image['areas_of_interest']:
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setSpacing(2)
            layout.setContentsMargins(0, 0, 0, 0)

            center = area_of_interest['center']
            radius = area_of_interest['radius'] + 10
            crop_arr = self.crop_image(img_arr, center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)
           
            highlight = QtImageViewer(self, container, center, True)
            highlight.setObjectName(f"highlight{count}")
            highlight.setMinimumSize(QSize(190, 170))  # Reduced height to make room for label
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

            listItem = QListWidgetItem()
            listItem.setSizeHint(QSize(190, 200)) # Increased height to accommodate label
            self.aoiListWidget.addItem(listItem)
            self.aoiListWidget.setItemWidget(listItem, container)
            
            self.highlights.append(highlight)
            highlight.leftMouseButtonPressed.connect(self.areaOfInterestClick)
            count += 1

        self.areaCountLabel.setText(f"{count} {'Area' if count == 1 else 'Areas'} of Interest")

    def loadThermalData(self, path):
        """Loads and converts thermal data based on the selected temperature unit.

        Args:
            path (str): Path to the thermal image file.

        Returns:
            np.ndarray: Temperature data array in the selected unit.
        """
        data = MetaDataHelper.getTemperatureData(path)
        return (data * 1.8) + 32 if self.temperature_unit == 'F' else data

    def previousImageButtonClicked(self):
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
            self.loadImage()
            self.scrollThumbnailIntoView()
        else:
            self.showNoImagesMessage()

    def nextImageButtonClicked(self):
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
            self.loadImage()
            self.scrollThumbnailIntoView()
        else:
            self.showNoImagesMessage()

    def showNoImagesMessage(self):
        """Displays an error message when there are no available images."""
        self.mainImage = None
        self.showError("No active images available.")

    def hideImageChange(self, state):
        """Toggles visibility of the current image and updates XML.

        Args:
            state (bool): True if the image should be hidden, False otherwise.
        """
        self.hideImageToggle.setChecked(state)
        image = self.images[self.current_image]
        image_element = image['xml']
        if image_element is not None:
            image_element.set('hidden', "True" if state else "False")
            self.xmlService.saveXmlFile(self.xml_path)
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
        else:
            self.logger.error("Image XML element is None, cannot update 'hidden' attribute.")

    def skipHiddenClicked(self, state):
        """Updates visibility setting for hidden images based on skipHidden checkbox.

        Args:
            state (bool): True if hidden images should be skipped, False otherwise.
        """
        self.show_hidden = not state

    def jumpToLineChanged(self):
        """Jumps to the specified image index when changed in the jump line input."""
        if self.jumpToLine.text() != "":
            self.current_image = int(self.jumpToLine.text()) - 1
            self.loadImage()
            self.scrollThumbnailIntoView()
            self.jumpToLine.setText("")

    def resizeEvent(self, event):
        """Handles window resize events to adjust the main image.

        Args:
            event (QResizeEvent): Resize event.
        """
        super().resizeEvent(event)
        if self.mainImage is not None:
            self.loadImage()

    def areaOfInterestClick(self, x, y, img):
        """Handles clicks on area of interest thumbnails.

        Args:
            x (int): X coordinate of the cursor.
            y (int): Y coordinate of the cursor.
            img (QtImageViewer): The clicked thumbnail image viewer.
        """
        self.mainImage.zoomToArea(img.center, 6)

    def KmlButtonClicked(self):
        """Handles clicks on the Generate KML button to create a KML file."""
        fileName, _ = QFileDialog.getSaveFileName(self, "Save KML File", "", "KML files (*.kml)")
        self.generateKml(fileName)

    def generateKml(self, output_path):
        """Generates a KML file from images' GPS data and saves it.

        Args:
            output_path (str): The file path to save the KML file.
        """
        kml = KMLService()
        kml_points = []
        for image in self.images:
            if image['hidden']:
                continue
            gps_coords = LocationInfo.getGPS(image['path'])
            if gps_coords:
                point = {"name": image['name'], "long": gps_coords['longitude'], "lat": gps_coords['latitude']}
                kml_points.append(point)
        kml.addPoints(kml_points)
        kml.saveKml(output_path)

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

    def showError(self, text):
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

    def getPosition(self, latitude, longitude):
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
            dms = LocationInfo.convertDecimalToDms(latitude, longitude)
            return f"{dms['latitude']['degrees']}°{dms['latitude']['minutes']}'{dms['latitude']['seconds']}\"{dms['latitude']['reference']} " \
                   f"{dms['longitude']['degrees']}°{dms['longitude']['minutes']}'{dms['longitude']['seconds']}\"{dms['longitude']['reference']}"
        elif self.position_format == 'UTM':
            utm = LocationInfo.convertDegreesToUtm(latitude, longitude)
            return f"{utm['zone_number']}{utm['zone_letter']} {utm['easting']} {utm['northing']}"


class ThumbnailLoader(QThread):
    """Threaded loader for generating and displaying image thumbnails."""

    thumbnailLoaded = pyqtSignal(int, QIcon)

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
                self.thumbnailLoaded.emit(index, icon)
