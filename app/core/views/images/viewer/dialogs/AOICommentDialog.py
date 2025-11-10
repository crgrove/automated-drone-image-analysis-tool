"""AOICommentDialog - Dialog for adding/editing user comments on flagged AOIs."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt


class AOICommentDialog(QDialog):
    """Dialog for entering or editing a user comment for an AOI."""

    def __init__(self, parent, initial_comment=""):
        """Initialize the comment dialog.

        Args:
            parent: Parent widget
            initial_comment: Existing comment text (if editing)
        """
        super().__init__(parent)
        self.comment = initial_comment
        self.max_length = 256

        self.setupUi()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle("AOI Comment")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        # Main layout
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel("Add a comment for this flagged AOI (max 256 characters):")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Text edit for comment
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Enter your comment here...")
        self.comment_edit.setPlainText(self.comment)
        self.comment_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.comment_edit)

        # Character counter
        self.char_count_label = QLabel(f"{len(self.comment)}/{self.max_length}")
        self.char_count_label.setAlignment(Qt.AlignRight)
        self.char_count_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        layout.addWidget(self.char_count_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Set focus to text edit
        self.comment_edit.setFocus()

    def on_text_changed(self):
        """Handle text changes to enforce character limit and update counter."""
        text = self.comment_edit.toPlainText()

        # Enforce character limit
        if len(text) > self.max_length:
            # Truncate text to max length
            self.comment_edit.blockSignals(True)
            cursor = self.comment_edit.textCursor()
            cursor_pos = cursor.position()

            truncated_text = text[:self.max_length]
            self.comment_edit.setPlainText(truncated_text)

            # Restore cursor position (at end if it was beyond limit)
            cursor.setPosition(min(cursor_pos, self.max_length))
            self.comment_edit.setTextCursor(cursor)
            self.comment_edit.blockSignals(False)

            text = truncated_text

        # Update character count
        char_count = len(text)
        self.char_count_label.setText(f"{char_count}/{self.max_length}")

        # Change color if approaching limit
        if char_count >= self.max_length:
            self.char_count_label.setStyleSheet("QLabel { color: red; font-size: 10pt; font-weight: bold; }")
        elif char_count >= self.max_length * 0.9:
            self.char_count_label.setStyleSheet("QLabel { color: orange; font-size: 10pt; }")
        else:
            self.char_count_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")

    def get_comment(self):
        """Get the entered comment text.

        Returns:
            str: The comment text
        """
        return self.comment_edit.toPlainText().strip()
