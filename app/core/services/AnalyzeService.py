import functools

import cv2
import os
import imghdr
import xml.etree.ElementTree as ET
import logging
import piexif
import time
import concurrent
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

	def __init__(self, id, algorithm, input, output, identifier_color, min_area, num_processes, max_aois, histogram_reference_path, kmeans_clusters, options):
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
		self.num_processes = num_processes
		self.max_aois = max_aois
		self.max_aois_limit_exceeded = False
		self.hist_ref_path = histogram_reference_path
		self.kmeans_clusters = kmeans_clusters
		self.__id = id
		self.images_with_aois = 0
		self.cancelled = False
	
	
	@pyqtSlot()
	def processFiles(self):
		"""
		processFiles iterates through all of the files in a directory and processes the image using the selected algorithm and features
		"""
		try:
			self.setupOutputDir();
			self.setupOutputXml()
			self.futures = [];
			
			start_time = time.time()
			files = os.listdir(self.input)
			self.sig_msg.emit("Processing "+str(len(files))+" files")
			#
			#loop through all of the files in the input directory and process them in multiple processes
			with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
				for file in files:
					full_path =  os.path.join(self.input, file)
					#skip if it's a directory
					if(os.path.isdir(full_path)):
						continue
					#skip if the file isn't an image
					if imghdr.what(full_path) is not None:
						future = executor.submit(AnalyzeService.processFile, self.algorithm, self.identifier_color, self.min_area, self.options, full_path, self.hist_ref_path , self.kmeans_clusters)
						future.add_done_callback(functools.partial(self.processComplete, file, full_path))
						self.futures.append(future);
					else:
						self.sig_msg.emit("Skipping "+file+ " - File is not an image")
			#generate the output xml with the information gathered during processing			
			self.writeXmlFile()
			ttl_time = round(time.time() - start_time, 3)
			self.sig_done.emit(self.__id, self.images_with_aois)
			self.sig_msg.emit("Total Processing Time: "+str(ttl_time)+" seconds")
		except Exception as e:
			logging.exception(e)

	@staticmethod
	def processFile(algorithm, identifier_color, min_area, options, full_path, hist_ref_path, kmeans_clusters):
		"""
		processFile processes a single image using the selected algorithm and features
		
		:String algorithm: the name of the algorithm to be used
		:Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Dictionary options: additional algorithm-specific options
		:String full_path: the path to the image being analyzed
		:String hist_ref_path: the path to the histogram matching reference image
		:Int kmeans_clusters: the number of clusters(colors) to maintain in the image
		:return numpy.ndarray, List: the numpy.ndarray representation of the image augmented with areas of interest circled and a list of the areas of interest
		"""
		img = cv2.imread(full_path)
		
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
		instance = cls(identifier_color, min_area, options)
			
		try:
			#process the image using the algorithm
			return instance.processImage(img)
		except Exception as e:
			logging.exception(e)
	
	@pyqtSlot()			
	def processComplete(self, file, full_path, future):
		"""
		processComplete processes the analyzed image
		
		:String file: the filename of the image
		:String full_path: the full path to the source image
		:concurrent.futures._base.Future future: object representing the execution of the callable
		"""
		if future.done() and not future.cancelled() and not self.cancelled:
			is_jpg = imghdr.what(full_path) == 'jpg' or imghdr.what(full_path) == 'jpeg'
			#if the image is a jpg read the exif information
			if is_jpg:
				exif_dict = piexif.load(full_path)
				try:
					exif_bytes = piexif.dump(exif_dict)
				except piexif._exceptions.InvalidImageDataError:
					is_jpg = False
			try:
				#returned by processFile method
				results = future.result()
				result = results[0]
				areas_of_interest = results[1]
				if result is not None:
					#save the image to the output directory and add the image/areas of interest to the output xml
					output_file = self.output+"/"+file
					cv2.imwrite(output_file, result)
					self.addImageToXml(file,areas_of_interest)
					self.sig_msg.emit('Areas of interest identified in '+file)
					self.images_with_aois += 1
					if is_jpg:
						piexif.insert(exif_bytes, output_file)
				else:
					self.sig_msg.emit('No areas of interested identified in '+file)
				if areas_of_interest is not None:
					if len(areas_of_interest) > self.max_aois and not self.max_aois_limit_exceeded:
						self.sig_aois.emit()
						self.max_aois_limit_exceeded = True
			except concurrent.futures.CancelledError as e:
				logging.exception(e)
				
	@pyqtSlot()
	def processCancel(self):
		"""
		processCancel cancels any asynchronous processes that have not completed
		"""
		for future in self.futures:
			future.cancel()
		self.cancelled = True
		self.sig_msg.emit("--- Cancelling Image Processing ---")	
			
	def setupOutputDir(self):
		"""
		setupOutputDir checks if the output directory exists.  If it does delete everything in it.
		"""
		try:
			if(os.path.isdir(self.output)):
				for the_file in os.listdir(self.output):
					file_path = os.path.join(self.output, the_file)
					try:
						if os.path.isfile(file_path):
							os.unlink(file_path)
						#elif os.path.isdir(file_path): shutil.rmtree(file_path)
					except Exception as e:
						logging.exception(e)
			else:
				os.mkdir(self.output)
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
			options_xml = ET.SubElement(settings_xml, "options")
			for key, value in self.options.items():
				option_xml = ET.SubElement(options_xml, "option")
				option_xml.set("name", key)
				option_xml.set("value", str(value))
			self.images_xml = ET.SubElement(self.xml, "images")
		except Exception as e:
			logging.exception(e)

	def addImageToXml(self, file, areas_of_interest):
		"""
		addImageToXml adds an image to the xml document
		
		:String file: the name of the file
		:List(Dictionary): the areas of interest for the image
		"""
		image = ET.SubElement(self.images_xml, 'image')
		image.set('file_name',file)
		for area in areas_of_interest:
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