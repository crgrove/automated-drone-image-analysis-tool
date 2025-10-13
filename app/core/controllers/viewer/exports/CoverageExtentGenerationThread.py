"""
CoverageExtentGenerationThread - Background thread for coverage extent calculation and KML export.

Handles the calculation of coverage extents and KML file generation in a separate thread.
"""

from PySide6.QtCore import QThread, Signal


class CoverageExtentGenerationThread(QThread):
    """Thread for generating coverage extent KML files."""
    finished = Signal(dict)  # Emits coverage_data on success
    canceled = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)  # current, total, message

    def __init__(self, coverage_service, kml_service, images, output_path):
        """
        Initialize the coverage extent generation thread.

        Args:
            coverage_service (CoverageExtentService): Service for calculating coverage extents
            kml_service (KMLGeneratorService): Service for generating KML files
            images: List of image data
            output_path (str): The file path where the KML will be saved
        """
        super().__init__()
        self.coverage_service = coverage_service
        self.kml_service = kml_service
        self.images = images
        self.output_path = output_path
        self._is_canceled = False

    def run(self):
        """
        Execute the coverage extent calculation and KML generation.

        Calculates coverage extents, generates KML, and emits appropriate signals.
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

                # Calculate coverage extents
                coverage_data = self.coverage_service.calculate_coverage_extents(
                    self.images,
                    progress_callback=progress_callback,
                    cancel_check=cancel_check
                )

                # Check if cancelled
                if coverage_data.get('cancelled', False):
                    self.canceled.emit()
                    return

                # Check if we got valid data
                if coverage_data['image_count'] == 0:
                    # Still emit finished with the data so controller can show appropriate message
                    self.finished.emit(coverage_data)
                    return

                # Generate KML file
                if not self._is_canceled:
                    self.progressUpdated.emit(
                        len(self.images),
                        len(self.images),
                        "Generating KML file..."
                    )
                    self.kml_service.generate_coverage_extent_kml(coverage_data, self.output_path)
                    
                if not self._is_canceled:
                    self.finished.emit(coverage_data)
                else:
                    self.canceled.emit()
                    
        except Exception as e:
            self.errorOccurred.emit(str(e))

    def cancel(self):
        """
        Cancel the coverage extent generation process.

        Sets the cancellation flag and emits the canceled signal.
        """
        self._is_canceled = True

