import qimage2ndarray
import imghdr
from pathlib import Path
from PyQt5.QtGui import QImage, QIntValidator, QPixmap, QImageReader, QIcon
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QFileDialog, QPushButton, QFrame, QVBoxLayout, QLabel
from qtwidgets import Toggle

from core.views.Viewer_ui import Ui_Viewer
from core.views.components.QtImageViewer import QtImageViewer
from core.services.KMLService import KMLService
from core.services.XmlService import XmlService
from helpers.LocationInfo import LocationInfo
from core.services.LoggerService import LoggerService
from helpers.MetaDataHelper import MetaDataHelper


class Viewer(QMainWindow, Ui_Viewer):
    """Controller for the Image Viewer(QMainWindow)."""

    def __init__(self, xml_path, position_format, temperature_unit, show_hidden):
        """
        __init__ constructor to build the ADIAT Image Viewer

        :string xml_path: Path to xml file containing results data
        :string position_format: The position format in which GPS coordinates will be displayed
        :string temperature_unit: The unit in which temperature values be displayed
        :boolean show_hidden: Wheher or not to show hidden images by default
        """
        QMainWindow.__init__(self)
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
        if temperature_unit == 'Fahrenheit':
            self.temperature_unit = 'F'
        else:
            self.temperature_unit = 'C'
        self.show_hidden = show_hidden
        self.skipHidden.setChecked(not self.show_hidden)
        self.skipHidden.clicked.connect(self.skipHiddenClicked)
        self.thumbnail_limit = 20
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
        """
        Kill the thumbnail threads before closing.
        """
        for thread, analyze in self.__threads:
            thread.quit()
        
    def addHideImageToggle(self):
        self.hideImageToggle = Toggle()
        self.ButtonLayout.replaceWidget(self.hideImageCheckbox, self.hideImageToggle)
        self.hideImageCheckbox.deleteLater()
        self.hideImageToggle.clicked.connect(self.hideImageChange)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Right:
            self.nextImageButtonClicked()
        if e.key() == Qt.Key_Left:
            self.previousImageButtonClicked()
        if e.key() == Qt.Key_Down or e.key() == Qt.Key_P:
            self.hideImageChange(True)
        if e.key() == Qt.Key_Up or e.key() == Qt.Key_U:
            self.hideImageChange(False)

    def loadImages(self):
        valid_images = []
        for index, image in enumerate(self.images[:]):
            path = Path(image['path'])
            image_file = path
            image['name'] = path.name
            if image_file.is_file() and imghdr.what(image['path']) is not None:
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

            frame.adjustSize()
            frame.setStyleSheet("""
                border: 1px solid grey;
                border-radius: 3px;
            """)
            overlay = QLabel(frame)
            overlay.setFixedSize(frame.width(), frame.height())
            overlay.setAttribute(Qt.WA_TransparentForMouseEvents)  # Ensure clicks pass through
            overlay.move(0, 0)  # Position the overlay at the top-left corner
            overlay.show()
            button.setProperty('overlay', overlay)
            self.thumbnailLayout.addWidget(frame)
            image['thumbnail'] = button

    def loadThumbnailsInRange(self, start_index, end_index):
        # Create and start a new thumbnail loader thread
        self.thumbnail_loader = ThumbnailLoader(self.images, start_index, end_index, self.loaded_thumbnails)
        thread = QThread()
        self.__threads.append((thread, self.thumbnail_loader))
        self.thumbnail_loader.moveToThread(thread)

        self.thumbnail_loader.thumbnailLoaded.connect(self.onThumbnailLoaded)
        self.thumbnail_loader.finished.connect(self.onThumbnailLoadFinished)

        thread.started.connect(self.thumbnail_loader.run)
        thread.start()

    def onThumbnailLoaded(self, index, icon):
        button = self.images[index]['thumbnail']
        button.setIcon(icon)
        button.setIconSize(QSize(100, 56))
        if self.images[index].get('hidden'):
            overlay = button.property('overlay')
            overlay.setStyleSheet("""
                background-color: rgba(128, 128, 128, 150);  /* Semi-transparent grey */
            """)
        self.loaded_thumbnails.append(index)

    def onThumbnailLoadFinished(self):
        for thread, analyze in self.__threads:
            thread.quit()

    def onThumbnailScroll(self):
        scrollbar = self.thumbnailScrollArea.horizontalScrollBar()
        max_scroll_value = scrollbar.maximum()
        current_scroll_value = scrollbar.value()
        total_images = len(self.images)

        # Calculate the visible range of thumbnails
        visible_start_index = int((current_scroll_value / max_scroll_value) * total_images)
        # Load more thumbnails to the left of the visible area
        visible_start_index = max(0, visible_start_index - int(self.thumbnail_limit))
        visible_end_index = min(visible_start_index + self.thumbnail_limit + 5, total_images)

        # Ensure that thumbnails are loaded within the updated range
        if (int(visible_start_index), int(visible_end_index)) != self.visible_thumbnails_range:
            self.loadThumbnailsInRange(visible_start_index, visible_end_index)
            self.visible_thumbnails_range = (int(visible_start_index), int(visible_end_index))

    def onThumbnailClicked(self):
        button = self.sender()
        self.current_image = button.property('imageIndex')
        self.loadImage()

    def scrollThumbnailIntoView(self):
        """
        Scroll the thumbnail scroll area to ensure the active thumbnail is visible
        """
        if self.active_thumbnail:
            self.thumbnailScrollArea.ensureWidgetVisible(self.active_thumbnail)

    def setActiveThumbnail(self, button):
        frame = button.property('frame')
        if self.active_thumbnail:
            self.active_thumbnail.setStyleSheet("border: 1px solid grey;")

        frame.setStyleSheet("""
            QFrame  {
                border: 2px solid blue;

            }
        """)
        self.active_thumbnail = frame

    def loadInitialImage(self):
        """
        loadInitialImage loads the image and areas of interest at index 0 from the images list
        Seperate from the standard loader because it needs to replace the placeholder widget
        """
        try:
            self.current_image = None
            for i in range(0, len(self.images)):
                if not self.show_hidden and self.images[i]['hidden']:
                    continue
                self.current_image = i
                break
            #If all the images are hidden load the first one anyway
            if self.current_image is None:
                self.current_image = 0
                
            image = self.images[self.current_image]
            # remove the placeholder
            self.placeholderImage.deleteLater()
            # setup the image widget
            self.mainImage = QtImageViewer(self, self.centralwidget)
            self.mainImage.setMinimumSize(QSize(0, 650))
            self.mainImage.setObjectName("mainImage")
            self.mainImage.aspectRatioMode = Qt.KeepAspectRatio
            self.mainImage.canZoom = True
            self.mainImage.canPan = True
            # load and set the image
            img = QImage(image['path'])
            self.mainImage.setImage(img)
            self.ImageLayout.replaceWidget(self.placeholderImage, self.mainImage)

            self.fileNameLabel.setText(image['name'])
            # create the areas of interest thumbnails
            self.loadAreasofInterest(image)
            # get the gps info from the image exif data and display it
            gps_coords = LocationInfo.getGPS(image['path'])
            if not gps_coords == {}:
                self.position = self.getPosition(gps_coords['latitude'], gps_coords['longitude'])
                self.statusbar.showMessage("GPS Coordinates: " + self.position)
            else:
                self.statusbar.showMessage("")
            self.indexLabel.setText("Image " + str(self.current_image + 1) + " of " + str(len(self.images)))
            if self.is_thermal:
                self.temperature_data = self.loadThermalData(image['path'])
            self.mainImage.mousePositionOnImageChanged.connect(self.mainImageMousePos)
            self.hideImageToggle.setChecked(image['hidden'])
        except Exception as e:
            self.logger.error(e)

    def mainImageMousePos(self, pos):
        if self.temperature_data is not None:
            shape = self.temperature_data.shape
            if (pos.y() >= 0 and pos.x() >= 0) and (pos.y() < shape[0] and pos.x() < shape[1]):
                if self.position:
                    new_message = "GPS Coordinates: " + self.position + "    Temperature: " + \
                        str(round(self.temperature_data[pos.y()][pos.x()], 2)) + u'\N{DEGREE SIGN}' + " " + self.temperature_unit
                else:
                    new_message = "Temperature: " + str(round(self.temperature_data[pos.y()][pos.x()], 2)) + u'\N{DEGREE SIGN}' + " " + self.temperature_unit
                self.statusbar.showMessage(new_message)

    def loadImage(self):
        """
        loadImage loads the image at the current_image index
        """
        try:
            image = self.images[self.current_image]
            self.setActiveThumbnail(image['thumbnail'])
            # load and set the image
            img = QImage(image['path'])
            self.mainImage.setImage(img)
            self.fileNameLabel.setText(image['name'])
            self.loadAreasofInterest(image)
            self.mainImage.resetZoom()
            self.mainImage.setFocus()
            self.hideImageToggle.setChecked(image['hidden'])
            # get the gps info from the image exif data and display it
            self.indexLabel.setText("Image " + str(self.current_image + 1) + " of " + str(len(self.images)))
            gps_coords = LocationInfo.getGPS(image['path'])
            self.position = None
            if not gps_coords == {}:
                self.position = self.getPosition(gps_coords['latitude'], gps_coords['longitude'])
                # self.statusbar.showMessage("GPS Coordinates: "+gps_coords['latitude']+", "+gps_coords['longitude'])
                self.statusbar.showMessage("GPS Coordinates: " + self.position)
            else:
                self.statusbar.showMessage("")
            self.indexLabel.setText("Image " + str(self.current_image + 1) + " of " + str(len(self.images)))
            if self.is_thermal:
                self.temperature_data = self.loadThermalData(image['path'])
            self.mainImage.mousePositionOnImageChanged.connect(self.mainImageMousePos)
        except Exception as e:
            self.logger.error(e)

    def loadAreasofInterest(self, image):
        """
        loadAreasofInterest loads the list of thumbnails representing the areas of interest from the image

        :Dictionary image: a dictionary of information about the image for which areas of interest will be loaded
        """
        # remove any thumbnails already in the list
        self.aoiListWidget.clear()

        # convert the image to an array
        img_arr = qimage2ndarray.imread(image['path'])
        count = 0
        self.highlights = []
        for area_of_interest in image['areas_of_interest']:
            center = area_of_interest['center']
            radius = area_of_interest['radius'] + 10
            # create a cropped image based on the image array.
            crop_arr = self.crop_image(img_arr, center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)
            # create the image widget
            highlight = QtImageViewer(self, self.aoiListWidget, center, True)
            highlight.setObjectName("highlight" + str(count))
            highlight.setMinimumSize(QSize(190, 190))
            highlight.aspectRatioMode = Qt.KeepAspectRatio
            # convert the cropped array back to an image.
            img = qimage2ndarray.array2qimage(crop_arr)
            highlight.setImage(img)
            highlight.canZoom = False
            highlight.canPan = False

            # add the image widget to a list of widgets.
            listItem = QListWidgetItem()
            listItem.setSizeHint(QSize(190, 190))
            self.aoiListWidget.addItem(listItem)
            self.aoiListWidget.setItemWidget(listItem, highlight)
            self.highlights.append(highlight)
            highlight.leftMouseButtonPressed.connect(self.areaOfInterestClick)
            count += 1
        if count == 1:
            self.areaCountLabel.setText(str(count) + " Area of Interest")
        else:
            self.areaCountLabel.setText(str(count) + " Areas of Interest")

    def loadThermalData(self, path):
        data = MetaDataHelper.getTemperatureData(path)
        if self.temperature_unit == 'F':
            return (data * 1.8000) + 32
        else:
            return data

    def previousImageButtonClicked(self):
        """
        previousImageButtonClicked click handler to navigate to the previous image in the images list
        """
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
            self.showNoImagesMessage

    def nextImageButtonClicked(self):
        """
        nextImageButtonClicked click handler to navigate to the next image in the images list
        """
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
            self.showNoImagesMessage

    def showNoImagesMessage(self):
        self.mainImage = None
        self.showError("No active images available.")

    def hideImageChange(self, state):
        """
        hideImageChange click handler to update the results xml to show/hide an image and go to next image in the images list if it is hidden
        """
        self.hideImageToggle.setChecked(state)
        # Ensure xml element exists
        image = self.images[self.current_image]
        image_element = image['xml']
        if image_element is not None:
            image_element.set('hidden', "True" if state else "False")
            self.xmlService.saveXmlFile(self.xml_path)
            overlay = image['thumbnail'].property('overlay')
            if state:

                overlay.setStyleSheet("""
                    background-color: rgba(128, 128, 128, 150);  /* Semi-transparent grey */
                """)
                if not image['hidden']:
                    self.hidden_image_count += 1

            else:
                overlay.setStyleSheet("""
                    background-color: none;
                """)
                if image['hidden']:
                    self.hidden_image_count -= 1
            image['hidden'] = state
            self.skipHidden.setText(f"Skip Hidden ({self.hidden_image_count}) ")
        else:
            self.logger.error("Image XML element is None, cannot update 'hidden' attribute.")

    def skipHiddenClicked(self, state):
        """
        skipHiddenClicked handler for the skipHidden Checkbox
        """
        self.show_hidden = not state

    def jumpToLineChanged(self):
        """
        jumpToLineChanged change handler to jump to a particular image
        """
        if not self.jumpToLine.text() == "":
            self.current_image = int(self.jumpToLine.text()) - 1
            self.loadImage()
            self.scrollThumbnailIntoView()
            self.jumpToLine.setText("")

    def resizeEvent(self, event):
        """
        resizeEvent event triggered by window resize that will resize that main image
        """
        QMainWindow.resizeEvent(self, event)
        if self.mainImage is not None:
            # self.mainImage.updateViewer()
            self.loadImage()

    def areaOfInterestClick(self, x, y, img):
        """
        areaOfInterestClick click handler for clicking on one of the area of interest thumbnail

        :Int x: the x coordinate of the cursor when clicked
        :Int y: the y coordinate of the cursor when clicked
        :QtImageViewer img: the thumbnail image
        """
        self.mainImage.zoomToArea(img.center, 6)

    def KmlButtonClicked(self):
        """
        KmlButtonClicked click handler for the genereate KML button
        Opens a save file dialog and calls generateKml to produce the KML file
        """
        fileName, _ = QFileDialog.getSaveFileName(self, "Save KML File", "", "KML files (*.kml)")
        self.generateKml(fileName)

    def generateKml(self, output_path):
        """
        generateKml produces the KML file and saves it to the output_path

        :String output_path: the path where the KML file will be saved
        """
        kml = KMLService()
        kml_points = list()
        for image in self.images:
            # images that do not have gps info in their exif data will be skipped
            if image['hidden']:
                continue
            gps_coords = LocationInfo.getGPS(image['path'])
            if not gps_coords == {}:
                point = dict()
                point["name"] = image['name']
                point["long"] = gps_coords['longitude']
                point["lat"] = gps_coords['latitude']
                kml_points.append(point)
        kml.addPoints(kml_points)
        kml.saveKml(output_path)

    def crop_image(self, img_arr, startx, starty, endx, endy):
        """
        crop_image produces an array representing a portion of a larger input array

        :numpy.ndarray img_array: the array representing the input image
        :Int startx: the x coordinate of the start position
        :Int starty: the y coordinate of the start position
        :Int endx: the x coordinate of the end position
        :Int endy: the y coordinate of the end position
        :return numpu.ndarray: the array representing the cropped image
        """
        sx = startx
        if sx < 0:
            sx = 0
        sy = starty
        if sy < 0:
            sy = 0

        img_width = img_arr.shape[1] - 1
        img_height = img_arr.shape[0] - 1
        ex = endx
        if ex > img_width:
            ex = img_width
        ey = endy
        if ey > img_height:
            ey = img_height
        return img_arr[sy:ey, sx:ex]

    def showError(self, text):
        """
        showError open a message box showing an error with the provided text

        :String text: the text to be included are the error message
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error Loading Images")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def getPosition(self, latitude, longitude):
        """
        getPosition takes in the latitude and longitude in degree, minute, second format and returns the position as a string in the selected coordinate format

        :string latitude: the latitude in degree, minute, second format
        :string longitude: the longitude in degree, minute, second format
        :return string: the location
        """
        if self.position_format == 'Lat/Long - Decimal Degrees':
            return "{lat}, {lng}".format(lat=latitude, lng=longitude)
        elif self.position_format == 'Lat/Long - Degrees, Minutes, Seconds':
            dms = LocationInfo.convertDecimalToDms(latitude, longitude)
            return "{lat_deg}\N{DEGREE SIGN}{lat_min}'{lat_sec}\"{lat_ref} {lng_deg}\N{DEGREE SIGN}{lng_min}'{lng_sec}\"{lng_ref}".format(
                lat_deg=dms['latitude']['degrees'], lat_min=dms['latitude']['minutes'], lat_sec=dms['latitude']['seconds'],
                lat_ref=dms['latitude']['reference'], lng_deg=dms['longitude']['degrees'], lng_min=dms['longitude']['minutes'],
                lng_sec=dms['longitude']['seconds'], lng_ref=dms['longitude']['reference']
            )
        elif self.position_format == 'UTM':
            utm = LocationInfo.convertDegreesToUtm(latitude, longitude)
            return "{zone}{letter} {easting} {northing}".format(
                zone=utm['zone_number'], letter=utm['zone_letter'], easting=utm['easting'], northing=utm['northing'])


class ThumbnailLoader(QThread):
    # Signal to notify that a thumbnail is loaded (index, QIcon)
    thumbnailLoaded = pyqtSignal(int, QIcon)

    def __init__(self, images, start_index, end_index, existing_thumbnails, parent=None):
        super().__init__(parent)
        self.images = images
        self.start_index = max(start_index, 0)
        self.end_index = min(end_index, len(images))
        self.existing_thumbnails = existing_thumbnails

    def run(self):
        for index in range(self.start_index, self.end_index):
            if index not in self.existing_thumbnails:
                image_path = self.images[index]['path']
                reader = QImageReader(image_path)
                reader.setScaledSize(QSize(100, 56))
                pixmap = QPixmap.fromImage(reader.read())
                icon = QIcon(pixmap)
                self.thumbnailLoaded.emit(index, icon)  # Emit signal when thumbnail is loaded
