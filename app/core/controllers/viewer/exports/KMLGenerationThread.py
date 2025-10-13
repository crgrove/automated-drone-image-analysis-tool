"""
KMLGenerationThread - Background thread for KML file generation.

Handles the generation of KML files in a separate thread to prevent UI blocking.
"""

from PySide6.QtCore import QThread, Signal


class KMLGenerationThread(QThread):
    """Thread for generating KML files."""
    finished = Signal()
    canceled = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)  # current, total, message

    def __init__(self, kml_generator, filtered_images, output_path):
        """
        Initialize the KML generation thread.

        Args:
            kml_generator (KMLGeneratorService): The KML generator instance
            filtered_images: List of filtered image data with flagged AOIs
            output_path (str): The file path where the KML will be saved
        """
        super().__init__()
        self.kml_generator = kml_generator
        self.filtered_images = filtered_images
        self.output_path = output_path
        self._is_canceled = False

    def run(self):
        """
        Execute the KML generation process.

        Generates the KML file and emits appropriate signals upon completion,
        cancellation, or error.
        """
        try:
            if not self._is_canceled:
                # Define progress callback
                def progress_callback(current, total, message):
                    if not self._is_canceled:
                        self.progressUpdated.emit(current, total, message)

                # Define cancel check
                def cancel_check():
                    return self._is_canceled

                # Generate the KML
                self.kml_generator.generate_kml_export(
                    self.filtered_images,
                    self.output_path,
                    progress_callback=progress_callback,
                    cancel_check=cancel_check
                )
                
                if not self._is_canceled:
                    self.finished.emit()
                else:
                    self.canceled.emit()
        except Exception as e:
            self.errorOccurred.emit(str(e))

    def cancel(self):
        """
        Cancel the KML generation process.

        Sets the cancellation flag and emits the canceled signal.
        """
        self._is_canceled = True
        self.canceled.emit()

