import logging
import numpy as np
import math
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
        self.segments = options['segments']

    def processImage(self, img):
        """
		processImage processes a single image using the Color Match algorithm
		
		:numpy.ndarray img: numpy.ndarray representing the subject image
        :return numpy.ndarray, List: numpy.ndarray representing the output image and a list of areas of interest
		"""
        try:
            masks = pieces = self.splitImage(img, self.segments);
            for x in range(0, len(pieces)):
                for y in range(0, len(pieces[x])):
                    rx_values = spectral.rx(pieces[x][y])
                    chi_values = chi2.ppf(self.chi_threshold, pieces[x][y].shape[-1])    
                    masks[x][y] =  np.uint8((1 * (rx_values > chi_values)))
            combined_mask = self.glueImage(masks)
            """
            if self.segments > 1:
                rx_values = spectral.rx(img)
                chi_values = chi2.ppf(self.chi_threshold, img.shape[-1])    
                img_mask =  np.uint8((1 * (rx_values > chi_values)))
                merge = 255*(combined_mask + img_mask)
                full_mask = merge.clip(0, 255).astype("uint8")
            else:
                full_mask = combined_mask    
            """
            #make a list of the identified areas.
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
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
    
    def splitImage(self, img, segments):
        """
        splitImage divides a single image into mupliple segments.
        
        :numpy.ndarray img: numpy.ndarray representing the subject image
        :int segments: the number of image segments we want to split the image into
        :return List: List lists of numpy.ndarrays representing the segments of the original image.
        """
        h, w, channels = img.shape
        pieces = []
        if(segments == 2):    
            w_size = math.ceil(w/2)
            pieces.append([])
            pieces [0].append(img[:, :w_size])
            pieces [0].append(img[:, w-w_size:])
        elif(segments == 4):
            w_size = math.ceil(w/2)
            h_size = math.ceil(h/2)
            pieces.append([])
            pieces.append([])
            pieces [0].append(img[:h_size, :w_size])
            pieces [0].append(img[:h_size, w-w_size:])
            pieces [1].append(img[h_size:, :w_size])
            pieces [1].append(img[h_size:, w-w_size:])
        elif(segments == 6):
            w_size = math.ceil(w/3)
            h_size = math.ceil(h/2)
            pieces.append([])
            pieces.append([])
            pieces [0].append(img[:h_size, :w_size])
            pieces [0].append(img[:h_size, w_size:w_size*2])
            pieces [0].append(img[:h_size, w_size*2:])
            pieces [1].append(img[h_size:, :w_size])
            pieces [1].append(img[h_size:, w_size:w_size*2])
            pieces [1].append(img[h_size:, w_size*2:])
        elif(segments == 9):
            w_size = math.ceil(w/3)
            h_size = math.ceil(h/3)
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces [0].append(img[:h_size, :w_size])
            pieces [0].append(img[:h_size, w_size:w_size*2])
            pieces [0].append(img[:h_size, w_size*2:])
            pieces [1].append(img[h_size:h_size*2, :w_size])
            pieces [1].append(img[h_size:h_size*2, w_size:w_size*2])
            pieces [1].append(img[h_size:h_size*2, w_size*2:])
            pieces [2].append(img[h_size*2:, :w_size])
            pieces [2].append(img[h_size*2:, w_size:w_size*2])
            pieces [2].append(img[h_size*2:, w_size*2:])
        elif(segments == 16):
            w_size = math.ceil(w/4)
            h_size = math.ceil(h/4)
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces [0].append(img[:h_size, :w_size])
            pieces [0].append(img[:h_size, w_size:w_size*2])
            pieces [0].append(img[:h_size, w_size*2:w_size*3])
            pieces [0].append(img[:h_size, w_size*3:])
            pieces [1].append(img[h_size:h_size*2, :w_size])
            pieces [1].append(img[h_size:h_size*2, w_size:w_size*2])
            pieces [1].append(img[h_size:h_size*2, w_size*2:w_size*3])
            pieces [1].append(img[h_size:h_size*2, w_size*3:])   
            pieces [2].append(img[h_size*2:h_size*3, :w_size])
            pieces [2].append(img[h_size*2:h_size*3, w_size:w_size*2])
            pieces [2].append(img[h_size*2:h_size*3, w_size*2:w_size*3])
            pieces [2].append(img[h_size*2:h_size*3, w_size*3:])
            pieces [3].append(img[h_size*3:, :w_size])
            pieces [3].append(img[h_size*3:, w_size:w_size*2])
            pieces [3].append(img[h_size*3:, w_size*2:w_size*3])
            pieces [3].append(img[h_size*3:, w_size*3:])
        elif(segments == 25):
            w_size = math.ceil(w/5)
            h_size = math.ceil(h/5)
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces [0].append(img[:h_size, :w_size])
            pieces [0].append(img[:h_size, w_size:w_size*2])
            pieces [0].append(img[:h_size, w_size*2:w_size*3])
            pieces [0].append(img[:h_size, w_size*3:w_size*4])
            pieces [0].append(img[:h_size, w_size*4:])
            pieces [1].append(img[h_size:h_size*2, :w_size])
            pieces [1].append(img[h_size:h_size*2, w_size:w_size*2])
            pieces [1].append(img[h_size:h_size*2, w_size*2:w_size*3])
            pieces [1].append(img[h_size:h_size*2, w_size*3:w_size*4])
            pieces [1].append(img[h_size:h_size*2, w_size*4:])
            pieces [2].append(img[h_size*2:h_size*3, :w_size])
            pieces [2].append(img[h_size*2:h_size*3, w_size:w_size*2])
            pieces [2].append(img[h_size*2:h_size*3, w_size*2:w_size*3])
            pieces [2].append(img[h_size*2:h_size*3, w_size*3:w_size*4])
            pieces [2].append(img[h_size*2:h_size*3, w_size*4:])
            pieces [3].append(img[h_size*3:h_size*4, :w_size])
            pieces [3].append(img[h_size*3:h_size*4, w_size:w_size*2])
            pieces [3].append(img[h_size*3:h_size*4, w_size*2:w_size*3])
            pieces [3].append(img[h_size*3:h_size*4, w_size*3:w_size*4])
            pieces [3].append(img[h_size*3:h_size*4, w_size*4:])
            pieces [4].append(img[h_size*4:, :w_size])
            pieces [4].append(img[h_size*4:, w_size:w_size*2])
            pieces [4].append(img[h_size*4:, w_size*2:w_size*3])
            pieces [4].append(img[h_size*4:, w_size*3:w_size*4])
            pieces [4].append(img[h_size*4:, w_size*4:])
        elif(segments == 36):
            w_size = math.ceil(w/6)
            h_size = math.ceil(h/6)
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces.append([])
            pieces [0].append(img[:h_size, :w_size])
            pieces [0].append(img[:h_size, w_size:w_size*2])
            pieces [0].append(img[:h_size, w_size*2:w_size*3])
            pieces [0].append(img[:h_size, w_size*3:w_size*4])
            pieces [0].append(img[:h_size, w_size*4:w_size*5])
            pieces [0].append(img[:h_size, w_size*5:])
            pieces [1].append(img[h_size:h_size*2, :w_size])
            pieces [1].append(img[h_size:h_size*2, w_size:w_size*2])
            pieces [1].append(img[h_size:h_size*2, w_size*2:w_size*3])
            pieces [1].append(img[h_size:h_size*2, w_size*3:w_size*4])
            pieces [1].append(img[h_size:h_size*2, w_size*4:w_size*5])
            pieces [1].append(img[h_size:h_size*2, w_size*5:])
            pieces [2].append(img[h_size*2:h_size*3, :w_size])
            pieces [2].append(img[h_size*2:h_size*3, w_size:w_size*2])
            pieces [2].append(img[h_size*2:h_size*3, w_size*2:w_size*3])
            pieces [2].append(img[h_size*2:h_size*3, w_size*3:w_size*4])
            pieces [2].append(img[h_size*2:h_size*3, w_size*4:w_size*5])
            pieces [2].append(img[h_size*2:h_size*3, w_size*5:])
            pieces [3].append(img[h_size*3:h_size*4, :w_size])
            pieces [3].append(img[h_size*3:h_size*4, w_size:w_size*2])
            pieces [3].append(img[h_size*3:h_size*4, w_size*2:w_size*3])
            pieces [3].append(img[h_size*3:h_size*4, w_size*3:w_size*4])
            pieces [3].append(img[h_size*3:h_size*4, w_size*4:w_size*5])
            pieces [3].append(img[h_size*3:h_size*4, w_size*5:])
            pieces [4].append(img[h_size*4:h_size*5, :w_size])
            pieces [4].append(img[h_size*4:h_size*5, w_size:w_size*2])
            pieces [4].append(img[h_size*4:h_size*5, w_size*2:w_size*3])
            pieces [4].append(img[h_size*4:h_size*5, w_size*3:w_size*4])
            pieces [4].append(img[h_size*4:h_size*5, w_size*4:w_size*5])
            pieces [4].append(img[h_size*4:h_size*5, w_size*5:])
            pieces [5].append(img[h_size*5:, :w_size])
            pieces [5].append(img[h_size*5:, w_size:w_size*2])
            pieces [5].append(img[h_size*5:, w_size*2:w_size*3])
            pieces [5].append(img[h_size*5:, w_size*3:w_size*4])
            pieces [5].append(img[h_size*5:, w_size*4:w_size*5])
            pieces [5].append(img[h_size*5:, w_size*5:])
        else:
            pieces.append([])
            pieces[0].append(img)
        return pieces        

    def glueImage(self, pieces):
        """
        glueImage combines the pieces of an image into a single image..
        
        :List pieces: a list of lists containing numpy.ndarrays representing the pieces of the image.
        :return numpy.ndarray: representing the combined image.
        """
        rows = []
        for x in range(0, len(pieces)):
            rows.append(cv2.hconcat(pieces[x]))
        return cv2.vconcat(rows); 
        
        