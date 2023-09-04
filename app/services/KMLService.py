import os
import simplekml

class KMLService:

	def __init__(self):
		self.kml = simplekml.Kml()
		
	def addPoints(self, points):
		for point in points:
			self.kml.newpoint(name=point["name"], coords = [(point["long"],point["lat"])])
			
	def saveKml(self, path):
		self.kml.save(path)