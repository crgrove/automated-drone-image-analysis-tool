# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RectilinearShape.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QGridLayout, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

class Ui_RectilinearShape(object):
    def setupUi(self, RectilinearShape):
        if not RectilinearShape.objectName():
            RectilinearShape.setObjectName(u"RectilinearShape")
        RectilinearShape.resize(760, 190)
        self.verticalLayout = QVBoxLayout(RectilinearShape)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_options = QHBoxLayout()
        self.horizontalLayout_options.setObjectName(u"horizontalLayout_options")
        self.optionsGridLayout = QGridLayout()
        self.optionsGridLayout.setObjectName(u"optionsGridLayout")
        self.optionsGridLayout.setHorizontalSpacing(6)
        self.optionsGridLayout.setVerticalSpacing(4)
        self.targetLabel = QLabel(RectilinearShape)
        self.targetLabel.setObjectName(u"targetLabel")
        font = QFont()
        font.setPointSize(10)
        self.targetLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.targetLabel, 0, 0, 1, 1)

        self.presetComboBox = QComboBox(RectilinearShape)
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.setObjectName(u"presetComboBox")
        self.presetComboBox.setFont(font)

        self.optionsGridLayout.addWidget(self.presetComboBox, 0, 1, 1, 3)

        self.gridSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.optionsGridLayout.addItem(self.gridSpacer, 0, 4, 1, 1)

        self.longSideLabel = QLabel(RectilinearShape)
        self.longSideLabel.setObjectName(u"longSideLabel")
        self.longSideLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.longSideLabel, 1, 0, 1, 1)

        self.longMinSpinBox = QDoubleSpinBox(RectilinearShape)
        self.longMinSpinBox.setObjectName(u"longMinSpinBox")
        self.longMinSpinBox.setFont(font)
        self.longMinSpinBox.setDecimals(1)
        self.longMinSpinBox.setMinimum(1.000000000000000)
        self.longMinSpinBox.setMaximum(2000.000000000000000)
        self.longMinSpinBox.setSingleStep(1.000000000000000)
        self.longMinSpinBox.setValue(35.000000000000000)

        self.optionsGridLayout.addWidget(self.longMinSpinBox, 1, 1, 1, 1)

        self.longToLabel = QLabel(RectilinearShape)
        self.longToLabel.setObjectName(u"longToLabel")
        self.longToLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.longToLabel, 1, 2, 1, 1)

        self.longMaxSpinBox = QDoubleSpinBox(RectilinearShape)
        self.longMaxSpinBox.setObjectName(u"longMaxSpinBox")
        self.longMaxSpinBox.setFont(font)
        self.longMaxSpinBox.setDecimals(1)
        self.longMaxSpinBox.setMinimum(1.000000000000000)
        self.longMaxSpinBox.setMaximum(2000.000000000000000)
        self.longMaxSpinBox.setSingleStep(1.000000000000000)
        self.longMaxSpinBox.setValue(80.000000000000000)

        self.optionsGridLayout.addWidget(self.longMaxSpinBox, 1, 3, 1, 1)

        self.shortSideLabel = QLabel(RectilinearShape)
        self.shortSideLabel.setObjectName(u"shortSideLabel")
        self.shortSideLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.shortSideLabel, 2, 0, 1, 1)

        self.shortMinSpinBox = QDoubleSpinBox(RectilinearShape)
        self.shortMinSpinBox.setObjectName(u"shortMinSpinBox")
        self.shortMinSpinBox.setFont(font)
        self.shortMinSpinBox.setDecimals(1)
        self.shortMinSpinBox.setMinimum(1.000000000000000)
        self.shortMinSpinBox.setMaximum(2000.000000000000000)
        self.shortMinSpinBox.setSingleStep(1.000000000000000)
        self.shortMinSpinBox.setValue(20.000000000000000)

        self.optionsGridLayout.addWidget(self.shortMinSpinBox, 2, 1, 1, 1)

        self.shortToLabel = QLabel(RectilinearShape)
        self.shortToLabel.setObjectName(u"shortToLabel")
        self.shortToLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.shortToLabel, 2, 2, 1, 1)

        self.shortMaxSpinBox = QDoubleSpinBox(RectilinearShape)
        self.shortMaxSpinBox.setObjectName(u"shortMaxSpinBox")
        self.shortMaxSpinBox.setFont(font)
        self.shortMaxSpinBox.setDecimals(1)
        self.shortMaxSpinBox.setMinimum(1.000000000000000)
        self.shortMaxSpinBox.setMaximum(2000.000000000000000)
        self.shortMaxSpinBox.setSingleStep(1.000000000000000)
        self.shortMaxSpinBox.setValue(55.000000000000000)

        self.optionsGridLayout.addWidget(self.shortMaxSpinBox, 2, 3, 1, 1)

        self.minConfidenceLabel = QLabel(RectilinearShape)
        self.minConfidenceLabel.setObjectName(u"minConfidenceLabel")
        self.minConfidenceLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.minConfidenceLabel, 0, 5, 1, 1)

        self.minConfidenceSpinBox = QDoubleSpinBox(RectilinearShape)
        self.minConfidenceSpinBox.setObjectName(u"minConfidenceSpinBox")
        self.minConfidenceSpinBox.setFont(font)
        self.minConfidenceSpinBox.setDecimals(0)
        self.minConfidenceSpinBox.setMinimum(0.000000000000000)
        self.minConfidenceSpinBox.setMaximum(100.000000000000000)
        self.minConfidenceSpinBox.setSingleStep(5.000000000000000)
        self.minConfidenceSpinBox.setValue(50.000000000000000)

        self.optionsGridLayout.addWidget(self.minConfidenceSpinBox, 0, 6, 1, 1)

        self.maxDetectionsLabel = QLabel(RectilinearShape)
        self.maxDetectionsLabel.setObjectName(u"maxDetectionsLabel")
        self.maxDetectionsLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.maxDetectionsLabel, 1, 5, 1, 1)

        self.maxDetectionsSpinBox = QSpinBox(RectilinearShape)
        self.maxDetectionsSpinBox.setObjectName(u"maxDetectionsSpinBox")
        self.maxDetectionsSpinBox.setFont(font)
        self.maxDetectionsSpinBox.setMinimum(1)
        self.maxDetectionsSpinBox.setMaximum(500)
        self.maxDetectionsSpinBox.setValue(25)

        self.optionsGridLayout.addWidget(self.maxDetectionsSpinBox, 1, 6, 1, 1)

        self.sizeToleranceLabel = QLabel(RectilinearShape)
        self.sizeToleranceLabel.setObjectName(u"sizeToleranceLabel")
        self.sizeToleranceLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.sizeToleranceLabel, 2, 5, 1, 1)

        self.sizeToleranceSpinBox = QSpinBox(RectilinearShape)
        self.sizeToleranceSpinBox.setObjectName(u"sizeToleranceSpinBox")
        self.sizeToleranceSpinBox.setFont(font)
        self.sizeToleranceSpinBox.setMinimum(0)
        self.sizeToleranceSpinBox.setMaximum(100)
        self.sizeToleranceSpinBox.setValue(20)

        self.optionsGridLayout.addWidget(self.sizeToleranceSpinBox, 2, 6, 1, 1)

        self.angleToleranceLabel = QLabel(RectilinearShape)
        self.angleToleranceLabel.setObjectName(u"angleToleranceLabel")
        self.angleToleranceLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.angleToleranceLabel, 3, 0, 1, 1)

        self.angleToleranceSpinBox = QDoubleSpinBox(RectilinearShape)
        self.angleToleranceSpinBox.setObjectName(u"angleToleranceSpinBox")
        self.angleToleranceSpinBox.setFont(font)
        self.angleToleranceSpinBox.setDecimals(1)
        self.angleToleranceSpinBox.setMinimum(1.000000000000000)
        self.angleToleranceSpinBox.setMaximum(30.000000000000000)
        self.angleToleranceSpinBox.setSingleStep(1.000000000000000)
        self.angleToleranceSpinBox.setValue(12.000000000000000)

        self.optionsGridLayout.addWidget(self.angleToleranceSpinBox, 3, 1, 1, 1)

        self.edgeContrastLabel = QLabel(RectilinearShape)
        self.edgeContrastLabel.setObjectName(u"edgeContrastLabel")
        self.edgeContrastLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.edgeContrastLabel, 3, 2, 1, 1)

        self.edgeContrastSpinBox = QDoubleSpinBox(RectilinearShape)
        self.edgeContrastSpinBox.setObjectName(u"edgeContrastSpinBox")
        self.edgeContrastSpinBox.setFont(font)
        self.edgeContrastSpinBox.setDecimals(1)
        self.edgeContrastSpinBox.setMinimum(1.000000000000000)
        self.edgeContrastSpinBox.setMaximum(100.000000000000000)
        self.edgeContrastSpinBox.setSingleStep(1.000000000000000)
        self.edgeContrastSpinBox.setValue(10.000000000000000)

        self.optionsGridLayout.addWidget(self.edgeContrastSpinBox, 3, 3, 1, 1)

        self.edgeSupportLabel = QLabel(RectilinearShape)
        self.edgeSupportLabel.setObjectName(u"edgeSupportLabel")
        self.edgeSupportLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.edgeSupportLabel, 3, 5, 1, 1)

        self.edgeSupportSpinBox = QDoubleSpinBox(RectilinearShape)
        self.edgeSupportSpinBox.setObjectName(u"edgeSupportSpinBox")
        self.edgeSupportSpinBox.setFont(font)
        self.edgeSupportSpinBox.setDecimals(2)
        self.edgeSupportSpinBox.setMinimum(0.050000000000000)
        self.edgeSupportSpinBox.setMaximum(1.000000000000000)
        self.edgeSupportSpinBox.setSingleStep(0.050000000000000)
        self.edgeSupportSpinBox.setValue(0.450000000000000)

        self.optionsGridLayout.addWidget(self.edgeSupportSpinBox, 3, 6, 1, 1)

        self.minBoxinessLabel = QLabel(RectilinearShape)
        self.minBoxinessLabel.setObjectName(u"minBoxinessLabel")
        self.minBoxinessLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.minBoxinessLabel, 4, 0, 1, 1)

        self.minBoxinessSpinBox = QDoubleSpinBox(RectilinearShape)
        self.minBoxinessSpinBox.setObjectName(u"minBoxinessSpinBox")
        self.minBoxinessSpinBox.setFont(font)
        self.minBoxinessSpinBox.setDecimals(2)
        self.minBoxinessSpinBox.setMinimum(0.050000000000000)
        self.minBoxinessSpinBox.setMaximum(1.000000000000000)
        self.minBoxinessSpinBox.setSingleStep(0.050000000000000)
        self.minBoxinessSpinBox.setValue(0.350000000000000)

        self.optionsGridLayout.addWidget(self.minBoxinessSpinBox, 4, 1, 1, 1)

        self.minShortSideLabel = QLabel(RectilinearShape)
        self.minShortSideLabel.setObjectName(u"minShortSideLabel")
        self.minShortSideLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.minShortSideLabel, 4, 2, 1, 1)

        self.minShortSideSpinBox = QSpinBox(RectilinearShape)
        self.minShortSideSpinBox.setObjectName(u"minShortSideSpinBox")
        self.minShortSideSpinBox.setFont(font)
        self.minShortSideSpinBox.setMinimum(4)
        self.minShortSideSpinBox.setMaximum(200)
        self.minShortSideSpinBox.setValue(12)

        self.optionsGridLayout.addWidget(self.minShortSideSpinBox, 4, 3, 1, 1)

        self.fallbackGsdLabel = QLabel(RectilinearShape)
        self.fallbackGsdLabel.setObjectName(u"fallbackGsdLabel")
        self.fallbackGsdLabel.setFont(font)

        self.optionsGridLayout.addWidget(self.fallbackGsdLabel, 4, 5, 1, 1)

        self.fallbackGsdSpinBox = QDoubleSpinBox(RectilinearShape)
        self.fallbackGsdSpinBox.setObjectName(u"fallbackGsdSpinBox")
        self.fallbackGsdSpinBox.setFont(font)
        self.fallbackGsdSpinBox.setDecimals(2)
        self.fallbackGsdSpinBox.setMinimum(0.000000000000000)
        self.fallbackGsdSpinBox.setMaximum(50.000000000000000)
        self.fallbackGsdSpinBox.setSingleStep(0.100000000000000)
        self.fallbackGsdSpinBox.setValue(0.000000000000000)

        self.optionsGridLayout.addWidget(self.fallbackGsdSpinBox, 4, 6, 1, 1)

        self.useBoxinessCheckBox = QCheckBox(RectilinearShape)
        self.useBoxinessCheckBox.setObjectName(u"useBoxinessCheckBox")
        self.useBoxinessCheckBox.setFont(font)
        self.useBoxinessCheckBox.setChecked(True)

        self.optionsGridLayout.addWidget(self.useBoxinessCheckBox, 5, 0, 1, 2)

        self.debugOutputCheckBox = QCheckBox(RectilinearShape)
        self.debugOutputCheckBox.setObjectName(u"debugOutputCheckBox")
        self.debugOutputCheckBox.setFont(font)
        self.debugOutputCheckBox.setChecked(False)

        self.optionsGridLayout.addWidget(self.debugOutputCheckBox, 5, 2, 1, 3)


        self.horizontalLayout_options.addLayout(self.optionsGridLayout)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_options.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_options)


        self.retranslateUi(RectilinearShape)

        QMetaObject.connectSlotsByName(RectilinearShape)
    # setupUi

    def retranslateUi(self, RectilinearShape):
        RectilinearShape.setWindowTitle(QCoreApplication.translate("RectilinearShape", u"Form", None))
