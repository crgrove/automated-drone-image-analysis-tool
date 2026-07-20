"""Control widget for streaming AI person detector configuration."""

from typing import Dict, Any, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QGroupBox,
    QSlider,
    QLabel,
    QCheckBox,
)

from core.services.streaming import StreamAlgorithmCapabilities
from core.views.streaming.components import InputProcessingTab, RenderingTab, FrameTab
from helpers.TranslationMixin import TranslationMixin


class AIPersonDetectorControlWidget(TranslationMixin, QWidget):
    """Tabbed controls for streaming AI person detection."""

    configChanged = Signal(dict)

    def __init__(
        self,
        parent=None,
        capabilities: Optional[StreamAlgorithmCapabilities] = None,
    ):
        super().__init__(parent)
        self.capabilities = capabilities or StreamAlgorithmCapabilities()
        self._build_ui()
        self._connect_signals()
        self._on_confidence_changed(self.confidence_slider.value())
        self._apply_translations()
        self._emit_config()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs)

        self.input_processing_tab = InputProcessingTab(capabilities=self.capabilities)
        self.frame_tab = FrameTab(capabilities=self.capabilities)
        self.rendering_tab = RenderingTab(
            show_detection_color_option=False,
            capabilities=self.capabilities,
        )
        self.tabs.addTab(self._create_detection_tab(), self.tr("Person Detection"))
        self.tabs.addTab(self.input_processing_tab, self.tr("Input && Processing"))
        self.tabs.addTab(self.frame_tab, self.tr("Frame"))
        self.tabs.addTab(self.rendering_tab, self.tr("Rendering && Cleanup"))

        # Keep the detector on the lighter legacy-style baseline by default.
        self.confidence_slider.setValue(50)
        self.input_processing_tab.set_processing_resolution(1280, 720)
        self.input_processing_tab.set_target_fps(None)
        self.rendering_tab.render_shape.setCurrentIndex(0)
        self.rendering_tab.render_text.setChecked(True)
        self.rendering_tab.max_detections_to_render.setValue(25)
        self.rendering_tab.enable_temporal_voting.setChecked(False)
        self.rendering_tab.temporal_window_frames.setValue(5)
        self.rendering_tab.temporal_threshold_frames.setValue(3)
        self.rendering_tab.enable_aspect_ratio_filter.setChecked(False)
        self.rendering_tab.min_aspect_ratio.setValue(0.2)
        self.rendering_tab.max_aspect_ratio.setValue(5.0)

    def _create_detection_tab(self) -> QWidget:
        """Create algorithm-specific controls tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        model_group = QGroupBox(self.tr("Model"))
        model_layout = QVBoxLayout(model_group)
        self.cpu_only_checkbox = QCheckBox(self.tr("Force CPU (disable DirectML)"))
        self.high_res_checkbox = QCheckBox(self.tr("Use 1024 model (higher quality, slower)"))
        model_layout.addWidget(self.cpu_only_checkbox)
        model_layout.addWidget(self.high_res_checkbox)
        layout.addWidget(model_group)

        detection_group = QGroupBox(self.tr("Detection"))
        detection_layout = QGridLayout(detection_group)
        detection_layout.setColumnMinimumWidth(0, 180)
        detection_layout.setColumnStretch(1, 1)

        detection_layout.addWidget(QLabel(self.tr("Confidence Threshold:")), 0, 0)
        confidence_layout = QHBoxLayout()
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(1, 100)
        self.confidence_slider.setValue(50)
        confidence_layout.addWidget(self.confidence_slider)
        self.confidence_label = QLabel("50%")
        confidence_layout.addWidget(self.confidence_label)
        detection_layout.addLayout(confidence_layout, 0, 1)

        layout.addWidget(detection_group)
        layout.addStretch()

        return widget

    def _connect_signals(self):
        self.confidence_slider.valueChanged.connect(self._on_confidence_changed)
        self.confidence_slider.valueChanged.connect(self._emit_config)
        self.cpu_only_checkbox.toggled.connect(self._emit_config)
        self.high_res_checkbox.toggled.connect(self._emit_config)

        self.input_processing_tab.resolution_preset.currentTextChanged.connect(
            self.input_processing_tab.on_resolution_preset_changed
        )
        self.input_processing_tab.resolution_preset.currentTextChanged.connect(self._emit_config)
        self.input_processing_tab.processing_width.valueChanged.connect(self._emit_config)
        self.input_processing_tab.processing_height.valueChanged.connect(self._emit_config)
        self.input_processing_tab.frame_rate_preset.currentTextChanged.connect(self._emit_config)
        self.input_processing_tab.render_at_processing_res.toggled.connect(self._emit_config)

        self.frame_tab.configChanged.connect(self._emit_config)

        self.rendering_tab.render_shape.currentTextChanged.connect(self._emit_config)
        self.rendering_tab.render_text.toggled.connect(self._emit_config)
        self.rendering_tab.render_contours.toggled.connect(self._emit_config)
        self.rendering_tab.max_detections_to_render.valueChanged.connect(self._emit_config)
        self.rendering_tab.enable_temporal_voting.toggled.connect(self._emit_config)
        self.rendering_tab.temporal_window_frames.valueChanged.connect(self._emit_config)
        self.rendering_tab.temporal_threshold_frames.valueChanged.connect(self._emit_config)
        self.rendering_tab.enable_aspect_ratio_filter.toggled.connect(self._emit_config)
        self.rendering_tab.min_aspect_ratio.valueChanged.connect(self._emit_config)
        self.rendering_tab.max_aspect_ratio.valueChanged.connect(self._emit_config)
        self.rendering_tab.enable_detection_clustering.toggled.connect(self._emit_config)
        self.rendering_tab.clustering_distance.valueChanged.connect(self._emit_config)

    def _on_confidence_changed(self, value: int):
        self.confidence_label.setText(f"{value}%")

    def _emit_config(self):
        self.configChanged.emit(self.get_config())

    def get_config(self) -> Dict[str, Any]:
        """Return current widget configuration."""
        processing_width, processing_height = self.input_processing_tab.get_processing_resolution()
        target_fps = self.input_processing_tab.get_target_fps()
        rendering_cfg = dict(self.rendering_tab.get_config())

        if not self.capabilities.supports_render_contours:
            rendering_cfg.pop("render_contours", None)
        if not self.capabilities.supports_use_detection_color:
            rendering_cfg.pop("use_detection_color_for_rendering", None)
        if not self.capabilities.supports_detection_clustering:
            rendering_cfg.pop("enable_detection_clustering", None)
            rendering_cfg.pop("clustering_distance", None)

        processing_resolution = None
        if processing_width is not None and processing_height is not None:
            processing_resolution = (processing_width, processing_height)

        config = {
            "person_detector_confidence": int(self.confidence_slider.value()),
            "confidence_threshold": float(self.confidence_slider.value()) / 100.0,
            "cpu_only": bool(self.cpu_only_checkbox.isChecked()),
            "high_resolution_model": bool(self.high_res_checkbox.isChecked()),
            "processing_width": processing_width,
            "processing_height": processing_height,
            "processing_resolution": processing_resolution,
            "target_fps": target_fps,
            "max_detections": int(rendering_cfg.get("max_detections_to_render", 25)),
            "max_detections_to_render": int(rendering_cfg.get("max_detections_to_render", 25)),
            "show_labels": bool(rendering_cfg.get("render_text", True)),
            "render_text": bool(rendering_cfg.get("render_text", True)),
            **rendering_cfg,
            **self.frame_tab.get_config(),
        }

        if self.capabilities.supports_render_at_processing_resolution:
            config["render_at_processing_res"] = self.input_processing_tab.render_at_processing_res.isChecked()

        return config

    def set_config(self, config: Dict[str, Any]):
        """Apply external configuration to widget state."""
        if "person_detector_confidence" in config:
            self.confidence_slider.setValue(int(config["person_detector_confidence"]))
        elif "confidence_threshold" in config:
            confidence = float(config["confidence_threshold"])
            self.confidence_slider.setValue(int(max(1, min(100, round(confidence * 100)))))

        if "cpu_only" in config:
            self.cpu_only_checkbox.setChecked(bool(config["cpu_only"]))
        if "high_resolution_model" in config:
            self.high_res_checkbox.setChecked(bool(config["high_resolution_model"]))

        if ("processing_width" in config and "processing_height" in config):
            self.input_processing_tab.set_processing_resolution(
                config["processing_width"],
                config["processing_height"],
            )
        elif (
            isinstance(config.get("processing_resolution"), tuple) and
            len(config["processing_resolution"]) == 2
        ):
            self.input_processing_tab.set_processing_resolution(
                config["processing_resolution"][0],
                config["processing_resolution"][1],
            )
        elif config.get("processing_resolution") is None:
            # Backward compatibility for older configs that used None as "Original".
            self.input_processing_tab.set_processing_resolution(None, None)

        if "target_fps" in config:
            self.input_processing_tab.set_target_fps(config["target_fps"])
        if self.capabilities.supports_render_at_processing_resolution and "render_at_processing_res" in config:
            self.input_processing_tab.render_at_processing_res.setChecked(
                bool(config["render_at_processing_res"])
            )

        rendering_config = {}
        for key in [
            "render_shape",
            "render_text",
            "render_contours",
            "max_detections_to_render",
            "enable_temporal_voting",
            "temporal_window_frames",
            "temporal_threshold_frames",
            "enable_aspect_ratio_filter",
            "min_aspect_ratio",
            "max_aspect_ratio",
            "enable_detection_clustering",
            "clustering_distance",
        ]:
            if key in config:
                rendering_config[key] = config[key]

        # Backward compatibility with older AIPerson keys.
        if "max_detections" in config and "max_detections_to_render" not in rendering_config:
            rendering_config["max_detections_to_render"] = int(config["max_detections"])
        if "show_labels" in config and "render_text" not in rendering_config:
            rendering_config["render_text"] = bool(config["show_labels"])

        if rendering_config:
            self.rendering_tab.set_config(rendering_config)

        frame_config = {}
        for key in [
            "mask_enabled",
            "frame_mask_enabled",
            "image_mask_enabled",
            "frame_buffer_pixels",
            "mask_image_path",
            "show_mask_overlay",
        ]:
            if key in config:
                frame_config[key] = config[key]
        if frame_config:
            self.frame_tab.set_config(frame_config)

        self._emit_config()
