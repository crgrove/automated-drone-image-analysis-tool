import numpy as np
import cv2

class AlgorithmService:
	"""Base class for algorithm services"""
	def __init__(self, name, identifier_color, min_area, aoi_radius, options):
		"""
		__init__ constructor
		
		:String name: the name of the algorithm to be used for analysis
		:Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
		:Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
		:Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
		:Dictionary options: additional algorithm-specific options
		"""
		self.name = name
		self.identifier_color = identifier_color
		self.min_area = min_area
		self.aoi_radius = aoi_radius
		self.options = options

	def processImage(self, image):
		"""
		processImage processes a single image file using the algorithm
		
		:numpy.ndarray image: the numpy.ndarray representation of an image
		"""
		raise NotImplementedError
	
	def circleAreasOfInterest(self, img, contours):
		"""
		circleAreasOfInterest augments the input image with circles around areas of interest
		:numpy.ndarray img: the numpy.ndarray representation of an image
		:numpy.ndarray contours: the numpy.ndarray representation of the areas of interest in the image
		:return numpy.ndarray, List, int: numpy.ndarray representing the output image, a list of areas of interest, and a count of the original areas of interest before they were combined to eliminate overlapping circles
		"""
		areas_of_interest = []
		image_copy = img.copy()
		temp_mask =  np.zeros(img.shape[:2],dtype=np.uint8)
		found = False
		base_contour_count = 0	
		# 3 step process.  Step 1, find all the areas >= the minimum size and mark them on a temporary mask.  Step 2, loop through combining any circles that overlap. Step 3, draw the final list of circles on a copy of the original image.

		if len(contours) > 0:
			for cnt in contours:
				area = cv2.contourArea(cnt)
				(x,y),radius = cv2.minEnclosingCircle(cnt)
				center = (int(x),int(y))
				radius = int(radius)+self.aoi_radius
				#if the area of the identified collection of pixels is >= the threshold we have set, go ahead and mark it.
				if area > self.min_area:
					found = True
					cv2.circle(temp_mask, center, radius,(255), -1)
					base_contour_count += 1
		if found:
			while True:
				new_contours, hierarchy = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
				for cnt in new_contours:
					area = cv2.contourArea(cnt)
					(x,y),radius = cv2.minEnclosingCircle(cnt)
					center = (int(x),int(y))
					radius = int(radius)
					cv2.circle(temp_mask, center, radius,(255), -1)
				if len(new_contours) == len(contours):
					contours = new_contours
					break
				contours = new_contours
			for cnt in contours:
				area = cv2.contourArea(cnt)
				(x,y),radius = cv2.minEnclosingCircle(cnt)
				center = (int(x),int(y))
				radius = int(radius)
				item = dict()
				item['center'] = center
				item['radius'] = radius
				item['area'] = area
				areas_of_interest.append(item)
				image_copy = cv2.circle(image_copy,center,radius,(self.identifier_color[2],self.identifier_color[1],self.identifier_color[0]),2)
			return image_copy, areas_of_interest, base_contour_count
		else :
			return None, None, None
	
class AlgorithmController:
	"""Base class for algorithm controllers"""
	def __init__(self, name, default_process_count):
		"""
		__init__ constructor
		
		:String name: the name of the algorithm to be used for analysis
		:Int default_process_count: the default number of processes to use for the algorithm
		"""
		self.name = name
		self.default_process_count = default_process_count
		
	def getOptions(self):
		"""
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
		raise NotImplementedError

	def validate(self):
		"""
		validate validates that the required values have been provided
		
		:return String: error message
		"""
		raise NotImplementedError

	def loadOptions(self, options):
		"""
		loadOptions sets UI elements based on options
		
		:Dictionary options: the options to use to set attributes
		"""
		raise NotImplementedError