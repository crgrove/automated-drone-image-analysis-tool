"""Unit tests for AlertService - the decision half.

Playing and displaying an alert lives in
:class:`~core.views.components.AlertPresenter.AlertPresenter` and is tested in
app/tests/core/views/components/test_alert_presenter.py. What is left here is
what the operator's thresholds mean, and it needs no Qt widget to check.
"""

import time
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from core.services.AlertService import (
    AlertConfig,
    AlertHistory,
    AlertManager,
    AlertType,
    create_audio_only_config,
    create_persistent_alert_config,
    create_visual_only_config,
)
from algorithms.streaming.ColorDetection.services import Detection


def _make_detection(confidence=0.9, area=2500, bbox=(10, 10, 50, 50)):
    return Detection(
        bbox=bbox,
        centroid=(bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2),
        area=area,
        confidence=confidence,
        timestamp=time.time(),
        contour=np.zeros((1, 1, 2), dtype=np.int32),
    )


@pytest.fixture
def patched_deps():
    """Only the logger needs patching now.

    AlertManager used to open an audio device and create a system tray in
    its constructor, so every test of the decision logic had to stub Qt
    first. The presentation moved to AlertPresenter and this class is
    Qt-free.
    """
    with patch("core.services.AlertService.LoggerService") as logger_cls:
        logger_cls.return_value = MagicMock()
        yield {"logger": logger_cls}


@pytest.fixture
def alert_manager(patched_deps):
    """AlertManager with all external systems mocked out."""
    return AlertManager()


def test_alert_history_add_and_last_time():
    history = AlertHistory()
    assert history.get_last_alert_time() == 0.0

    history.add_alert(detection_count=3)
    assert history.get_last_alert_time() > 0
    assert len(history.alerts) == 1


def test_alert_history_respects_max_history():
    history = AlertHistory(max_history=5)
    for i in range(10):
        history.add_alert(detection_count=i)
    assert len(history.alerts) == 5
    assert history.alerts[0][1] == 5


def test_alert_history_count_in_time_window():
    history = AlertHistory()
    history.add_alert(1)
    history.add_alert(2)
    history.add_alert(3)
    assert history.get_alert_count(time_window=3600) == 3
    # Negative window means cutoff is in the future — no alerts qualify.
    assert history.get_alert_count(time_window=-1) == 0


def test_alert_history_empty_stats():
    history = AlertHistory()
    stats = history.get_stats()
    assert stats == {"total_alerts": 0, "avg_detections": 0, "last_alert": None}


def test_alert_history_stats_computed():
    history = AlertHistory()
    history.add_alert(4)
    history.add_alert(6)
    stats = history.get_stats()
    assert stats["total_alerts"] == 2
    assert stats["avg_detections"] == 5
    assert stats["last_alert"] is not None
    assert "alerts_last_hour" in stats
    assert "alerts_last_minute" in stats


def test_default_alert_config():
    cfg = AlertConfig()
    assert cfg.enabled is True
    assert cfg.alert_type == AlertType.BOTH
    assert cfg.min_confidence == 0.5
    assert cfg.cooldown_ms == 2000


def test_audio_only_config_factory():
    cfg = create_audio_only_config(cooldown_ms=500, min_confidence=0.3)
    assert cfg.alert_type == AlertType.AUDIO_ONLY
    assert cfg.cooldown_ms == 500
    assert cfg.min_confidence == 0.3
    assert cfg.show_system_notification is False


def test_visual_only_config_factory():
    cfg = create_visual_only_config()
    assert cfg.alert_type == AlertType.VISUAL_ONLY
    assert cfg.use_system_sound is False
    assert cfg.show_system_notification is True


def test_persistent_alert_config_factory():
    cfg = create_persistent_alert_config(consecutive_count=10, min_confidence=0.8)
    assert cfg.require_consecutive_detections is True
    assert cfg.consecutive_count == 10
    assert cfg.min_confidence == 0.8


def test_alert_manager_init_defaults(alert_manager):
    assert isinstance(alert_manager.config, AlertConfig)
    assert alert_manager._consecutive_detections == 0
    assert alert_manager._alert_processing_enabled is True


def test_filter_detections_by_confidence(alert_manager):
    detections = [
        _make_detection(confidence=0.9),
        _make_detection(confidence=0.2),  # below min_confidence=0.5
    ]
    filtered = alert_manager._filter_detections(detections)
    assert len(filtered) == 1
    assert filtered[0].confidence == 0.9


def test_filter_detections_by_area(alert_manager):
    detections = [
        _make_detection(area=100),  # below min_area=500
        _make_detection(area=2000),
    ]
    filtered = alert_manager._filter_detections(detections)
    assert len(filtered) == 1
    assert filtered[0].area == 2000


def test_filter_detections_caps_at_max(alert_manager):
    alert_manager.config.max_detections_per_alert = 2
    detections = [_make_detection() for _ in range(5)]
    filtered = alert_manager._filter_detections(detections)
    assert len(filtered) == 2


