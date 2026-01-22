"""
CalTopoMapDialog - Dialog for selecting a CalTopo map.

This dialog displays the user's CalTopo maps and allows selection
of a target map for exporting AOIs.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QListWidget, QListWidgetItem, QLineEdit)
from PySide6.QtCore import Qt, Signal
from helpers.TranslationMixin import TranslationMixin
from PySide6.QtGui import QFont
from datetime import datetime


class CalTopoMapDialog(TranslationMixin, QDialog):
    """
    Dialog for selecting a CalTopo map.

    Displays user's maps in a list with search/filter functionality.
    """

    # Signal emitted when map is selected
    map_selected = Signal(dict)  # Emits selected map dictionary

    def __init__(self, parent=None, maps_list=None):
        """
        Initialize the map selection dialog.

        Args:
            parent: Parent widget
            maps_list: List of map dictionaries from CalTopoService
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Select CalTopo Map"))
        self.resize(600, 500)
        self.setModal(True)

        self.maps_list = maps_list or []
        self.selected_map = None

        self.setup_ui()
        self._apply_translations()
        self.populate_maps()

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel(self.tr("Select a CalTopo map to export flagged AOIs:"))
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel(self.tr("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("Filter maps by name..."))
        self.search_box.textChanged.connect(self.filter_maps)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Maps list
        self.maps_list_widget = QListWidget()
        self.maps_list_widget.itemDoubleClicked.connect(self.on_map_double_clicked)
        self.maps_list_widget.itemClicked.connect(self.on_map_clicked)
        layout.addWidget(self.maps_list_widget)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(self.info_label)

        # Button row
        button_layout = QHBoxLayout()

        self.select_button = QPushButton(self.tr("Select Map"))
        self.select_button.clicked.connect(self.on_select_clicked)
        self.select_button.setEnabled(False)

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, modal dialogs sometimes need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the search box so users can type immediately
        if hasattr(self, 'search_box'):
            self.search_box.setFocus()

    def populate_maps(self):
        """Populate the maps list widget."""
        self.maps_list_widget.clear()

        for map_data in self.maps_list:
            # Create list item
            item = QListWidgetItem()

            # Format map information
            title = map_data.get('title', 'Untitled Map')
            # map_id = map_data.get('id', '')  # Reserved for future use
            modified = map_data.get('modified', '')

            # Format modified date if available
            modified_str = ""
            if modified:
                try:
                    # Parse ISO date and format nicely
                    dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    modified_str = dt.strftime("%b %d, %Y %I:%M %p")
                except Exception:
                    modified_str = modified

            # Set display text
            display_text = f"{title}"
            if modified_str:
                display_text += f"\n  Last modified: {modified_str}"

            item.setText(display_text)
            item.setData(Qt.UserRole, map_data)

            self.maps_list_widget.addItem(item)

        # Update info label
        count = len(self.maps_list)
        self.info_label.setText(f"{count} map{'s' if count != 1 else ''} available")

    def filter_maps(self, search_text):
        """Filter maps list based on search text.

        Args:
            search_text (str): Search query
        """
        search_text = search_text.lower()

        for i in range(self.maps_list_widget.count()):
            item = self.maps_list_widget.item(i)
            map_data = item.data(Qt.UserRole)
            title = map_data.get('title', '').lower()

            # Show/hide based on search match
            item.setHidden(search_text not in title)

    def on_map_clicked(self, item):
        """Handle map item click.

        Args:
            item (QListWidgetItem): Clicked item
        """
        self.selected_map = item.data(Qt.UserRole)
        self.select_button.setEnabled(True)

    def on_map_double_clicked(self, item):
        """Handle map item double-click.

        Args:
            item (QListWidgetItem): Double-clicked item
        """
        self.selected_map = item.data(Qt.UserRole)
        self.on_select_clicked()

    def on_select_clicked(self):
        """Handle Select Map button click."""
        if self.selected_map:
            self.map_selected.emit(self.selected_map)
            self.accept()
