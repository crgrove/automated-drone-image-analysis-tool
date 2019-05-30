import logging
import numpy as np
import cv2
import spectral
import scipy
from scipy.stats import chi2

from .Algorithm import Algorithm
from ...helpers.ColorUtils import ColorUtils

#Based on TX Spectrail Detection Algorithm seen here: http://cver.hrail.crasar.org/algorithm/
class ColorAnomaly(Algorithm):

    def __init__(self, identifier, min_area, options):
        super().__init__('ColorAnomaly', identifier, options)
        self.chi_threshold = options['threshold']
        self.min_area = min_area

    def processImage(self, img):
        #copy the image so we can compare back to the orginal
        try:
            image_copy = img.copy()
            areas_of_interest = []
            
            rx_values = spectral.rx(image_copy)
            chi_values = chi2.ppf(self.chi_threshold, image_copy.shape[-1])
            
            mask =  np.uint8((1 * (rx_values > chi_values)))
            
            #make a list of the identified areas.
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            
            found = False

            if len(contours) > 0:
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    (x,y),radius = cv2.minEnclosingCircle(cnt)
                    center = (int(x),int(y))
                    radius = int(radius)+8
                    #if the area of the identified collection of pixels is >= the threshold we have set, go ahead and mark it.
                    if area > self.min_area:
                        image_copy = cv2.circle(image_copy,center,radius,(self.identifier_color[2],self.identifier_color[1],self.identifier_color[0]),2)
                        found = True
                        item = dict()
                        item['center'] = center
                        item['radius'] = radius
                        item['area'] = area
                        areas_of_interest.append(item)
            if found:
                return image_copy, areas_of_interest
            else :
                return None, None
        except Exception as e:
            logging.exception(e)
