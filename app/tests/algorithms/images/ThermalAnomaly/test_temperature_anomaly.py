import platform

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from unittest.mock import patch, MagicMock


@pytest.mark.skipif(platform.system() == "Linux", reason="Thermal E2E is Windows-only for now (algorithms.conf platforms)")
def testTemperatureAnomalyE2E(main_window, testData, qtbot, thermal_sdk_available):
    main_window.inputFolderLine.setText(testData['Thermal_Input'])
    main_window.outputFolderLine.setText(testData['Thermal_Output'])
    assert main_window.algorithmWidget is not None
    main_window.algorithmComboBox.setCurrentIndex(
        main_window.algorithmComboBox.findData('ThermalAnomaly'))
    main_window.minAreaSpinBox.setValue(10)
    main_window.maxAreaSpinBox.setValue(0)
    assert main_window.algorithmWidget is not None
    assert not main_window.AdvancedFeaturesWidget.isVisible()
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.anomalySpinBox.setValue(6)
    algorithmWidget.anomalyTypeComboBox.setCurrentText('Above Mean')
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

    mock_dialog = MagicMock()
    mock_dialog.exec.return_value = QDialog.DialogCode.Rejected
    mock_dialog.get_results.return_value = None

    with patch('core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog', return_value=mock_dialog):
        qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: main_window.viewer is not None, timeout=5000)

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
