import logging
from PyQt5 import QtGui
import qimage2ndarray
import piexif
import imghdr
from pathlib import Path
from PyQt5.QtGui import QImage, QPixmap, QKeySequence, QIntValidator
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QListWidget, QFileDialog, QAction

from core.views.Viewer_ui import Ui_Viewer
from core.views.components.QtImageViewer import QtImageViewer
from core.services.KMLService import KMLService
from helpers.LocationInfo import LocationInfo

class Viewer(QMainWindow, Ui_Viewer):
	"""Controller for the Image Viewer(QMainWindow)."""
	def __init__(self, images):
		"""
		__init__ constructor to build the ADIAT Image Viewer
		
		:List(Dictionary) images: Images that will be displayed in the viewer
		"""
		QMainWindow.__init__(self)
		self.setupUi(self)
		
		self.images = images
		
		for image in self.images[:]:
			path = Path(image['path'])
			image_file = path
			image['name'] = path.name
			if not image_file.is_file():
				self.images.remove(image)
			elif imghdr.what(image['path']) is None:
				self.images.remove(image)
		
		if len(self.images) == 0:
			self.mainImage = None
			self.showError("No images available.")
		else:
			self.current_image = 0
			self.loadInitialImage()
			self.previousImageButton.clicked.connect(self.previousImageButtonClicked)
			self.nextImageButton.clicked.connect(self.nextImageButtonClicked)
			self.KmlButton.clicked.connect(self.KmlButtonClicked)
			self.jumpToLine.setValidator(QIntValidator(1, len(self.images), self))
			self.jumpToLine.editingFinished.connect(self.jumpToLineChanged)
	
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Right:
			self.nextImageButtonClicked()
		if e.key() == Qt.Key_Left:
			self.previousImageButtonClicked()
			
		
	def loadInitialImage(self):
		"""
		loadInitialImage loads the image and areas of interest at index 0 from the images list
		Seperate from the standard loader because it needs to replace the placeholder widget
		"""
		try:
			image = self.images[0]
			#remove the placeholder
			self.placeholderImage.deleteLater()
			#setup the image widget
			self.mainImage = QtImageViewer(self, self.centralwidget)
			self.mainImage.setMinimumSize(QSize(0, 650))
			self.mainImage.setObjectName("mainImage")
			self.mainImage.aspectRatioMode = Qt.KeepAspectRatio
			self.mainImage.canZoom = True
			self.mainImage.canPan = True
			#load and set the image
			img = QImage(image['path'])
			self.mainImage.setImage(img)
			self.ImageLayout.replaceWidget(self.placeholderImage, self.mainImage)
			
			self.fileNameLabel.setText(image['name'])
			#create the areas of interest thumbnails
			self.loadAreasofInterest(image)
			#get the gps info from the image exif data and display it
			gps_coords = LocationInfo.getGPS(image['path'])
			if not gps_coords == {}:
				self.statusbar.showMessage("GPS Coordinates: "+gps_coords['latitude']+", "+gps_coords['longitude'])
			else:
				self.statusbar.showMessage("")
			self.indexLabel.setText("Image "+str(self.current_image + 1)+" of "+str(len(self.images)))
		except Exception as e:
			logging.exception(e)

	def loadImage(self):
		"""
		loadImage loads the image at the current_image index
		"""
		try:
			image = self.images[self.current_image]
		
			#load and set the image
			img = QImage(image['path'])
			self.mainImage.setImage(img)
			self.fileNameLabel.setText(image['name'])
			self.loadAreasofInterest(image)
			self.mainImage.resetZoom()
			#get the gps info from the image exif data and display it
			self.indexLabel.setText("Image "+str(self.current_image + 1)+" of "+str(len(self.images)))
			gps_coords = LocationInfo.getGPS(image['path'])
			if not gps_coords == {}:
				self.statusbar.showMessage("GPS Coordinates: "+gps_coords['latitude']+", "+gps_coords['longitude'])
			else:
				self.statusbar.showMessage("")	
			self.indexLabel.setText("Image "+str(self.current_image + 1)+" of "+str(len(self.images)))
		except Exception as e:
			logging.exception(e)
	def loadAreasofInterest(self, image):
		"""
		loadAreasofInterest loads the list of thumbnails representing the areas of interest from the image
		
		:Dictionary image: a dictionary of information about the image for which areas of interest will be loaded
		"""
		#remove any thumbnails already in the list
		self.aoiListWidget.clear()
		
		#convert the image to an array
		img_arr = qimage2ndarray.imread(image['path'])
		img_width = img_arr.shape[1] - 1
		img_height = img_arr.shape[0] - 1
		count = 0
		cur_pos = 0;
		self.highlights = []
		for area_of_interest in image['areas_of_interest']:
			center = area_of_interest['center']
			radius = area_of_interest['radius']+10
			#create a cropped image based on the image array.
			crop_arr = self.crop_image(img_arr, center[0]-radius, center[1] - radius, center[0]+radius, center[1]+radius)
			#create the image widget
			highlight = QtImageViewer(self, self.aoiListWidget, center, True)
			highlight.setObjectName("highlight"+str(count))
			highlight.setMinimumSize(QSize(190, 190))
			highlight.aspectRatioMode = Qt.KeepAspectRatio
			#convert the cropped  array back to an image.
			img = qimage2ndarray.array2qimage(crop_arr)
			highlight.setImage(img)
			highlight.canZoom = False
			highlight.canPan = False

			#add the image widget to a list of widgets.
			listItem = QListWidgetItem()
			listItem.setSizeHint(QSize(190, 190))    
			self.aoiListWidget.addItem(listItem)
			self.aoiListWidget.setItemWidget(listItem, highlight)
			self.highlights.append(highlight)
			highlight.leftMouseButtonPressed.connect(self.areaOfInterestClick)
			count += 1
		if count == 1:
			self.areaCountLabel.setText(str(count)+ " Area of Interest")
		else:
			self.areaCountLabel.setText(str(count)+ " Areas of Interest")

	def previousImageButtonClicked(self):
		"""
		previousImageButtonClicked click handler to navigate to the previous image in the images list
		"""
		if self.current_image == 0:
			self.current_image = len(self.images) -1
		else:
			self.current_image -= 1
		self.loadImage()

	def nextImageButtonClicked(self):
		"""
		nextImageButtonClicked click handler to navigate to the next image in the images list
		"""
		if (self.current_image == len(self.images) -1):
			self.current_image = 0
		else:
			self.current_image += 1
		self.loadImage()
	
	def jumpToLineChanged(self):
		"""
		jumpToLineChanged change handler to jump to a particular image
		"""
		if not self.jumpToLine.text() == "":
			self.current_image = int(self.jumpToLine.text())-1
			self.loadImage()
			self.jumpToLine.setText("")
		
	def resizeEvent(self, event):
		"""
		resizeEvent event triggered by window resize that will resize that main image
		"""
		QMainWindow.resizeEvent(self, event)
		if self.mainImage is not None:
			#self.mainImage.updateViewer()
			self.loadImage()

	def areaOfInterestClick(self, x, y, img):
		"""
		areaOfInterestClick click handler for clicking on one of the area of interest thumbnail
		
		:Int x: the x coordinate of the cursor when clicked
		:Int y: the y coordinate of the cursor when clicked
		:QtImageViewer img: the thumbnail image
		"""
		self.mainImage.zoomToArea(img.center,6)
		
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
		kml = KMLService();
		kml_points = list()
		for image in self.images:
			#images that do not have gps info in their exif data will be skipped
			gps_coords = LocationInfo.getGPS(image['path'])
			if not gps_coords == {}:
				point = dict()
				point["name"] = image['name']
				point["long"] = gps_coords['longitude']
				point["lat"] = gps_coords['latitude']
				kml_points.append(point)
		kml.addPoints(kml_points)
		kml.saveKml(output_path)
			
	def crop_image(self,img_arr,startx,starty, endx, endy):
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
		return img_arr[sy:ey,sx:ex]
	
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