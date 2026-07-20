# -*- coding: utf-8 -*-

"""
HSV Control Widget UI.

UI class for HSV color detection control widget with tabbed interface.
The tabs are created programmatically, but the base structure is defined here.
"""

from PySide6 import QtCore, QtGui, QtWidgets


class Ui_HSVControlWidget(object):
    """UI class for HSV Control Widget."""
    
    def setupUi(self, HSVControlWidget):
        """Setup UI with tab widget structure."""
        HSVControlWidget.setObjectName("HSVControlWidget")
        
        # Main layout
        self.mainLayout = QtWidgets.QVBoxLayout(HSVControlWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget (tabs will be added programmatically)
        self.tabs = QtWidgets.QTabWidget(HSVControlWidget)
        self.tabs.setObjectName("tabs")
        self.mainLayout.addWidget(self.tabs)
        
        # Tab placeholders (will be replaced programmatically)
        # Tab 1: Color Selection
        self.tab_color = QtWidgets.QWidget()
        self.tab_color.setObjectName("tab_color")
        self.tabs.addTab(self.tab_color, "")
        
        # Tab 2: Detection
        self.tab_detection = QtWidgets.QWidget()
        self.tab_detection.setObjectName("tab_detection")
        self.tabs.addTab(self.tab_detection, "")
        
        # Tab 3: Processing
        self.tab_processing = QtWidgets.QWidget()
        self.tab_processing.setObjectName("tab_processing")
        self.tabs.addTab(self.tab_processing, "")
        
        # Tab 4: Motion Detection
        self.tab_motion = QtWidgets.QWidget()
        self.tab_motion.setObjectName("tab_motion")
        self.tabs.addTab(self.tab_motion, "")
        
        # Tab 5: Fusion & Temporal
        self.tab_fusion = QtWidgets.QWidget()
        self.tab_fusion.setObjectName("tab_fusion")
        self.tabs.addTab(self.tab_fusion, "")
        
        # Tab 6: False Pos. Reduction
        self.tab_fpr = QtWidgets.QWidget()
        self.tab_fpr.setObjectName("tab_fpr")
        self.tabs.addTab(self.tab_fpr, "")
        
        # Tab 7: Rendering
        self.tab_rendering = QtWidgets.QWidget()
        self.tab_rendering.setObjectName("tab_rendering")
        self.tabs.addTab(self.tab_rendering, "")
        
        self.retranslateUi(HSVControlWidget)
        QtCore.QMetaObject.connectSlotsByName(HSVControlWidget)

    def retranslateUi(self, HSVControlWidget):
        """Translate UI strings."""
        _translate = QtCore.QCoreApplication.translate
        HSVControlWidget.setWindowTitle(_translate("HSVControlWidget", "HSVControlWidget"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_color), _translate("HSVControlWidget", "Color Selection"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_detection), _translate("HSVControlWidget", "Detection"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_processing), _translate("HSVControlWidget", "Processing"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_motion), _translate("HSVControlWidget", "Motion Detection"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_fusion), _translate("HSVControlWidget", "Fusion & Temporal"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_fpr), _translate("HSVControlWidget", "False Pos. Reduction"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_rendering), _translate("HSVControlWidget", "Rendering"))

