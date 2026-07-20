import sys

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.MRMap.views.MRMap_ui import Ui_MRMap

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QListView, QVBoxLayout, QWidget

from algorithms import DetectionExpansion as _DE


class MRMapController(QWidget, Ui_MRMap, AlgorithmController):
    """Controller for the RX Anomaly algorithm widget."""

    def __init__(self, config, theme):
        """
        Initializes the MRMapController widget and sets up the UI.

        Connects the threshold slider to the updatethreshold handler.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.setupUi(self)
        self._init_combo_data()
        self._fixComboBoxForMacOS(self.colorspaceComboBox)
        self._fixComboBoxForMacOS(self.segmentsComboBox)
        self.thresholdSlider.valueChanged.connect(self.updatethreshold)
        self._build_expansion_controls()

    def _build_expansion_controls(self):
        """Add optional AOI expansion checkboxes. Defaults are fixed in DetectionExpansion."""
        container = QWidget(self)
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 6, 0, 0)
        v.setSpacing(4)

        header = QLabel(self.tr("Detection Expansion (optional)"))
        hf = header.font()
        hf.setPointSize(10)
        hf.setBold(True)
        header.setFont(hf)
        v.addWidget(header)

        row = QHBoxLayout()
        self.thresholdExpansionCheckBox = QCheckBox(self.tr("Threshold Expansion"), container)
        self.thresholdExpansionCheckBox.setToolTip(self.tr(
            "When enabled, expand each AOI to also include pixels with histogram bin-counts\n"
            "below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;\n"
            "pixels outside are added if they are connected through other qualifying pixels."
        ).format(_DE.DEFAULT_THRESHOLD_EXPANSION))
        row.addWidget(self.thresholdExpansionCheckBox)

        row.addSpacing(20)
        self.hueExpansionCheckBox = QCheckBox(self.tr("Hue Expansion"), container)
        self.hueExpansionCheckBox.setToolTip(self.tr(
            "When enabled, expand each AOI through neighbors whose hue is within +/- {0}\n"
            "(OpenCV units) of the mean hue of the original detected pixels.\n"
            "Pixels with saturation below {1}% or value below {2}% are excluded."
        ).format(
            _DE.DEFAULT_HUE_EXPANSION,
            _DE.DEFAULT_HUE_EXPANSION_SAT_FLOOR_PCT,
            _DE.DEFAULT_HUE_EXPANSION_VAL_FLOOR_PCT,
        ))
        row.addWidget(self.hueExpansionCheckBox)
        row.addStretch(1)
        v.addLayout(row)

        # Attach to the root layout of the .ui file.
        self.verticalLayout.addWidget(container)

    def _fixComboBoxForMacOS(self, combo):
        """Force non-native dropdown rendering on macOS and size the popup to fit items.

        The popup view's minimumWidth is sized to the widest item plus padding
        so dropdown entries render without truncation on every platform (the
        native Windows popup otherwise left this at 0).
        """
        combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        if sys.platform == 'darwin':
            combo.setView(QListView())

        view = combo.view()
        model = combo.model()
        widest = 0
        for row in range(combo.count()):
            width = view.sizeHintForIndex(model.index(row, combo.modelColumn())).width()
            if width > widest:
                widest = width
        # +24 accounts for the scrollbar / viewport margin
        view.setMinimumWidth(widest + 24)

    def _init_combo_data(self):
        """Attach stable option keys so translated labels do not affect config values."""
        for index in range(self.segmentsComboBox.count()):
            text = self.segmentsComboBox.itemText(index)
            try:
                self.segmentsComboBox.setItemData(index, int(text))
            except ValueError:
                continue

        for index in range(self.colorspaceComboBox.count()):
            self.colorspaceComboBox.setItemData(index, self.colorspaceComboBox.itemText(index))

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing the selected option values, including 'threshold', 'segments', 'window', and 'colorspace'.
        """
        options = dict()
        options['threshold'] = int(self.thresholdValueLabel.text())
        options['segments'] = int(self.segmentsComboBox.currentData())
        options['window'] = self.windowSpinBox.value()
        options['colorspace'] = str(self.colorspaceComboBox.currentData())
        options['threshold_expansion'] = (
            _DE.DEFAULT_THRESHOLD_EXPANSION if self.thresholdExpansionCheckBox.isChecked() else 0
        )
        if self.hueExpansionCheckBox.isChecked():
            options['hue_expansion'] = _DE.DEFAULT_HUE_EXPANSION
            options['hue_expansion_sat_floor'] = _DE.DEFAULT_HUE_EXPANSION_SAT_FLOOR_PCT
            options['hue_expansion_val_floor'] = _DE.DEFAULT_HUE_EXPANSION_VAL_FLOOR_PCT
        else:
            options['hue_expansion'] = 0
            options['hue_expansion_sat_floor'] = 0
            options['hue_expansion_val_floor'] = 0
        return options

    def updatethreshold(self):
        """
        Handles changes to the threshold slider.

        Updates the threshold value label based on the current slider position.
        """
        self.thresholdValueLabel.setText(str(self.thresholdSlider.value()))

    def validate(self):
        """
        Validates that the required values have been provided.

        Returns:
            str: An error message if validation fails, otherwise None.
        """
        return None

    def load_options(self, options):
        """
        Sets UI elements based on the provided options.

        Args:
            options (dict): The options to use to set UI attributes, including 'threshold', 'segments', 'window', and 'colorspace'.
        """
        if 'threshold' in options:
            self.thresholdValueLabel.setText(str(options['threshold']))
            self.thresholdSlider.setProperty("value", int(options['threshold']))
        if 'segments' in options:
            index = self.segmentsComboBox.findData(int(options['segments']))
            if index >= 0:
                self.segmentsComboBox.setCurrentIndex(index)
            else:
                self.segmentsComboBox.setCurrentText(str(options['segments']))
        if 'window' in options:
            self.windowSpinBox.setValue(int(options['window']))
        if 'colorspace' in options:
            index = self.colorspaceComboBox.findData(str(options['colorspace']))
            if index >= 0:
                self.colorspaceComboBox.setCurrentIndex(index)
            else:
                self.colorspaceComboBox.setCurrentText(str(options['colorspace']))
        if 'threshold_expansion' in options:
            try:
                self.thresholdExpansionCheckBox.setChecked(int(options.get('threshold_expansion') or 0) > 0)
            except (TypeError, ValueError):
                self.thresholdExpansionCheckBox.setChecked(False)
        if 'hue_expansion' in options:
            try:
                self.hueExpansionCheckBox.setChecked(int(options.get('hue_expansion') or 0) > 0)
            except (TypeError, ValueError):
                self.hueExpansionCheckBox.setChecked(False)
