from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtGui import QFont, QColor

from core.views.images.ImageAnalysisGuide_ui import Ui_ImageAnalysisGuide
from core.services.SettingsService import SettingsService
from core.controllers.images.guidePages import (
    ReviewOrNewPage,
    DirectoriesPage,
    ImageCapturePage,
    TargetSizePage,
    AlgorithmSelectionPage,
    AlgorithmParametersPage,
    GeneralSettingsPage
)


class ImageAnalysisGuide(QDialog, Ui_ImageAnalysisGuide):
    """Wizard dialog for initial setup and configuration of ADIAT.

    Provides a multi-page wizard interface for configuring image analysis
    parameters including directories, image capture settings, target size,
    algorithm selection, algorithm parameters, and general settings.

    Attributes:
        wizardCompleted: Signal emitted when wizard is completed. Emits a dict
            containing all wizard configuration data.
        settings_service: Instance of SettingsService for accessing settings.
        current_page: Current page index (0-based).
        total_pages: Total number of pages in the wizard.
        wizard_data: Dictionary containing all wizard configuration data.
        pages: List of page instances for each wizard step.
    """

    wizardCompleted = Signal(dict)  # Emits wizard data when completed
    reviewRequested = Signal(str)  # Emits XML file path when review is requested

    def __init__(self, parent=None):
        """Initialize the Image Analysis Guide wizard.

        Args:
            parent: Parent widget for the dialog.
        """
        super().__init__(parent)
        self.setupUi(self)

        self.settings_service = SettingsService()
        self.current_page = 0
        self.total_pages = 7  # Review/New, Directories, Image Capture, Target Size, Algorithm, Algorithm Parameters, General Settings

        # Create or bind to algorithm parameters page
        self._create_algorithm_parameters_page()

        # Wizard data
        self.wizard_data = {
            'review_mode': None,  # 'review' or 'new'
            'review_file_path': None,  # Path to ADIAT_Data.xml file
            'input_directory': '',
            'output_directory': '',
            'drone': None,  # Selected drone row (single sensor)
            'drone_sensors': [],  # All sensor configurations for selected camera
            'altitude': 100,
            'altitude_unit': 'ft',
            'gsd': None,
            'gsd_list': [],  # List of GSD values for all sensors
            'object_size_min': 1,
            'object_size_max': 6,
            'algorithm': None,
            'identifier_color': QColor(0, 255, 0),  # Default green
            'max_processes': 4,
            'normalize_histogram': False,
            'skip_future': False,
            'first_image_path': None,  # Path to first image for metadata extraction
            'processing_resolution': '50%'  # Default processing resolution
        }

        # Create page instances (ReviewOrNewPage is first)
        self.pages = [
            ReviewOrNewPage(self.wizard_data, self.settings_service, self),
            DirectoriesPage(self.wizard_data, self.settings_service, self),
            ImageCapturePage(self.wizard_data, self.settings_service, self),
            TargetSizePage(self.wizard_data, self.settings_service, self),
            AlgorithmSelectionPage(self.wizard_data, self.settings_service, self),
            AlgorithmParametersPage(self.wizard_data, self.settings_service, self),
            GeneralSettingsPage(self.wizard_data, self.settings_service, self)
        ]

        # Set up callbacks for page interactions
        self.pages[0].on_validation_changed = self._update_navigation_buttons
        self.pages[1].on_input_directory_changed = lambda: self.pages[2].scan_input_directory()
        self.pages[1].on_validation_changed = self._update_navigation_buttons
        self.pages[4].on_algorithm_selected = self._on_algorithm_selected

        # Initialize pages
        for page in self.pages:
            page.setup_ui()
            page.connect_signals()
            page.load_data()

        # Set window title
        self.setWindowTitle("ADIAT Image Analysis Guide")

        # Connect navigation signals
        self.continueButton.clicked.connect(self._on_continue)
        self.backButton.clicked.connect(self._on_back)
        self.cancelButton.clicked.connect(self.reject)

        # Initially disable continue button until directories are set
        self._update_navigation_buttons()

    def _on_algorithm_selected(self):
        """Handle algorithm selection - enable continue button.

        Called when an algorithm is selected on the algorithm selection page.
        Updates navigation buttons to reflect the new selection state.
        """
        if self.current_page == 4:  # AlgorithmSelectionPage is now at index 4
            self._update_navigation_buttons()

    def _create_algorithm_parameters_page(self):
        """Create the algorithm parameters page UI programmatically.

        Creates the algorithm parameters page widget if it doesn't exist in the
        .ui file. This provides backward compatibility for UI files that may not
        include this page.
        """
        # If the page already exists in the .ui, bind to it and return
        existing_page = self.stackedWidget.findChild(QWidget, "pageAlgorithmParameters")
        if existing_page is not None:
            self.pageAlgorithmParameters = existing_page
            self.algorithmParametersContainer = self.pageAlgorithmParameters.findChild(QWidget, "algorithmParametersContainer")
            return

        # Otherwise create it programmatically (backward compatibility)
        self.pageAlgorithmParameters = QWidget()
        self.pageAlgorithmParameters.setObjectName("pageAlgorithmParameters")
        vertical_layout = QVBoxLayout(self.pageAlgorithmParameters)
        vertical_layout.setObjectName("verticalLayout_algorithmParameters")
        vertical_layout.setContentsMargins(-1, 5, -1, -1)
        title_label = QLabel(self.pageAlgorithmParameters)
        title_label.setObjectName("labelPage5Title_AlgorithmParameters")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setText("Algorithm Parameters")
        vertical_layout.addWidget(title_label)
        line = QFrame(self.pageAlgorithmParameters)
        line.setObjectName("line_algorithmParameters")
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        vertical_layout.addWidget(line)
        self.algorithmParametersContainer = QWidget(self.pageAlgorithmParameters)
        self.algorithmParametersContainer.setObjectName("algorithmParametersContainer")
        vertical_layout.addWidget(self.algorithmParametersContainer)
        # Note: pageAlgorithmParameters is already in the .ui file, so we don't need to insert it
        # The .ui file should have it at the correct index (5, after ReviewOrNew, Directories, ImageCapture, TargetSize, AlgorithmSelection)

    def _on_continue(self):
        """Handle continue button click.

        Saves current page data, validates it, and either moves to the next
        page or completes the wizard if on the last page.
        """
        # Save current page data
        if self.current_page < len(self.pages):
            self.pages[self.current_page].save_data()

        # Check if we're on the review page and review mode is selected
        if self.current_page == 0 and self.wizard_data.get('review_mode') == 'review':
            # Validate that file is selected
            if not self.pages[0].validate():
                return  # Don't proceed if validation fails
            
            # Emit review signal and close wizard
            review_file = self.wizard_data.get('review_file_path')
            if review_file:
                self.reviewRequested.emit(review_file)
                self.accept()
            return

        # Validate current page
        if self.current_page < len(self.pages):
            if not self.pages[self.current_page].validate():
                return  # Don't proceed if validation fails

        # Move to next page or complete
        if self.current_page < self.total_pages - 1:
            # Exit current page
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_exit()

            self.current_page += 1
            self.stackedWidget.setCurrentIndex(self.current_page)

            # Enter new page
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_enter()

            self._update_navigation_buttons()
            
            # Set focus to an appropriate widget on the new page (not the close button)
            self._set_focus_on_page()
        else:
            # Last page - complete wizard
            self._complete_wizard()

    def _on_back(self):
        """Handle back button click.

        Saves current page data, exits the current page, and navigates to the
        previous page if not on the first page.
        """
        if self.current_page > 0:
            # Exit current page
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_exit()
                self.pages[self.current_page].save_data()

            self.current_page -= 1
            self.stackedWidget.setCurrentIndex(self.current_page)

            # Enter previous page
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_enter()

            self._update_navigation_buttons()

    def _set_focus_on_page(self):
        """Set focus to an appropriate widget on the current page."""
        if self.current_page == 1:  # DirectoriesPage
            # Focus on the first input directory button or line edit
            if hasattr(self, 'inputDirectoryButton'):
                self.inputDirectoryButton.setFocus()
        elif self.current_page == 2:  # ImageCapturePage
            # Focus on the drone combo box
            if hasattr(self, 'droneComboBox'):
                self.droneComboBox.setFocus()
        # For other pages, let Qt handle default focus
        # This prevents the Close button from getting focus

    def _update_navigation_buttons(self):
        """Update navigation button states.

        Enables/disables the back and continue buttons based on the current
        page and validation state. Changes continue button text to "Start
        Processing" on the last page.
        """
        self.backButton.setEnabled(self.current_page > 0)

        # Special handling for first page (ReviewOrNewPage)
        if self.current_page == 0:
            review_mode = self.wizard_data.get('review_mode')
            if review_mode == 'review':
                # Show "Load Results" button when review file is selected
                self.continueButton.setText("Load Results")
                can_continue = self.pages[0].validate()
                self.continueButton.setEnabled(can_continue)
            elif review_mode == 'new':
                # New analysis was selected, enable continue button
                self.continueButton.setText("Continue")
                can_continue = self.pages[0].validate()
                self.continueButton.setEnabled(can_continue)
            else:
                # No selection yet
                self.continueButton.setText("Continue")
                self.continueButton.setEnabled(False)
        elif self.current_page == self.total_pages - 1:
            self.continueButton.setText("Start Processing")
            self.continueButton.setEnabled(True)  # Always enable on last page
        else:
            self.continueButton.setText("Continue")
            # Validate current page to determine if continue should be enabled
            if self.current_page < len(self.pages):
                can_continue = self.pages[self.current_page].validate()
                self.continueButton.setEnabled(can_continue)
            else:
                self.continueButton.setEnabled(True)

    def _complete_wizard(self):
        """Complete the wizard and save settings.

        Saves all page data, persists settings to SettingsService, and emits
        the wizardCompleted signal with the collected wizard data before
        accepting the dialog.
        """
        # Save all page data
        for page in self.pages:
            page.save_data()

        # Save skip preference (from GeneralSettingsPage)
        # This is already saved via signal handler, but ensure it's saved here too
        skip_value = 'Yes' if self.skipCheckBox.isChecked() else 'No'
        self.settings_service.set_setting('SkipImageAnalysisGuide', skip_value)

        # Save wizard data to settings
        if self.wizard_data['drone'] is not None:
            # Save drone selection (could save model name)
            pass

        # Save altitude unit preference
        self.settings_service.set_setting('DistanceUnit', self.wizard_data['altitude_unit'])

        # Save max processes
        self.settings_service.set_setting('MaxProcesses', str(self.wizard_data['max_processes']))

        # Save normalize histogram
        normalize = 'Yes' if self.wizard_data['normalize_histogram'] else 'No'
        self.settings_service.set_setting('NormalizeHistogram', normalize)

        # Save identifier color
        color = self.wizard_data['identifier_color']
        color_str = f"{color.red()},{color.green()},{color.blue()}"
        self.settings_service.set_setting('IdentifierColor', color_str)

        # Save processing resolution
        if self.wizard_data.get('processing_resolution'):
            self.settings_service.set_setting('ProcessingResolution', self.wizard_data['processing_resolution'])

        # Emit signal with wizard data
        self.wizardCompleted.emit(self.wizard_data)

        # Accept dialog
        self.accept()

    def reject(self) -> None:
        """Handle Close/Cancel. Persist skip preference before closing.

        Overrides QDialog.reject() to save the skip wizard preference before
        closing the dialog, ensuring user preferences are preserved even if
        the wizard is cancelled.
        """
        try:
            # Save skip preference (from GeneralSettingsPage)
            skip_value = 'Yes' if self.skipCheckBox.isChecked() else 'No'
            self.settings_service.set_setting('SkipImageAnalysisGuide', skip_value)
        finally:
            super().reject()