#if QT_CONFIG(tooltip)
        self.targetLabel.setToolTip(QCoreApplication.translate("RectilinearShape", u"The kind of object to search for. Each preset sets the expected top-down size range;\n"
"choose Custom size to enter your own. Detection is driven by size and straight edges,\n"
"not colour, so it works for black, grey or earth-toned targets.", None))
#endif // QT_CONFIG(tooltip)
        self.targetLabel.setText(QCoreApplication.translate("RectilinearShape", u"Target Type:", None))
        self.presetComboBox.setItemText(0, QCoreApplication.translate("RectilinearShape", u"Suitcase (any orientation)", None))
        self.presetComboBox.setItemText(1, QCoreApplication.translate("RectilinearShape", u"Suitcase (lying flat)", None))
        self.presetComboBox.setItemText(2, QCoreApplication.translate("RectilinearShape", u"Cooler or box", None))
        self.presetComboBox.setItemText(3, QCoreApplication.translate("RectilinearShape", u"Small tent", None))
        self.presetComboBox.setItemText(4, QCoreApplication.translate("RectilinearShape", u"Custom size", None))

#if QT_CONFIG(tooltip)
        self.presetComboBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"The kind of object to search for. Each preset sets the expected top-down size range;\n"
"choose Custom size to enter your own. Detection is driven by size and straight edges,\n"
"not colour, so it works for black, grey or earth-toned targets.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.longSideLabel.setToolTip(QCoreApplication.translate("RectilinearShape", u"Expected length of the longer side of the target, seen from directly above.", None))
#endif // QT_CONFIG(tooltip)
        self.longSideLabel.setText(QCoreApplication.translate("RectilinearShape", u"Long Side:", None))
