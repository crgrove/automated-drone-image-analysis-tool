import functools
from itertools import count
import operator

import cv2
import os
import imghdr
import shutil
import xml.etree.ElementTree as ET
import logging
from numpy import full
import piexif
import time
import concurrent
from pathlib import Path
from helpers.ExifTransfer import ExifTransfer
from core.services.HistogramNormalizationService import HistogramNormalizationService
from core.services.KMeansClustersService import KMeansClustersService
from concurrent.futures import ProcessPoolExecutor
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

"""****Import Algorithm Services****"""
from algorithms.ColorMatch.services.ColorMatchService import ColorMatchService
from algorithms.RXAnomaly.services.RXAnomalyService import RXAnomalyService
from algorithms.MatchedFilter.services.MatchedFilterService import MatchedFilterService
"""****End Algorithm Import****"""

class AnalyzeService(QObject):
	"""Service to process images using a selected algorithm"""
	#Signals to send info back to the GUI
	sig_msg = pyqtSignal(str)
	sig_aois = pyqtSignal()
	sig_done = pyqtSignal(int, int)

	def __init__(self, id, algorithm, input, output, identifier_color, min_area, num_processes, max_aois, aoi_radius, histogram_reference_path, kmeans_clusters, options):
		"""
		__init__ constructor
		
		:Int id: numeric id
		:String algorithm: the name of the algorithm to be used for analysis
		:String input: the path to the input directory containing the images to be processed
		:String output: the path to the output directory where images will be stored
		:Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int num_processes: the number of concurrent processes to be used to process images
		:Int max_aois: the threshold for a maximum number of areas of interest in a single image before a warning is produced
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:String histogram_reference_path: the path to the histogram matching reference image
		:Int kmeans_clusters: the number of clusters(colors) to maintain in the image
		:Dictionary options: additional algorithm-specific options
		"""
		super().__init__()
		self.algorithm = algorithm
		self.input = input
		self.output_dir = output
		self.output = os.path.join(output, "ADIAT_Results")
		self.identifier_color = identifier_color
		self.options = options
		self.min_area = min_area
		self.aoi_radius = aoi_radius
		self.num_processes = num_processes
		self.max_aois = max_aois
		self.max_aois_limit_exceeded = False
		self.hist_ref_path = histogram_reference_path
		self.kmeans_clusters = kmeans_clusters
		self.__id = id
		self.images_with_aois = []
		self.cancelled = False
	
	
	@pyqtSlot()
	def processFiles(self):
		"""
		processFiles iterates through all of the files in a directory and processes the image using the selected algorithm and features
		"""
		try:
			self.setupOutputDir();
			self.setupOutputXml()
			image_files = []
			
			start_time = time.time()
			for subdir, dirs, files in os.walk(self.input):
				for file in files:
					image_files.append(os.path.join(subdir, file))
			self.sig_msg.emit("Processing "+str(len(image_files))+" files")
			
			position = 0
			batch_size = 100
			#loop through all of the files in the input directory and process them in multiple processes.  Breaking up into 100 file batches to limit the amount of time it takes to cancel.
			while True and not self.cancelled:
				with ProcessPoolExecutor(max_workers=self.num_processes) as self.executor:
					for i in range (position, position + batch_size):
						if i >= len(image_files):
							break;
						full_path = image_files[i]
						
						#skip if it's a directory
						if(os.path.isdir(image_files[position])):
							continue
						#skip if the file isn't an image
						if imghdr.what(full_path) is not None:
							future = self.executor.submit(AnalyzeService.processFile, i, self.algorithm, self.identifier_color, self.min_area, self.aoi_radius, self.options, full_path, self.hist_ref_path , self.kmeans_clusters)
							future.add_done_callback(self.processComplete)
						else:
							self.sig_msg.emit("Skipping "+full_path+ " - File is not an image")
				position = position + batch_size
				if position >= len(image_files):
					break
			#generate the output xml with the information gathered during processing			
			self.images_with_aois = sorted(self.images_with_aois, key=operator.itemgetter('path'))
			for img in self.images_with_aois:
				self.addImageToXml(img)
			self.writeXmlFile()
			ttl_time = round(time.time() - start_time, 3)
			self.sig_done.emit(self.__id, len(self.images_with_aois))
			self.sig_msg.emit("Total Processing Time: "+str(ttl_time)+" seconds")
		except Exception as e:
			logging.exception(e)

	@staticmethod
	def processFile(i, algorithm, identifier_color, min_area, aoi_radius, options, full_path, hist_ref_path, kmeans_clusters):
		"""
		processFile processes a single image using the selected algorithm and features
		
		:String algorithm: the name of the algorithm to be used
		:Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:Dictionary options: additional algorithm-specific options
		:String full_path: the path to the image being analyzed
		:String hist_ref_path: the path to the histogram matching reference image
		:Int kmeans_clusters: the number of clusters(colors) to maintain in the image
		:return numpy.ndarray, List: the numpy.ndarray representation of the image augmented with areas of interest circled and a list of the areas of interest
		"""
		img = cv2.imread(full_path)
		path = Path(full_path)
		file_name = path.name
		
		#if the histogram reference image path is not empty, create an instance of the HistogramNormalizationService
		histogram_service = None
		if hist_ref_path is not None:
			histogram_service = HistogramNormalizationService(hist_ref_path)
			img = histogram_service.matchHistograms(img)
				
		#if the kmeans clusters number is not empty, create an instance of the KMeansClustersService			
		kmeans_service = None
		if kmeans_clusters is not None:
			kmeans_service = KMeansClustersService(kmeans_clusters)
			img = kmeans_service.generateClusters(img)
				
		#Create an instance of the algorithm class
		cls = globals()[algorithm+"Service"]
		instance = cls(identifier_color, min_area, aoi_radius, options)
			
		try:
			#process the image using the algorithm
			return instance.processImage(img,file_name,full_path)
		except Exception as e:
			logging.exception(e)
	
	@pyqtSlot()			
	def processComplete(self, future):
		"""
		processComplete processes the analyzed image

		:concurrent.futures._base.Future future: object representing the execution of the callable
		"""
		if future.done() and not future.cancelled() and not self.cancelled:
			result = future.result()
			is_jpg = imghdr.what(result.full_path) == 'jpg' or imghdr.what(result.full_path) == 'jpeg'
			#if the image is a jpg read the exif information
			if is_jpg:
				exif_dict = piexif.load(result.full_path)
				if not 'GPS' in exif_dict:
					is_jpg = False
			try:
				#returned by processFile method		
				if result.augmented_image is not None:
					#save the image to the output directory and add the image/areas of interest to the output xml
					output_file = result.full_path.replace(self.input, self.output)
					path = Path(output_file)
					if not os.path.exists(path.parents[0]):
						os.makedirs(path.parents[0])
					cv2.imwrite(output_file, result.augmented_image)
					self.images_with_aois.append({"path": output_file, "aois": result.areas_of_interest})
					self.sig_msg.emit('Areas of interest identified in '+result.file_name)
					if is_jpg:
						try:
							piexif.transplant(result.full_path, output_file)
						except  piexif._exceptions.InvalidImageDataError as e:
							#piexif doesn't always work, but it's way faster than PIL.  If piexif fails try PIL
							ExifTransfer.transfer_exif(result.full_path, output_file)
							
				else:
					self.sig_msg.emit('No areas of interested identified in '+result.file_name)
				if result.areas_of_interest is not None:
					if result.base_contour_count > self.max_aois and not self.max_aois_limit_exceeded:
						self.sig_aois.emit()
						self.max_aois_limit_exceeded = True
			except concurrent.futures.CancelledError as e:
				logging.exception(e)
				
	@pyqtSlot()
	def processCancel(self):
		"""
		processCancel cancels any asynchronous processes that have not completed
		"""
		self.cancelled = True
		self.sig_msg.emit("--- Cancelling Image Processing ---")	
		self.executor.shutdown(wait = False, cancel_futures=True)
			
	def setupOutputDir(self):
		"""
		setupOutputDir creates the output directory
		"""
		try:
			if(os.path.exists(self.output)):
				try:
					shutil.rmtree(self.output)
				except Exception as e:
					logging.exception(e)
			os.makedirs(self.output)
		except Exception as e:
			logging.exception(e)

	def setupOutputXml(self):
		"""
		setupOutputXml creates the xml document add adds information about the parameters set by the user
		"""
		try:
			self.xml = ET.Element('data')
			settings_xml = ET.SubElement(self.xml, "settings")
			settings_xml.set("input_dir", self.input)
			settings_xml.set("output_dir", self.output_dir)
			settings_xml.set("identifier_color", self.identifier_color)
			settings_xml.set("algorithm", self.algorithm)
			settings_xml.set("num_processes", str(self.num_processes))
			settings_xml.set("min_area", str(self.min_area))
			settings_xml.set("hist_ref_path", str(self.hist_ref_path ))
			settings_xml.set("kmeans_clusters", str(self.kmeans_clusters))
			options_xml = ET.SubElement(settings_xml, "options")
			for key, value in self.options.items():
				option_xml = ET.SubElement(options_xml, "option")
				option_xml.set("name", key)
				option_xml.set("value", str(value))
			self.images_xml = ET.SubElement(self.xml, "images")
		except Exception as e:
			logging.exception(e)

	def addImageToXml(self, img):
		"""
		addImageToXml adds an image to the xml document
		
		:Dictionary img: the full path to the output file and a list of areas of interest
		"""
		image = ET.SubElement(self.images_xml, 'image')
		image.set('path',img["path"])
		for area in img["aois"]:
			area_xml = ET.SubElement(image, 'areas_of_interest')
			area_xml.set('center', str(area['center']))
			area_xml.set('radius', str(area['radius']))
			area_xml.set('area', str(area['area']))


	def writeXmlFile(self):
		"""
		writeXmlFile saves the xml document
		"""
		mydata = ET.ElementTree(self.xml)
		file_path = os.path.join(self.output, "ADIAT_Data.xml")
		with open(file_path, "wb") as fh:
			mydata.write(fh)