def test_check_cooldown_passes_when_no_history(alert_manager):
    assert alert_manager._check_cooldown() is True


def test_check_cooldown_blocks_recent_alert(alert_manager):
    alert_manager.history.add_alert(1)
    alert_manager.config.cooldown_ms = 60_000  # 1 minute
    assert alert_manager._check_cooldown() is False


def test_persistent_alert_requires_consecutive(alert_manager):
    alert_manager.config.require_consecutive_detections = True
    alert_manager.config.consecutive_count = 3
    detections = [_make_detection()]

    # First two calls should not trigger (below consecutive_count)
    assert alert_manager._should_trigger_persistent_alert(detections, time.time()) is False
    assert alert_manager._should_trigger_persistent_alert(detections, time.time()) is False
    # Third call reaches threshold
    assert alert_manager._should_trigger_persistent_alert(detections, time.time()) is True


def test_persistent_counter_resets_on_gap(alert_manager):
    alert_manager.config.require_consecutive_detections = True
    alert_manager.config.consecutive_count = 3
    alert_manager.config.detection_persistence_ms = 100  # 100 ms window
    detections = [_make_detection()]

    alert_manager._should_trigger_persistent_alert(detections, time.time())
    alert_manager._should_trigger_persistent_alert(detections, time.time())
    assert alert_manager._consecutive_detections == 2

    # Sleep past persistence window — counter should reset to 1
    time.sleep(0.15)
    alert_manager._should_trigger_persistent_alert(detections, time.time())
    assert alert_manager._consecutive_detections == 1


def test_process_detections_skips_when_disabled(alert_manager):
    alert_manager.config.enabled = False
    with patch.object(alert_manager, "_trigger_alert_safe") as trigger:
        alert_manager.process_detections([_make_detection()], time.time())
        trigger.assert_not_called()


def test_process_detections_skips_when_emergency_disabled(alert_manager):
    alert_manager._alert_processing_enabled = False
    with patch.object(alert_manager, "_trigger_alert_safe") as trigger:
        alert_manager.process_detections([_make_detection()], time.time())
        trigger.assert_not_called()


def test_process_detections_no_valid_detections_resets_counter(alert_manager):
    alert_manager._consecutive_detections = 5
    alert_manager.process_detections([_make_detection(confidence=0.1)], time.time())
    assert alert_manager._consecutive_detections == 0


def test_process_detections_immediate_mode_triggers(alert_manager):
    alert_manager.config.require_consecutive_detections = False
    with patch.object(alert_manager, "_trigger_alert_safe") as trigger:
        alert_manager.process_detections([_make_detection()], time.time())
        trigger.assert_called_once()


def test_disable_and_enable_alert_processing(alert_manager):
    alert_manager.disable_alert_processing()
    assert alert_manager._alert_processing_enabled is False
    alert_manager.enable_alert_processing()
    assert alert_manager._alert_processing_enabled is True


def test_reset_statistics_clears_state(alert_manager):
    alert_manager.history.add_alert(1)
    alert_manager._consecutive_detections = 7
    alert_manager._last_detection_time = 1234
    alert_manager.reset_statistics()
    assert alert_manager.history.alerts == []
    assert alert_manager._consecutive_detections == 0
    assert alert_manager._last_detection_time == 0


def test_get_statistics_includes_config(alert_manager):
    stats = alert_manager.get_statistics()
    assert "config" in stats
    assert stats["config"]["enabled"] is True
    assert "consecutive_detections" in stats


def test_config_dict_matches_alert_type():
    with patch("core.services.AlertService.LoggerService"):
        mgr = AlertManager(config=AlertConfig(alert_type=AlertType.AUDIO_ONLY))
    cfg_dict = mgr._get_config_dict()
    assert cfg_dict["audio_enabled"] is True
    assert cfg_dict["visual_enabled"] is False


def test_update_config_emits_signal(alert_manager):
    new_cfg = AlertConfig(cooldown_ms=9999)
    received = []
    alert_manager.alertConfigChanged.connect(lambda d: received.append(d))
    alert_manager.update_config(new_cfg)
    assert alert_manager.config.cooldown_ms == 9999
    assert len(received) == 1
    assert received[0]["cooldown_ms"] == 9999


def test_trigger_alert_records_history_and_emits(alert_manager):
    detections = [_make_detection()]
    triggered = []
    alert_manager.alertTriggered.connect(lambda info, dets: triggered.append((info, dets)))

    alert_manager._trigger_alert(detections, time.time())

    assert len(alert_manager.history.alerts) == 1
    assert alert_manager._consecutive_detections == 0
    assert len(triggered) == 1
    assert triggered[0][0]["detection_count"] == 1


def test_process_detections_auto_disables_on_error(alert_manager):
    with patch.object(alert_manager, "_filter_detections", side_effect=RuntimeError("boom")):
        alert_manager.process_detections([_make_detection()], time.time())
    assert alert_manager._alert_processing_enabled is False
