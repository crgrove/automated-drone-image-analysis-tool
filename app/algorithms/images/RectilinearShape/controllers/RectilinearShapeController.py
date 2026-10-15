"""
RectilinearShapeController.py - advanced options panel for the Rectilinear Shape algorithm.

Exposes every option the service reads. Target sizes are shown in centimetres
or inches according to the DistanceUnit setting and always stored in
centimetres.
"""

from PySide6.QtWidgets import QWidget

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.RectilinearShape.services.RectilinearPresets import (
    DEFAULT_OPTIONS,
    PRESET_CUSTOM,
    PRESET_IDS,
    PRESET_SIZES_CM,
    apply_preset,
    cm_to_display,
    display_to_cm,
    normalize_options,
    size_range_error,
)
from algorithms.images.RectilinearShape.views.RectilinearShape_ui import Ui_RectilinearShape
from core.services.SettingsService import SettingsService
from helpers.FormatHelper import FormatHelper


class RectilinearShapeController(QWidget, Ui_RectilinearShape, AlgorithmController):
    """Controller for the Rectilinear Shape algorithm widget."""

    def __init__(self, config, theme):
        """Build the panel and show the default options.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme (unused; part of the controller contract).
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.setupUi(self)
        self.use_inches = FormatHelper.prefers_feet(SettingsService().get_setting('DistanceUnit'))
        # Set while a preset is writing the size boxes, so that write is not
        # mistaken for the operator editing a size.
        self._applying_preset = False
        for index in range(min(self.presetComboBox.count(), len(PRESET_IDS))):
            self.presetComboBox.setItemData(index, PRESET_IDS[index])
        self.fixComboBoxForMacOS(self.presetComboBox)
        self._configure_size_units()

        self.presetComboBox.currentIndexChanged.connect(self._on_preset_changed)
        for spin_box in self._size_spin_boxes():
            spin_box.valueChanged.connect(self._on_size_edited)
        self.useBoxinessCheckBox.toggled.connect(self.minBoxinessSpinBox.setEnabled)

        self.load_options(DEFAULT_OPTIONS)

    def _size_spin_boxes(self):
        """The four size boxes, in long-min, long-max, short-min, short-max order."""
        return (self.longMinSpinBox, self.longMaxSpinBox, self.shortMinSpinBox, self.shortMaxSpinBox)

    def _configure_size_units(self):
        """Set suffix, range and precision of the size boxes for the display unit."""
        suffix = self.tr(" in") if self.use_inches else self.tr(" cm")
        # Two decimals in inches keep a cm -> in -> cm round trip within 0.02 cm.
        decimals = 2 if self.use_inches else 1
        for spin_box in self._size_spin_boxes():
            spin_box.setDecimals(decimals)
            spin_box.setSuffix(suffix)
            spin_box.setRange(cm_to_display(1.0, self.use_inches), cm_to_display(2000.0, self.use_inches))
            spin_box.setSingleStep(1.0)

    def _set_sizes_cm(self, sizes_cm):
        """Show four cm sizes in the size boxes without flipping the preset to custom."""
        self._applying_preset = True
        try:
            for spin_box, value_cm in zip(self._size_spin_boxes(), sizes_cm):
                spin_box.setValue(cm_to_display(value_cm, self.use_inches))
        finally:
            self._applying_preset = False

    def _sizes_cm(self):
        """The four sizes as entered, in cm."""
        return tuple(display_to_cm(spin_box.value(), self.use_inches) for spin_box in self._size_spin_boxes())

    def _on_preset_changed(self, index):
        """Fill the size boxes from the chosen preset; custom leaves them as they are."""
        sizes = PRESET_SIZES_CM.get(self.presetComboBox.itemData(index))
        if sizes is not None:
            self._set_sizes_cm(sizes)

    def _on_size_edited(self, value):
        """Editing a size by hand makes the target a custom one."""
        if self._applying_preset or self.presetComboBox.currentData() == PRESET_CUSTOM:
            return
        custom_index = self.presetComboBox.findData(PRESET_CUSTOM)
        self.presetComboBox.blockSignals(True)
        self.presetComboBox.setCurrentIndex(custom_index)
        self.presetComboBox.blockSignals(False)

    def get_options(self):
        """Collect the panel's values into the service's options dict.

        Returns:
            dict: Every key in DEFAULT_OPTIONS. Preset sizes are taken from the
            preset table rather than read back off the widgets, so an inch
            display can never nudge them.
        """
        options = dict(DEFAULT_OPTIONS)
        preset = self.presetComboBox.currentData() or PRESET_CUSTOM
        if preset in PRESET_SIZES_CM:
            apply_preset(options, preset)
        else:
            options['target_preset'] = PRESET_CUSTOM
            options['long_side_cm_min'], options['long_side_cm_max'], \
                options['short_side_cm_min'], options['short_side_cm_max'] = (round(v, 2) for v in self._sizes_cm())
        options['size_tolerance'] = self.sizeToleranceSpinBox.value() / 100.0
        options['angle_tolerance_deg'] = self.angleToleranceSpinBox.value()
        options['min_edge_contrast'] = self.edgeContrastSpinBox.value()
        options['min_edge_support'] = self.edgeSupportSpinBox.value()
        options['use_boxiness'] = self.useBoxinessCheckBox.isChecked()
        options['min_boxiness'] = self.minBoxinessSpinBox.value()
        options['min_short_side_px'] = self.minShortSideSpinBox.value()
        options['min_confidence'] = self.minConfidenceSpinBox.value()
        options['max_detections_per_image'] = self.maxDetectionsSpinBox.value()
        fallback = self.fallbackGsdSpinBox.value()
        options['fallback_gsd_cm'] = fallback if fallback > 0 else None
        options['debug_output'] = self.debugOutputCheckBox.isChecked()
        return options

    def validate(self):
        """Check the size ranges are ordered and the short side fits inside the long side.

        Returns:
            str | None: A translated error message, or None when valid.
        """
        error = size_range_error(*self._sizes_cm())
        if error == 'long_order':
            return self.tr("The minimum long side must not be larger than the maximum long side.")
        if error == 'short_order':
            return self.tr("The minimum short side must not be larger than the maximum short side.")
        if error == 'short_exceeds_long':
            return self.tr("The short side range must not exceed the long side range.")
        return None

    def load_options(self, options):
        """Show an options dict, filling any missing key with its default.

        Accepts dicts from earlier builds and dicts read back from
        ADIAT_Data.xml, where every value is a string and falsy values are "".

        Args:
            options (dict): Options to display.
        """
        if not isinstance(options, dict):
            return
        settings = normalize_options(options)
        preset_index = self.presetComboBox.findData(settings['target_preset'])
        self.presetComboBox.blockSignals(True)
        self.presetComboBox.setCurrentIndex(max(0, preset_index))
        self.presetComboBox.blockSignals(False)
        self._set_sizes_cm((
            settings['long_side_cm_min'], settings['long_side_cm_max'],
            settings['short_side_cm_min'], settings['short_side_cm_max'],
        ))
        self.sizeToleranceSpinBox.setValue(int(round(settings['size_tolerance'] * 100.0)))
        self.angleToleranceSpinBox.setValue(settings['angle_tolerance_deg'])
        self.edgeContrastSpinBox.setValue(settings['min_edge_contrast'])
        self.edgeSupportSpinBox.setValue(settings['min_edge_support'])
        self.useBoxinessCheckBox.setChecked(settings['use_boxiness'])
        self.minBoxinessSpinBox.setValue(settings['min_boxiness'])
        self.minBoxinessSpinBox.setEnabled(settings['use_boxiness'])
        self.minShortSideSpinBox.setValue(settings['min_short_side_px'])
        self.minConfidenceSpinBox.setValue(settings['min_confidence'])
        self.maxDetectionsSpinBox.setValue(settings['max_detections_per_image'])
        self.fallbackGsdSpinBox.setValue(settings['fallback_gsd_cm'] or 0.0)
        self.debugOutputCheckBox.setChecked(settings['debug_output'])
