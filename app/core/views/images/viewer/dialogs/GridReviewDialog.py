"""
GridReviewDialog - Settings dialog for the viewer's grid review mode.

Lets the reviewer pick the review grid size (rows x columns), toggle
auto-marking on advance, and apply a GSD-based suggestion sized so a
person remains comfortably visible when one cell fills the viewport.
Accepted values are persisted to QSettings as the defaults for images
that have no stored grid yet; images with a sweep already in progress
keep their own grid (stored in the result XML).
"""

from PySide6.QtWidgets import QDialog

from core.views.images.viewer.ui.GridReviewDialog_ui import Ui_GridReviewDialog
from helpers.TranslationMixin import TranslationMixin


class GridReviewDialog(TranslationMixin, QDialog, Ui_GridReviewDialog):
    """Dialog for grid review preferences and the GSD-based suggestion."""

    def __init__(self, parent=None, settings_service=None, current_rows=4,
                 current_cols=4, auto_mark=True, sub_guide=True,
                 suggestion=None, person_px=None):
        """Initialize the dialog.

        Args:
            parent: Parent widget.
            settings_service: SettingsService used to persist accepted values.
            current_rows: Grid rows preloaded into the spinbox.
            current_cols: Grid columns preloaded into the spinbox.
            auto_mark: Initial auto-mark checkbox state.
            sub_guide: Initial state of the in-cell 3x3 focus-guide toggle.
            suggestion: Optional (rows, cols) GSD-based suggestion.
            person_px: Optional on-screen person height (pixels) at cell
                zoom for the suggested grid, shown next to the suggestion.
        """
        super().__init__(parent)
        self.setupUi(self)
        self._apply_translations()
        self.settings_service = settings_service
        self._suggestion = suggestion

        self.rowsSpinBox.setValue(int(current_rows))
        self.colsSpinBox.setValue(int(current_cols))
        self.autoMarkCheckBox.setChecked(bool(auto_mark))
        self.subGuideCheckBox.setChecked(bool(sub_guide))

        if suggestion is not None:
            rows, cols = suggestion
            if person_px is not None:
                text = self.tr(
                    "Suggested: {rows}×{cols} (person ≈ {px} px on screen at cell zoom)"
                ).format(rows=rows, cols=cols, px=int(round(person_px)))
            else:
                text = self.tr("Suggested: {rows}×{cols}").format(rows=rows, cols=cols)
            self.suggestionLabel.setText(text)
            self.useSuggestionButton.setEnabled(True)
            self.useSuggestionButton.clicked.connect(self._use_suggestion)

    def _use_suggestion(self):
        """Copy the GSD-based suggestion into the spinboxes."""
        rows, cols = self._suggestion
        self.rowsSpinBox.setValue(rows)
        self.colsSpinBox.setValue(cols)

    def values(self):
        """Return the chosen (rows, cols, auto_mark)."""
        return (self.rowsSpinBox.value(), self.colsSpinBox.value(),
                self.autoMarkCheckBox.isChecked())

    def sub_guide_enabled(self):
        """Return the chosen focus-guide toggle state."""
        return self.subGuideCheckBox.isChecked()

    def apply_to_all(self):
        """Return True when the grid size should apply to every image.

        This is a one-shot action, not a saved preference, so it is not
        persisted; it always starts unchecked when the dialog opens.
        """
        return self.applyAllCheckBox.isChecked()

    def accept(self):
        """Persist the chosen values as defaults, then close."""
        if self.settings_service is not None:
            rows, cols, auto_mark = self.values()
            self.settings_service.set_setting('GridReviewRows', rows)
            self.settings_service.set_setting('GridReviewCols', cols)
            self.settings_service.set_setting('GridReviewAutoMark', auto_mark)
            self.settings_service.set_setting('GridReviewSubGuide', self.sub_guide_enabled())
        super().accept()
