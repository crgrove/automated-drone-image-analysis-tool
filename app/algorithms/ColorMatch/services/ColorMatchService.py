import logging
import numpy as np
import cv2

from algorithms.Algorithm import AlgorithmService

class ColorMatchService(AlgorithmService):
    """Service that executes the Color Match algorithm"""
    def __init__(self, identifier, min_area, aoi_radius, options):
        """
		__init__ constructor for the algorithm
		
		:Tuple(int,int,int) identifier: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:Dictionary options: additional algorithm-specific options
		"""
        super().__init__('ColorMatch', identifier, min_area, aoi_radius, options)
        self.min_rgb = options['color_range'][0]
        self.max_rgb = options['color_range'][1]

    def processImage(self, img):
        """
		processImage processes a single image using the Color Match algorithm
		
		:numpy.ndarray img: numpy.ndarray representing the subject image
        :return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
        try:
            #get the color range boundries
            cv_lower_limit = np.array([self.min_rgb[2], self.min_rgb[1], self.min_rgb[0]], dtype=np.uint8)
            cv_upper_limit = np.array([self.max_rgb[2], self.max_rgb[1], self.max_rgb[0]], dtype=np.uint8)
            
            #find the pixels that are in our color range (https://docs.opencv.org/3.4.3/da/d97/tutorial_threshold_inRange.html)
            mask = cv2.inRange(img, cv_lower_limit, cv_upper_limit)

            #keep the pixels we just identified
            #res = cv2.bitwise_and(img,img, mask= mask)
            
            #make a list of the identified areas.
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            return self.circleAreasOfInterest(img, contours)
        
        except Exception as e:
            logging.exception(e)
            return None, None