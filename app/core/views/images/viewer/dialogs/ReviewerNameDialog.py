from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from helpers.TranslationMixin import TranslationMixin


class ReviewerNameDialog(TranslationMixin, QDialog):
    """Dialog for capturing reviewer name for review tracking."""

    def __init__(self, parent=None, current_name=""):
        """
        Initialize the Reviewer Name Dialog.

        Args:
            parent: Parent widget.
            current_name (str): Current reviewer name to pre-fill.
        """
        super().__init__(parent)
        self.reviewer_name = current_name
        self.remember = False
        self._setup_ui()
        self._apply_translations()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(self.tr("Reviewer Name"))
        self.setModal(True)
        self.setMinimumWidth(400)

        # Set custom tooltip styling
        self.setStyleSheet("""
            QToolTip {
                background-color: lightblue;
                color: black;
                border: 1px solid #333333;
                padding: 4px;
                font-size: 11px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title label
        title_label = QLabel(self.tr("Review Tracking"))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(self.tr(
            "Enter your name to track your review activity.\n"
            "This helps coordinate reviews across multiple reviewers."
        ))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel(self.tr("Your Name:"))
        name_label.setMinimumWidth(100)
        self.name_input = QLineEdit()
        self.name_input.setText(self.reviewer_name)
        self.name_input.setPlaceholderText(self.tr("Enter your name"))
        self.name_input.setToolTip(self.tr("Enter your full name or identifier for review tracking"))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Remember checkbox
        self.remember_checkbox = QCheckBox(self.tr("Remember my name"))
        self.remember_checkbox.setChecked(True)
        self.remember_checkbox.setToolTip(self.tr(
            "Save your name for future review sessions.\n"
            "You can change it later in Preferences or by clicking the reviewer name in the viewer."
        ))
        layout.addWidget(self.remember_checkbox)

        # Spacer
        layout.addSpacing(10)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton(self.tr("OK"))
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.ok_button.setMinimumWidth(80)

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumWidth(80)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Focus on name input
        self.name_input.setFocus()
        self.name_input.selectAll()

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, modal dialogs sometimes need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the name input so users can type immediately
        if hasattr(self, 'name_input'):
            self.name_input.setFocus()
            self.name_input.selectAll()

    def _on_ok_clicked(self):
        """Handle OK button click."""
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                self.tr("Name Required"),
                self.tr("Please enter your name to continue.")
            )
            self.name_input.setFocus()
            return

        self.reviewer_name = name
        self.remember = self.remember_checkbox.isChecked()
        self.accept()

    def get_reviewer_name(self):
        """
        Get the entered reviewer name.

        Returns:
            str: The reviewer name.
        """
        return self.reviewer_name

    def remember_name(self):
        """
        Check if user wants to remember their name.

        Returns:
            bool: True if remember checkbox is checked.
        """
        return self.remember
