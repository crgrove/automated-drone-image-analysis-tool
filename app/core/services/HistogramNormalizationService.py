import cv2
import numpy as np
import imghdr
from skimage import exposure
from core.services.LoggerService import LoggerService

class HistogramNormalizationService:
	"""Service to adjust the histagram of a source image to match that of a reference image"""
	def __init__(self, hist_ref_path):
		"""
		__init__ constructor for the service
		
		:String hist_ref_path: the path to the reference image
		"""
		self.logger = LoggerService()
		if imghdr.what(hist_ref_path) is not None:
			
			self.hist_ref_img = cv2.imdecode(np.fromfile(hist_ref_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
		
	def matchHistograms(self,src):
		"""
		matchHistograms runs skimage.exposure to match the histagram of a subjec image to a reference image
		
		:numpy.ndarray src: the numpy.ndarray representation of the subject image
		:return numpy.ndarray: the modified subject image
		"""
		try:
			return exposure.match_histograms(src, self.hist_ref_img , channel_axis= -1)				
					
		except Exception as e:
			self.logger.error(e)