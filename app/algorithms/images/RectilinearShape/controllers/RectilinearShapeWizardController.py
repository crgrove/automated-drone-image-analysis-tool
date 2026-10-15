"""
RectilinearShapeWizardController.py - guided setup page for the Rectilinear Shape algorithm.

One page: what to look for (a preset, or custom sizes) and how many
candidates to show (Low / Medium / High). Everything else takes its default;
the advanced panel exposes the rest.
"""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.RectilinearShape.services.RectilinearPresets import (
    DEFAULT_OPTIONS,
    PRESET_CUSTOM,
    PRESET_IDS,
    PRESET_SIZES_CM,
    SENSITIVITY_IDS,
    SENSITIVITY_MEDIUM,
    SENSITIVITY_TO_CONFIDENCE,
    apply_preset,
    cm_to_display,
    display_to_cm,
    normalize_options,
    sensitivity_for_confidence,
    size_range_error,
)
from algorithms.images.RectilinearShape.views.RectilinearShapeWizard_ui import Ui_RectilinearShapeWizard
from core.services.SettingsService import SettingsService
from core.views.components.LabeledSlider import TextLabeledSlider
from helpers.FormatHelper import FormatHelper


class RectilinearShapeWizardController(QWidget, Ui_RectilinearShapeWizard, AlgorithmController):
    """Wizard controller for the Rectilinear Shape algorithm."""

    def __init__(self, config, theme):
        """Build the page and show the defaults.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme (unused; part of the controller contract).
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme
        self.setupUi(self)
        self.use_inches = FormatHelper.prefers_feet(SettingsService().get_setting('DistanceUnit'))
        for index in range(min(self.presetComboBox.count(), len(PRESET_IDS))):
            self.presetComboBox.setItemData(index, PRESET_IDS[index])
        self.fixComboBoxForMacOS(self.presetComboBox)
        self._configure_size_units()

        # Slider positions map to SENSITIVITY_IDS by index.
        self.sensitivitySlider = TextLabeledSlider(
            self,
            presets=[self.tr("Low"), self.tr("Medium"), self.tr("High")],
        )
        layout = QVBoxLayout(self.sensitivitySliderPlaceholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.sensitivitySlider)

        self.presetComboBox.currentIndexChanged.connect(self._on_preset_changed)
        self.load_options(DEFAULT_OPTIONS)

    def _size_spin_boxes(self):
        """The four size boxes, in long-min, long-max, short-min, short-max order."""
        return (self.longMinSpinBox, self.longMaxSpinBox, self.shortMinSpinBox, self.shortMaxSpinBox)

    def _configure_size_units(self):
        """Set suffix, range and precision of the size boxes for the display unit."""
        suffix = self.tr(" in") if self.use_inches else self.tr(" cm")
        decimals = 2 if self.use_inches else 1
        for spin_box in self._size_spin_boxes():
            spin_box.setDecimals(decimals)
            spin_box.setSuffix(suffix)
            spin_box.setRange(cm_to_display(1.0, self.use_inches), cm_to_display(2000.0, self.use_inches))

    def _set_sizes_cm(self, sizes_cm):
        """Show four cm sizes in the size boxes."""
        for spin_box, value_cm in zip(self._size_spin_boxes(), sizes_cm):
            spin_box.setValue(cm_to_display(value_cm, self.use_inches))

    def _sizes_cm(self):
        """The four sizes as entered, in cm."""
        return tuple(display_to_cm(spin_box.value(), self.use_inches) for spin_box in self._size_spin_boxes())

    def _on_preset_changed(self, index):
        """Show the preset's sizes; the boxes are editable only for a custom target."""
        preset = self.presetComboBox.itemData(index)
        sizes = PRESET_SIZES_CM.get(preset)
        if sizes is not None:
            self._set_sizes_cm(sizes)
        self.customSizeWidget.setEnabled(preset == PRESET_CUSTOM)

    def _sensitivity_id(self):
        """Stable id of the slider position."""
        index = max(0, min(len(SENSITIVITY_IDS) - 1, self.sensitivitySlider.value()))
        return SENSITIVITY_IDS[index]

    def get_options(self):
        """Full service options: defaults, the chosen target, and the sensitivity's threshold.

        The dict is handed to the main window's advanced panel as-is, so it
        must carry every service key, not just the two the page asks about.
        """
        options = dict(DEFAULT_OPTIONS)
        preset = self.presetComboBox.currentData() or PRESET_CUSTOM
        if preset in PRESET_SIZES_CM:
            apply_preset(options, preset)
        else:
            options['target_preset'] = PRESET_CUSTOM
            options['long_side_cm_min'], options['long_side_cm_max'], \
                options['short_side_cm_min'], options['short_side_cm_max'] = (round(v, 2) for v in self._sizes_cm())
        sensitivity = self._sensitivity_id()
        options['min_confidence'] = SENSITIVITY_TO_CONFIDENCE[sensitivity]
        # Kept so the page restores the exact slider position on re-entry.
        options['sensitivity'] = sensitivity
        return options

    def validate(self):
        """Check custom sizes are ordered; presets are always valid.

        Returns:
            str | None: A translated error message, or None when valid.
        """
        if self.presetComboBox.currentData() != PRESET_CUSTOM:
            return None
        error = size_range_error(*self._sizes_cm())
        if error == 'long_order':
            return self.tr("The minimum long side must not be larger than the maximum long side.")
        if error == 'short_order':
            return self.tr("The minimum short side must not be larger than the maximum short side.")
        if error == 'short_exceeds_long':
            return self.tr("The short side range must not exceed the long side range.")
        return None

    def load_options(self, options):
        """Restore the page from an options dict.

        Args:
            options (dict): Options as produced by get_options() or saved by
                an earlier run; missing keys take their defaults.
        """
        if not isinstance(options, dict):
            return
        settings = normalize_options(options)
        preset_index = max(0, self.presetComboBox.findData(settings['target_preset']))
        self.presetComboBox.blockSignals(True)
        self.presetComboBox.setCurrentIndex(preset_index)
        self.presetComboBox.blockSignals(False)
        self._set_sizes_cm((
            settings['long_side_cm_min'], settings['long_side_cm_max'],
            settings['short_side_cm_min'], settings['short_side_cm_max'],
        ))
        self.customSizeWidget.setEnabled(settings['target_preset'] == PRESET_CUSTOM)

        sensitivity = options.get('sensitivity')
        if sensitivity not in SENSITIVITY_IDS:
            sensitivity = sensitivity_for_confidence(settings['min_confidence']) if 'min_confidence' in options \
                else SENSITIVITY_MEDIUM
        self.sensitivitySlider.setValue(SENSITIVITY_IDS.index(sensitivity))
