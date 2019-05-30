import logging
from ast import literal_eval

from ..views.ColorMatch_ui import Ui_ColorMatch

from PyQt5.QtGui import QFontDatabase, QFont, QIcon, QColor
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale, QThread, pyqtSlot
from PyQt5.QtWidgets import QWidget,QApplication, QColorDialog, QMessageBox

from ...helpers.ColorUtils import ColorUtils

class ColorMatch(QWidget, Ui_ColorMatch):
    """Main Window."""

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.selectedColor = None
        self.colorButton.clicked.connect(self.colorButtonClicked)

        self.rRangeSpinBox.valueChanged.connect(self.updateColors)
        self.gRangeSpinBox.valueChanged.connect(self.updateColors)
        self.bRangeSpinBox.valueChanged.connect(self.updateColors)

    def colorButtonClicked(self):
        try:
            if self.selectedColor is not None:
                    self.selectedColor = QColorDialog().getColor(self.selectedColor)
            else:
                    self.selectedColor = QColorDialog().getColor()
            if self.selectedColor.isValid():
                self.updateColors();
        except Exception as e:
            logging.exception(e)

    def updateColors(self):
        if self.selectedColor is not None:
            rgb = [self.selectedColor.red(),self.selectedColor.green(),self.selectedColor.blue()]
            self.lowerColor, self.upperColor = ColorUtils.getColorRange(rgb, self.rRangeSpinBox.value(), self.gRangeSpinBox.value(), self.bRangeSpinBox.value())
            #Convert the RGB tuples to hex for CSS
            hex_lower = '#%02x%02x%02x' % self.lowerColor
            hex_upper = '#%02x%02x%02x' % self.upperColor
            self.min_color.setStyleSheet("background-color: "+hex_lower)
            self.mid_color.setStyleSheet("background-color: "+self.selectedColor.name())
            self.max_color.setStyleSheet("background-color: "+hex_upper)

    def getOptions(self):
        options = dict()
        options['color_range'] = [self.lowerColor, self.upperColor]
        options['selected_color'] = (self.selectedColor.red(),self.selectedColor.green(),self.selectedColor.blue())
        options['range_values']=(self.rRangeSpinBox.value(), self.gRangeSpinBox.value(), self.bRangeSpinBox.value())
        return options

    def validate(self):
        if self.selectedColor is None:
            return "Please select a search color."
        return None;

    def loadOptions(self, options):
        if 'range_values' in options and 'selected_color' in options:
            ranges = literal_eval(options['range_values'])
            self.rRangeSpinBox.setValue(ranges[0])
            self.gRangeSpinBox.setValue(ranges[1])
            self.bRangeSpinBox.setValue(ranges[2])
            selected_color = literal_eval(options['selected_color'])
            self.selectedColor = QColor(selected_color[0],selected_color[1],selected_color[2])
            self.updateColors()