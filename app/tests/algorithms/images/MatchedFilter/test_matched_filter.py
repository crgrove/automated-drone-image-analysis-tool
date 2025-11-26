from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


def testMatchedFilterE2E(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    assert main_window.algorithmWidget is not None
    main_window.algorithmComboBox.setCurrentText('Matched Filter')
    assert main_window.algorithmWidget is not None
    assert main_window.AdvancedFeaturesWidget.isVisible()
    algorithmWidget = main_window.algorithmWidget
    # Use new wizard-based API
    if hasattr(algorithmWidget, 'add_color_row'):
        color = QColor(0, 170, 255)
        # Use default threshold of 0.3 (more reasonable than 0.07)
        algorithmWidget.add_color_row(color, threshold=0.3)
    else:
        # Legacy fallback
        algorithmWidget.thresholdSlider.setValue(7)
        algorithmWidget.selectedColor = QColor(0, 170, 255)
        algorithmWidget.update_colors()
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()
    assert not main_window.viewResultsButton.isEnabled()
    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    assert not main_window.startButton.isEnabled()
    assert main_window.cancelButton.isEnabled()
    assert not main_window.startButton.isEnabled()
    qtbot.waitUntil(lambda: main_window.viewResultsButton.isEnabled(), timeout=20000)
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()
    assert main_window.viewResultsButton.isEnabled()
    qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)
    assert main_window.viewer is not None
    viewer = main_window.viewer
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert viewer.aoiListWidget.count() != 0
    assert viewer.aoiListWidget.count() != 0
    assert viewer.statusBar.text() != ""
    qtbot.mouseClick(viewer.nextImageButton, Qt.MouseButton.LeftButton)
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert viewer.aoiListWidget.count() != 0
    assert viewer.aoiListWidget.count() != 0
    assert viewer.statusBar.text() != ""
    qtbot.mouseClick(viewer.previousImageButton, Qt.MouseButton.LeftButton)
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert viewer.aoiListWidget.count() != 0
    assert viewer.aoiListWidget.count() != 0
    assert viewer.statusBar.text() != ""
