"""AlertService.py - deciding when a detection is worth alerting on.

Applies the operator's thresholds - minimum confidence, minimum area,
cooldown, and an optional "must persist across N consecutive frames" rule -
and emits ``alertTriggered`` when they are met.

**Sounding the alert is not this class's job.** It used to be: it opened an
audio device, created a ``QSystemTrayIcon``, and put up a ``QMessageBox``,
all from ``app/core/services/`` where CLAUDE.md 2.1 reserves the layer for
business logic. The presentation moved to
:class:`~core.views.components.AlertPresenter.AlertPresenter`, which
subscribes to the signals below; this module is now Qt-free apart from
``QObject``/``Signal`` themselves.

Detections are duck-typed on purpose (``bbox``, ``area``, ``confidence``).
The concrete class lives in ``algorithms.streaming.ColorDetection``, and
importing it from here made ``core.services`` depend on an algorithm package
- the circular-import hazard CLAUDE.md 2.2.1 warns about.
"""

from core.services.LoggerService import LoggerService
from PySide6.QtCore import QObject, Signal
from enum import Enum
from dataclasses import dataclass
from types import SimpleNamespace
from typing import List, Dict, Any, Optional
from helpers.TranslationMixin import TranslationMixin
import threading
import time


class AlertType(Enum):
    AUDIO_ONLY = "audio_only"
    VISUAL_ONLY = "visual_only"
    BOTH = "both"
    NONE = "none"


@dataclass
class AlertConfig:
    """Configuration for alert system.

    Attributes:
        enabled: Whether alerts are enabled.
        alert_type: Type of alert (audio, visual, both, none).
        audio_file: Path to custom sound file.
        use_system_sound: Whether to use system sound.
        audio_volume: Audio volume (0.0 to 1.0).
        show_system_notification: Whether to show system tray notifications.
        show_popup_window: Whether to show popup windows.
        flash_window: Whether to flash the window.
        min_confidence: Minimum confidence to trigger alert.
        min_area: Minimum area to trigger alert.
        max_detections_per_alert: Limit detections shown in alert.
        cooldown_ms: Minimum time between alerts in milliseconds.
        detection_persistence_ms: How long detection must persist in milliseconds.
        require_consecutive_detections: Whether to require consecutive detections.
        consecutive_count: Number of consecutive detections required.
    """
    enabled: bool = True
    alert_type: AlertType = AlertType.BOTH

    # Audio settings
    audio_file: Optional[str] = None  # Path to custom sound file
    use_system_sound: bool = True
    audio_volume: float = 0.7  # 0.0 to 1.0

    # Visual settings
    show_system_notification: bool = True
    show_popup_window: bool = False
    flash_window: bool = True

    # Threshold settings
    min_confidence: float = 0.5  # Minimum confidence to trigger alert
    min_area: int = 500  # Minimum area to trigger alert
    max_detections_per_alert: int = 5  # Limit detections shown in alert

    # Timing settings
    cooldown_ms: int = 2000  # Minimum time between alerts
    detection_persistence_ms: int = 1000  # How long detection must persist

    # Advanced settings
    require_consecutive_detections: bool = True
    consecutive_count: int = 3


