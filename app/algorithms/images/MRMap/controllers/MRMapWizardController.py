"""
Wizard controller for MRMap algorithm.

Provides a simplified, guided interface for configuring MRMap detection parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup, QHBoxLayout, QLabel, QCheckBox

from algorithms import DetectionExpansion as _DE

from algorithms.AlgorithmController import AlgorithmController
from core.views.components.LabeledSlider import TextLabeledSlider
from algorithms.images.MRMap.views.MRMapWizard_ui import Ui_MRMapWizard


class MRMapWizardController(QWidget, Ui_MRMapWizard, AlgorithmController):
    """Wizard controller for MRMap algorithm."""

    def __init__(self, config, theme):
        """Initialize the wizard controller."""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults."""
        # Radio button group for complex scenes
        complex_group = QButtonGroup(self)
        complex_group.addButton(self.radioComplexNo)
        complex_group.addButton(self.radioComplexYes)

        # Aggressiveness slider with text labels matching mockup
        self.aggressivenessSlider = TextLabeledSlider(
            self,
            presets=[
                self.tr("Very \nConservative"),
                self.tr("Conservative"),
                self.tr("Moderate"),
                self.tr("Aggressive"),
                self.tr("Very \nAggressive"),
            ]
        )
        placeholder = self.aggressivenessSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.aggressivenessSlider)

        self._build_expansion_controls()

    def _build_expansion_controls(self):
        """Add optional AOI expansion checkboxes. Defaults are fixed in DetectionExpansion."""
        container = QWidget(self)
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 10, 0, 0)
        v.setSpacing(4)

        header = QLabel(self.tr("Detection Expansion (optional)"))
        header_font = header.font()
        header_font.setPointSize(12)
        header.setFont(header_font)
        v.addWidget(header)

        row = QHBoxLayout()
        self.thresholdExpansionCheck = QCheckBox(self.tr("Threshold Expansion"), container)
        self.thresholdExpansionCheck.setToolTip(self.tr(
            "When enabled, expand each AOI to also include pixels with histogram bin-counts\n"
            "below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;\n"
            "pixels outside are added if they are connected through other qualifying pixels."
        ).format(_DE.DEFAULT_THRESHOLD_EXPANSION))
        row.addWidget(self.thresholdExpansionCheck)

        row.addSpacing(20)
        self.hueExpansionCheck = QCheckBox(self.tr("Hue Expansion"), container)
        self.hueExpansionCheck.setToolTip(self.tr(
            "When enabled, expand each AOI through neighbors whose hue is within +/- {0}\n"
            "(OpenCV units) of the mean hue of the original detected pixels.\n"
            "Pixels with saturation below {1}% or value below {2}% are excluded."
        ).format(
            _DE.DEFAULT_HUE_EXPANSION,
            _DE.DEFAULT_HUE_EXPANSION_SAT_FLOOR_PCT,
            _DE.DEFAULT_HUE_EXPANSION_VAL_FLOOR_PCT,
        ))
        row.addWidget(self.hueExpansionCheck)
        row.addStretch(1)
        v.addLayout(row)

        self.verticalLayout_root.insertWidget(self.verticalLayout_root.count() - 1, container)

    def _read_ui_state(self):
        """Read current UI selections into simple values."""
        complex_scene = self.radioComplexYes.isChecked()
        aggr_index = self.aggressivenessSlider.value()
        aggr_label, aggr_value = self.aggressivenessSlider.getCurrentPreset()
        return complex_scene, aggr_index, aggr_label, aggr_value

    def get_options(self):
        """Get algorithm options."""
        options = dict()
        complex_scene, aggr_index, aggr_label, aggr_value = self._read_ui_state()

        # Map to threshold and other params based on aggressiveness
        # Index 0 (Very Conservative) = low threshold, Index 4 (Very Aggressive) = high threshold
        threshold_map = {
            0: 200,  # Very Conservative
            1: 150,  # Conservative
            2: 100,  # Moderate
            3: 50,  # Aggressive
            4: 10   # Very Aggressive
        }
        threshold = threshold_map.get(aggr_index, 50)

        # Set default segments and window (can be adjusted based on complexity)
        segments = 4 if complex_scene else 1
        window = 5

        # Service-expected fields
        options['threshold'] = threshold
        options['segments'] = segments
        options['window'] = window
        options['colorspace'] = 'LAB'  # Default to LAB to match UI default
        options['threshold_expansion'] = (
            _DE.DEFAULT_THRESHOLD_EXPANSION if self.thresholdExpansionCheck.isChecked() else 0
        )
        if self.hueExpansionCheck.isChecked():
            options['hue_expansion'] = _DE.DEFAULT_HUE_EXPANSION
            options['hue_expansion_sat_floor'] = _DE.DEFAULT_HUE_EXPANSION_SAT_FLOOR_PCT
            options['hue_expansion_val_floor'] = _DE.DEFAULT_HUE_EXPANSION_VAL_FLOOR_PCT
        else:
            options['hue_expansion'] = 0
            options['hue_expansion_sat_floor'] = 0
            options['hue_expansion_val_floor'] = 0

        # Wizard fields retained for reference
        options['complex_scene'] = complex_scene
        options['aggressiveness_index'] = aggr_index
        options['aggressiveness_label'] = aggr_label
        options['aggressiveness_value'] = aggr_value

        return options

    def validate(self):
        """Validate configuration."""
        # Always valid - no required inputs
        return None

    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return

        # Complex scene
        if 'complex_scene' in options:
            complex_scene = options.get('complex_scene', False)
            self.radioComplexYes.setChecked(bool(complex_scene))
            self.radioComplexNo.setChecked(not bool(complex_scene))

        # Aggressiveness
        if 'aggressiveness_index' in options:
            aggr_index = options.get('aggressiveness_index')
            if isinstance(aggr_index, int):
                self.aggressivenessSlider.setValue(max(0, min(4, aggr_index)))
        elif 'threshold' in options:
            # Reverse map threshold to index
            threshold = int(options['threshold'])
            if threshold <= 25:
                index = 0  # Very Conservative
            elif threshold <= 45:
                index = 1  # Conservative
            elif threshold <= 55:
                index = 2  # Moderate
            elif threshold <= 70:
                index = 3  # Aggressive
            else:
                index = 4  # Very Aggressive
            self.aggressivenessSlider.setValue(index)

        if 'threshold_expansion' in options:
            try:
                self.thresholdExpansionCheck.setChecked(int(options.get('threshold_expansion') or 0) > 0)
            except (TypeError, ValueError):
                self.thresholdExpansionCheck.setChecked(False)
        if 'hue_expansion' in options:
            try:
                self.hueExpansionCheck.setChecked(int(options.get('hue_expansion') or 0) > 0)
            except (TypeError, ValueError):
                self.hueExpansionCheck.setChecked(False)
