import sys
import os
import pytest
import importlib
import platform
import tempfile
import time
import traceback
from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtWidgets import QApplication

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))


# Throwaway location for any QSettings a test needs to write to.
#
# Services construct QSettings with the application's real organization and
# application names (``QSettings("ADIAT", "CalTopoAPI")``, ...). On Windows
# those resolve to HKCU\Software\ADIAT, so a test that *writes* settings edits
# the developer's own configuration. The credential-helper suite did exactly
# that: save_credentials() with fixture values overwrote real stored CalTopo
# API credentials, leaving the app authenticating as XYZ789/cred_id_456 until
# the user noticed and re-entered them by hand.
#
# There is no global escape hatch: QSettings.setDefaultFormat() does not apply
# to the QSettings(organization, application) constructor, and setPath() has no
# effect for NativeFormat on Windows. Isolation therefore has to be injected
# per service (see the isolated_qsettings fixture below).
QSETTINGS_TEST_DIR = tempfile.mkdtemp(prefix="adiat-test-qsettings-")

# Redirect QStandardPaths (AppDataLocation, CacheLocation, ...) to Qt's test
# locations. Without this, tests that build a QWebEngineProfile write into the
# same on-disk profile the running application uses, and Chromium fails with
# "Unable to create cache" because the directory is already locked - tests and
# the app fight over one profile.
QStandardPaths.setTestModeEnabled(True)

# ...but test mode is a SINGLE shared location, so it only separates the tests
# from the app, not one test process from another. Two pytest processes -- a
# split/parallel run, a bisect alongside a full run, or simply a second suite
# started while the first is going -- then fight over the same Chromium lock
# files. Chromium reports "Unable to move the cache: Access is denied", its GPU
# cache fails to initialise, and the process later dies with a native access
# violation inside QtWebEngine teardown: no Python frame, no failing test, just
# exit 139 partway through app/tests/core/views. Two concurrent runs of that
# directory reproduced it every time; serial runs mostly survive, which is what
# made it look like a random flake.
#
# Give each process its own cache directory, and keep Chromium off the GPU
# entirely -- these tests never render a page, and the GPU shader cache is a
# second shared-state hazard with no upside here.
#
# Must be set before QtWebEngine initialises, hence module scope in conftest.
_WEBENGINE_CACHE_DIR = tempfile.mkdtemp(prefix="adiat-test-webengine-")
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(part for part in (
    os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", ""),
    f"--disk-cache-dir={_WEBENGINE_CACHE_DIR}",
    "--disable-gpu",
    "--disable-gpu-shader-disk-cache",
    "--disable-software-rasterizer",
) if part)


@pytest.fixture
def isolated_qsettings(request):
    """An INI-backed QSettings under a temp directory, never the user's store.

    Pass this into services that persist settings (for example
    ``CalTopoCredentialHelper(settings=isolated_qsettings)``) so tests can
    write freely without touching real configuration.

    Returns:
        QSettings: A per-test settings object rooted in QSETTINGS_TEST_DIR.
    """
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, QSETTINGS_TEST_DIR)
    settings = QSettings(
        QSettings.IniFormat,
        QSettings.UserScope,
        "ADIAT-Tests",
        request.node.name[:64],
    )
    yield settings
    settings.clear()
    settings.sync()


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


@pytest.fixture(scope='session', autouse=True)
def _prime_qt_and_qtawesome():
    """Ensure a QApplication exists and qtawesome icon fonts are registered.

    qtawesome registers its bundled icon fonts on first use; when that first
    use happens before any QApplication exists the fonts never register and
    later 'fa6s.*' icon lookups raise "Invalid font prefix". Warming
    qtawesome here, with the application created, keeps icon-dependent tests
    independent of collection order.
    """
    application = QApplication.instance() or QApplication([])
    try:
        import qtawesome
        qtawesome.icon('fa6s.flag')
    except Exception:
        pass
    return application


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
        time.sleep(0.1)
    except Exception as e:
        # Don't fail tests on cleanup errors, but log them
        print(f"Warning: Cleanup error in main_window fixture: {e}")
        traceback.print_exc()
