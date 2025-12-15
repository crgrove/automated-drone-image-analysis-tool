"""
AlertService.py - Real-time alert system for color detection

Provides audio and visual alerts for detected objects with configurable
thresholds and cooldown periods to prevent alert spam.
"""

# Set environment variable to avoid numpy._core issues - MUST be first
from core.services.LoggerService import LoggerService
from algorithms.streaming.ColorDetection.services import Detection
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QSystemTrayIcon, QMessageBox, QApplication
from PySide6.QtCore import QObject, QTimer, Signal, Qt, QMetaObject
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import threading
import time
import os
import importlib

# QSound is optional - may not be available in all PySide6 builds
QSound = None
try:
    from PySide6.QtMultimedia import QSound
except ImportError:
    # QSound not available - audio alerts will use system sounds only
    pass

winsound = None
try:
    winsound = importlib.import_module("winsound")
except ImportError:
    winsound = None
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'


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
        self._lock = threading.Lock()

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


class AlertManager(QObject):
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

        # Audio system
        self._audio_system = self._init_audio_system()

        # System tray (for notifications) - optional feature
        self._system_tray = None
        try:
            self._init_system_tray()
        except Exception as e:
            self.logger.warning(f"System tray initialization failed, notifications disabled: {e}")
            self._system_tray = None

        # Detection tracking for persistence
        self._detection_buffer = []
        self._buffer_lock = threading.Lock()

        # self.logger.info("Alert manager initialized")

    def _init_audio_system(self) -> Optional[Any]:
        """Initialize audio system for alerts.

        Returns:
            QSound instance if custom audio file is configured and QSound is available, None otherwise.
        """
        try:
            if QSound is None:
                # QSound not available - will use system sounds
                return None
            if self.config.audio_file and os.path.exists(self.config.audio_file):
                return QSound(self.config.audio_file)
            else:
                # Use default system sound or built-in beep
                return None
        except Exception as e:
            self.logger.error(f"Error initializing audio system: {e}")
            return None

    def _init_system_tray(self):
        """Initialize system tray for notifications.

        Sets up system tray icon for displaying notifications. Handles
        platform-specific differences and fallbacks gracefully.
        """
        try:
            # Check if system tray is supported on this platform
            if not QSystemTrayIcon.isSystemTrayAvailable():
                self.logger.warning("System tray not available on this platform")
                self._system_tray = None
                return

            # Create basic system tray icon
            self._system_tray = QSystemTrayIcon()

            app = QApplication.instance()
            if app:
                try:
                    style = app.style()
                    icon = style.standardIcon(style.SP_ComputerIcon)
                    self._system_tray.setIcon(icon)
                except Exception as e:
                    self.logger.warning(f"Failed to set system tray icon from style: {e}")
                    # Create a simple fallback icon
                    pixmap = QPixmap(16, 16)
                    pixmap.fill(Qt.blue)
                    icon = QIcon(pixmap)
                    self._system_tray.setIcon(icon)
            else:
                # Fallback: create a simple default icon
                pixmap = QPixmap(16, 16)
                pixmap.fill(Qt.gray)
                icon = QIcon(pixmap)
                self._system_tray.setIcon(icon)

            # Set tooltip
            try:
                self._system_tray.setToolTip("ADIAT - Color Detection Alerts")
            except Exception as e:
                self.logger.warning(f"Failed to set system tray tooltip: {e}")

            # Show the tray icon (this can sometimes fail)
            try:
                self._system_tray.show()
                # Verify it's actually visible
                if not self._system_tray.isVisible():
                    self.logger.warning("System tray icon not visible after show()")
            except Exception as e:
                self.logger.warning(f"Failed to show system tray icon: {e}")
                self._system_tray = None

        except Exception as e:
            self.logger.error(f"Error initializing system tray: {e}")
            self._system_tray = None

    def update_config(self, config: AlertConfig):
        """Update alert configuration.

        Args:
            config: New alert configuration to apply.
        """
        self.config = config

        # Reinitialize audio if needed
        if config.audio_file != getattr(self.config, 'audio_file', None):
            self._audio_system = self._init_audio_system()

        self.alertConfigChanged.emit(self._get_config_dict())
        # self.logger.info("Alert configuration updated")

    def process_detections(self, detections: List[Detection], timestamp: float):
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

    def _filter_detections(self, detections: List[Detection]) -> List[Detection]:
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

    def _should_trigger_persistent_alert(self, detections: List[Detection], timestamp: float) -> bool:
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

    def _should_trigger_immediate_alert(self, detections: List[Detection], timestamp: float) -> bool:
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

    def _trigger_alert_safe(self, detections: List[Detection], timestamp: float):
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

    def _trigger_alert(self, detections: List[Detection], timestamp: float):
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

            # Trigger audio alert
            if self.config.alert_type in [AlertType.AUDIO_ONLY, AlertType.BOTH]:
                self._play_audio_alert()

            # Trigger visual alert
            if self.config.alert_type in [AlertType.VISUAL_ONLY, AlertType.BOTH]:
                self._show_visual_alert(alert_info, detections)

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

    def _play_audio_alert(self):
        """Play audio alert.

        Attempts to play custom sound file or system sound based on configuration.
        Handles errors gracefully to prevent blocking.
        """
        try:
            if self._audio_system:
                # Play custom sound file with timeout protection
                try:
                    self._audio_system.play()
                except Exception as e:
                    self.logger.warning(f"Custom audio playback failed: {e}")
            elif self.config.use_system_sound and winsound is not None:
                # Play system beep/sound with timeout protection
                try:
                    # Use non-blocking system sound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                except Exception as e:
                    self.logger.warning(f"System sound failed: {e}")
            elif self.config.use_system_sound:
                # Fallback for non-Windows systems
                try:
                    # Terminal bell - note: logger won't produce sound, but log for debugging
                    # self.logger.debug("Alert: Terminal bell (system sound fallback)")
                    pass
                except Exception:
                    pass  # Even this can sometimes fail
        except Exception as e:
            self.logger.error(f"Error playing audio alert: {e}")

    def _show_visual_alert(self, alert_info: Dict[str, Any], detections: List[Detection]):
        """Show visual alert.

        Displays system tray notifications and/or popup windows based on
        configuration.

        Args:
            alert_info: Dictionary containing alert metadata.
            detections: List of detections that triggered the alert.
        """
        try:
            # Create alert message
            message = self._create_alert_message(alert_info, detections)

            # System tray notification with timeout protection
            if self.config.show_system_notification and self._system_tray:
                try:
                    # Check if system tray is available and visible
                    if self._system_tray.isVisible() and QSystemTrayIcon.isSystemTrayAvailable():
                        # Use a timer to avoid blocking the main thread

                        def show_notification():
                            try:
                                self._system_tray.showMessage(
                                    "ADIAT - Color Detection Alert",
                                    message,
                                    QSystemTrayIcon.Information,
                                    3000  # Reduced timeout
                                )
                            except Exception as e:
                                self.logger.warning(f"System tray notification failed: {e}")

                        QTimer.singleShot(0, show_notification)
                    else:
                        self.logger.warning("System tray not available for notifications")
                except Exception as e:
                    self.logger.warning(f"System tray notification error: {e}")

            # Popup window
            if self.config.show_popup_window:
                # This should be called from the main thread
                try:
                    QMetaObject.invokeMethod(
                        self,
                        "_show_popup_message",
                        Qt.QueuedConnection,
                        message
                    )
                except Exception as e:
                    self.logger.warning(f"Popup window invocation failed: {e}")

        except Exception as e:
            self.logger.error(f"Error showing visual alert: {e}")

    def _create_alert_message(self, alert_info: Dict[str, Any], detections: List[Detection]) -> str:
        """Create formatted alert message.

        Args:
            alert_info: Dictionary containing alert metadata.
            detections: List of detections that triggered the alert.

        Returns:
            Formatted alert message string.
        """
        message = f"Detected {alert_info['detection_count']} object(s)\n"
        message += f"Average confidence: {alert_info['avg_confidence']:.2f}\n"
        message += f"Total area: {alert_info['total_area']:.0f} pixels\n"

        if len(detections) <= 3:  # Show details for small number of detections
            message += "\nDetails:\n"
            for i, detection in enumerate(detections, 1):
                x, y, w, h = detection.bbox
                message += f"  #{i}: ({x},{y}) {w}x{h} conf:{detection.confidence:.2f}\n"

        return message.strip()

    def _show_popup_message(self, message: str):
        """Show popup message (must be called from main thread).

        Args:
            message: Message text to display in popup.
        """
        try:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("ADIAT - Detection Alert")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec()
        except Exception as e:
            self.logger.error(f"Error showing popup: {e}")

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
            dummy_detection = Detection(
                bbox=(100, 100, 50, 50),
                centroid=(125, 125),
                area=2500,
                confidence=0.9,
                timestamp=time.time(),
                contour=None
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
