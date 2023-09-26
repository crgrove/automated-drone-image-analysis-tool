import functools

import numpy as np
import cv2
import os
import imghdr
import xml.etree.ElementTree as ET
import logging
import piexif
import time
import asyncio
import concurrent
from core.services.HistogramNormalizationService import HistogramNormalizationService
from core.services.KMeansClustersService import KMeansClustersService

from concurrent.futures import ProcessPoolExecutor
from helpers.ColorUtils import ColorUtils
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

"""****Import Algorithms****"""
from algorithms.ColorMatch.services.ColorMatchService import ColorMatchService
from algorithms.RXAnomaly.services.RXAnomalyService import RXAnomalyService
from algorithms.MatchedFilter.services.MatchedFilterService import MatchedFilterService
"""****End Algorithm Import****"""

class AnalyzeService(QObject):

	#Signals to send info back to the GUI
	sig_msg = pyqtSignal(str)
	sig_aois = pyqtSignal()
	sig_done = pyqtSignal(int, int)

	def __init__(self, id,algorithm, input, output, identifier_color, min_area, num_processes, maxAOIs, histogram_reference_path, kmeans_clusters, options):
		super().__init__()
		self.algorithm = algorithm
		self.input = input
		self.output_dir = output
		self.output = os.path.join(output, "ADIAT_Results")
		self.identifier_color = identifier_color
		self.options = options
		self.min_area = min_area
		self.num_processes = num_processes
		self.maxAOIs = maxAOIs
		self.maxAOIsLimitExceeded = False
		self.hist_ref_path = histogram_reference_path
		self.kmeans_clusters = kmeans_clusters
		self.__id = id
		self.images_with_aois = 0
		self.cancelled = False
	
	
	@pyqtSlot()
	def processFiles(self):
		try:
			self.setupOutputDir();
			self.setupOutputXml()
			self.futures = [];

			histogram_service = None
			if self.hist_ref_path is not None:
				histogram_service = HistogramNormalizationService(self.hist_ref_path)
			kmeans_service = None
			if self.kmeans_clusters is not None:
				kmeans_service = KMeansClustersService(self.kmeans_clusters)
			#Create an instance of the algorithm class
			cls = globals()[self.algorithm+"Service"]
			instance = cls(self.identifier_color, self.min_area, self.options)
			
			start_time = time.time()
			files = os.listdir(self.input)
			self.sig_msg.emit("Processing "+str(len(files))+" files")
			#loop through all of the files in the input directory and process them in multiple processes
			with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
				for file in files:
					full_path =  os.path.join(self.input, file)
					if(os.path.isdir(full_path)):
						continue
					if imghdr.what(full_path) is not None:
						future = executor.submit(AnalyzeService.processFile, instance, file, full_path, histogram_service, kmeans_service)
						future.add_done_callback(functools.partial(self.processComplete, file, full_path))
						self.futures.append(future);
					else:
						self.sig_msg.emit("Skipping "+file+ " - File is not an image")
						
			self.writeXmlFile()
			ttl_time = round(time.time() - start_time, 3)
			self.sig_done.emit(self.__id, self.images_with_aois)
			self.sig_msg.emit("Total Processing Time: "+str(ttl_time)+" seconds")
		except Exception as e:
			logging.exception(e)

	@staticmethod
	def processFile(instance, file, full_path, histogram_service, kmeans_service):
		img = cv2.imread(full_path)
		if histogram_service is not None:
			img = histogram_service.matchHistograms(img)
		if kmeans_service is not None:
			img = kmeans_service.generateClusters(img)
		try:
			return instance.processImage(img)
		except Exception as e:
			logging.exception(e)
	
	@pyqtSlot()			
	def processComplete(self, file, full_path, future):
		if future.done() and not future.cancelled() and not self.cancelled:
			exif_dict = piexif.load(full_path)
			exif_bytes = piexif.dump(exif_dict)
			try:
				results = future.result()
				result = results[0]
				areas_of_interest = results[1]
				if result is not None:
					output_file = self.output+"/"+file
					cv2.imwrite(output_file, result)
					self.addImageToXml(file,areas_of_interest)
					self.sig_msg.emit('Areas of interest identified in '+file)
					self.images_with_aois += 1
					piexif.insert(exif_bytes, output_file)
				else:
					self.sig_msg.emit('No areas of interested identified in '+file)
				if areas_of_interest is not None:
					if len(areas_of_interest) > self.maxAOIs and not self.maxAOIsLimitExceeded:
						self.sig_aois.emit()
						self.maxAOIsLimitExceeded = True
			except concurrent.futures.CancelledError:
				print('No result, task was cancelled')
	@pyqtSlot()			
	def processCancel(self):
		for future in self.futures:
			future.cancel()
		self.cancelled = True
		self.sig_msg.emit("--- Canceling Image Processing ---")	
			
	def setupOutputDir(self):
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
		image = ET.SubElement(self.images_xml, 'image')
		image.set('file_name',file)
		for area in areas_of_interest:
			area_xml = ET.SubElement(image, 'areas_of_interest')
			area_xml.set('center', str(area['center']))
			area_xml.set('radius', str(area['radius']))
			area_xml.set('area', str(area['area']))


	def writeXmlFile(self):
		mydata = ET.ElementTree(self.xml)
		file_path = os.path.join(self.output, "ADIAT_Data.xml")
		with open(file_path, "wb") as fh:
			mydata.write(fh)