import logging
import numpy as np
import cv2
import spectral
import scipy
from scipy.stats import chi2

from algorithms.Algorithm import AlgorithmService
from helpers.ColorUtils import ColorUtils

#Based on TX Spectrail Detection Algorithm seen here: http://cver.hrail.crasar.org/algorithm/
class RXAnomalyService(AlgorithmService):
    """Service that executes the RX Anomaly algorithm"""
    def __init__(self, identifier, min_area, aoi_radius, options):
        """
		__init__ constructor for the algorithm
		
		:Tuple(int,int,int) identifier: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:Dictionary options: additional algorithm-specific options
		"""
        super().__init__('RXAnomaly', identifier, min_area, aoi_radius, options)
        #self.chi_threshold = options['threshold']
        self.chi_threshold = self.getThreshold(options['sensitivity'])

    def processImage(self, img):
        """
		processImage processes a single image using the Color Match algorithm
		
		:numpy.ndarray img: numpy.ndarray representing the subject image
        :return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
        try:
            rx_values = spectral.rx(img)
            chi_values = chi2.ppf(self.chi_threshold, img.shape[-1])
            
            mask =  np.uint8((1 * (rx_values > chi_values)))
            
            #make a list of the identified areas.
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            return self.circleAreasOfInterest(img, contours)
        except Exception as e:
            logging.exception(e)
            
    def getThreshold(self, sensitivity):
        """
		getThreshold get the chi2 threshold based on a sensitivity value
		
		:int sensitivity: sensitivity value to convert to chi2 threshold
        :return float
		"""
        return 1 - float("."+("1".zfill(sensitivity+5)))
        
        