"""Unit tests for AlertPresenter - the audio/visual half of alerting.

These were AlertService's tests. The audio device, the system-tray
notification and the popup box moved out of ``app/core/services/`` because a
service must not build UI (CLAUDE.md 2.1); the decision logic they used to
sit beside is covered in app/tests/core/services/test_alert_service.py.

Every channel degrades quietly and independently: no ``QSound`` in this
PySide6 build, no system tray on this platform, a tray icon that refuses to
show. An alert that cannot be sounded must not take the detection pipeline
down with it, which is what most of these cases are about.
"""

import time

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from core.services.AlertService import AlertConfig, AlertManager, AlertType
from core.views.components.AlertPresenter import AlertPresenter

PRESENTER = "core.views.components.AlertPresenter"


def _make_detection(confidence=0.9, area=2500, bbox=(10, 10, 50, 50)):
    """A detection is duck-typed; the presenter reads bbox and confidence."""
    return MagicMock(
        bbox=bbox,
        centroid=(bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2),
        area=area,
        confidence=confidence,
        timestamp=time.time(),
        contour=np.zeros((1, 1, 2), dtype=np.int32),
    )


@pytest.fixture
def presenter(app):
    """A presenter over a real manager, with the logger and tray stubbed."""
    with patch(f"{PRESENTER}.LoggerService") as logger_cls, \
            patch(f"{PRESENTER}.QSystemTrayIcon") as tray_cls, \
            patch(f"{PRESENTER}.QApplication") as qapp_cls, \
            patch("core.services.AlertService.LoggerService"):
        tray_cls.isSystemTrayAvailable.return_value = False
        tray_cls.Information = 0
        qapp_cls.instance.return_value = None
        logger_cls.return_value = MagicMock()
        yield AlertPresenter(AlertManager(AlertConfig()))


# ---------------------------------------------------------------------------
# subscription
# ---------------------------------------------------------------------------

def test_attaching_renders_the_managers_alerts(presenter):
    """The presenter subscribes; the manager never holds a reference to it,
    which is what lets the manager be tested with no Qt widgets at all."""
    presenter.manager.config.alert_type = AlertType.AUDIO_ONLY
    presenter.attach()

    with patch.object(presenter, "_play_audio_alert") as play:
        presenter.manager.alertTriggered.emit({"detection_count": 1}, [])

    play.assert_called_once()


def test_detaching_stops_rendering(presenter):
    presenter.attach()
    presenter.detach()

    with patch.object(presenter, "_play_audio_alert") as play:
        presenter.manager.alertTriggered.emit({"detection_count": 1}, [])

    play.assert_not_called()


def test_detaching_twice_is_harmless(presenter):
    presenter.attach()
    presenter.detach()
    presenter.detach()      # must not raise


def test_the_alert_type_decides_which_channels_fire(presenter):
    presenter.attach()
    presenter.manager.config.alert_type = AlertType.VISUAL_ONLY

    with patch.object(presenter, "_play_audio_alert") as play, \
            patch.object(presenter, "_show_visual_alert") as show:
        presenter.manager.alertTriggered.emit({"detection_count": 1}, [])

    play.assert_not_called()
    show.assert_called_once()


# ---------------------------------------------------------------------------
# _init_audio_system branches
# ---------------------------------------------------------------------------

def test_init_audio_system_returns_none_when_qsound_unavailable(presenter):
    with patch(f"{PRESENTER}.QSound", None):
        presenter.manager.config.audio_file = "/path/fake.wav"
        result = presenter._init_audio_system()
    assert result is None


def test_init_audio_system_returns_none_when_file_missing(presenter):
    with patch(f"{PRESENTER}.QSound", MagicMock()), \
            patch("os.path.exists", return_value=False):
        presenter.manager.config.audio_file = "/not/there.wav"
        result = presenter._init_audio_system()
    assert result is None


def test_init_audio_system_creates_qsound_when_valid(presenter):
    with patch(f"{PRESENTER}.QSound", MagicMock()), \
            patch("os.path.exists", return_value=True):
        presenter.manager.config.audio_file = "/exists.wav"
        result = presenter._init_audio_system()
    assert result is not None


def test_init_audio_system_logs_on_exception(presenter):
    """A bad sound file must not stop the presenter being built."""
    with patch(f"{PRESENTER}.QSound", MagicMock(side_effect=RuntimeError("audio fail"))), \
            patch("os.path.exists", return_value=True):
        presenter.manager.config.audio_file = "/exists.wav"
        result = presenter._init_audio_system()
    assert result is None


# ---------------------------------------------------------------------------
# _play_audio_alert branches
# ---------------------------------------------------------------------------

def test_play_audio_custom_sound(presenter):
    presenter._audio_system = MagicMock()
    presenter._play_audio_alert()
    presenter._audio_system.play.assert_called_once()


def test_play_audio_custom_sound_handles_error(presenter):
    presenter._audio_system = MagicMock()
    presenter._audio_system.play.side_effect = RuntimeError("fail")
    presenter._play_audio_alert()      # must not raise


def test_play_audio_system_sound_windows(presenter):
    presenter._audio_system = None
    presenter.manager.config.use_system_sound = True
    fake_winsound = MagicMock()
    fake_winsound.MB_ICONEXCLAMATION = 0x30

    with patch(f"{PRESENTER}.winsound", fake_winsound):
        presenter._play_audio_alert()

    fake_winsound.MessageBeep.assert_called_once()


