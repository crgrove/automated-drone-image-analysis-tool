import numpy as np
import cv2

class ColorUtils:
    @staticmethod
    def getColorRange(rgb, r_range, g_range, b_range):

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
    
    @staticmethod
    def convertRgbToHsv(rgb):
        color = np.uint8([[[rgb[0], rgb[1], rgb[2]]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
        return [hsv_color[0][0][0], hsv_color[0][0][1], hsv_color[0][0][2]]