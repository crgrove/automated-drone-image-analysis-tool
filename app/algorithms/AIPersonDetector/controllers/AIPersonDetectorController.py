import os
import subprocess
import onnxruntime as ort
import sys
from algorithms.Algorithm import AlgorithmController
from algorithms.AIPersonDetector.views.AIPersonDetector_ui import Ui_AIPersonDetector
from core.services.LoggerService import LoggerService

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt


class AIPersonDetectorController(QWidget, Ui_AIPersonDetector, AlgorithmController):
    """Controller for the Matched Filter algorithm widget."""

    def __init__(self, config):
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)
        self.confidenceSlider.valueChanged.connect(self.update_confidence)
        self.GPULabel.linkActivated.connect(self.show_gpu_requirements_popup)  # connect popup handler
        self._update_gpu_label()

    def update_confidence(self):
        self.confidenceValueLabel.setText(str(self.confidenceSlider.value()))

    def get_options(self):
        options = dict()
        options['person_detector_confidence'] = float(self.confidenceValueLabel.text())
        return options

    def validate(self):
        return None

    def load_options(self, options):
        if 'person_detector_confidence' in options:
            self.confidenceValueLabel.setText(str(options['person_detector_confidence']))
            self.confidenceSlider.setProperty("value", int(options['person_detector_confidence']))

    def _update_gpu_label(self):
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
        # Show a popup with requirements when the requirements link is clicked
        msg = (
            "<div style='font-size:10pt'><b>ONNX Runtime GPU Requirements:</b><br><ol>"
            "<li>Have a CUDA-enable NVIDA graphics card</li>"
            "<li>CUDA Toolkit is installed and in PATH</li>"
            "<li>cuDNN is installed (C:\\Program Files\\NVIDIA\\CUDNN)</li>"
            "<li>cuDNN directory is in your system PATH</li>"
            "<li>ONNX Runtime has CUDAExecutionProvider available</li></ol></div>"
            ""
            "<br><span style='font-size:10pt;color:#666;'>"
            "See the <a href='https://onnxruntime.ai/docs/build/eps.html#cuda'>official documentation</a> for details."
            "</span>"
        )
        QMessageBox.information(self, "ONNX Runtime GPU Requirements", msg)

    def _check_onnxruntime_gpu_env(self):
        results = {
            "cuda_installed": False,
            "cudnn_installed": False,
            "cudnn_in_path": False,
            "ort_cuda_provider_available": False,
        }

        # Check CUDA
        try:
            subprocess.check_output(['nvcc', '--version'], encoding='utf-8')
            results["cuda_installed"] = True
        except Exception:
            results["cuda_installed"] = False

        # Check cuDNN (just check if directory exists)
        cuda_path = os.environ.get('CUDA_PATH') or os.environ.get('CUDA_HOME')
        print(cuda_path)
        cudnn_installed = False

        # Also check the default directory (Windows)
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

        results["overall"] = (
            results["ort_cuda_provider_available"]
            and results["cudnn_in_path"]
            and results["cuda_installed"]
        )
        return results
