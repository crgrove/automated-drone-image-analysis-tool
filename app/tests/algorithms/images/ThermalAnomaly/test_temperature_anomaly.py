from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog
from unittest.mock import patch, MagicMock


def testTemperatureAnomalyE2E(main_window, testData, qtbot, thermal_sdk_available):
    main_window.inputFolderLine.setText(testData['Thermal_Input'])
    main_window.outputFolderLine.setText(testData['Thermal_Output'])
    assert main_window.algorithmWidget is not None
    main_window.algorithmComboBox.setCurrentText('Temperature Anomaly')
    main_window.minAreaSpinBox.setValue(10)
    main_window.maxAreaSpinBox.setValue(0)
    assert main_window.algorithmWidget is not None
    assert not main_window.AdvancedFeaturesWidget.isVisible()
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.anomalySpinBox.setValue(6)
    algorithmWidget.anomalyTypeComboBox.setCurrentText('Above Mean')
    # colorMapComboBox doesn't exist in ThermalAnomalyController - color map is handled elsewhere
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()
    assert not main_window.viewResultsButton.isEnabled()
    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    assert not main_window.startButton.isEnabled()
    assert main_window.cancelButton.isEnabled()
    assert not main_window.startButton.isEnabled()
    qtbot.waitUntil(lambda: main_window.viewResultsButton.isEnabled(), timeout=45000)
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()
    assert main_window.viewResultsButton.isEnabled()
    # Patch BearingRecoveryDialog to automatically skip (returns Rejected = Skip)
    # This prevents the modal dialog from blocking test execution
    # Create a mock dialog that returns Rejected when exec() is called (Skip action)
    mock_dialog = MagicMock()
    mock_dialog.exec.return_value = QDialog.DialogCode.Rejected
    mock_dialog.get_results.return_value = None

    # Patch where the dialog is instantiated in BearingRecoveryController
    with patch('core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog', return_value=mock_dialog):
        qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)

        # Wait for viewer to initialize (dialog.exec() is mocked, so it won't block)
        qtbot.waitUntil(lambda: main_window.viewer is not None, timeout=5000)

    assert main_window.viewer is not None
    viewer = main_window.viewer
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert viewer.aoiListWidget.count() != 0
    assert viewer.aoiListWidget.count() != 0
    qtbot.mouseClick(viewer.nextImageButton, Qt.MouseButton.LeftButton)
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert viewer.aoiListWidget.count() != 0
    assert viewer.aoiListWidget.count() != 0
    qtbot.mouseClick(viewer.previousImageButton, Qt.MouseButton.LeftButton)
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0
    assert viewer.main_image is not None
    assert viewer.aoiListWidget is not None
    assert viewer.aoiListWidget.count() != 0
    assert viewer.aoiListWidget.count() != 0
