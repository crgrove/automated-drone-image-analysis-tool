class AlgorithmService:

	def __init__(self, name, identifier_color, options):
		self.name = name
		self.identifier_color = identifier_color
		self.options = options

	def processImage(self, image):
	 	raise NotImplementedError
	
class AlgorithmController:

	def __init__(self, name, default_process_count):
		self.name = name
		self.default_process_count = default_process_count