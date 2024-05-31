import numpy as np
import cv2

from algorithms.Algorithm import AlgorithmService, AnalysisResult

from core.services.LoggerService import LoggerService

from helpers.ColorUtils import ColorUtils
from helpers.thermalParser import Thermal
from helpers.MetaDataHelper import MetaDataHelper
from core.services.ThermalParserService import ThermalParserService

class ThermalRangeService(AlgorithmService):
	"""Service that executes the Thermal Range algorithm"""
	def __init__(self, identifier, min_area, aoi_radius, combine_aois, options):
		"""
		__init__ constructor for the algorithm
		
		:Tuple(int,int,int) identifier: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:Boolean combine_aois: If true overlapping aois will be combined.
		:Dictionary options: additional algorithm-specific options
		"""
		self.logger = LoggerService()
		super().__init__('MatchedFilter', identifier, min_area, aoi_radius, combine_aois, options, True)
		self.min_temp = options['minTemp']
		self.max_temp = options['maxTemp']
		self.color_map = options['colorMap']

	def processImage(self, img, full_path, input_dir, output_dir):
		"""
		processImage processes a single image using the Thermal Range algorithm
		
		:numpy.ndarray img: numpy.ndarray representing the subject image
		:String full_path: the path to the image being analyzed
		:String input_dir: the base input folder
		:String output_dir: the base output folder
		:return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
		try:
			#copy the image so we can compare back to the orginal
			#calculate the match filter scores 
			#thermal = Thermal(dtype=np.float32)
			#temperature_c, thermal_img = thermal.parse(full_path, self.color_map )
			thermal = ThermalParserService(dtype=np.float32)
			temperature_c, thermal_img = thermal.parseFile(full_path, self.color_map )
			mask =  np.uint8(1 * ((temperature_c > self.min_temp ) & (temperature_c < self.max_temp)))
			#make a list of the identified areas.
			contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)	
			augmented_image, areas_of_interest, base_contour_count =  self.circleAreasOfInterest(thermal_img, contours)
			output_path= full_path.replace(input_dir, output_dir)
			if augmented_image is not None:
				self.storeImage(full_path, output_path, augmented_image, temperature_c)   
			return AnalysisResult(full_path, output_path, areas_of_interest, base_contour_count)
		except Exception as e:
			return AnalysisResult(full_path, error_message = str(e))