#if QT_CONFIG(tooltip)
        self.longMinSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Shortest expected long side.", None))
#endif // QT_CONFIG(tooltip)
        self.longToLabel.setText(QCoreApplication.translate("RectilinearShape", u"to", None))
#if QT_CONFIG(tooltip)
        self.longMaxSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Longest expected long side.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.shortSideLabel.setToolTip(QCoreApplication.translate("RectilinearShape", u"Expected length of the shorter side of the target, seen from directly above.", None))
#endif // QT_CONFIG(tooltip)
        self.shortSideLabel.setText(QCoreApplication.translate("RectilinearShape", u"Short Side:", None))
#if QT_CONFIG(tooltip)
        self.shortMinSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Shortest expected short side.", None))
#endif // QT_CONFIG(tooltip)
        self.shortToLabel.setText(QCoreApplication.translate("RectilinearShape", u"to", None))
#if QT_CONFIG(tooltip)
        self.shortMaxSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Longest expected short side.", None))
#endif // QT_CONFIG(tooltip)
        self.minConfidenceLabel.setText(QCoreApplication.translate("RectilinearShape", u"Min Confidence:", None))
#if QT_CONFIG(tooltip)
        self.minConfidenceSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Only shapes scoring at least this confidence (0-100) become AOIs.\n"
