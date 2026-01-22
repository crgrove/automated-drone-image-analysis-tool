from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QAbstractButton, QComboBox, QGroupBox, QLabel, QTabWidget, QWidget


class TranslationMixin:
    """
    Mixin that provides translation support for any class.
    
    - For QObject subclasses: This tr() works alongside Qt's built-in tr()
    - For non-QObject classes: This provides the tr() method they need
    
    The tr() method is named to match Qt's convention so pyside6-lupdate
    can automatically extract strings.
    
    To override the translation context, set _translation_context in your class:
        class MyWidget(TranslationMixin, QWidget):
            _translation_context = "SharedContext"
    """

    _translation_context: str | None = None

    def tr(self, text: str) -> str:
        """Translate text using the class name (or override) as context."""
        context = self._translation_context or self.__class__.__name__
        return QCoreApplication.translate(context, text)

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
