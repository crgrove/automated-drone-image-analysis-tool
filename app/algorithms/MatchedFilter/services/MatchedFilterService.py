import logging
import numpy as np
import cv2
import spectral

from algorithms.Algorithm import AlgorithmService

class MatchedFilterService(AlgorithmService):
	"""Service that executes the Matched Filter algorithm"""
	def __init__(self, identifier, min_area, aoi_radius, options):
		"""
		__init__ constructor for the algorithm
		
		:Tuple(int,int,int) identifier: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:Dictionary options: additional algorithm-specific options
		"""
		super().__init__('MatchedFilter', identifier, min_area, aoi_radius, options)
		self.match_color = options['selected_color']
		self.threshold = options['match_filter_threshold']

	def processImage(self, img):
		"""
		processImage processes a single image using the Color Match algorithm
		
		:numpy.ndarray img: numpy.ndarray representing the subject image
		:return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
		try:
			#copy the image so we can compare back to the orginal
			#calculate the match filter scores 
			scores = spectral.matched_filter(img, np.array([self.match_color[2], self.match_color[1], self.match_color[0]], dtype=np.uint8))
			mask =  np.uint8((1 * (scores > self.threshold)))

			#make a list of the identified areas.
			contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
			return self.circleAreasOfInterest(img, contours)
		except Exception as e:
			logging.exception(e)
			return None, None