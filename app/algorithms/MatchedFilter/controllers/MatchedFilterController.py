import logging
from ast import literal_eval

from algorithms.Algorithm import AlgorithmController
from algorithms.MatchedFilter.views.MatchedFilter_ui import Ui_MatchedFilter

from PyQt5.QtGui import QFontDatabase, QFont, QIcon, QColor
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale, QThread, pyqtSlot
from PyQt5.QtWidgets import QWidget,QApplication, QColorDialog, QMessageBox

from helpers.ColorUtils import ColorUtils

class MatchedFilter(QWidget, Ui_MatchedFilter, AlgorithmController):
    """Main Window."""

    def __init__(self):
        QWidget.__init__(self)
        AlgorithmController.__init__(self, 'MatchedFilter', 10)
        self.setupUi(self)
        self.selectedColor = None
        self.thresholdSlider.valueChanged.connect(self.updateThreshold)
        self.colorButton.clicked.connect(self.colorButtonClicked)

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
            self.colorSample.setStyleSheet("background-color: "+self.selectedColor.name())
    
    def updateThreshold(self):
        if self.thresholdSlider.value() == .1:
            self.thresholdValueLabel.setText('.1')
        elif self.thresholdSlider.value() == 10:
            self.thresholdValueLabel.setText('1')   
        else:
            self.thresholdValueLabel.setText("."+str(self.thresholdSlider.value()))
    
    def getOptions(self):
        options = dict()
        options['selected_color'] = (self.selectedColor.red(),self.selectedColor.green(),self.selectedColor.blue())
        options['match_filter_threshold'] = float(self.thresholdValueLabel.text())
        return options

    def validate(self):
        if self.selectedColor is None:
            return "Please select a search color."
        return None;

    def loadOptions(self, options):
        if 'selected_color' in options:
            selected_color = literal_eval(options['selected_color'])
            self.selectedColor = QColor(selected_color[0],selected_color[1],selected_color[2])
        if 'match_filter_threshold' in options:
            self.thresholdValueLabel.setText(str(options['match_filter_threshold']))
            self.thresholdSlider.setProperty("value", int(float(options['threshold'])*10))