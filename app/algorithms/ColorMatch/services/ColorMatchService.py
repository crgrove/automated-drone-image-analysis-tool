import logging
import numpy as np
import cv2

from algorithms.Algorithm import AlgorithmService

class ColorMatchService(AlgorithmService):
    """Service that executes the Color Match algorithm"""
    def __init__(self, identifier, min_area, options):
        """
		__init__ constructor for the algorithm
		
		:Tuple(int,int,int) identifier: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Dictionary options: additional algorithm-specific options
		"""
        super().__init__('ColorMatch', identifier, options)
        self.min_rgb = options['color_range'][0]
        self.max_rgb = options['color_range'][1]
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
            #get the color range boundries
            cv_lower_limit = np.array([self.min_rgb[2], self.min_rgb[1], self.min_rgb[0]], dtype=np.uint8)
            cv_upper_limit = np.array([self.max_rgb[2], self.max_rgb[1], self.max_rgb[0]], dtype=np.uint8)
            
            #find the pixels that are in our color range (https://docs.opencv.org/3.4.3/da/d97/tutorial_threshold_inRange.html)
            mask = cv2.inRange(img, cv_lower_limit, cv_upper_limit)

            #keep the pixels we just identified
            #res = cv2.bitwise_and(img,img, mask= mask)
            
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