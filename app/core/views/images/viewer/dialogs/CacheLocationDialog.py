"""
CacheLocationDialog - Dialog for locating cache folders when not found.

Prompts the user to select an ADIAT_Results folder containing cached thumbnails
and colors, allowing them to reuse existing caches instead of regenerating.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from pathlib import Path


class CacheLocationDialog(QDialog):
    """
    Dialog for selecting an alternative cache location.

    Allows users to browse to an ADIAT_Results folder containing
    pre-generated cache directories (.thumbnails).
    """

    def __init__(self, parent=None, missing_caches=None):
        """
        Initialize the cache location dialog.

        Args:
            parent: Parent widget
            missing_caches: List of missing cache types (e.g., ['AOI thumbnails', 'Image thumbnails', 'Colors'])
        """
        super().__init__(parent)
        self.selected_path = None
        self.missing_caches = missing_caches or []

        self.setWindowTitle("Cache Not Found")
        self.setModal(True)
        self.setMinimumWidth(500)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title label
        title = QLabel("Cached Data Not Found")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Missing caches info
        if self.missing_caches:
            missing_text = "The following cached items were not found:\n"
            for cache_type in self.missing_caches:
                missing_text += f"  • {cache_type}\n"
            missing_label = QLabel(missing_text)
            missing_label.setStyleSheet("color: #ff9933; padding: 10px; background-color: #3a3a3a; border-radius: 4px;")
            layout.addWidget(missing_label)

        # Explanation
        explanation = QLabel(
            "Without cached data, thumbnails and colors will be generated on-demand, "
            "which may cause delays when viewing results.\n\n"
            "If you have previously processed this dataset and have an ADIAT_Results "
            "folder with cached data, you can locate it now to improve performance."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("color: #cccccc;")
        layout.addWidget(explanation)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        locate_btn = QPushButton("Locate Cache Folder...")
        locate_btn.clicked.connect(self._browse_for_cache)
        locate_btn.setMinimumWidth(150)
        button_layout.addWidget(locate_btn)

        skip_btn = QPushButton("Skip (Generate On-Demand)")
        skip_btn.clicked.connect(self.reject)
        skip_btn.setMinimumWidth(150)
        button_layout.addWidget(skip_btn)

        layout.addLayout(button_layout)

        # Set stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)

    def _browse_for_cache(self):
        """Open a file dialog to browse for the ADIAT_Results folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select ADIAT_Results Folder",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if folder:
            folder_path = Path(folder)

            # Validate that the folder contains cache directories
            has_thumbnails = (folder_path / '.thumbnails').exists()

            if not has_thumbnails:
                QMessageBox.warning(
                    self,
                    "Invalid Cache Folder",
                    "The selected folder does not contain thumbnail cache directory.\n\n"
                    "Expected to find:\n"
                    "  • .thumbnails/\n\n"
                    "Please select a valid ADIAT_Results folder."
                )
                return

            # Success - set the path and close
            self.selected_path = folder_path

            # Show confirmation of what was found
            found_items = ["Thumbnails"]

            QMessageBox.information(
                self,
                "Cache Found",
                f"Found cached data for:\n  • " + "\n  • ".join(found_items) + "\n\n"
                "These caches will be used to improve loading performance."
            )

            self.accept()

    def get_selected_path(self):
        """
        Get the selected cache folder path.

        Returns:
            Path object or None if no path was selected
        """
        return self.selected_path
