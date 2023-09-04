import numpy as np
import cv2
import os
import imghdr
import logging
from skimage import exposure

class HistagramNormalizationService:

	def __init__(self, hist_ref_path):
		if imghdr.what(hist_ref_path) is not None:
			self.hist_ref_img = cv2.imread(hist_ref_path)
		
	def matchHistagrams(self,src):
		try:
			multi = True if src.shape[-1] > 1 else False
			return exposure.match_histograms(src, self.hist_ref_img , multichannel=multi)				
					
		except Exception as e:
			logging.exception(e)
	
	def setRefernceImage(self, hist_ref_path):
		if imghdr.what(hist_ref_path) is not None:
			self.hist_ref_img = cv2.imread(hist_ref_path)