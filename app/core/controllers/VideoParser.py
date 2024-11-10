from core.views.VideoParser_ui import Ui_VideoParser
from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from core.services.LoggerService import LoggerService
from core.services.VideoParserService import VideoParserService


class VideoParser(QDialog, Ui_VideoParser):
    """Controller for the VideoParser Dialog.

    This class manages the video parsing dialog, handling user interactions,
    launching the video parsing process in a separate thread, and updating
    the UI based on process events.
    """

    def __init__(self):
        """Initializes the VideoParser dialog."""
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
        """Handles the video file selection button click.

        Opens a file dialog for the user to select a video file, then
        updates the `videoSelectLine` text field with the selected file path.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Select a Video File")
        if filename:
            self.videoSelectLine.setText(filename)

    def srtSelectButtonClicked(self):
        """Handles the subtitle (SRT) file selection button click.

        Opens a file dialog for the user to select an SRT file, then
        updates the `srtSelectLine` text field with the selected file path.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Select a SRT file", filter="SRT (*.srt)")
        if filename:
            self.srtSelectLine.setText(filename)

    def outputSelectButtonClicked(self):
        """Handles the output directory selection button click.

        Opens a directory selection dialog for the user to choose an
        output directory, then updates the `outputLine` text field with
        the selected directory path.
        """
        initial_dir = self.outputLine.text() if self.outputLine.text() else ""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", initial_dir, QFileDialog.ShowDirsOnly)
        if directory:
            self.outputLine.setText(directory)

    def startButtonClicked(self):
        """Handles the start button click to begin video parsing.

        Verifies that the necessary input fields are filled, disables the start
        button, initiates the `VideoParserService` in a separate thread, and
        connects signals from the worker thread to update the UI.
        """
        try:
            # Verify that the video file and output directory are set
            if not self.videoSelectLine.text() or not self.outputLine.text():
                self.showError("Please set the video file and output directory.")
                return

            self.setStartButton(False)
            self.addLogEntry("--- Starting video processing ---")

            # Initialize the video parser service and move it to a separate thread
            self.parserService = VideoParserService(
                1, self.videoSelectLine.text(), self.srtSelectLine.text(), self.outputLine.text(), self.timespinBox.value()
            )
            thread = QThread()
            self.__threads.append((thread, self.parserService))
            self.parserService.moveToThread(thread)

            # Connect signals from the parser service
            self.parserService.sig_msg.connect(self.onWorkerMsg)
            self.parserService.sig_done.connect(self.onWorkerDone)

            # Start the processing thread
            thread.started.connect(self.parserService.processVideo)
            thread.start()
            self.running = True
            self.setCancelButton(True)
        except Exception as e:
            self.logger.error(e)
            self.running = False
            self.setStartButton(True)
            self.setCancelButton(False)
            for thread, process in self.__threads:
                thread.quit()

    def cancelButtonClicked(self):
        """Handles the cancel button click to terminate video parsing.

        Signals the `VideoParserService` to cancel the process and disables
        the cancel button.
        """
        self.parserService.processCancel()
        self.running = False
        self.setCancelButton(False)

    def closeEvent(self, event):
        """Overrides the close event to handle in-progress video processing.

        If the video processing is in progress, prompts the user for confirmation
        before closing. Cancels the video processing if the user confirms.

        Args:
            event (QCloseEvent): The close event.
        """
        if self.running:
            reply = QMessageBox.question(
                self, 'Confirmation', 'Are you sure you want to cancel the video processing in progress?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.parserService.processCancel()
                for thread, process in self.__threads:
                    thread.quit()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    @pyqtSlot(str)
    def onWorkerMsg(self, text):
        """Slot to handle log messages from the worker thread.

        Adds a new entry to the output log.

        Args:
            text (str): The message text to log.
        """
        self.addLogEntry(text)

    @pyqtSlot(int, int)
    def onWorkerDone(self, id, image_count):
        """Slot to handle the completion signal from the worker thread.

        Logs the completion of the video processing, updates the button states,
        and terminates the thread.

        Args:
            id (int): The identifier for the worker thread.
            image_count (int): The total number of images created.
        """
        self.addLogEntry("--- Video Processing Completed ---")
        self.addLogEntry(f"{image_count} images created")
        self.running = False
        self.setStartButton(True)
        self.setCancelButton(False)

        for thread, process in self.__threads:
            thread.quit()

    def addLogEntry(self, text):
        """Adds a new line of text to the output window log.

        Args:
            text (str): The text to add to the log window.
        """
        self.outputWindow.appendPlainText(text)

    def setStartButton(self, enabled):
        """Sets the start button state based on the `enabled` parameter.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        if enabled:
            self.startButton.setStyleSheet("background-color: rgb(0, 136, 0); color: rgb(228, 231, 235);")
            self.startButton.setEnabled(True)
        else:
            self.startButton.setStyleSheet("")
            self.startButton.setEnabled(False)

    def setCancelButton(self, enabled):
        """Sets the cancel button state based on the `enabled` parameter.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        if enabled:
            self.cancelButton.setStyleSheet("background-color: rgb(136, 0, 0); color: rgb(228, 231, 235);")
            self.cancelButton.setEnabled(True)
        else:
            self.cancelButton.setStyleSheet("")
            self.cancelButton.setEnabled(False)
