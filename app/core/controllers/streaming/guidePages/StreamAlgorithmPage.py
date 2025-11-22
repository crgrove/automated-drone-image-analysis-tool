"""Algorithm selection for the streaming setup wizard."""

from .BasePage import BasePage


class StreamAlgorithmPage(BasePage):
    """Page for selecting streaming algorithm via guided decision tree."""

    def __init__(self, wizard_data, settings_service, dialog):
        """Initialize the page."""
        super().__init__(wizard_data, settings_service, dialog)
        # Algorithm selection state
        self.algorithm_decision_state = {
            'specific_color': None
        }
        self.selected_algorithm = None

    def setup_ui(self) -> None:
        """Initialize UI components."""
        self._reset_algorithm_selection()

    def connect_signals(self) -> None:
        """Connect UI signals to handlers."""
        self.dialog.buttonYes.clicked.connect(lambda: self._on_algorithm_button_clicked(True))
        self.dialog.buttonNo.clicked.connect(lambda: self._on_algorithm_button_clicked(False))
        self.dialog.resetAlgorithmButton.clicked.connect(self._on_reset_algorithm_clicked)

    def load_data(self) -> None:
        """Load algorithm selection if available."""
        # Don't load from settings - only use what's in wizard_data
        # This ensures algorithm resets between wizard sessions but persists when going back/forward
        # wizard_data["algorithm"] will be None for a fresh wizard, or contain the selection when navigating

    def validate(self) -> bool:
        """Validate that an algorithm is selected."""
        return self.selected_algorithm is not None

    def save_data(self) -> None:
        """Save selected algorithm to wizard_data."""
        if self.selected_algorithm:
            self.wizard_data["algorithm"] = self.selected_algorithm

    def on_enter(self):
        """Called when entering the page."""
        # Check if we have a saved algorithm in wizard_data
        saved_algorithm = self.wizard_data.get("algorithm")
        if saved_algorithm:
            # Restore the saved algorithm selection
            self.selected_algorithm = saved_algorithm
            self._show_algorithm_result()
        else:
            # No saved algorithm - start fresh
            self._reset_algorithm_selection()

    def on_exit(self):
        """Called when leaving the page."""
        # Save algorithm selection
        if self.selected_algorithm:
            self.wizard_data["algorithm"] = self.selected_algorithm

    def _on_reset_algorithm_clicked(self):
        """Handle reset button click - show brief feedback then reset."""
        # Show active state briefly
        active_style = """
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: white;
                border-radius: 4px;
            }
        """
        self.dialog.resetAlgorithmButton.setStyleSheet(active_style)

        # Reset the algorithm selection
        self._reset_algorithm_selection()

    def _reset_algorithm_selection(self):
        """Reset algorithm selection to initial state."""
        self.algorithm_decision_state = {
            'specific_color': None
        }
        self.selected_algorithm = None
        # Clear algorithm from wizard_data to ensure fresh start
        self.wizard_data["algorithm"] = None
        self.dialog.labelCurrentQuestion.setText("Are you looking for specific colors?")
        self.dialog.labelAlgorithmResult.setVisible(False)
        self.dialog.buttonYes.setVisible(True)
        self.dialog.buttonNo.setVisible(True)
        self._reset_algorithm_buttons_style()

    def _reset_algorithm_buttons_style(self):
        """Reset both algorithm selection buttons to inactive state."""
        # Inactive state: transparent background with light gray border
        inactive_style = """
            QPushButton {
                background-color: transparent;
                border: 1px solid #888888;
                color: #CCCCCC;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(136, 136, 136, 0.1);
                border: 1px solid #AAAAAA;
            }
            QPushButton:pressed {
                background-color: rgba(136, 136, 136, 0.2);
            }
        """
        self.dialog.buttonYes.setStyleSheet(inactive_style)
        self.dialog.buttonNo.setStyleSheet(inactive_style)
        self.dialog.resetAlgorithmButton.setStyleSheet(inactive_style)

    def _on_algorithm_button_clicked(self, answer):
        """Handle algorithm button click - show brief feedback then process answer."""
        # Show which button was clicked with active style
        active_style = """
            QPushButton {
                background-color: #4A90E2;
                border: none;
                color: white;
                border-radius: 4px;
            }
        """

        if answer:
            self.dialog.buttonYes.setStyleSheet(active_style)
        else:
            self.dialog.buttonNo.setStyleSheet(active_style)

        # Process the answer (this will reset buttons if moving to next question)
        self._on_algorithm_answer(answer)

        # Reset both buttons to inactive state after processing
        # (This ensures both are inactive for the next question)
        self._reset_algorithm_buttons_style()

    def _on_algorithm_answer(self, answer):
        """Handle algorithm selection decision tree answers."""
        state = self.algorithm_decision_state

        if state['specific_color'] is None:
            state['specific_color'] = answer
            if answer:  # Yes - looking for specific colors
                # Color Detection (color range)
                self.selected_algorithm = "ColorDetection"
                self._show_algorithm_result()
            else:  # No - not looking for specific colors
                # Color Anomaly & Motion Detection (combined detection)
                self.selected_algorithm = "ColorAnomalyAndMotionDetection"
                self._show_algorithm_result()

    def _show_algorithm_result(self):
        """Display the selected algorithm result."""
        if self.selected_algorithm:
            # Map algorithm key to display name
            algorithm_names = {
                "MotionDetection": "Motion Detection",
                "ColorDetection": "Color Detection",
                "ColorAnomalyAndMotionDetection": "Color Anomaly & Motion Detection"
            }
            display_name = algorithm_names.get(self.selected_algorithm, self.selected_algorithm)
            self.dialog.labelAlgorithmResult.setText(f"Selected Algorithm: {display_name}")
            self.dialog.labelAlgorithmResult.setVisible(True)
            self.dialog.buttonYes.setVisible(False)
            self.dialog.buttonNo.setVisible(False)
            self.wizard_data["algorithm"] = self.selected_algorithm
            # Notify parent that algorithm is selected (for enabling continue button)
            if hasattr(self, "on_validation_changed"):
                self.on_validation_changed()


    @staticmethod
    def _algorithm_registry() -> dict:
        """Return algorithm registry (kept for compatibility)."""
        return {
            "MotionDetection": {
                "label": "Motion Detection",
            },
            "ColorDetection": {
                "label": "Color Detection",
            },
            "ColorAnomalyAndMotionDetection": {
                "label": "Color Anomaly & Motion Detection",
            },
        }