def test_play_audio_system_sound_without_winsound(presenter):
    """macOS and Linux have no winsound; the alert is simply silent."""
    presenter._audio_system = None
    presenter.manager.config.use_system_sound = True

    with patch(f"{PRESENTER}.winsound", None):
        presenter._play_audio_alert()   # must not raise


# ---------------------------------------------------------------------------
# _show_visual_alert branches
# ---------------------------------------------------------------------------

def _alert_info():
    return {"detection_count": 1, "total_area": 100, "avg_confidence": 0.9}


def test_show_visual_alert_emits_system_tray_notification(presenter):
    presenter.manager.config.show_system_notification = True
    presenter._system_tray = MagicMock()
    presenter._system_tray.isVisible.return_value = True

    with patch(f"{PRESENTER}.QSystemTrayIcon") as MockTray, \
            patch(f"{PRESENTER}.QTimer") as MockTimer:
        MockTray.isSystemTrayAvailable.return_value = True
        MockTray.Information = 0
        presenter._show_visual_alert(_alert_info(), [_make_detection()])

    MockTimer.singleShot.assert_called_once()


def test_show_visual_alert_skips_when_tray_invisible(presenter):
    presenter.manager.config.show_system_notification = True
    presenter._system_tray = MagicMock()
    presenter._system_tray.isVisible.return_value = False

    with patch(f"{PRESENTER}.QSystemTrayIcon") as MockTray:
        MockTray.isSystemTrayAvailable.return_value = True
        presenter._show_visual_alert(_alert_info(), [_make_detection()])

    presenter._system_tray.showMessage.assert_not_called()


def test_show_visual_alert_no_tray_configured(presenter):
    presenter.manager.config.show_system_notification = True
    presenter._system_tray = None

    presenter._show_visual_alert(_alert_info(), [_make_detection()])   # no raise


def test_show_visual_alert_popup_window_invocation(presenter):
    """The box is built on the GUI thread: the decision runs on a worker."""
    presenter.manager.config.show_system_notification = False
    presenter.manager.config.show_popup_window = True

    with patch(f"{PRESENTER}.QTimer") as MockTimer:
        presenter._show_visual_alert(_alert_info(), [_make_detection()])

    MockTimer.singleShot.assert_called_once()


# ---------------------------------------------------------------------------
# _create_alert_message
# ---------------------------------------------------------------------------

def test_create_alert_message_includes_counts(presenter):
    message = presenter._create_alert_message(
        {"detection_count": 1, "total_area": 2500, "avg_confidence": 0.8},
        [_make_detection(confidence=0.8)])

    assert "1" in message
    assert "0.80" in message


def test_create_alert_message_hides_details_for_many(presenter):
    """Per-detection lines are useful for two or three, noise for twenty."""
    message = presenter._create_alert_message(
        {"detection_count": 5, "total_area": 12500, "avg_confidence": 0.9},
        [_make_detection() for _ in range(5)])

    assert "#1" not in message


# ---------------------------------------------------------------------------
# _show_popup_message
# ---------------------------------------------------------------------------

def test_show_popup_message(presenter):
    with patch(f"{PRESENTER}.QMessageBox") as MockMsgBox:
        presenter._show_popup_message("test message")

    MockMsgBox.return_value.exec.assert_called_once()


def test_show_popup_message_swallows_errors(presenter):
    with patch(f"{PRESENTER}.QMessageBox",
               side_effect=RuntimeError("can't create")):
        presenter._show_popup_message("test")      # must not raise


# ---------------------------------------------------------------------------
# construction and lifecycle
# ---------------------------------------------------------------------------

def test_init_system_tray_not_available(app):
    """A platform without a tray still gets audio and popups."""
    with patch(f"{PRESENTER}.QSystemTrayIcon") as MockTray, \
            patch(f"{PRESENTER}.LoggerService"), \
            patch("core.services.AlertService.LoggerService"):
        MockTray.isSystemTrayAvailable.return_value = False
        presenter = AlertPresenter(AlertManager())

    assert presenter._system_tray is None


def test_a_config_change_reopens_the_audio_device(presenter):
    """The sound file may have changed, and the presenter owns the device -
    the manager only announces the change."""
    presenter.attach()

    with patch.object(presenter, "_init_audio_system",
                      return_value="reopened") as reinit:
        presenter.manager.update_config(AlertConfig())

    reinit.assert_called_once()
    assert presenter._audio_system == "reopened"


def test_test_alert_delegates_to_the_manager(presenter):
    """The presenter renders; the manager still decides, even for a test."""
    with patch.object(presenter.manager, "_trigger_alert_safe") as mock_trigger:
        presenter.test_alert()

    mock_trigger.assert_called_once()


def test_the_service_module_imports_no_widgets():
    """The whole point of the split. Import lines only - the docstring names
    the classes it used to build."""
    from core.services import AlertService

    with open(AlertService.__file__, encoding="utf-8") as handle:
        imports = [line for line in handle
                   if line.startswith(("import ", "from "))]

    widget_imports = [line for line in imports
                      if "QtWidgets" in line or "QtGui" in line
                      or "QtMultimedia" in line]
    assert widget_imports == []
    # ...and it no longer reaches into an algorithm package (CLAUDE.md 2.2.1).
    assert [line for line in imports if "algorithms" in line] == []
