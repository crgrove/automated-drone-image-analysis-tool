import sys

from PySide6.QtWidgets import QComboBox, QListView


class AlgorithmController:
    """Base class for algorithm controllers that manages algorithm options and validation.

    Provides a common interface for algorithm configuration UI controllers.
    Subclasses must implement get_options(), validate(), and load_options().

    Attributes:
        name: Name of the algorithm.
        is_thermal: Whether this algorithm is for thermal images.
    """

    def __init__(self, config):
        """Initialize the AlgorithmController with the given name and thermal flag.

        Args:
            config: Algorithm config dictionary containing 'name' and 'type'.
        """
        self.name = config['name']
        self.is_thermal = (config['type'] == 'Thermal')

    def get_options(self):
        """Populate and return options based on user-selected values.

        Returns:
            Dictionary of option names and their values.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def validate(self):
        """Validate that the required values have been provided.

        Returns:
            Error message string if validation fails, else None.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def load_options(self, options):
        """Set UI elements based on provided options.

        Args:
            options: Dictionary of options to set.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    @staticmethod
    def fixComboBoxForMacOS(combo):
        """Fix combobox dropdown positioning and truncation on macOS.

        Sets size-adjust policy on all platforms and forces Qt's own list-style
        popup on macOS instead of the native Cocoa menu-style popup.

        Args:
            combo: QComboBox instance to fix.
        """
        combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        if sys.platform == 'darwin':
            combo.setView(QListView())
            combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
            combo.view().setMinimumWidth(combo.minimumSizeHint().width())
