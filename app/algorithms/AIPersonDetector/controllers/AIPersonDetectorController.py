import os
import subprocess
import onnxruntime as ort
import sys
import re
from algorithms.Algorithm import AlgorithmController
from algorithms.AIPersonDetector.views.AIPersonDetector_ui import Ui_AIPersonDetector
from core.services.LoggerService import LoggerService

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt


class AIPersonDetectorController(QWidget, Ui_AIPersonDetector, AlgorithmController):
    """
    Controller class for the AI Person Detector algorithm widget.
    Handles UI updates, configuration, and environment checks for GPU support.
    """

    def __init__(self, config):
        """
        Initialize the controller and connect UI events.

        Args:
            config (dict): Configuration options for the algorithm controller.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)
        self.confidenceSlider.valueChanged.connect(self.update_confidence)
        self.GPULabel.linkActivated.connect(self.show_gpu_requirements_popup)
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

        results = self._check_onnxruntime_gpu_env()
        if results["overall"]:
            self.GPULabel.setText(
                f'<span style="color:green;">&#x2714; GPU Available</span> &nbsp; {requirements_link}'
            )
        else:
            self.GPULabel.setText(
                f'<span style="color:red;">&#x274C; GPU Not Available</span> &nbsp; {requirements_link}'
            )

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

    def _check_onnxruntime_gpu_env(self):
        """
        Check the runtime environment for ONNX GPU support:
        - CUDA Toolkit installation (version >= 12.0)
        - cuDNN installation
        - cuDNN path configuration
        - ONNX Runtime CUDAExecutionProvider availability

        Returns:
            dict: A dictionary summarizing each check and an overall result.
                {
                    "cuda_installed": bool,
                    "cuda_version_sufficient": bool,
                    "cudnn_installed": bool,
                    "cudnn_in_path": bool,
                    "ort_cuda_provider_available": bool,
                    "overall": bool
                }
        """
        results = {
            "cuda_installed": False,
            "cuda_version_sufficient": False,
            "cudnn_installed": False,
            "cudnn_in_path": False,
            "ort_cuda_provider_available": False,
        }

        # Check CUDA
        try:
            output = subprocess.check_output(['nvcc', '--version'], encoding='utf-8')
            results["cuda_installed"] = True

            # Parse version from output
            match = re.search(r"release (\d+)\.(\d+)", output)
            if match:
                major, _ = int(match.group(1)), int(match.group(2))
                results["cuda_version_sufficient"] = major >= 12
        except Exception:
            results["cuda_installed"] = False
            results["cuda_version_sufficient"] = False

        # Check cuDNN (just check if directory exists)
        cuda_path = os.environ.get('CUDA_PATH') or os.environ.get('CUDA_HOME')
        cudnn_installed = False

        if os.name == 'nt':
            default_cudnn_dir = r"C:\Program Files\NVIDIA\CUDNN"
            if os.path.isdir(default_cudnn_dir):
                cudnn_installed = True

        results["cudnn_installed"] = cudnn_installed

        # Check cuDNN in PATH
        env_var = 'PATH' if os.name == 'nt' else 'LD_LIBRARY_PATH'
        search_path = os.environ.get(env_var, '')
        cudnn_dir = os.path.join(cuda_path, 'bin' if os.name == 'nt' else 'lib64') if cuda_path else ''
        results["cudnn_in_path"] = cudnn_dir in search_path if cudnn_dir else False

        # Check ONNX Runtime GPU provider
        providers = ort.get_available_providers()
        results["ort_cuda_provider_available"] = 'CUDAExecutionProvider' in providers

        # Overall check includes version requirement
        results["overall"] = (
            results["cuda_installed"]
            and results["cuda_version_sufficient"]
            and results["cudnn_in_path"]
            and results["ort_cuda_provider_available"]
        )
        return results
