import numpy as np
import cv2
import imghdr
import logging

class KMeansClustersService:
	"""Service to generate an image with a limited number of colors"""
	def __init__(self, clusters):
		"""
		__init__ constructor for the service
		
		:Int clusters: the number of clusters(colors) for the K-Means Clusters algorithm to return
		"""
		self.num_clusters = clusters
		
	def generateClusters(self,src):
		"""
		generateClusters processes an image and returns one with the defined number of clusters(colors)
		
		:numpy.ndarray src: the numpy.ndarray representation of an image
		:return numpy.ndarray: the modified image with the specified number of images
		"""
		try:
			Z = src.reshape((-1,3))

			#convert to np.float32
			Z = np.float32(Z)

			#define criteria, number of clusters(K) and apply kmeans()
			criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 5, .75)
			ret,label,center=cv2.kmeans(Z,self.num_clusters,None,criteria,5,cv2.KMEANS_RANDOM_CENTERS)

			#convert back into uint8
			center = np.uint8(center)
			res = center[label.flatten()]
			res2 = res.reshape((src.shape))
			return res2
		except Exception as e:
			logging.exception(e)