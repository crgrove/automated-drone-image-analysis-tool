from PySide6.QtCore import QThread, Signal


class PdfGenerationThread(QThread):
    """Thread for generating the PDF report."""
    finished = Signal()
    canceled = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)  # current, total, message

    def __init__(self, pdf_generator, output_path):
        """Initializes the PdfGenerationThread.

        Args:
            pdf_generator (PdfGeneratorService): The PDF generator instance responsible for creating the report.
            output_path (str): The file path where the generated PDF will be saved.
        """
        super().__init__()
        self.pdf_generator = pdf_generator
        self.output_path = output_path
        self._is_canceled = False

    def run(self):
        """Executes the PDF generation process.

        If the process is not canceled, it generates the PDF report and emits
        the `finished` signal upon successful completion.
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

                error_message = self.pdf_generator.generate_report(
                    self.output_path,
                    progress_callback=progress_callback,
                    cancel_check=cancel_check
                )
                if error_message:
                    self.errorOccurred.emit(error_message)  # Emit error if there's an error message
                else:
                    self.finished.emit()  # Emit finished if successful
        except Exception as e:
            self.errorOccurred.emit(str(e))  # Emit error if an exception occurs

    def cancel(self):
        """Cancels the PDF generation process.

        Sets the `_is_canceled` flag to True and emits the `canceled` signal.
        """
        self._is_canceled = True
        self.canceled.emit()
