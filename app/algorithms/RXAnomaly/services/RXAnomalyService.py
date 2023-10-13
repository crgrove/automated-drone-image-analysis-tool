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
    def __init__(self, identifier, min_area, options):
        """
		__init__ constructor for the algorithm
		
		:Tuple(int,int,int) identifier: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Dictionary options: additional algorithm-specific options
		"""
        super().__init__('RXAnomaly', identifier, options)
        #self.chi_threshold = options['threshold']
        self.chi_threshold = self.getThreshold(options['sensitivity'])
        self.min_area = min_area

    def processImage(self, img):
        """
		processImage processes a single image using the Color Match algorithm
		
		:numpy.ndarray img: numpy.ndarray representing the subject image
        :return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
        try:
            #copy the image so we can compare back to the orginal
            image_copy = img.copy()
            areas_of_interest = []
            
            rx_values = spectral.rx(image_copy)
            chi_values = chi2.ppf(self.chi_threshold, image_copy.shape[-1])
            
            mask =  np.uint8((1 * (rx_values > chi_values)))
            
            #make a list of the identified areas.
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            temp_mask =  np.zeros(img.shape[:2],dtype=np.uint8)
            found = False
            
            #2 step process.  Step 1, find all the areas >= the minimum size and mark them on a temporary mask.  Step 2, run it through again to get the "distinct" contours so that we don't have overlapping circles.
            if len(contours) > 0:
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    (x,y),radius = cv2.minEnclosingCircle(cnt)
                    center = (int(x),int(y))
                    radius = int(radius)+8
                    #if the area of the identified collection of pixels is >= the threshold we have set, go ahead and mark it.
                    if area > self.min_area:
                        found = True
                        cv2.circle(temp_mask, center, radius,(255), -1)
                        
            if found:
                contours, hierarchy = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    (x,y),radius = cv2.minEnclosingCircle(cnt)
                    center = (int(x),int(y))
                    radius = int(radius)+8
                    item = dict()
                    item['center'] = center
                    item['radius'] = radius
                    item['area'] = area
                    areas_of_interest.append(item)
                    image_copy = cv2.circle(image_copy,center,radius,(self.identifier_color[2],self.identifier_color[1],self.identifier_color[0]),2)
                return image_copy, areas_of_interest
            else :
                return None, None
        except Exception as e:
            logging.exception(e)
            
    def getThreshold(self, sensitivity):
        """
		getThreshold get the chi2 threshold based on a sensitivity value
		
		:int sensitivity: sensitivity value to convert to chi2 threshold
        :return float
		"""
        return 1 - float("."+("1".zfill(sensitivity+5)))
        
        