import logging
import numpy as np
import cv2
import spectral

from algorithms.Algorithm import AlgorithmService
from helpers.ColorUtils import ColorUtils

class MatchedFilterService(AlgorithmService):

    def __init__(self, identifier, min_area, options):
        super().__init__('MatchedFilter', identifier, options)
        self.match_color = options['selected_color']
        self.threshold = options['match_filter_threshold']
        self.min_area = min_area
        print (self.match_color)

    def processImage(self, img):
        #copy the image so we can compare back to the orginal
        try:
            image_copy = img.copy()
            areas_of_interest = []
            #calculate the match filter scores 
            scores = spectral.matched_filter(image_copy,  np.array([self.match_color[2], self.match_color[1], self.match_color[0]], dtype=np.uint8))
            mask =  np.uint8((1 * (scores > self.threshold)))

            #make a list of the identified areas.
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
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
            return None, None