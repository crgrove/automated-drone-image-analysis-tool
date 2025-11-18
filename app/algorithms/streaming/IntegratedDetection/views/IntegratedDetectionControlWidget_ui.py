# -*- coding: utf-8 -*-

"""
Integrated Detection Control Widget UI.

UI class for integrated detection control widget with tabbed interface.
The tabs are created programmatically, but the base structure is defined here.
"""

from PySide6 import QtCore, QtGui, QtWidgets


class Ui_IntegratedDetectionControlWidget(object):
    """UI class for Integrated Detection Control Widget."""
    
    def setupUi(self, IntegratedDetectionControlWidget):
        """Setup UI with tab widget structure."""
        IntegratedDetectionControlWidget.setObjectName("IntegratedDetectionControlWidget")
        
        # Main layout
        self.mainLayout = QtWidgets.QVBoxLayout(IntegratedDetectionControlWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget (tabs will be added programmatically)
        self.tabs = QtWidgets.QTabWidget(IntegratedDetectionControlWidget)
        self.tabs.setObjectName("tabs")
        self.mainLayout.addWidget(self.tabs)
        
        # Tab placeholders (will be replaced programmatically)
        # Tab 1: Input & Processing
        self.tab_input = QtWidgets.QWidget()
        self.tab_input.setObjectName("tab_input")
        self.tabs.addTab(self.tab_input, "Input & Processing")
        
        # Tab 2: Motion Detection
        self.tab_motion = QtWidgets.QWidget()
        self.tab_motion.setObjectName("tab_motion")
        self.tabs.addTab(self.tab_motion, "Motion Detection")
        
        # Tab 3: Color Anomaly
        self.tab_color = QtWidgets.QWidget()
        self.tab_color.setObjectName("tab_color")
        self.tabs.addTab(self.tab_color, "Color Anomaly")
        
        # Tab 4: Fusion & Temporal
        self.tab_fusion = QtWidgets.QWidget()
        self.tab_fusion.setObjectName("tab_fusion")
        self.tabs.addTab(self.tab_fusion, "Fusion & Temporal")
        
        # Tab 5: False Positive Reduction
        self.tab_fpr = QtWidgets.QWidget()
        self.tab_fpr.setObjectName("tab_fpr")
        self.tabs.addTab(self.tab_fpr, "False Pos. Reduction")
        
        # Tab 6: Rendering
        self.tab_render = QtWidgets.QWidget()
        self.tab_render.setObjectName("tab_render")
        self.tabs.addTab(self.tab_render, "Rendering")
        
        self.retranslateUi(IntegratedDetectionControlWidget)
        QtCore.QMetaObject.connectSlotsByName(IntegratedDetectionControlWidget)

    def retranslateUi(self, IntegratedDetectionControlWidget):
        """Translate UI strings."""
        _translate = QtCore.QCoreApplication.translate
        # Tab names are set in setupUi, no additional translation needed

