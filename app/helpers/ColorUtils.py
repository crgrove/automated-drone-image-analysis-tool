import numpy as np
import cv2

class ColorUtils:
    """Provides functions to aid in the manipulation of colors"""
    @staticmethod
    def getColorRange(rgb, r_range, g_range, b_range):
        """
		getColorRange takes a base color and then returns a min and max based on ranges provided for the red, green, and blue color channels
        
        :Tuple(int,int,int): the rgb values representing the base color
        :Int r_range: the range for the red channel
        :Int g_range: the range for the green channel
        :Int b_range: the range fot the blue channel
        return: Tuple(int,int,int), Tuple(int,int,int): the rgb values representing the min and max colors for the given range
		"""
        upper_r = rgb[0]+r_range
        upper_g = rgb[1]+g_range
        upper_b = rgb[2]+b_range

        if upper_r > 255:
            upper_r = 255
        if upper_g > 255:
            upper_g = 255
        if upper_b > 255:
            upper_b = 255

        lower_r = rgb[0]-r_range
        lower_g = rgb[1]-g_range
        lower_b = rgb[2]-b_range
        if lower_r < 0:
            lower_r = 0
        if lower_g < 0:
            lower_g = 0
        if lower_b < 0:
            lower_b = 0 
        return  (lower_r,lower_g,lower_b), (upper_r,upper_g,upper_b)