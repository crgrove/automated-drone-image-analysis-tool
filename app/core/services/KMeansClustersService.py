import numpy as np
import cv2
import os
import imghdr
import logging

class KMeansClustersService:

	def __init__(self, clusters):
		self.num_clusters = clusters
		
	def generateClusters(self,src):
		try:
			Z = src.reshape((-1,3))

			# convert to np.float32
			Z = np.float32(Z)

			# define criteria, number of clusters(K) and apply kmeans()
			criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 5, .75)
			ret,label,center=cv2.kmeans(Z,self.num_clusters,None,criteria,5,cv2.KMEANS_RANDOM_CENTERS)

			# Now convert back into uint8, and make original image
			center = np.uint8(center)
			res = center[label.flatten()]
			res2 = res.reshape((src.shape))
			return res2
		except Exception as e:
			logging.exception(e)