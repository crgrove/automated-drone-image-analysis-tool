class AlgorithmService:
	"""Base class for algorithm services"""
	def __init__(self, name, identifier_color, options):
		"""
		__init__ constructor
		
		:String name: the name of the algorithm to be used for analysis
		:Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
		:Dictionary options: additional algorithm-specific options
		"""
		self.name = name
		self.identifier_color = identifier_color
		self.options = options

	def processImage(self, image):
		"""
		processImage processes a single image file using the algorithm
		
		:numpy.ndarray image: the numpy.ndarray representation of an image
		"""
		raise NotImplementedError
	
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