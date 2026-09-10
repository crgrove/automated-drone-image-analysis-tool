from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


def testColorRangeE2E(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    assert main_window.algorithmWidget is not None
    main_window.algorithmComboBox.setCurrentIndex(
        main_window.algorithmComboBox.findData('ColorRange'))
    assert main_window.algorithmWidget is not None
    assert main_window.AdvancedFeaturesWidget.isVisible()
    algorithmWidget = main_window.algorithmWidget
    main_window.minAreaSpinBox.setValue(10)
    # Use new wizard-based API
    if hasattr(algorithmWidget, 'add_color_row'):
        color = QColor(0, 170, 255)
        # Add color with ±75 range for each channel
        # R: 0 ± 75 = 0 to 75 (clamped to 0-255)
        # G: 170 ± 75 = 95 to 245
        # B: 255 ± 75 = 180 to 255 (clamped to 0-255)
        algorithmWidget.add_color_row(color, r_min=0, r_max=75, g_min=95, g_max=245, b_min=180, b_max=255)
        assert len(algorithmWidget.color_rows) > 0, "Color should be added to color_rows"
    else:
        # Legacy fallback
        algorithmWidget.rRangeSpinBox.setValue(75)
        algorithmWidget.gRangeSpinBox.setValue(75)
        algorithmWidget.bRangeSpinBox.setValue(75)
        algorithmWidget.selectedColor = QColor(0, 170, 255)
        algorithmWidget.update_colors()

    validation_error = algorithmWidget.validate()
    assert validation_error is None, f"Algorithm validation failed: {validation_error}"

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
