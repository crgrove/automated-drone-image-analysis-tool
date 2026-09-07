import os
import subprocess
import re
from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.AIPersonDetector.views.AIPersonDetector_ui import Ui_AIPersonDetector
from core.services.LoggerService import LoggerService

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt
from helpers.TranslationMixin import TranslationMixin


class AIPersonDetectorController(TranslationMixin, QWidget, Ui_AIPersonDetector, AlgorithmController):
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
        Update the GPU status label to say whether acceleration is really available.

        Asks ONNX Runtime what it can offer rather than deciding from the
        platform, because the platform does not answer the question. Deciding
        from it was wrong in both directions: macOS reported no GPU even once
        the service was using CoreML, and every other platform reported one
        whether or not DirectML was actually present - it is absent on Linux,
        and on any Windows machine without a DirectX12 GPU. The label and the
        session now read the same provider name from
        ``AIPersonDetectorService.accelerated_provider_name()``, so they
        cannot disagree about what ADIAT would even attempt.
        """
        # Deliberately does not touch self.cpu_only. That option selects a
        # different model and slice size (640 vs 1024), so deriving it from
        # hardware detection would quietly change which network runs on any
        # machine without an accelerator. This method reports; it does not
        # reconfigure. The service requests the accelerated provider either
        # way and logs when it has to fall back.
        accelerated = self._acceleration_available()

        if accelerated:
            gpu_text = self.tr("GPU Available")
            self.GPULabel.setText(
                f'<span style="color:green;">&#x2714; {gpu_text}</span>'
            )
        else:
            gpu_text = self.tr("GPU Not Available")
            self.GPULabel.setText(
                f'<span style="color:red;">&#x274C; {gpu_text}</span>'
            )

    def _acceleration_available(self):
        """Whether this machine's accelerated ONNX provider is actually loadable.

        A missing or unimportable onnxruntime means CPU, not a crash: the
        parameter widget has to render even on a build where the DLL failed to
        load, and the service raises its own clear error when analysis starts.

        Costs one onnxruntime import - measured at ~0.7s the first time this
        widget is built in a session, then nothing. That is the price of the
        label telling the truth, and it is spent on a library the run itself
        loads seconds later anyway.
        """
        try:
            from algorithms.images.AIPersonDetector.services.AIPersonDetectorService import (
                AIPersonDetectorService,
            )
            import onnxruntime as ort

            return AIPersonDetectorService.accelerated_provider_name() in ort.get_available_providers()
        except Exception as e:
            self.logger.warning(f"Could not determine ONNX provider availability, assuming CPU: {e}")
            return False
