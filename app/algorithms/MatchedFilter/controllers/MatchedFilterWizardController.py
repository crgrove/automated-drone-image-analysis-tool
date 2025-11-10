"""
Wizard controller for Matched Filter algorithm.

Provides a simplified, guided interface for configuring matched filter detection.
"""

from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QPushButton
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal

from algorithms.AlgorithmController import AlgorithmController
from algorithms.MatchedFilter.views.MatchedFilterWizard_ui import Ui_MatchedFilterWizard
from algorithms.MatchedFilter.views.MatchedFilterRowWizardWidget import MatchedFilterRowWizardWidget
from algorithms.MatchedFilter.controllers.MatchedFilterRangeViewerController import MatchedFilterRangeViewer
from algorithms.Shared.views.ColorSelectionMenu import ColorSelectionMenu
from helpers.IconHelper import IconHelper


class MatchedFilterWizardController(QWidget, Ui_MatchedFilterWizard, AlgorithmController):
    """Wizard controller for Matched Filter algorithm."""
    
    # Signal emitted when validation state changes (e.g., when rows are added/removed)
    validation_changed = Signal()
    
    def __init__(self, config, theme):
        """Initialize the wizard controller."""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme
        
        # List of target row widgets
        self.target_rows = []
        
        self.setupUi(self)
        self._wire_up_ui()
    
    def _wire_up_ui(self):
        """Attach custom widgets and set defaults."""
        # Empty state label
        self.emptyLabel = QLabel("No Targets Selected", self.targetsContainer)
        self.emptyLabel.setAlignment(Qt.AlignCenter)
        self.emptyLabel.setStyleSheet("color: #888; font-style: italic;")
        self.emptyLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.targetsLayout.addWidget(self.emptyLabel, 1, Qt.AlignCenter)
        
        # View Range button (hidden until targets are added)
        self.viewRangeButton = QPushButton("View Range", self.widgetAddButton)
        self.viewRangeButton.setFont(self.addTargetButton.font())
        self.viewRangeButton.setIcon(IconHelper.create_icon('fa6s.eye', self.theme))
        self.viewRangeButton.clicked.connect(self.view_range_button_clicked)
        self.viewRangeButton.hide()
        # Insert before the spacer
        self.horizontalLayout_add.insertWidget(1, self.viewRangeButton)
        
        # Common color selection menu (RGB mode for matched filter)
        self.color_selection_menu = ColorSelectionMenu(
            self,
            on_color_selected=self._on_color_selected_from_menu,
            get_default_qcolor=self._get_default_qcolor,
            mode='RGB'
        )
        self.color_selection_menu.attach_to(self.addTargetButton)
        
        # Update empty state visibility
        self._update_empty_state()
        self._update_view_range_button()
        self.validation_changed.emit()
        
        # Ensure an in-page widget has focus so the dialog Close button doesn't take it
        try:
            self.addTargetButton.setFocus(Qt.OtherFocusReason)
        except Exception:
            pass
    
    def _get_default_qcolor(self):
        """Return the most recent color or a sensible default."""
        if self.target_rows:
            return self.target_rows[-1].get_color()
        return QColor(255, 0, 0)
    
    def _on_color_selected_from_menu(self, color: QColor):
        """Handle color chosen from the shared color selection menu."""
        self.add_target_row(color)
    
    def add_target_row(self, color, aggressiveness_index=2):
        """
        Add a new target row widget.
        
        Args:
            color: QColor or tuple (r, g, b) for the target color
            aggressiveness_index: Aggressiveness preset index (0-4, default 2 = Moderate)
        """
        row = MatchedFilterRowWizardWidget(self.targetsContainer, color, aggressiveness_index)
        row.delete_requested.connect(self.remove_target_row)
        row.changed.connect(self._on_target_changed)
        
        self.target_rows.append(row)
        self.targetsLayout.addWidget(row, 0, Qt.AlignLeft)
        
        # Clear focus from Add Target button
        self.addTargetButton.clearFocus()
        
        self._update_empty_state()
        self._update_view_range_button()
        self.validation_changed.emit()
    
    def remove_target_row(self, row):
        """
        Remove a target row widget.
        
        Args:
            row: MatchedFilterRowWidget instance to remove
        """
        if self.target_rows:
            self.target_rows.remove(row)
            self.targetsLayout.removeWidget(row)
            row.deleteLater()
            
            self._update_empty_state()
            self._update_view_range_button()
    
    def _on_target_changed(self):
        """Handle when any target row changes."""
        pass  # Could add validation or other updates here
    
    def _update_empty_state(self):
        """Show a centered message when no targets are configured."""
        if self.target_rows:
            self.emptyLabel.hide()
        else:
            self.emptyLabel.show()
    
    def _update_view_range_button(self):
        """Show/hide view range button based on whether targets are configured."""
        if self.target_rows:
            self.viewRangeButton.show()
        else:
            self.viewRangeButton.hide()
    
    def view_range_button_clicked(self):
        """
        Handles the view range button click.
        
        Opens the View Range dialog, displaying detection regions for the
        currently configured matched-filter colors. For multiple colors,
        the viewer combines them (OR), matching the algorithm's behavior.
        """
        if not self.target_rows:
            return
            
        # Build color config list for viewer
        color_configs = []
        for row in self.target_rows:
            color_configs.append({
                'selected_color': row.get_rgb(),
                'match_filter_threshold': row.get_threshold()
            })
        
        rangeDialog = MatchedFilterRangeViewer(color_configs)
        rangeDialog.exec()
    
    def get_options(self):
        """Get algorithm options."""
        options = dict()
        
        if not self.target_rows:
            # Return empty/None values if no targets configured
            options['color_configs'] = []
            options['selected_color'] = None
            options['match_filter_threshold'] = None
            return options
        
        # New format (matches non-wizard controller): list of color configurations
        color_configs = []
        for row in self.target_rows:
            rgb = row.get_rgb()
            threshold = row.get_threshold()
            color_configs.append({
                'selected_color': rgb,
                'match_filter_threshold': threshold,
            })
        options['color_configs'] = color_configs
        
        # Legacy format: use first target for backward compatibility
        first_row = self.target_rows[0]
        options['selected_color'] = first_row.get_rgb()
        options['match_filter_threshold'] = first_row.get_threshold()
        
        return options
    
    def validate(self):
        """Validate configuration."""
        if not self.target_rows:
            return "Please add at least one target color to detect."
        return None
    
    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return
        
        from ast import literal_eval
        
        # Clear existing target rows
        for row in self.target_rows[:]:
            self.remove_target_row(row)
        
        # Try new format first
        if 'targets' in options and options['targets']:
            targets = options['targets']
            # Handle string format
            if isinstance(targets, str):
                targets = literal_eval(targets)
            
            for target_config in targets:
                if isinstance(target_config, dict):
                    target_color = target_config.get('target_color')
                    aggr_index = target_config.get('aggressiveness_index', 2)  # Default to Moderate
                    
                    if isinstance(target_color, str):
                        target_color = literal_eval(target_color)
                    
                    if target_color:
                        color = QColor(target_color[0], target_color[1], target_color[2])
                        self.add_target_row(color, aggr_index)
        
        # Fall back to legacy single-target format
        elif 'target_color' in options and options['target_color']:
            target_color = options['target_color']
            aggr_index = options.get('aggressiveness_index', 2)  # Default to Moderate
            
            if isinstance(target_color, str):
                target_color = literal_eval(target_color)
            
            if target_color:
                color = QColor(target_color[0], target_color[1], target_color[2])
                self.add_target_row(color, aggr_index)
        
        self._update_empty_state()
        self._update_view_range_button()
        # Note: validation_changed is already emitted by add_target_row/remove_target_row