class AlertHistory:
    """Tracks alert history for cooldown management.

    Thread-safe history tracking for managing alert cooldowns and statistics.

    Attributes:
        max_history: Maximum number of alerts to keep in history.
        alerts: List of (timestamp, detection_count) tuples.
    """

    def __init__(self, max_history: int = 100):
        """Initialize alert history tracker.

        Args:
            max_history: Maximum number of alerts to keep in history. Defaults to 100.
        """
        self.max_history = max_history
        self.alerts = []  # List of (timestamp, detection_count) tuples
        # RLock because get_stats() holds the lock while calling get_alert_count(),
        # which also acquires it.
        self._lock = threading.RLock()

    def add_alert(self, detection_count: int):
        """Add alert to history.

        Args:
            detection_count: Number of detections in this alert.
        """
        with self._lock:
            timestamp = time.time()
            self.alerts.append((timestamp, detection_count))

            # Limit history size
            if len(self.alerts) > self.max_history:
                self.alerts = self.alerts[-self.max_history:]

    def get_last_alert_time(self) -> float:
        """Get timestamp of last alert.

        Returns:
            Timestamp of last alert, or 0.0 if no alerts.
        """
        with self._lock:
            if self.alerts:
                return self.alerts[-1][0]
            return 0.0

    def get_alert_count(self, time_window: float) -> int:
        """Get number of alerts in time window.

        Args:
            time_window: Time window in seconds to count alerts.

        Returns:
            Number of alerts in the specified time window.
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - time_window

            return sum(1 for timestamp, _ in self.alerts if timestamp >= cutoff_time)

    def get_stats(self) -> Dict[str, Any]:
        """Get alert statistics.

        Returns:
            Dictionary containing total alerts, average detections, last alert
            time, and alerts in last hour/minute.
        """
        with self._lock:
            if not self.alerts:
                return {'total_alerts': 0, 'avg_detections': 0, 'last_alert': None}

            total_alerts = len(self.alerts)
            avg_detections = sum(count for _, count in self.alerts) / total_alerts
            last_alert = self.alerts[-1][0]

            return {
                'total_alerts': total_alerts,
                'avg_detections': avg_detections,
                'last_alert': last_alert,
                'alerts_last_hour': self.get_alert_count(3600),
                'alerts_last_minute': self.get_alert_count(60)
            }


class AlertManager(TranslationMixin, QObject):
    """Manages real-time alerts for color detection system.

    Features:
    - Audio alerts with system or custom sounds
    - Visual notifications (system tray, popups, window flashing)
    - Configurable thresholds and cooldowns
    - Alert history tracking
    - Prevention of alert spam

    Attributes:
        alertTriggered: Signal emitted when alert is triggered (alert_info, detections).
        alertConfigChanged: Signal emitted when config changes (new config dict).
        statsChanged: Signal emitted when statistics change (stats dict).
    """

    # Signals
    alertTriggered = Signal(dict, list)  # alert_info, detections
    alertConfigChanged = Signal(dict)  # new config
    statsChanged = Signal(dict)  # alert statistics

    def __init__(self, config: AlertConfig = None):
        """Initialize the alert manager.

        Args:
            config: Alert configuration. If None, uses default AlertConfig.
        """
        super().__init__()
        self.logger = LoggerService()

        # Configuration
        self.config = config or AlertConfig()

        # Alert state
        self.history = AlertHistory()
        self._consecutive_detections = 0
        self._last_detection_time = 0
        self._alert_processing_enabled = True  # Emergency disable flag

        # No audio device and no system tray here. Deciding that an alert
        # is warranted is this class's job; sounding it is
        # AlertPresenter's, which subscribes to alertTriggered - see the
        # module docstring.

        # Detection tracking for persistence
        self._detection_buffer = []
        self._buffer_lock = threading.Lock()

        # self.logger.info("Alert manager initialized")

    def update_config(self, config: AlertConfig):
        """Update alert configuration.

        Args:
            config: New alert configuration to apply.
        """
        self.config = config
        # alertConfigChanged is how the presenter learns to re-open its
        # audio device; this class no longer owns one.
        self.alertConfigChanged.emit(self._get_config_dict())
        # self.logger.info("Alert configuration updated")

    def process_detections(self, detections: List[Any], timestamp: float):
        """Process detections and trigger alerts if conditions are met.

        Filters detections by thresholds, checks persistence requirements,
        and triggers alerts if cooldown period has passed.

        Args:
            detections: List of current detections.
            timestamp: Detection timestamp.
        """
        try:
            if not self.config.enabled or not self._alert_processing_enabled:
                return

            # Simplified alert processing to prevent hanging
            # Filter detections by threshold
            valid_detections = self._filter_detections(detections)

            if not valid_detections:
                self._consecutive_detections = 0
                return

            # Check persistence requirement
            if self.config.require_consecutive_detections:
                if self._should_trigger_persistent_alert(valid_detections, timestamp):
                    self._trigger_alert_safe(valid_detections, timestamp)
            else:
                # Check cooldown and trigger immediately
                if self._should_trigger_immediate_alert(valid_detections, timestamp):
                    self._trigger_alert_safe(valid_detections, timestamp)

        except Exception as e:
            self.logger.error(f"Error processing detections for alerts: {e}")
            # Auto-disable alerts if they're causing problems
            self.disable_alert_processing()

    def _filter_detections(self, detections: List[Any]) -> List[Any]:
        """Filter detections based on alert thresholds.

        Args:
            detections: List of detections to filter.

        Returns:
            Filtered list of detections that meet confidence and area thresholds.
        """
        valid_detections = []

        for detection in detections:
            # Check confidence threshold
            if detection.confidence < self.config.min_confidence:
                continue

            # Check area threshold
            if detection.area < self.config.min_area:
                continue

            valid_detections.append(detection)

        # Limit number of detections
        return valid_detections[:self.config.max_detections_per_alert]

    def _should_trigger_persistent_alert(self, detections: List[Any], timestamp: float) -> bool:
        """Check if persistent alert should be triggered.

        Args:
            detections: List of current detections.
            timestamp: Detection timestamp.

        Returns:
            True if alert should be triggered based on consecutive detection
            count and cooldown period.
        """
        current_time = time.time()

        # Update consecutive detection counter
        if current_time - self._last_detection_time <= (self.config.detection_persistence_ms / 1000.0):
            self._consecutive_detections += 1
        else:
            self._consecutive_detections = 1

        self._last_detection_time = current_time

        # Check if we have enough consecutive detections
        if self._consecutive_detections < self.config.consecutive_count:
            return False

        # Check cooldown
        return self._check_cooldown()

    def _should_trigger_immediate_alert(self, detections: List[Any], timestamp: float) -> bool:
        """Check if immediate alert should be triggered.

        Args:
            detections: List of current detections.
            timestamp: Detection timestamp.

        Returns:
            True if cooldown period has passed.
        """
        return self._check_cooldown()

    def _check_cooldown(self) -> bool:
        """Check if cooldown period has passed.

        Returns:
            True if enough time has passed since last alert.
        """
        current_time = time.time()
        last_alert_time = self.history.get_last_alert_time()

        return (current_time - last_alert_time) >= (self.config.cooldown_ms / 1000.0)

    def _trigger_alert_safe(self, detections: List[Any], timestamp: float):
        """Trigger alert with timeout protection to prevent hanging.

        Uses a background thread to trigger alerts, preventing blocking of
        the main processing thread.

        Args:
            detections: List of detections that triggered the alert.
            timestamp: Detection timestamp.
        """
        try:
            # Use a separate thread to prevent blocking
            def alert_worker():
                try:
                    self._trigger_alert(detections, timestamp)
                except Exception as e:
                    self.logger.error(f"Error in alert worker thread: {e}")

            # Start alert in background thread with daemon flag to prevent hanging on exit
            alert_thread = threading.Thread(target=alert_worker, daemon=True)
            alert_thread.start()

            # Don't wait for thread to complete - fire and forget

        except Exception as e:
            self.logger.error(f"Error in safe alert trigger: {e}")

    def _trigger_alert(self, detections: List[Any], timestamp: float):
        """Trigger alert for detections.

        Plays audio and/or visual alerts, records in history, and emits signals.

        Args:
            detections: List of detections that triggered the alert.
            timestamp: Detection timestamp.
        """
        try:
            # Create alert info
            alert_info = {
                'timestamp': timestamp,
                'detection_count': len(detections),
                'total_area': sum(d.area for d in detections),
                'avg_confidence': sum(d.confidence for d in detections) / len(detections),
                'max_confidence': max(d.confidence for d in detections),
                'alert_type': self.config.alert_type.value
            }

            # Record in history
            self.history.add_alert(len(detections))

            # Reset consecutive counter
            self._consecutive_detections = 0

            # Emit signal
            self.alertTriggered.emit(alert_info, detections)

            # Update statistics
            stats = self.history.get_stats()
            stats.update(alert_info)
            self.statsChanged.emit(stats)

            # self.logger.info(f"Alert triggered: {len(detections)} detections, confidence: {alert_info['avg_confidence']:.2f}")

        except Exception as e:
            self.logger.error(f"Error triggering alert: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics.

        Returns:
            Dictionary containing alert history statistics and current configuration.
        """
        stats = self.history.get_stats()
        stats.update({
            'config': self._get_config_dict(),
            'consecutive_detections': self._consecutive_detections,
            'last_detection_time': self._last_detection_time
        })
        return stats

    def _get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary.

        Returns:
            Dictionary representation of current alert configuration.
        """
        return {
            'enabled': self.config.enabled,
            'alert_type': self.config.alert_type.value,
            'min_confidence': self.config.min_confidence,
            'min_area': self.config.min_area,
            'cooldown_ms': self.config.cooldown_ms,
            'audio_enabled': self.config.alert_type in [AlertType.AUDIO_ONLY, AlertType.BOTH],
            'visual_enabled': self.config.alert_type in [AlertType.VISUAL_ONLY, AlertType.BOTH],
            'require_consecutive': self.config.require_consecutive_detections,
            'consecutive_count': self.config.consecutive_count
        }

    def reset_statistics(self):
        """Reset alert statistics.

        Clears alert history and resets counters.
        """
        self.history = AlertHistory()
        self._consecutive_detections = 0
        self._last_detection_time = 0
        # self.logger.info("Alert statistics reset")

    def test_alert(self):
        """Test alert system with dummy detection.

        Creates a dummy detection and triggers an alert to test the system.
        """
        try:
            # Create dummy detection for testing
            dummy_detection = SimpleNamespace(
                bbox=(100, 100, 50, 50),
                centroid=(125, 125),
                area=2500,
                confidence=0.9,
                timestamp=time.time(),
                contour=None,
            )

            # Use safe trigger to prevent hanging
            self._trigger_alert_safe([dummy_detection], time.time())
            # self.logger.info("Alert test initiated")

        except Exception as e:
            self.logger.error(f"Error testing alert: {e}")

    def disable_alert_processing(self):
        """Emergency disable of alert processing to prevent hangs.

        Disables alert processing if errors are detected to prevent system
        hangs or blocking.
        """
        self._alert_processing_enabled = False
        self.logger.warning("Alert processing has been disabled due to errors")

    def enable_alert_processing(self):
        """Re-enable alert processing.

        Re-enables alert processing after it has been disabled.
        """
        self._alert_processing_enabled = True
        # self.logger.info("Alert processing has been re-enabled")


# Convenience functions for common alert configurations

def create_audio_only_config(cooldown_ms: int = 2000, min_confidence: float = 0.5) -> AlertConfig:
    """Create audio-only alert configuration.

    Args:
        cooldown_ms: Cooldown period in milliseconds. Defaults to 2000.
        min_confidence: Minimum confidence threshold. Defaults to 0.5.

    Returns:
        AlertConfig configured for audio-only alerts.
    """
    return AlertConfig(
        alert_type=AlertType.AUDIO_ONLY,
        cooldown_ms=cooldown_ms,
        min_confidence=min_confidence,
        show_system_notification=False,
        show_popup_window=False
    )


def create_visual_only_config(cooldown_ms: int = 3000, min_confidence: float = 0.6) -> AlertConfig:
    """Create visual-only alert configuration.

    Args:
        cooldown_ms: Cooldown period in milliseconds. Defaults to 3000.
        min_confidence: Minimum confidence threshold. Defaults to 0.6.

    Returns:
        AlertConfig configured for visual-only alerts.
    """
    return AlertConfig(
        alert_type=AlertType.VISUAL_ONLY,
        cooldown_ms=cooldown_ms,
        min_confidence=min_confidence,
        use_system_sound=False,
        show_system_notification=True
    )


def create_persistent_alert_config(consecutive_count: int = 5, min_confidence: float = 0.7) -> AlertConfig:
    """Create configuration requiring persistent detections.

    Args:
        consecutive_count: Number of consecutive detections required. Defaults to 5.
        min_confidence: Minimum confidence threshold. Defaults to 0.7.

    Returns:
        AlertConfig configured for persistent detection alerts.
    """
    return AlertConfig(
        alert_type=AlertType.BOTH,
        require_consecutive_detections=True,
        consecutive_count=consecutive_count,
        min_confidence=min_confidence,
        cooldown_ms=5000
    )