"Raise if rock fields or talus produce many hits; lower to see weaker candidates.", None))
#endif // QT_CONFIG(tooltip)
        self.maxDetectionsLabel.setText(QCoreApplication.translate("RectilinearShape", u"Max Per Image:", None))
#if QT_CONFIG(tooltip)
        self.maxDetectionsSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"At most this many AOIs are kept per image, highest confidence first.\n"
"Protects reviewers from floods of hits in rocky or built-up terrain.", None))
#endif // QT_CONFIG(tooltip)
        self.sizeToleranceLabel.setText(QCoreApplication.translate("RectilinearShape", u"Size Tolerance:", None))
#if QT_CONFIG(tooltip)
        self.sizeToleranceSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"How far a shape may fall outside the size range before its score starts to drop.\n"
"Raise when altitude data is uncertain or the terrain is steep.", None))
#endif // QT_CONFIG(tooltip)
        self.sizeToleranceSpinBox.setSuffix(QCoreApplication.translate("RectilinearShape", u"%", None))
        self.angleToleranceLabel.setText(QCoreApplication.translate("RectilinearShape", u"Angle Tolerance:", None))
#if QT_CONFIG(tooltip)
        self.angleToleranceSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"How far from a right angle (or from parallel) two edges may be and still form a rectangle.\n"
