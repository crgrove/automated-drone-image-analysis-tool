import os
import shutil
from pathlib import Path
import re
import cv2
import math
from datetime import datetime, timedelta

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from core.services.LoggerService import LoggerService
from helpers.MetaDataHelper import MetaDataHelper

class VideoParserService(QObject):
	"""Service to parse video into images """
	#Signals to send info back to the GUI
	sig_msg = pyqtSignal(str)
	sig_done = pyqtSignal(int, int)

	def __init__(self, id, video, srt, output, interval):
		"""
		__init__ constructor
		
		:Int id: numeric id
		:String video: the path to the video file to be processed
		:String str: the path to the srt file to be processed
		:String output: the path to the output directory where images will be stored
		:int interval: length of time in seconds between frames being captured
		"""
		self.logger = LoggerService()
		super().__init__()
		self.__id = id
		self.video_path = video
		self.srt_path = srt
		self.output_dir = output
		self.interval = interval
		self.cancelled = False
	
	@pyqtSlot()
	def processVideo(self):
		"""
		processVideo converts a video into still images with metadata sources from an SRT file
		"""
		try:
			cap = cv2.VideoCapture(self.video_path)

			fps = cap.get(cv2.CAP_PROP_FPS)
			frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
			duration = round(frame_count/fps)
			est_capture = math.floor(duration/self.interval)+1
			self.sig_msg.emit("Video length: %i seconds.  %i images will be captured" % (duration, est_capture))

			#Ensure the file provides is a vidoe file.
			if not cap.isOpened():
				self.sig_msg.emit("SRT File Not Provided")
				self.sig_done.emit(self.__id, 0)
				return
			elif cap.get(cv2.CAP_PROP_FPS) == 0:
				self.sig_msg.emit("SRT File Not Provided")
				self.sig_done.emit(self.__id, 0)
				return
			
			srt_list = []
			if self.srt_path != "":
				self.sig_msg.emit("Parsing SRT File")
				srt_data = Path(self.srt_path).read_text()
				srt_entries = re.split("(?:\r?\n){2,}", srt_data)
				for entry in srt_entries:
					data = re.split("(?:\r?\n)", entry)
					if len(data) == 6:
						time_data= data[1]
						times = re.split("\s.*\s", data[1])
						start_time = datetime.strptime(times[0], '%H:%M:%S,%f')
						end_time = datetime.strptime(times[1], '%H:%M:%S,%f')

						uav_data = re.findall(r'(?<=\[).+?(?=\])' , data[4])
						uav_dict = {}
						for uav_entry in uav_data:
							split = re.split("\s*:\s*", uav_entry)
							uav_dict[split[0]] = split[1]

						srt_list.append({"start": start_time, 
							"end": end_time, 
							"latitude": float(uav_dict['latitude']) if "latitude" in uav_dict else None, 
							"longitude": float(uav_dict['longitude']) if "longitude" in uav_dict else None, 
							"altitude": float(uav_dict['altitude']) if "altitude" in uav_dict else 0})
			else:
				self.sig_msg.emit("SRT File Not Provided")
			
			self.setupOutputDir();
			time_marker = 0
			time = datetime
			success = True
			image_count = 0
			base_name = os.path.basename(self.video_path)
			self.sig_msg.emit("Capturing images")
			while success and not self.cancelled:
					
					frame_id = int(fps*time_marker)
					cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
					time = datetime(1900, 1, 1) + timedelta(seconds = cap.get(cv2.CAP_PROP_POS_MSEC))

					item  = None
					if len(srt_list):
						item = next((item for item in srt_list if item["start"] <= time and item["end"] >= time), None)
					success,image = cap.read()
					if success:
						output_file = self.output_dir + '/%s_%ds.jpg'%(base_name, time_marker)
						cv2.imwrite(output_file,image)
						if item is not None:
							if item["latitude"] is not None and item["longitude"] is not None:
								latitude_ref = "N" if item["latitude"] >= 0 else 'S'
								longitude_ref = "E" if item["longitude"] >= 0 else 'W'
								MetaDataHelper.setTags(output_file, {"GPSLatitude": item["latitude"], "GPSLatitudeRef": latitude_ref, "GPSLongitude": item["longitude"], "GPSLongitudeRef": longitude_ref, "GPSAltitude": item["altitude"]})				
						image_count += 1
					time_marker += self.interval
					if image_count%10 == 0:
						self.sig_msg.emit("%i images captured" % (image_count))
			self.sig_done.emit(self.__id, image_count)
		except Exception as e:
			self.logger.error(e)		
				
	@pyqtSlot()
	def processCancel(self):
		"""
		processCancel cancels any asynchronous processes that have not completed
		"""
		self.cancelled = True
		self.sig_msg.emit("--- Cancelling Video Processing ---")
	
	def setupOutputDir(self):
		"""
		setupOutputDir creates the output directory
		"""
		try:
			if not os.path.exists(self.output_dir):
				os.mkdirs(self.output_dir)
		except Exception as e:
			self.logger.error(e)