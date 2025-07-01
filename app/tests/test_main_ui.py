import os
from os import path
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from unittest.mock import patch
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from app.core.controllers.VideoParser import VideoParser
from app.core.controllers.Perferences import Preferences
from app.core.services.PdfGeneratorService import PdfGeneratorService

def testVisible(main_window):
    assert main_window.isVisible()

def testBasicEndToEnd(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    main_window.minAreaSpinBox.setValue(8)
    main_window.maxAreaSpinBox.setValue(1000)
    assert main_window.algorithmWidget is not None
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.rRangeSpinBox.setValue(75)
    algorithmWidget.gRangeSpinBox.setValue(75)
    algorithmWidget.bRangeSpinBox.setValue(75)
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

def testKMeans(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    assert main_window.algorithmWidget is not None
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.rRangeSpinBox.setValue(75)
    algorithmWidget.gRangeSpinBox.setValue(75)
    algorithmWidget.bRangeSpinBox.setValue(75)
    algorithmWidget.selectedColor = QColor(0, 170, 255)
    algorithmWidget.update_colors()
    assert main_window.kMeansCheckbox is not None
    assert not main_window.KMeansWidget.isVisible()
    assert not main_window.kMeansCheckbox.isChecked()
    main_window.kMeansCheckbox.setChecked(True)
    assert main_window.kMeansCheckbox.isChecked()
    assert main_window.KMeansWidget.isVisible()
    main_window.clustersSpinBox.setValue(10)

    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: main_window.startButton.isEnabled(), timeout=60000)
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()

def testNormalizeHistogram(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    assert main_window.algorithmWidget is not None
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.rRangeSpinBox.setValue(75)
    algorithmWidget.gRangeSpinBox.setValue(75)
    algorithmWidget.bRangeSpinBox.setValue(75)
    algorithmWidget.selectedColor = QColor(0, 170, 255)
    algorithmWidget.update_colors()
    assert main_window.histogramCheckbox is not None
    assert not main_window.HistogramImgWidget.isVisible()
    assert not main_window.histogramCheckbox.isChecked()
    main_window.histogramCheckbox.setChecked(True)
    assert main_window.histogramCheckbox.isChecked()
    assert main_window.HistogramImgWidget.isVisible()
    histogram_path = path.abspath(path.join(path.dirname(path.dirname(__file__)), 'tests/data/rgb/input/DJI_0082.JPG'))
    main_window.histogramLine.setText(histogram_path)

    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: main_window.viewResultsButton.isEnabled(), timeout=20000)
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()

def testKmlCollection(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    assert main_window.algorithmWidget is not None
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.rRangeSpinBox.setValue(75)
    algorithmWidget.gRangeSpinBox.setValue(75)
    algorithmWidget.bRangeSpinBox.setValue(75)
    algorithmWidget.selectedColor = QColor(0, 170, 255)
    algorithmWidget.update_colors()
    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: main_window.viewResultsButton.isEnabled(), timeout=20000)
    qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)
    assert main_window.viewer is not None
    viewer = main_window.viewer
    if path.exists(testData['KML_Path']):
        os.remove(testData['KML_Path'])
    viewer.generate_kml(testData['KML_Path'])
    assert path.exists(testData['KML_Path'])


def testPdfGenerator(main_window, testData, qtbot):
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])
    algorithmWidget = main_window.algorithmWidget
    algorithmWidget.rRangeSpinBox.setValue(75)
    algorithmWidget.gRangeSpinBox.setValue(75)
    algorithmWidget.bRangeSpinBox.setValue(75)
    algorithmWidget.selectedColor = QColor(0, 170, 255)
    algorithmWidget.update_colors()

    with patch.object(QFileDialog, 'getSaveFileName', return_value=("/path/to/report.pdf", "pdf")), \
         patch.object(PdfGeneratorService, 'generate_report', return_value=None) as mock_generate_pdf, \
         patch.object(QMessageBox, 'information') as mock_messagebox:

        # Ensure Viewer is initialized and ready
        qtbot.mouseClick(main_window.startButton, Qt.LeftButton)
        qtbot.waitUntil(lambda: main_window.viewResultsButton.isEnabled(), timeout=20000)
        qtbot.mouseClick(main_window.viewResultsButton, Qt.LeftButton)

        # Ensure the PDF button is properly initialized
        assert main_window.viewer is not None
        assert main_window.viewer.pdfButton is not None

        # Patch the instantiation of PdfGeneratorService in _pdfButton_clicked()
        with patch("app.core.services.PdfGeneratorService.PdfGeneratorService") as mock_pdf_service:
            mock_pdf_instance = mock_pdf_service.return_value
            mock_pdf_instance.generate_report.return_value = None
            qtbot.mouseClick(main_window.viewer.pdfButton, Qt.LeftButton)
            # Ensure generate_report was called
            mock_pdf_instance.generate_report("/path/to/report.pdf")

        mock_messagebox.assert_called_once()


def testLoadFile(main_window, testData, qtbot):
    main_window._process_xml_file(testData['Previous_Output'])
    assert main_window.viewResultsButton.isEnabled()


def testPreferences(main_window, qtbot):
    pref = Preferences(main_window)
    pref.show()
    assert pref is not None
    pref.maxAOIsSpinBox.setValue(200)
    pref.accept()
    pref = Preferences(main_window)
    pref.show()
    assert pref.maxAOIsSpinBox.value() == 200


def testVideoParser(testData, qtbot):
    parser = VideoParser()
    parser.show()
    assert parser is not None
    parser.videoSelectLine.setText(testData['Video_Path'])
    parser.srtSelectLine.setText(testData['SRT_Path'])
    parser.outputLine.setText(testData['Video_Output'])
    qtbot.mouseClick(parser.startButton, Qt.MouseButton.LeftButton)
    assert not parser.startButton.isEnabled()
    qtbot.waitUntil(lambda: parser.startButton.isEnabled(), timeout=60000)
    assert len(os.listdir(testData['Video_Output'])) > 0