"Raise for soft or sagging targets such as tents; lower to reject more natural clutter.", None))
#endif // QT_CONFIG(tooltip)
        self.angleToleranceSpinBox.setSuffix(QCoreApplication.translate("RectilinearShape", u"\u00b0", None))
        self.edgeContrastLabel.setText(QCoreApplication.translate("RectilinearShape", u"Edge Contrast:", None))
#if QT_CONFIG(tooltip)
        self.edgeContrastSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Minimum brightness step across an edge (0-255 scale).\n"
"Raise if grass, gravel or shadows produce many weak edges; lower for faded or dusty targets.", None))
#endif // QT_CONFIG(tooltip)
        self.edgeSupportLabel.setText(QCoreApplication.translate("RectilinearShape", u"Edge Support:", None))
#if QT_CONFIG(tooltip)
        self.edgeSupportSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Fraction of a candidate's outline that must lie on a real edge.\n"
"Lower for partly hidden or blurred targets; raise if rock fractures produce many hits.", None))
#endif // QT_CONFIG(tooltip)
        self.minBoxinessLabel.setText(QCoreApplication.translate("RectilinearShape", u"Min Boxiness:", None))
#if QT_CONFIG(tooltip)
        self.minBoxinessSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Threshold for candidates found from edge orientation alone, used when blur or low contrast\n"
"breaks the edges up. Raise if textured ground produces spurious hits.", None))
#endif // QT_CONFIG(tooltip)
        self.minShortSideLabel.setText(QCoreApplication.translate("RectilinearShape", u"Min Short Side:", None))
#if QT_CONFIG(tooltip)
        self.minShortSideSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Smallest target size, in processing pixels, worth searching for. Images where the target\n"
"would be smaller are skipped and logged - raise the processing resolution or fly lower.", None))
#endif // QT_CONFIG(tooltip)
        self.minShortSideSpinBox.setSuffix(QCoreApplication.translate("RectilinearShape", u" px", None))
        self.fallbackGsdLabel.setText(QCoreApplication.translate("RectilinearShape", u"Fallback GSD:", None))
#if QT_CONFIG(tooltip)
        self.fallbackGsdSpinBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Ground sample distance (cm per pixel at full resolution) to assume when an image has no usable\n"
"altitude or camera metadata. Leave at None to report such images as errors instead.", None))
#endif // QT_CONFIG(tooltip)
        self.fallbackGsdSpinBox.setSuffix(QCoreApplication.translate("RectilinearShape", u" cm/px", None))
        self.fallbackGsdSpinBox.setSpecialValueText(QCoreApplication.translate("RectilinearShape", u"None", None))
#if QT_CONFIG(tooltip)
        self.useBoxinessCheckBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Score candidates on how strongly two perpendicular edge directions dominate the area,\n"
"and use that to find targets whose edges are too broken up to trace.", None))
#endif // QT_CONFIG(tooltip)
        self.useBoxinessCheckBox.setText(QCoreApplication.translate("RectilinearShape", u"Use Boxiness", None))
#if QT_CONFIG(tooltip)
        self.debugOutputCheckBox.setToolTip(QCoreApplication.translate("RectilinearShape", u"Save an overlay per image (edges, candidates, boxiness heatmap) to a rectilinear_debug folder\n"
"in the output folder. Useful for tuning in new terrain; slows processing.", None))
#endif // QT_CONFIG(tooltip)
        self.debugOutputCheckBox.setText(QCoreApplication.translate("RectilinearShape", u"Write Debug Images", None))
    # retranslateUi

