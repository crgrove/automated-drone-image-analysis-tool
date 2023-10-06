import simplekml

class KMLService:
	"""Service to generate a KML file with points representing the loacation at which  images containing areas of interest were taken"""
	def __init__(self):
		"""
		__init__ constructor for the service
		"""
		self.kml = simplekml.Kml()
		
	def addPoints(self, points):
		"""
		addPoints adds a list of points to the KML document
		
		:List(Dictionary) points: the points to be added to the KML document
		"""
		for point in points:
			self.kml.newpoint(name=point["name"], coords = [(point["long"],point["lat"])])
			
	def saveKml(self, path):
		"""
		saveKml saves the KML file
		
		:String path: the location where the KML document will be stored
		"""
		self.kml.save(path)