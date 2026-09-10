from PySide6.QtCore import Qt


def testRXAnomalyE2E(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    assert main_window.algorithmWidget is not None
    main_window.algorithmComboBox.setCurrentIndex(
        main_window.algorithmComboBox.findData('RXAnomaly'))
    assert main_window.algorithmWidget is not None
    assert main_window.AdvancedFeaturesWidget.isVisible()
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.sensitivitySlider.setValue(7)
    algorithmWidget.segmentsComboBox.setCurrentText(str(2))
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()
    assert not main_window.viewResultsButton.isEnabled()

    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    assert not main_window.startButton.isEnabled()
    assert main_window.cancelButton.isEnabled()
    # A generous budget for the slow Windows VM; Start re-enables when the run finishes.
    qtbot.waitUntil(lambda: main_window.startButton.isEnabled(), timeout=200000)
    assert not main_window.cancelButton.isEnabled()
    assert main_window.viewResultsButton.isEnabled(), "expected AOIs for this fixture/params"

    qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)
    assert main_window.viewer is not None
    viewer = main_window.viewer
    assert len(viewer.images) > 0
    assert viewer.main_image.hasImage()
    assert viewer.aoiListWidget.count() > 0
    assert viewer.statusBar.text() != ""

    start_index = viewer.current_image
    qtbot.mouseClick(viewer.nextImageButton, Qt.MouseButton.LeftButton)
    assert viewer.current_image == (start_index + 1) % len(viewer.images)
    assert viewer.main_image.hasImage()
    assert viewer.aoiListWidget.count() > 0
    assert viewer.statusBar.text() != ""

    qtbot.mouseClick(viewer.previousImageButton, Qt.MouseButton.LeftButton)
    assert viewer.current_image == start_index
    assert viewer.main_image.hasImage()
    assert viewer.aoiListWidget.count() > 0
    assert viewer.statusBar.text() != ""
