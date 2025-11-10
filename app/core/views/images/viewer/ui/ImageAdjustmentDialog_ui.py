# -*- coding: utf-8 -*-

# Form implementation for Image Adjustment Dialog
# ADIAT - Automated Drone Image Analysis Tool
# Image adjustment dialog with real-time sliders for exposure, highlights, shadows, clarity, and radius

from PySide6 import QtCore, QtGui, QtWidgets


class Ui_ImageAdjustmentDialog(object):
    def setupUi(self, ImageAdjustmentDialog):
        print("TESTING")
        ImageAdjustmentDialog.setObjectName("ImageAdjustmentDialog")
        ImageAdjustmentDialog.resize(350, 400)
        ImageAdjustmentDialog.setWindowTitle("Image Adjustments")
        ImageAdjustmentDialog.setModal(True)

        # Main layout
        self.verticalLayout = QtWidgets.QVBoxLayout(ImageAdjustmentDialog)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")

        # Title label
        self.titleLabel = QtWidgets.QLabel(ImageAdjustmentDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setText("Image Adjustments")
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)

        # Create adjustment controls with expanded ranges for more pronounced effects
        self._create_slider_group("Exposure", "exposureSlider", "exposureLabel", "exposureValue", -200, 200, 0)
        self._create_slider_group("Highlights", "highlightsSlider", "highlightsLabel", "highlightsValue", -200, 200, 0)
        self._create_slider_group("Shadows", "shadowsSlider", "shadowsLabel", "shadowsValue", -200, 200, 0)
        self._create_slider_group("Clarity", "claritySlider", "clarityLabel", "clarityValue", -200, 200, 0)
        self._create_slider_group("Radius", "radiusSlider", "radiusLabel", "radiusValue", 1, 100, 10)

        # Spacer
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        # Button layout
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")

        # Reset button
        self.resetButton = QtWidgets.QPushButton(ImageAdjustmentDialog)
        self.resetButton.setText("Reset")
        self.resetButton.setObjectName("resetButton")
        self.buttonLayout.addWidget(self.resetButton)

        # Button spacer
        buttonSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(buttonSpacer)

        # Apply button
        self.applyButton = QtWidgets.QPushButton(ImageAdjustmentDialog)
        self.applyButton.setText("Apply")
        self.applyButton.setObjectName("applyButton")
        self.buttonLayout.addWidget(self.applyButton)

        # Close button
        self.closeButton = QtWidgets.QPushButton(ImageAdjustmentDialog)
        self.closeButton.setText("Close")
        self.closeButton.setObjectName("closeButton")
        self.buttonLayout.addWidget(self.closeButton)

        self.verticalLayout.addLayout(self.buttonLayout)

    def _create_slider_group(self, label_text, slider_name, label_name, value_name, min_val, max_val, default_val):
        """Create a labeled slider group with value display."""
        # Group widget
        group_widget = QtWidgets.QWidget()
        group_widget.setObjectName(f"{slider_name}Group")

        # Group layout
        group_layout = QtWidgets.QVBoxLayout(group_widget)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(5)

        # Label layout
        label_layout = QtWidgets.QHBoxLayout()

        # Label
        label = QtWidgets.QLabel()
        label.setText(label_text)
        font = QtGui.QFont()
        font.setPointSize(10)
        label.setFont(font)
        label.setObjectName(label_name)
        setattr(self, label_name, label)
        label_layout.addWidget(label)

        group_layout.addLayout(label_layout)

        # Slider
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider.setTickInterval((max_val - min_val) // 4)
        slider.setObjectName(slider_name)
        setattr(self, slider_name, slider)
        group_layout.addWidget(slider)

        # Slider row layout for slider and input field
        slider_row_layout = QtWidgets.QHBoxLayout()
        slider_row_layout.setContentsMargins(0, 0, 0, 0)
        slider_row_layout.setSpacing(15)

        # Add slider to the left side of the row (will expand to fill available space)
        slider_row_layout.addWidget(slider, 1)  # Stretch factor 1 to expand

        # Value input textbox at the end of the slider row
        value_input = QtWidgets.QLineEdit()
        value_input.setText(str(default_val))
        value_input.setMinimumWidth(50)
        value_input.setMaximumWidth(60)
        value_input.setAlignment(QtCore.Qt.AlignRight)
        value_input.setObjectName(f"{value_name}Input")
        setattr(self, f"{value_name}Input", value_input)
        slider_row_layout.addWidget(value_input, 0)  # No stretch, fixed size

        # Add the slider row layout to the group
        group_layout.addLayout(slider_row_layout)

        self.verticalLayout.addWidget(group_widget)

    def retranslateUi(self, ImageAdjustmentDialog):
        _translate = QtCore.QCoreApplication.translate
        ImageAdjustmentDialog.setWindowTitle(_translate("ImageAdjustmentDialog", "Image Adjustments"))
