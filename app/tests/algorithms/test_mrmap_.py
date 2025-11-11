from PySide6.QtCore import Qt


def testMrMapE2E(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    main_window.minAreaSpinBox.setValue(200)
    assert main_window.algorithmWidget is not None
    main_window.algorithmComboBox.setCurrentText('MRMap Algorithm')
    assert main_window.algorithmWidget is not None
    assert main_window.AdvancedFeaturesWidget.isVisible()
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.thresholdSlider.setValue(95)
    algorithmWidget.segmentsComboBox.setCurrentText(str(2))
    algorithmWidget.colorspaceComboBox.setCurrentText('RGB')
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
    assert len(viewer.aoiListWidget) != 0
    assert len(viewer.aoiListWidget) != 0
    assert viewer.statusbar.currentMessage() != ""
    qtbot.mouseClick(viewer.nextImageButton, Qt.MouseButton.LeftButton)
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert len(viewer.aoiListWidget) != 0
    assert len(viewer.aoiListWidget) != 0
    assert viewer.statusbar.currentMessage() != ""
    qtbot.mouseClick(viewer.previousImageButton, Qt.MouseButton.LeftButton)
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert len(viewer.aoiListWidget) != 0
    assert len(viewer.aoiListWidget) != 0
    assert viewer.statusbar.currentMessage() != ""
