import sys
import os
import qdarktheme
import pytest
import sys
from app.core.controllers.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

@pytest.fixture
def testData():
    return{
        'RGB_Input' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/input')),
        'RGB_Output' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/output')),
        'Thermal_Input' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/thermal/input')),
        'Thermal_Output' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/thermal/output')),
        'KML_Path' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/test.kml')),
        'Previous_Output' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/output/ADIAT_Results/ADIAT_Data.xml')),
        'Video_Path' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/video/DJI_0462.MP4')),
        'SRT_Path' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/video/DJI_0462.SRT')),
        'Video_Output' : os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/video/output')),
        'EXIF_Input_Path': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/input/DJI_0082.JPG')),
        'EXIF_Output_Path': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/output/ADIAT_Results/DJI_0082.JPG')),
    }


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])

@pytest.fixture(scope='function')
def main_window(qtbot):
    version = "TEST"
    qdarktheme.setup_theme()
    mw = MainWindow(qdarktheme, version)
    mw.show()
    qtbot.addWidget(mw)
    return mw
