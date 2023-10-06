import cv2
import imghdr
import logging
from skimage import exposure

class HistogramNormalizationService:
	"""Service to adjust the histagram of a source image to match that of a reference image"""
	def __init__(self, hist_ref_path):
		"""
		__init__ constructor for the service
		
		:String hist_ref_path: the path to the reference image
		"""
		if imghdr.what(hist_ref_path) is not None:
			self.hist_ref_img = cv2.imread(hist_ref_path)
		
	def matchHistograms(self,src):
		"""
		matchHistograms runs skimage.exposure to match the histagram of a subjec image to a reference image
		
		:numpy.ndarray src: the numpy.ndarray representation of the subject image
		:return numpy.ndarray: the modified subject image
		"""
		try:
			return exposure.match_histograms(src, self.hist_ref_img , channel_axis= -1)				
					
		except Exception as e:
			logging.exception(e)