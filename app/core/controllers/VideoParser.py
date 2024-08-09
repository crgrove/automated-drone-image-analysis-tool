from core.views.VideoParser_ui import Ui_VideoParser
from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from core.services.LoggerService import LoggerService
from core.services.VideoParserService import VideoParserService

class VideoParser(QDialog, Ui_VideoParser):
	"""Controller for the VideoParser Dialog"""
	
	def __init__(self):
		"""
		__init__ constructor for the dialog
		
		"""
		QDialog.__init__(self)
		self.setupUi(self)
		self.__threads = [] 
		self.running = False
		self.logger = LoggerService()
		self.videoSelectButton.clicked.connect(self.videoSelectButtonClicked)
		self.srtSelectButton.clicked.connect(self.srtSelectButtonClicked)
		self.outputSelectButton.clicked.connect(self.outputSelectButtonClicked)
		self.startButton.clicked.connect(self.startButtonClicked)
		self.cancelButton.clicked.connect(self.cancelButtonClicked)

	def videoSelectButtonClicked(self):
		"""
		videoSelectButtonClicked click handler for the histogram reference image loaded
		Opens a file dialog
		"""
		filename, ok = QFileDialog.getOpenFileName(self,"Select a Video File")
		if filename:
			self.videoSelectLine.setText(filename)

	def srtSelectButtonClicked(self):
		"""
		srtSelectButtonClicked click handler for the histogram reference image loaded
		Opens a file dialog
		"""
		
		filename, ok = QFileDialog.getOpenFileName(self,"Select a SRT file", filter="SRT (*.srt)")
		if filename:
			self.srtSelectLine.setText(filename)

	def outputSelectButtonClicked(self):
		"""
		outputFolderButtonClicked click handler for the output folder button
		Opens a file/directory dialog
		"""
		dir = ""
		if self.outputLine.text() != "":
			dir = self.outputLine.text()
		directory = QFileDialog.getExistingDirectory(self, "Select Directory",dir, QFileDialog.ShowDirsOnly)
		if directory:
			self.outputLine.setText(directory)

	def startButtonClicked(self):
		"""
		startButtonClicked click handler for triggering the video parsing process
		"""
		try:
			#verify that the directories have been set.
			if self.videoSelectLine.text() == "" or self.outputLine == "" :
				self.showError("Please set the video file and output directory.")
				return;
		
			self.setStartButton(False)
			
			self.addLogEntry("--- Starting video processing ---")
			
			#Create instance of the analysis class with the selected algorithm
			self.parserService = VideoParserService(1, self.videoSelectLine.text(),self.srtSelectLine.text(), self.outputLine.text(), self.timespinBox.value())

			#This must be done in a separate thread so that it won't block the GUI updates to the log
			thread = QThread()
			self.__threads.append((thread, self.parserService))
			self.parserService.moveToThread(thread)

			#Connecting the slots messages back from the analysis thread
			self.parserService.sig_msg.connect(self.onWorkerMsg)
			self.parserService.sig_done.connect(self.onWorkerDone)

			thread.started.connect(self.parserService.processVideo)
			thread.start()
			self.running = True
			self.setCancelButton(True)
		except Exception as e:
			self.running = False
			self.setStartButton(True)
			self.setCancelButton(False)
			for thread, process in self.__threads:
				thread.quit()
			self.logger.error(e)

	def cancelButtonClicked(self):
		"""
		cancelButtonClicked click handler that cancelled in progress analysis
		"""
		self.parserService.processCancel()
		self.running = False
		self.setCancelButton(False)

	def closeEvent(self, event):
		# This method is called when the dialog is about to be closed
		if self.running:
			reply = QMessageBox.question(self, 'Confirmation', 
										'Are you sure you cancel the video processing in progress?',
										QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
			
			if reply == QMessageBox.Yes:
				self.parserService.processCancel()
				for thread, process in self.__threads:
					thread.quit()
				event.accept()  # Accept the close event
			else:
				event.ignore()  # Ignore the close event
		else:
			event.accept()

	@pyqtSlot(str)
	def onWorkerMsg(self, text):
		"""
		onWorkerMsg calls the addLogEntry method to add a new line to the output window
		
		:String text: the text to add to the output window
		"""
		self.addLogEntry(text)

	@pyqtSlot(int, int)
	def onWorkerDone(self, id, image_count):
		"""
		onWorkerDone  Oncompletion of the analysis process adds a log entry with information specific to the results and updates button states
		
		:Int id: the id of the calling object
		:Int images_with_aois: the number of images that include areas of interest
		"""
		self.addLogEntry("--- Video Processing Completed ---")
		self.addLogEntry("%i images created" % (image_count))
		self.running = False
		self.setStartButton(True)
		self.setCancelButton(False)

		for thread, process in self.__threads:
			thread.quit()
	

	def addLogEntry(self, text):
		"""
		addLogEntry adds a new line of text to the output window
		
		:String text: the text to add to the output window
		"""
		self.outputWindow.appendPlainText(text);
	
	def setStartButton(self, enabled):
		"""
		setStartButton updates the start button based on the enabled parameter
		
		:Boolean enabled: True to enable and False to disable the button
		"""
		if enabled:
			self.startButton.setStyleSheet("background-color: rgb(0, 136, 0);\n""color: rgb(228, 231, 235);")
			self.startButton.setEnabled(True)	
		else:
			self.startButton.setStyleSheet("")
			self.startButton.setEnabled(False)
			
	def setCancelButton(self, enabled):
		"""
		setCancelButton updates the cancel button based on the enabled parameter
		
		:Boolean enabled: True to enable and False to disable the button
		"""
		if enabled:
			self.cancelButton.setStyleSheet("background-color: rgb(136, 0, 0);\n""color: rgb(228, 231, 235);")
			self.cancelButton.setEnabled(True)	
		else:
			self.cancelButton.setStyleSheet("")
			self.cancelButton.setEnabled(False)