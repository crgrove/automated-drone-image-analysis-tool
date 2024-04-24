import sys
import platform
import os
import logging
import traceback
class LoggerService:
	"""Class to write errors to application log file."""
	logger = None 
	def __init__(self):
		"""
		__init__ constructor
		
		"""
		if platform.system() == 'Windows':
			home_path = os.path.expanduser("~")
			app_path = home_path + '/AppData/Roaming/ADIAT/'
			if(not os.path.exists(app_path)):
				os.makedirs(app_path)
		else:
			app_path = 'Library/Application Support/ADIAT/'
			if(not os.path.exists(app_path)):
				os.makedirs(app_path)
		log_path = app_path +'adiat_logs.txt'
		self.logger = logging.getLogger(__name__)
		stdoutHandler = logging.StreamHandler(stream=sys.stdout)
		fileHandler = logging.FileHandler(log_path)
		stdoutFmt = logging.Formatter(
		"%(name)s: %(asctime)s | %(levelname)s | %(process)d >>> %(message)s")
		stdoutHandler.setFormatter(stdoutFmt)
		fileHandler.setFormatter(stdoutFmt)
		self.logger.addHandler(stdoutHandler)
		self.logger.addHandler(fileHandler)
		
	def warning(self, message):
		self.logger.warning(message)
	
	def error(self, message):
		print(traceback.format_exc())
		self.logger.error(message)