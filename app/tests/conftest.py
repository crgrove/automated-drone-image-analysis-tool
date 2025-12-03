import sys
import os
import pytest
import importlib
import platform
from PySide6.QtWidgets import QApplication

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

# Lazy import to avoid dependency issues for streaming tests
try:
    qdarktheme = importlib.import_module("qdarktheme")
except ImportError:
    qdarktheme = None

try:
    MainWindowModule = importlib.import_module("core.controllers.images.MainWindow")
    MainWindow = MainWindowModule.MainWindow
except ImportError:
    MainWindow = None

_MAIN_WINDOW_AVAILABLE = qdarktheme is not None and MainWindow is not None


def _check_thermal_sdk_available():
    """Check if DJI thermal SDK DLL is available."""
    try:
        # Determine the base path
        # Match the logic in DjiThermalParserService._get_default_filepaths()
        if getattr(sys, 'frozen', False):
            app_root = sys._MEIPASS
        else:
            # __file__ is app/tests/conftest.py
            # Go up one level to get app/ (same as DjiThermalParserService goes up 4 levels from its location)
            tests_dir = os.path.dirname(__file__)  # app/tests
            app_root = os.path.dirname(tests_dir)  # app

        folder_plugin = os.path.join(app_root, 'external')
        system = platform.system()
        architecture = platform.architecture()[0]

        if system == "Windows":
            if architecture == "32bit":
                dll_path = os.path.join(folder_plugin,
                                        'dji_thermal_sdk_v1.7_20241205/windows/release_x86/libdirp.dll')
            elif architecture == "64bit":
                dll_path = os.path.join(folder_plugin,
                                        'dji_thermal_sdk_v1.7_20241205/windows/release_x64/libdirp.dll')
            else:
                return False
        elif system == "Linux":
            if architecture == "32bit":
                dll_path = os.path.join(folder_plugin,
                                        'dji_thermal_sdk_v1.7_20241205/linux/release_x86/libdirp.so')
            elif architecture == "64bit":
                dll_path = os.path.join(folder_plugin,
                                        'dji_thermal_sdk_v1.7_20241205/linux/release_x64/libdirp.so')
            else:
                return False
        else:
            return False

        exists = os.path.exists(dll_path)
        # Note: Even if the file exists, it might not be loadable due to missing dependencies
        # But we check for existence as a basic requirement
        return exists
    except Exception:
        # Silently return False on any error
        return False


@pytest.fixture
def thermal_sdk_available():
    """Fixture to check if thermal SDK is available."""
    if not _check_thermal_sdk_available():
        pytest.skip("DJI thermal SDK DLL not available")
    return True


@pytest.fixture
def testData():
    return {
        'RGB_Input': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/input')),
        'RGB_Output': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/output')),
        'Thermal_Input': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/thermal/input')),
        'Thermal_Output': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/thermal/output')),
        'KML_Path': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/test.kml')),
        'Previous_Output': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/output/ADIAT_Results/ADIAT_Data.xml')),
        'Video_Path': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/video/DJI_0462.MP4')),
        'SRT_Path': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/video/DJI_0462.SRT')),
        'Video_Output': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/video/output')),
        'EXIF_Input_Path': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/input/DJI_0082.JPG')),
        'EXIF_Output_Path': os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/data/rgb/output/ADIAT_Results/DJI_0082.JPG')),
    }


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope='function')
def main_window(qtbot):
    if not _MAIN_WINDOW_AVAILABLE:
        pytest.skip("MainWindow dependencies not available")
    # qdarktheme.setup_theme()  # Not needed with PySide6, theme is set via stylesheet
    mw = MainWindow(qdarktheme)
    mw.show()
    qtbot.addWidget(mw)

    yield mw

    # Cleanup: Ensure all threads and processes are stopped
    try:
        # Close viewer if open
        if hasattr(mw, 'viewer') and mw.viewer is not None:
            mw.viewer.close()
            qtbot.wait(100)  # Give time for cleanup

        # Stop all analysis threads and terminate processes
        if hasattr(mw, '_MainWindow__threads'):
            for thread, analyze_service in mw._MainWindow__threads:
                if thread.isRunning():
                    # Cancel the analysis first
                    if analyze_service is not None and hasattr(analyze_service, 'process_cancel'):
                        try:
                            analyze_service.process_cancel()
                        except Exception:
                            pass

                    # Terminate the process pool if it exists
                    if analyze_service is not None and hasattr(analyze_service, 'pool'):
                        try:
                            analyze_service.pool.terminate()
                            analyze_service.pool.join(timeout=1)
                        except Exception:
                            pass

                    # Stop the thread
                    thread.quit()
                    thread.wait(3000)  # Wait up to 3 seconds for thread to finish

        # Also check for any remaining analyzeService
        if hasattr(mw, 'analyzeService') and mw.analyzeService is not None:
            if hasattr(mw.analyzeService, 'pool'):
                try:
                    mw.analyzeService.pool.terminate()
                    mw.analyzeService.pool.join(timeout=1)
                except Exception:
                    pass

        # Close the main window
        mw.close()
        qtbot.wait(200)  # Give time for cleanup

        # Small delay to ensure processes are fully terminated
        import time
        time.sleep(0.1)
    except Exception as e:
        # Don't fail tests on cleanup errors, but log them
        import traceback
        print(f"Warning: Cleanup error in main_window fixture: {e}")
        traceback.print_exc()
