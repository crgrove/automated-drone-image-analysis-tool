"""
UIStyleController - Manages UI styling and button states.

Provides centralized button styling logic for the viewer, including active/inactive states.
"""


class UIStyleController:
    """
    Controller for managing UI element styling, particularly button states.

    Handles dynamic styling based on button active/inactive states and theme.
    """

    def __init__(self, parent_viewer, theme):
        """
        Initialize the UI style controller.

        Args:
            parent_viewer: The main Viewer instance
            theme (str): Current theme name ('Dark' or 'Light')
        """
        self.parent = parent_viewer
        self.theme = theme

    def update_toolbutton_style(self, button, is_active, property_name="buttonActive"):
        """
        Update a QToolButton's styling based on its active state.

        Args:
            button: The QToolButton to style
            is_active (bool): Whether the button is in active state
            property_name (str): The property name to use for the CSS selector
        """
        if button is None:
            return

        button.setProperty(property_name, is_active)

        if self.theme.lower() == 'light':
            # Light theme colors
            style = f"""
                QToolButton[{property_name}="true"] {{
                    background-color: #4A90E2;
                    border: 2px solid #357ABD;
                    border-radius: 4px;
                    padding: 2px;
                }}
                QToolButton[{property_name}="true"]:hover {{
                    background-color: #5BA0F2;
                    border: 2px solid #4A90E2;
                }}
                QToolButton[{property_name}="false"] {{
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    padding: 2px;
                }}
                QToolButton[{property_name}="false"]:hover {{
                    border: 1px solid #888;
                    background-color: rgba(136, 136, 136, 0.1);
                }}
                QToolButton[{property_name}="false"]:pressed {{
                    background-color: rgba(136, 136, 136, 0.2);
                }}
            """
        else:
            # Dark theme colors
            style = f"""
                QToolButton[{property_name}="true"] {{
                    background-color: #5A7FB8;
                    border: 2px solid #4A6B9A;
                    border-radius: 4px;
                    padding: 2px;
                }}
                QToolButton[{property_name}="true"]:hover {{
                    background-color: #6A8FC8;
                    border: 2px solid #5A7FB8;
                }}
                QToolButton[{property_name}="false"] {{
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    padding: 2px;
                }}
                QToolButton[{property_name}="false"]:hover {{
                    border: 1px solid #888;
                    background-color: rgba(136, 136, 136, 0.1);
                }}
                QToolButton[{property_name}="false"]:pressed {{
                    background-color: rgba(136, 136, 136, 0.2);
                }}
            """

        button.setStyleSheet(style)
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()

    def update_magnify_button_style(self):
        """Update the magnify button styling based on magnifying glass state."""
        if hasattr(self.parent, 'magnifyButton') and hasattr(self.parent, 'magnifying_glass_enabled'):
            self.update_toolbutton_style(
                self.parent.magnifyButton,
                self.parent.magnifying_glass_enabled,
                "magnifyActive"
            )

    def update_show_pois_button_style(self):
        """Update the Show POIs button styling based on its checked state."""
        if hasattr(self.parent, 'showPOIsButton'):
            self.update_toolbutton_style(
                self.parent.showPOIsButton,
                self.parent.showPOIsButton.isChecked(),
                "buttonActive"
            )

    def update_show_aois_button_style(self):
        """Update the Show AOIs button styling based on its checked state."""
        if hasattr(self.parent, 'showAOIsButton'):
            self.update_toolbutton_style(
                self.parent.showAOIsButton,
                self.parent.showAOIsButton.isChecked(),
                "buttonActive"
            )

    def update_adjustments_button_style(self):
        """Update the adjustments button styling based on dialog state."""
        if hasattr(self.parent, 'adjustmentsButton') and hasattr(self.parent, 'adjustments_dialog_open'):
            self.update_toolbutton_style(
                self.parent.adjustmentsButton,
                self.parent.adjustments_dialog_open,
                "dialogActive"
            )

    def update_measure_button_style(self):
        """Update the measure button styling based on dialog state."""
        if hasattr(self.parent, 'measureButton') and hasattr(self.parent, 'measure_dialog_open'):
            self.update_toolbutton_style(
                self.parent.measureButton,
                self.parent.measure_dialog_open,
                "dialogActive"
            )

    def update_gps_map_button_style(self):
        """Update the GPS map button styling based on map window state."""
        if hasattr(self.parent, 'GPSMapButton') and hasattr(self.parent, 'gps_map_open'):
            self.update_toolbutton_style(
                self.parent.GPSMapButton,
                self.parent.gps_map_open,
                "mapActive"
            )

    def update_rotate_image_button_style(self):
        """Update the rotate image button styling based on window state."""
        if hasattr(self.parent, 'rotateImageButton') and hasattr(self.parent, 'rotate_image_open'):
            self.update_toolbutton_style(
                self.parent.rotateImageButton,
                self.parent.rotate_image_open,
                "rotateActive"
            )
