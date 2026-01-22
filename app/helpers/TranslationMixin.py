from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QAbstractButton, QComboBox, QGroupBox, QLabel, QTabWidget, QWidget


class TranslationMixin:
    """Shared translation helper using the class name as the context."""

    _translation_context = None

    @classmethod
    def _get_translation_context(cls) -> str:
        return cls._translation_context or cls.__name__

    def tr(self, text: str) -> str:
        """Translation method - named 'tr' so pyside6-lupdate can extract strings."""
        return QCoreApplication.translate(self._get_translation_context(), text)

    def _apply_translations(self) -> None:
        """Translate static widget text, titles, tooltips, and placeholders."""
        if not isinstance(self, QWidget):
            return

        for widget in self.findChildren(QWidget):
            window_title = widget.windowTitle()
            if window_title:
                widget.setWindowTitle(self.tr(window_title))

            if isinstance(widget, QAbstractButton):
                text = widget.text()
                if text:
                    widget.setText(self.tr(text))

            if isinstance(widget, QLabel):
                text = widget.text()
                if text:
                    widget.setText(self.tr(text))

            if isinstance(widget, QGroupBox):
                title = widget.title()
                if title:
                    widget.setTitle(self.tr(title))

            if isinstance(widget, QTabWidget):
                for idx in range(widget.count()):
                    tab_text = widget.tabText(idx)
                    if tab_text:
                        widget.setTabText(idx, self.tr(tab_text))

            if isinstance(widget, QComboBox):
                for idx in range(widget.count()):
                    item_text = widget.itemText(idx)
                    if item_text:
                        widget.setItemText(idx, self.tr(item_text))

            tooltip = widget.toolTip()
            if tooltip:
                widget.setToolTip(self.tr(tooltip))

            placeholder = getattr(widget, "placeholderText", None)
            if callable(placeholder):
                placeholder_text = widget.placeholderText()
                if placeholder_text:
                    widget.setPlaceholderText(self.tr(placeholder_text))
