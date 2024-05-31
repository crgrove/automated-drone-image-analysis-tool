import platform
import numpy as np
import cv2
import os
from pathlib import Path
from helpers.MetaDataHelper import MetaDataHelper

class AlgorithmService:
	"""Base class for algorithm services"""
	def __init__(self, name, identifier_color, min_area, aoi_radius, combine_aois, options, is_thermal = False):
		"""
		__init__ constructor
		
		:String name: the name of the algorithm to be used for analysis
		:Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:Boolean combine_aois: If true overlapping aois will be combined.
		:Dictionary options: additional algorithm-specific options
		:Boolean thermal: is this a thermal image algorithm
		"""
		self.name = name
		self.identifier_color = identifier_color
		self.min_area = min_area
		self.aoi_radius = aoi_radius
		self.combine_aois = combine_aois
		self.options = options
		self.is_thermal = is_thermal

	def processImage(self, img, full_path, input_dir, output_dir):
		"""
		processImage processes a single image file using the algorithm
		
		:numpy.ndarray img: numpy.ndarray representing the subject image
		:String full_path: the path to the image being analyzed
		:String input_dir: the base input folder
		:String output_dir: the base output folder
		:return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
		raise NotImplementedError
	
	def circleAreasOfInterest(self, img, contours):
		"""
		circleAreasOfInterest augments the input image with circles around areas of interest
		:numpy.ndarray img: the numpy.ndarray representation of an image
		:numpy.ndarray contours: the numpy.ndarray representation of the areas of interest in the image
		:return numpy.ndarray, List, int: numpy.ndarray representing the output image, a list of areas of interest, and a count of the original areas of interest before they were combined to eliminate overlapping circles
		"""
		
		found = False
		# 3 step process.  Step 1, find all the areas >= the minimum size and mark them on a temporary mask.  Step 2, loop through combining any circles that overlap. Step 3, draw the final list of circles on a copy of the original image.

		if len(contours) > 0:
			areas_of_interest = []
			temp_mask =  np.zeros(img.shape[:2],dtype=np.uint8)
			base_contour_count = 0	
			for cnt in contours:
				area = cv2.contourArea(cnt)
				(x,y),radius = cv2.minEnclosingCircle(cnt)
				center = (int(x),int(y))
				radius = int(radius)+self.aoi_radius
				#if the area of the identified collection of pixels is >= the threshold we have set, go ahead and mark it.
				if area >= self.min_area:
					found = True
					cv2.circle(temp_mask, center, radius,(255), -1)
					base_contour_count += 1
					#if not combining overlapping aois, add the circles to the image copy.
					if not self.combine_aois:
						item = dict()
						item['center'] = center
						item['radius'] = radius
						item['area'] = area
						areas_of_interest.append(item)
						image_copy = cv2.circle(img,center,radius,(self.identifier_color[2],self.identifier_color[1],self.identifier_color[0]),2)
		
		if found:
			#if combining overlapping aois, go through that process now.
			if self.combine_aois:
				while True:
					new_contours, hierarchy = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
					for cnt in new_contours:
						area = cv2.contourArea(cnt)
						(x,y),radius = cv2.minEnclosingCircle(cnt)
						center = (int(x),int(y))
						radius = int(radius)
						cv2.circle(temp_mask, center, radius,(255), -1)
					if len(new_contours) == len(contours):
						contours = new_contours
						break
					contours = new_contours
				for cnt in contours:
					area = cv2.contourArea(cnt)
					(x,y),radius = cv2.minEnclosingCircle(cnt)
					center = (int(x),int(y))
					radius = int(radius)
					item = dict()
					item['center'] = center
					item['radius'] = radius
					item['area'] = area
					areas_of_interest.append(item)
					image_copy = cv2.circle(img,center,radius,(self.identifier_color[2],self.identifier_color[1],self.identifier_color[0]),2)
			#if any results >= the min area are found, go ahead an return them 
			return image_copy, areas_of_interest, base_contour_count
		else :
			return None, None, None
		
	def storeImage (self, input_file, output_file, augmented_image, temperature_data = None):
		path = Path(output_file)
		if not os.path.exists(path.parents[0]):
			os.makedirs(path.parents[0])
		cv2.imwrite(output_file, augmented_image)
		if platform.system() == "Darwin":
			MetaDataHelper.transferExifPiexif(input_file, output_file)
		else:
			if temperature_data is not None:
				MetaDataHelper.transferAll(input_file, output_file)
				MetaDataHelper.transferTemperatureData(temperature_data, output_file)
			else:
				MetaDataHelper.transferExifPiexif(input_file, output_file)
		
class AlgorithmController:
	"""Base class for algorithm controllers"""
	def __init__(self, name, default_process_count, thermal = False):
		"""
		__init__ constructor
		
		:String name: the name of the algorithm to be used for analysis
		:Int default_process_count: the default number of processes to use for the algorithm
		:Bool thermal: is this algorithm for thermal images
		"""
		self.name = name
		self.default_process_count = default_process_count
		self.is_thermal = thermal
		
	def getOptions(self):
		"""
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
		raise NotImplementedError

	def validate(self):
		"""
		validate validates that the required values have been provided
		
		:return String: error message
		"""
		raise NotImplementedError

	def loadOptions(self, options):
		"""
		loadOptions sets UI elements based on options
		
		:Dictionary options: the options to use to set attributes
		"""
		raise NotImplementedError
	
class AnalysisResult:
	"""Class for the object that will be returned by the processImage method """
	input_path = None #type = string 
	output_path = None #type = string 
	areas_of_interest = None  #type = List
	base_contour_count = None  # type = int
	error_message = None  # type = str
	
	def __init__(self, input_path=None, output_path=None, areas_of_interest=None, base_contour_count=None, error_message = None):
		self.input_path=input_path
		self.output_path=output_path
		self.areas_of_interest = areas_of_interest
		self.base_contour_count = base_contour_count
		self.error_message = error_message