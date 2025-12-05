"""
CalTopoAPIMapDialog - Dialog for selecting a CalTopo map using the API.

Displays a nested folder structure of maps and folders from CalTopo,
similar to the actual CalTopo interface.
"""

import json

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTreeWidget, QTreeWidgetItem, QLineEdit,
                               QMessageBox, QHeaderView, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from datetime import datetime
from core.views.images.viewer.dialogs.CalTopoCredentialDialog import CalTopoCredentialDialog


class CalTopoAPIMapDialog(QDialog):
    """
    Dialog for selecting a CalTopo map from a nested folder structure.

    Displays maps and folders in a tree view similar to CalTopo's interface.
    """

    # Signal emitted when map is selected
    map_selected = Signal(dict)  # Emits selected map dictionary with 'id', 'title', 'team_id'

    def __init__(self, parent=None, account_data=None, credential_helper=None, api_service=None):
        """
        Initialize the map selection dialog.

        Args:
            parent: Parent widget
            account_data: Account data dictionary from CalTopo API
            credential_helper: CalTopoCredentialHelper instance for updating credentials
            api_service: CalTopoAPIService instance for refreshing account data
        """
        super().__init__(parent)
        self.setWindowTitle("Select CalTopo Map")
        self.setModal(True)
        self.resize(700, 600)

        self.account_data = account_data or {}
        self.selected_map = None
        self.credential_helper = credential_helper
        self.api_service = api_service

        self.setup_ui()
        self.populate_tree()

    def setup_ui(self):
        """
        Set up the dialog UI.

        Creates and arranges all UI elements including search box, tree widget,
        and action buttons.
        """
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title_label = QLabel("Select a CalTopo map:")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter maps by name...")
        self.search_box.textChanged.connect(self.filter_tree)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Type", "Last Updated"])
        self.tree_widget.setRootIsDecorated(True)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        self.tree_widget.setSelectionMode(QTreeWidget.SingleSelection)

        # Set column widths
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        layout.addWidget(self.tree_widget)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(self.info_label)

        # Buttons
        button_layout = QHBoxLayout()

        # Update Credentials button (only show if credential_helper is provided)
        if self.credential_helper:
            self.update_credentials_button = QPushButton("Update Credentials")
            self.update_credentials_button.clicked.connect(self.on_update_credentials_clicked)
            button_layout.addWidget(self.update_credentials_button)

        button_layout.addStretch()

        self.select_button = QPushButton("Select Map")
        self.select_button.clicked.connect(self.on_select_clicked)
        self.select_button.setEnabled(False)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

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

    def populate_tree(self):
        """
        Populate the tree widget with maps and folders from account data.

        Builds a hierarchical tree structure from the account data, organizing
        maps and folders in a nested structure similar to CalTopo's interface.
        """
        self.tree_widget.clear()

        if not self.account_data:
            self.info_label.setText("No account data available.")
            return

        # Get state from account data
        # The API response structure is: {"result": {"state": {"features": [...]}}}
        # But _api_request already extracts "result", so account_data should have "state" directly
        features = []

        # Try primary structure: account_data.state.features
        state = self.account_data.get('state', {})
        if isinstance(state, dict):
            features = state.get('features', [])

        # If features is empty, try alternative structure
        # Sometimes the response might have features directly
        if not features:
            features = self.account_data.get('features', [])

        # If still empty, try nested structure (in case result wasn't extracted)
        if not features and 'result' in self.account_data:
            nested_result = self.account_data.get('result', {})
            if isinstance(nested_result, dict):
                nested_state = nested_result.get('state', {})
                if isinstance(nested_state, dict):
                    features = nested_state.get('features', [])
                # Also try features directly in result
                if not features:
                    features = nested_result.get('features', [])

        # Debug: Log the structure if no features found
        if not features:
            try:
                debug_info = f"Account data keys: {list(self.account_data.keys())}"
                if 'state' in self.account_data:
                    state_info = self.account_data['state']
                    if isinstance(state_info, dict):
                        debug_info += f"\nState keys: {list(state_info.keys())}"
                self.info_label.setText(f"No maps found. {debug_info}")
                print(f"DEBUG: {debug_info}")
                print(f"DEBUG: Account data structure (first 1000 chars): {json.dumps(self.account_data, indent=2, default=str)[:1000]}")
            except Exception as e:
                self.info_label.setText(f"No maps found. Error: {str(e)}")
            return

        # Build folder structure
        folders = {}  # folder_id -> folder_item
        root_items = []  # Items without a parent
        folder_parent_map = {}  # folder_id -> parent_folder_id (for nested folders)

        # First pass: create all folder items and track their parent relationships
        # Folders can be:
        # 1. Explicit Folder features with class='Folder'
        # 2. Features whose ID matches a folderId in maps or other folders

        # First, collect all folder IDs that are needed (from maps and nested folders)
        folder_ids_needed = set()
        for feature in features:
            props = feature.get('properties', {})
            feature_type = props.get('class', '')

            if feature_type == 'CollaborativeMap':
                # Maps can reference folders
                folder_id = props.get('folderId')
                if folder_id:
                    folder_ids_needed.add(folder_id)
            elif feature_type == 'UserFolder':
                # Folders can also be nested (have a parent folder)
                feature_id = feature.get('id')
                if feature_id:
                    folder_ids_needed.add(feature_id)
                    # Track parent folder relationship
                    parent_folder_id = props.get('folderId')
                    if parent_folder_id:
                        folder_parent_map[feature_id] = parent_folder_id
                        # Also add parent folder ID to the set of needed folders
                        folder_ids_needed.add(parent_folder_id)

        # Second, create folder items by matching folder IDs to features
        for feature in features:
            feature_id = feature.get('id')
            props = feature.get('properties', {})
            feature_type = props.get('class', '')

            # Check if this feature is a UserFolder we need
            if feature_type == 'UserFolder' and feature_id in folder_ids_needed and feature_id not in folders:
                folder_item = QTreeWidgetItem()
                folder_item.setText(0, props.get('title', f'Folder {feature_id[:8]}...'))
                folder_item.setText(1, "Folder")
                folder_item.setText(2, "")  # Folders don't have a modified date
                folder_item.setData(0, Qt.UserRole, {'type': 'folder', 'id': feature_id})
                folders[feature_id] = folder_item

        # Create placeholder folders for any remaining folder IDs we couldn't match
        for folder_id in folder_ids_needed:
            if folder_id not in folders:
                folder_item = QTreeWidgetItem()
                folder_item.setText(0, f"Folder {folder_id[:8]}...")
                folder_item.setText(1, "Folder")
                folder_item.setText(2, "")
                folder_item.setData(0, Qt.UserRole, {'type': 'folder', 'id': folder_id})
                folders[folder_id] = folder_item

        # Third, organize folders into their parent-child relationships
        # Process folders in order so parent folders are added before children
        folders_to_add = list(folders.keys())
        folders_added = set()

        def add_folder_to_tree(folder_id):
            """Recursively add folder and its children to the tree."""
            if folder_id in folders_added:
                return

            folder_item = folders[folder_id]
            parent_folder_id = folder_parent_map.get(folder_id)

            if parent_folder_id and parent_folder_id in folders:
                # This folder has a parent, add it as a child
                parent_item = folders[parent_folder_id]
                parent_item.addChild(folder_item)
                folders_added.add(folder_id)
                # Recursively add parent if not already added
                add_folder_to_tree(parent_folder_id)
            else:
                # This is a root-level folder, add it to the tree
                self.tree_widget.addTopLevelItem(folder_item)
                folders_added.add(folder_id)

        # Add all folders to the tree (this will handle nesting)
        for folder_id in folders_to_add:
            add_folder_to_tree(folder_id)

        # Second pass: add maps and organize into folders
        for feature in features:
            props = feature.get('properties', {})
            feature_type = props.get('class', '')

            # Only show CollaborativeMap items
            if feature_type != 'CollaborativeMap':
                continue

            map_id = feature.get('id')
            if not map_id:
                continue

            title = props.get('title', 'Untitled Map')
            folder_id = props.get('folderId')

            # Try to get modified timestamp from multiple possible locations
            # CalTopo API uses 'updated' field (in milliseconds)
            modified = None
            # First try properties.updated (primary field in CalTopo API)
            modified = props.get('updated')
            # Fallback to other possible names
            if not modified:
                modified = props.get('modified')
            if not modified:
                modified = props.get('lastModified') or props.get('last_modified')
            if not modified:
                modified = feature.get('updated') or feature.get('modified')
            if not modified:
                modified = feature.get('lastModified') or feature.get('last_modified')

            # Debug: Log if modified is not found (only for first map to avoid spam)
            if not modified:
                # Only log once per dialog load
                if not hasattr(self, '_debug_logged'):
                    print("DEBUG: Modified timestamp not found in API response.")
                    print("DEBUG: Sample feature structure (first map):")
                    print(f"  Feature keys: {list(feature.keys())}")
                    print(f"  Properties keys: {list(props.keys())}")
                    print("DEBUG: Sample feature (first 800 chars):")
                    print(json.dumps(feature, indent=2, default=str)[:800])
                    self._debug_logged = True

            # Format modified date
            modified_str = ""
            if modified is not None and modified != 0:
                try:
                    # Modified might be in milliseconds (if > 1e10) or seconds
                    if isinstance(modified, (int, float)):
                        if modified > 1e10:
                            # Assume milliseconds
                            dt = datetime.fromtimestamp(modified / 1000)
                        else:
                            # Assume seconds
                            dt = datetime.fromtimestamp(modified)
                        modified_str = dt.strftime("%b %d, %Y %I:%M %p")
                    elif isinstance(modified, str):
                        # Try parsing as ISO format or other string formats
                        try:
                            # Try ISO format
                            dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                            modified_str = dt.strftime("%b %d, %Y %I:%M %p")
                        except BaseException:
                            modified_str = modified
                except Exception:
                    # If all parsing fails, just show the raw value
                    modified_str = str(modified)

            # Check if map is locked (readonly, locked, or similar property)
            is_locked = (
                props.get('locked', False) or
                props.get('readonly', False) or
                props.get('readOnly', False) or
                feature.get('locked', False) or
                feature.get('readonly', False) or
                feature.get('readOnly', False)
            )

            # Create map item
            map_item = QTreeWidgetItem()
            map_item.setText(0, title)
            map_item.setText(1, "Map")
            map_item.setText(2, modified_str)
            map_item.setData(0, Qt.UserRole, {
                'type': 'map',
                'id': map_id,
                'title': title,
                'team_id': self.account_data.get('team_id'),  # Store team_id for API calls
                'locked': is_locked
            })

            # Disable selection for locked maps
            if is_locked:
                map_item.setFlags(map_item.flags() & ~Qt.ItemIsSelectable)
                # Gray out the text to indicate it's locked
                for col in range(3):
                    map_item.setForeground(col, map_item.foreground(col).color().darker(150))

            # Add to appropriate parent
            if folder_id and folder_id in folders:
                folders[folder_id].addChild(map_item)
            else:
                root_items.append(map_item)

        # Expand all folders that have children
        def expand_folder(item):
            """Recursively expand folders that have children."""
            if item.childCount() > 0:
                item.setExpanded(True)
                for i in range(item.childCount()):
                    expand_folder(item.child(i))

        # Expand all folders
        for i in range(self.tree_widget.topLevelItemCount()):
            expand_folder(self.tree_widget.topLevelItem(i))

        # Add root items (maps without folders) to tree
        for item in root_items:
            self.tree_widget.addTopLevelItem(item)

        # Update info label
        map_count = sum(1 for feature in features
                        if feature.get('properties', {}).get('class') == 'CollaborativeMap')
        self.info_label.setText(f"{map_count} map{'s' if map_count != 1 else ''} available")

    def filter_tree(self, search_text):
        """Filter tree items based on search text.

        Args:
            search_text (str): Search query
        """
        search_text = search_text.lower()

        def filter_item(item):
            """Recursively filter items."""
            text = item.text(0).lower()
            matches = search_text in text

            # Check children
            for i in range(item.childCount()):
                child = item.child(i)
                child_matches = filter_item(child)
                if child_matches:
                    matches = True

            item.setHidden(not matches)
            return matches

        # Filter all top-level items
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            filter_item(item)

    def on_item_clicked(self, item, column):
        """
        Handle item click.

        Updates the selected map and enables/disables the select button
        based on whether a valid map is selected.

        Args:
            item: Clicked tree item
            column: Column index
        """
        data = item.data(0, Qt.UserRole)
        if data and data.get('type') == 'map':
            # Check if map is locked
            if data.get('locked', False):
                self.selected_map = None
                self.select_button.setEnabled(False)
            else:
                self.selected_map = data
                self.select_button.setEnabled(True)
        else:
            self.selected_map = None
            self.select_button.setEnabled(False)

    def on_item_double_clicked(self, item, column):
        """
        Handle item double-click.

        Accepts the dialog if a valid map is double-clicked.

        Args:
            item: Double-clicked tree item
            column: Column index
        """
        data = item.data(0, Qt.UserRole)
        if data and data.get('type') == 'map':
            # Check if map is locked
            if not data.get('locked', False):
                self.selected_map = data
                self.on_select_clicked()

    def on_update_credentials_clicked(self):
        """Handle Update Credentials button click."""
        if not self.credential_helper:
            return

        # Get existing credentials
        existing_credentials = self.credential_helper.get_credentials()

        # Show credential dialog
        credential_dialog = CalTopoCredentialDialog(
            self,
            existing_credentials=existing_credentials,
            ask_to_change=True
        )

        if credential_dialog.exec() != CalTopoCredentialDialog.Accepted:
            return

        credentials = credential_dialog.get_credentials()
        if not credentials:
            return

        team_id, credential_id, credential_secret = credentials

        # Save new credentials
        self.credential_helper.save_credentials(team_id, credential_id, credential_secret)

        # Refresh account data if API service is available
        if self.api_service:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                success, account_data = self.api_service.get_account_data(
                    team_id, credential_id, credential_secret
                )

                if success and account_data:
                    self.account_data = account_data
                    self.populate_tree()
                    QMessageBox.information(
                        self,
                        "Credentials Updated",
                        "Credentials have been updated and the map list has been refreshed."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Update Failed",
                        "Failed to refresh account data with new credentials.\n\n"
                        "Please check your credentials and try again."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Update Error",
                    f"An error occurred while updating credentials:\n\n{str(e)}"
                )
            finally:
                QApplication.restoreOverrideCursor()
        else:
            QMessageBox.information(
                self,
                "Credentials Updated",
                "Credentials have been updated. Please close and reopen this dialog to refresh the map list."
            )

    def on_select_clicked(self):
        """
        Handle Select Map button click.

        Emits the map_selected signal with the selected map data and
        accepts the dialog.
        """
        if self.selected_map:
            self.map_selected.emit(self.selected_map)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "No Map Selected",
                "Please select a map from the list."
            )
