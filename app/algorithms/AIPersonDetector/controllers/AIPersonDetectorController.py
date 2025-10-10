import os
import subprocess
import sys
import re
from algorithms.AlgorithmController import AlgorithmController
from algorithms.AIPersonDetector.views.AIPersonDetector_ui import Ui_AIPersonDetector
from core.services.LoggerService import LoggerService
from helpers.CudaCheck import CudaCheck

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt


class AIPersonDetectorController(QWidget, Ui_AIPersonDetector, AlgorithmController):
    """
    Controller class for the AI Person Detector algorithm widget.
    Handles UI updates, configuration, and environment checks for GPU support.
    """

    def __init__(self, config, theme):
        """
        Initialize the controller and connect UI events.

        Args:
            config (dict): Configuration options for the algorithm controller.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)
        self.confidenceSlider.valueChanged.connect(self.update_confidence)
        self.GPULabel.linkActivated.connect(self.show_gpu_requirements_popup)
        self.cpu_only = False
        self._update_gpu_label()

    def update_confidence(self):
        """
        Update the label displaying the current confidence threshold
        when the slider value changes.
        """
        self.confidenceValueLabel.setText(str(self.confidenceSlider.value()))

    def get_options(self):
        """
        Retrieve current user-selected options from the UI.

        Returns:
            dict: A dictionary containing the 'person_detector_confidence' option.
        """
        options = dict()
        options['person_detector_confidence'] = float(self.confidenceValueLabel.text())
        options['cpu_only'] = self.cpu_only
        return options

    def validate(self):
        """
        Validate the current configuration.

        Returns:
            None: Always returns None (stub for future validation).
        """
        return None

    def load_options(self, options):
        """
        Load provided options into the UI.

        Args:
            options (dict): Dictionary of options (expects 'person_detector_confidence').
        """
        if 'person_detector_confidence' in options:
            self.confidenceValueLabel.setText(str(options['person_detector_confidence']))
            self.confidenceSlider.setProperty("value", int(float(options['person_detector_confidence'])))

    def _update_gpu_label(self):
        """
        Update the GPU status label to indicate whether GPU acceleration is available.
        Adds a requirements link for more info.
        """
        requirements_link = (
            '<a href="gpu_reqs" style="text-decoration: underline; color: #0066cc;">'
            'Requirements</a>'
        )
        if sys.platform == 'darwin':
            self.GPULabel.setText(
                f'<span style="color:red;">&#x274C; GPU Not Available</span> &nbsp; {requirements_link}'
            )
            return

        results = CudaCheck.check_onnxruntime_gpu_env()
        if results["overall"]:
            self.GPULabel.setText(
                f'<span style="color:green;">&#x2714; GPU Available</span> &nbsp; {requirements_link}'
            )
            self.cpu_only = False
        else:
            self.GPULabel.setText(
                f'<span style="color:red;">&#x274C; GPU Not Available</span> &nbsp; {requirements_link}'
            )
            self.cpu_only = True

    def show_gpu_requirements_popup(self, link):
        """
        Show a popup dialog with details on ONNX Runtime GPU requirements.

        Args:
            link (str): The link identifier (unused, required for signal compatibility).
        """
        msg = (
            "<div style='font-size:10pt'><b>ONNX Runtime GPU Requirements:</b><br><ol>"
            "<li>Have a CUDA-enable NVIDA graphics card</li>"
            "<li>CUDA Toolkit version 12 or great is installed and in PATH</li>"
            "<li>cuDNN version 9 or great is installed (C:\\Program Files\\NVIDIA\\CUDNN)</li>"
            "<li>cuDNN directory is in your system PATH</li>"
            "<li>ONNX Runtime has CUDAExecutionProvider available</li></ol></div>"
            ""
            "<br><span style='font-size:10pt;color:#666;'>"
            "See the <a href='https://onnxruntime.ai/docs/build/eps.html#cuda'>official documentation</a> for details."
            "</span>"
        )
        QMessageBox.information(self, "ONNX Runtime GPU Requirements", msg)
