import logging
import numpy as np
import cv2

from .Algorithm import Algorithm
from ...helpers.ColorUtils import ColorUtils

class ColorMatch(Algorithm):

    def __init__(self, identifier, min_area, options):
        super().__init__('ColorMatch', identifier, options)
        self.min_rgb = options['color_range'][0]
        self.max_rgb = options['color_range'][1]
        self.min_area = min_area

    def processImage(self, img):
        #copy the image so we can compare back to the orginal
        try:
            image_copy = img.copy()
            areas_of_interest = []
            #get the color range boundries
            cv_lower_limit = np.array([self.min_rgb[2], self.min_rgb[1], self.min_rgb[0]], dtype=np.uint8)
            cv_upper_limit = np.array([self.max_rgb[2], self.max_rgb[1], self.max_rgb[0]], dtype=np.uint8)
            
            #find the pixels that are in our color range (https://docs.opencv.org/3.4.3/da/d97/tutorial_threshold_inRange.html)
            mask = cv2.inRange(img, cv_lower_limit, cv_upper_limit)

            #keep the pixels we just identified
            #res = cv2.bitwise_and(img,img, mask= mask)
            
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
            return None, None