"""
ColorPickerDialog - Dialog wrapper for ColorPickerImageViewer.

Provides a simple dialog interface for color selection from images.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QPushButton
from PySide6.QtCore import Qt
from .ColorPickerImageViewer import ColorPickerImageViewer


class ColorPickerDialog(QDialog):
    """
    Dialog for selecting a color from an image using an eyedropper tool.

    Usage:
        dialog = ColorPickerDialog(parent)
        if dialog.exec():
            color = dialog.get_selected_color()  # Returns (r, g, b) tuple or None
    """

    def __init__(self, parent=None, initial_image_path=None):
        """
        Initialize the ColorPickerDialog.

        Args:
            parent: Parent widget
            initial_image_path: Optional path to image to load initially
        """
        super().__init__(parent)

        self.selected_color = None  # (r, g, b) tuple

        self.setWindowTitle("Select Color from Image")
        self.setMinimumSize(600, 500)

        # Layout
        layout = QVBoxLayout(self)

        # Image viewer
        self.viewer = ColorPickerImageViewer(self)
        self.viewer.colorSelected.connect(self._on_color_selected)
        layout.addWidget(self.viewer)

        # Button box (no need for duplicate Load Image button - viewer has one)
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        # Rename OK to 'Use Color' and disable until a color is selected
        self._ok_button = button_box.button(QDialogButtonBox.Ok)
        if self._ok_button is not None:
            self._ok_button.setText("Use Color")
            self._ok_button.setEnabled(False)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        # Load initial image if provided
        if initial_image_path:
            self.viewer.load_image(initial_image_path)

    def _on_color_selected(self, r, g, b):
        """Handle color selection from viewer."""
        self.selected_color = (r, g, b)
        # Enable OK button now that a color is chosen
        if hasattr(self, "_ok_button") and self._ok_button is not None:
            self._ok_button.setEnabled(True)

    def get_selected_color(self):
        """
        Get the selected color.

        Returns:
            tuple: (r, g, b) tuple or None if no color was selected
        """
        # Try to get from signal handler first
        if self.selected_color:
            return self.selected_color

        # Fallback to viewer's current color
        return self.viewer.get_current_color()

    def set_image_from_path(self, filepath):
        """
        Load an image from file path.

        Args:
            filepath: Path to image file

        Returns:
            bool: True if image loaded successfully
        """
        return self.viewer.load_image(filepath)

    def set_image_from_array(self, image_array):
        """
        Set image from numpy array.

        Args:
            image_array: numpy array in BGR format (as from cv2.imread)

        Returns:
            bool: True if image set successfully
        """
        return self.viewer.set_image_from_array(image_array)
