class Algorithm:

	def __init__(self, name, identifier_color, options):
		self.name = name
		self.identifier_color = identifier_color
		self.options = options

	def processImage(self, image):
	 	raise NotImplementedError