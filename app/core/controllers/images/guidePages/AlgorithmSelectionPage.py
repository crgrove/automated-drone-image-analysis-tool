"""
Algorithm Selection page for the Image Analysis Guide wizard.
"""

from .BasePage import BasePage


class AlgorithmSelectionPage(BasePage):
    """Page for algorithm selection via decision tree."""
    
    def __init__(self, wizard_data, settings_service, dialog):
        """Initialize the page."""
        super().__init__(wizard_data, settings_service, dialog)
        # Algorithm selection state
        self.algorithm_decision_state = {
            'thermal': None,
            'temperature_range': None,
            'person_only': None,
            'specific_color': None,
            'direct_color_control': None,
            'consistent_lighting': None,
            'complex_background': None
        }
        self.selected_algorithm = None
    
    def setup_ui(self):
        """Initialize UI components."""
        self._reset_algorithm_selection()
    
    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.dialog.buttonYes.clicked.connect(lambda: self._on_algorithm_button_clicked(True))
        self.dialog.buttonNo.clicked.connect(lambda: self._on_algorithm_button_clicked(False))
        self.dialog.resetAlgorithmButton.clicked.connect(self._on_reset_algorithm_clicked)
    
    def load_data(self):
        """Load algorithm selection if available."""
        # Algorithm selection starts fresh each time
        pass
    
    def validate(self) -> bool:
        """Validate that an algorithm is selected."""
        return self.selected_algorithm is not None
    
    def save_data(self):
        """Save selected algorithm to wizard_data."""
        self.wizard_data['algorithm'] = self.selected_algorithm
    
    def on_enter(self):
        """Called when entering the page."""
        # Reset if no algorithm selected
        if not self.selected_algorithm:
            self._reset_algorithm_selection()
    
    def on_exit(self):
        """Called when leaving the page."""
        # Save algorithm selection
        if self.selected_algorithm:
            self.wizard_data['algorithm'] = self.selected_algorithm
    
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
            'thermal': None,
            'temperature_range': None,
            'person_only': None,
            'specific_color': None,
            'direct_color_control': None,
            'consistent_lighting': None,
            'complex_background': None
        }
        self.selected_algorithm = None
        self.dialog.labelCurrentQuestion.setText("Are you using thermal images?")
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
        
        if state['thermal'] is None:
            state['thermal'] = answer
            if answer:  # Yes - thermal
                self.dialog.labelCurrentQuestion.setText("Are you looking for anomalies within a specific temperature range?")
            else:  # No - not thermal
                self.dialog.labelCurrentQuestion.setText("Do you specifically want to detect people?")
        
        elif state['thermal'] and state['temperature_range'] is None:
            state['temperature_range'] = answer
            if answer:  # Yes - temperature range
                self.selected_algorithm = "Temperature Range"
                self._show_algorithm_result()
            else:  # No - temperature anomaly
                self.selected_algorithm = "Temperature Anomaly"
                self._show_algorithm_result()
        
        elif not state['thermal'] and state['person_only'] is None:
            state['person_only'] = answer
            if answer:  # Yes - person only
                self.selected_algorithm = "AI Person Detector"
                self._show_algorithm_result()
            else:  # No - not person only
                self.dialog.labelCurrentQuestion.setText("Are you trying to find a specific color?")
        
        elif not state['thermal'] and not state['person_only'] and state['specific_color'] is None:
            state['specific_color'] = answer
            if answer:  # Yes - specific color
                self.dialog.labelCurrentQuestion.setText("Do you want to manually adjust the color range?")
            else:  # No - not specific color
                self.dialog.labelCurrentQuestion.setText("Do your images contain complex backgrounds or structures?")
        
        elif state['specific_color'] and state['direct_color_control'] is None:
            state['direct_color_control'] = answer
            if answer:  # Yes - direct control
                self.dialog.labelCurrentQuestion.setText("Do your images include shadows or areas with uneven lighting?")
            else:  # No - matched filter
                self.selected_algorithm = "Matched Filter"
                self._show_algorithm_result()
        
        elif state['direct_color_control'] and state['consistent_lighting'] is None:
            state['consistent_lighting'] = answer
            if answer:  # Yes - RGB
                self.selected_algorithm = "Color Range (HSV)"
            else:  # No - HSV
                self.selected_algorithm = "Color Range (RGB)"
            self._show_algorithm_result()
        
        elif not state['specific_color'] and state['complex_background'] is None:
            state['complex_background'] = answer
            if answer:  # Yes - complex
                self.selected_algorithm = "MRMap Algorithm"
            else:  # No - simple
                self.selected_algorithm = "RX Anomaly"
            self._show_algorithm_result()
    
    def _show_algorithm_result(self):
        """Display the selected algorithm result."""
        if self.selected_algorithm:
            self.dialog.labelAlgorithmResult.setText(f"Selected Algorithm: {self.selected_algorithm}")
            self.dialog.labelAlgorithmResult.setVisible(True)
            self.dialog.buttonYes.setVisible(False)
            self.dialog.buttonNo.setVisible(False)
            self.wizard_data['algorithm'] = self.selected_algorithm
            # Notify parent that algorithm is selected (for enabling continue button)
            if hasattr(self, 'on_algorithm_selected'):
                self.on_algorithm_selected()

