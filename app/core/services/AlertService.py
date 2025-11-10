"""
AlertService.py - Real-time alert system for color detection

Provides audio and visual alerts for detected objects with configurable
thresholds and cooldown periods to prevent alert spam.
"""

# Set environment variable to avoid numpy._core issues - MUST be first
import os
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'

import time
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtWidgets import QSystemTrayIcon, QMessageBox, QApplication
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtMultimedia import QSound

from core.services.streaming.RealtimeColorDetectionService import Detection
from core.services.LoggerService import LoggerService


class AlertType(Enum):
    AUDIO_ONLY = "audio_only"
    VISUAL_ONLY = "visual_only"
    BOTH = "both"
    NONE = "none"


@dataclass
class AlertConfig:
    """Configuration for alert system."""
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
    """Tracks alert history for cooldown management."""

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.alerts = []  # List of (timestamp, detection_count) tuples
        self._lock = threading.Lock()

    def add_alert(self, detection_count: int):
        """Add alert to history."""
        with self._lock:
            timestamp = time.time()
            self.alerts.append((timestamp, detection_count))

            # Limit history size
            if len(self.alerts) > self.max_history:
                self.alerts = self.alerts[-self.max_history:]

    def get_last_alert_time(self) -> float:
        """Get timestamp of last alert."""
        with self._lock:
            if self.alerts:
                return self.alerts[-1][0]
            return 0.0

    def get_alert_count(self, time_window: float) -> int:
        """Get number of alerts in time window."""
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - time_window

            return sum(1 for timestamp, _ in self.alerts if timestamp >= cutoff_time)

    def get_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
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
    """
    Manages real-time alerts for color detection system.

    Features:
    - Audio alerts with system or custom sounds
    - Visual notifications (system tray, popups, window flashing)
    - Configurable thresholds and cooldowns
    - Alert history tracking
    - Prevention of alert spam
    """

    # Signals
    alertTriggered = Signal(dict, list)  # alert_info, detections
    alertConfigChanged = Signal(dict)  # new config
    statsChanged = Signal(dict)  # alert statistics

    def __init__(self, config: AlertConfig = None):
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

        self.logger.info("Alert manager initialized")

    def _init_audio_system(self) -> Optional[QSound]:
        """Initialize audio system for alerts."""
        try:
            if self.config.audio_file and os.path.exists(self.config.audio_file):
                return QSound(self.config.audio_file)
            else:
                # Use default system sound or built-in beep
                return None
        except Exception as e:
            self.logger.error(f"Error initializing audio system: {e}")
            return None

    def _init_system_tray(self):
        """Initialize system tray for notifications."""
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
        """Update alert configuration."""
        self.config = config

        # Reinitialize audio if needed
        if config.audio_file != getattr(self.config, 'audio_file', None):
            self._audio_system = self._init_audio_system()

        self.alertConfigChanged.emit(self._get_config_dict())
        self.logger.info("Alert configuration updated")

    def process_detections(self, detections: List[Detection], timestamp: float):
        """
        Process detections and trigger alerts if conditions are met.

        Args:
            detections: List of current detections
            timestamp: Detection timestamp
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
        """Filter detections based on alert thresholds."""
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
        """Check if persistent alert should be triggered."""
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
        """Check if immediate alert should be triggered."""
        return self._check_cooldown()

    def _check_cooldown(self) -> bool:
        """Check if cooldown period has passed."""
        current_time = time.time()
        last_alert_time = self.history.get_last_alert_time()

        return (current_time - last_alert_time) >= (self.config.cooldown_ms / 1000.0)

    def _trigger_alert_safe(self, detections: List[Detection], timestamp: float):
        """Trigger alert with timeout protection to prevent hanging."""
        try:
            # Use a separate thread to prevent blocking
            import threading

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
        """Trigger alert for detections."""
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

            self.logger.info(f"Alert triggered: {len(detections)} detections, confidence: {alert_info['avg_confidence']:.2f}")

        except Exception as e:
            self.logger.error(f"Error triggering alert: {e}")

    def _play_audio_alert(self):
        """Play audio alert."""
        try:
            if self._audio_system:
                # Play custom sound file with timeout protection
                try:
                    self._audio_system.play()
                except Exception as e:
                    self.logger.warning(f"Custom audio playback failed: {e}")
            elif self.config.use_system_sound:
                # Play system beep/sound with timeout protection
                try:
                    import winsound
                    # Use non-blocking system sound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                except ImportError:
                    # Fallback for non-Windows systems
                    try:
                        print('\a')  # Terminal bell
                    except Exception:
                        pass  # Even this can sometimes fail
                except Exception as e:
                    self.logger.warning(f"System sound failed: {e}")
        except Exception as e:
            self.logger.error(f"Error playing audio alert: {e}")

    def _show_visual_alert(self, alert_info: Dict[str, Any], detections: List[Detection]):
        """Show visual alert."""
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
                from PySide6.QtCore import QMetaObject, Qt
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
        """Create formatted alert message."""
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
        """Show popup message (must be called from main thread)."""
        try:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("ADIAT - Detection Alert")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec()
        except Exception as e:
            self.logger.error(f"Error showing popup: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        stats = self.history.get_stats()
        stats.update({
            'config': self._get_config_dict(),
            'consecutive_detections': self._consecutive_detections,
            'last_detection_time': self._last_detection_time
        })
        return stats

    def _get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
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
        """Reset alert statistics."""
        self.history = AlertHistory()
        self._consecutive_detections = 0
        self._last_detection_time = 0
        self.logger.info("Alert statistics reset")

    def test_alert(self):
        """Test alert system with dummy detection."""
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
            self.logger.info("Alert test initiated")

        except Exception as e:
            self.logger.error(f"Error testing alert: {e}")

    def disable_alert_processing(self):
        """Emergency disable of alert processing to prevent hangs."""
        self._alert_processing_enabled = False
        self.logger.warning("Alert processing has been disabled due to errors")

    def enable_alert_processing(self):
        """Re-enable alert processing."""
        self._alert_processing_enabled = True
        self.logger.info("Alert processing has been re-enabled")


# Convenience functions for common alert configurations

def create_audio_only_config(cooldown_ms: int = 2000, min_confidence: float = 0.5) -> AlertConfig:
    """Create audio-only alert configuration."""
    return AlertConfig(
        alert_type=AlertType.AUDIO_ONLY,
        cooldown_ms=cooldown_ms,
        min_confidence=min_confidence,
        show_system_notification=False,
        show_popup_window=False
    )


def create_visual_only_config(cooldown_ms: int = 3000, min_confidence: float = 0.6) -> AlertConfig:
    """Create visual-only alert configuration."""
    return AlertConfig(
        alert_type=AlertType.VISUAL_ONLY,
        cooldown_ms=cooldown_ms,
        min_confidence=min_confidence,
        use_system_sound=False,
        show_system_notification=True
    )


def create_persistent_alert_config(consecutive_count: int = 5, min_confidence: float = 0.7) -> AlertConfig:
    """Create configuration requiring persistent detections."""
    return AlertConfig(
        alert_type=AlertType.BOTH,
        require_consecutive_detections=True,
        consecutive_count=consecutive_count,
        min_confidence=min_confidence,
        cooldown_ms=5000
    )
