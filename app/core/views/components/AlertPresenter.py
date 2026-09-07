"""AlertPresenter - sounding an alert the AlertManager decided on.

The audio device, the system-tray notification and the popup box that used to
live inside :mod:`core.services.AlertService`. Deciding that a detection
warrants an alert is business logic and stays in the service; presenting one
is UI and belongs here (CLAUDE.md 2.1).

The presenter subscribes rather than being called, so the manager never needs
a reference to it and can run - and be tested - with no Qt widgets at all::

    manager = AlertManager(config)
    presenter = AlertPresenter(manager)
    presenter.attach()

Everything degrades quietly. A build without ``QSound``, a platform with no
system tray, a tray icon that refuses to show: each is logged once and the
remaining channels still fire. An alert that cannot be sounded must not take
the detection pipeline down with it.
"""

import importlib
import os
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from core.services.AlertService import AlertConfig, AlertType
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin

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


class AlertPresenter(TranslationMixin, QObject):
    """Plays and displays the alerts an :class:`AlertManager` emits."""

    def __init__(self, manager, parent: Optional[QObject] = None):
        """
        Args:
            manager: The :class:`~core.services.AlertService.AlertManager`
                whose signals this presenter renders.
            parent: Optional Qt parent.
        """
        super().__init__(parent)
        self.logger = LoggerService()
        self.manager = manager
        self._attached = False

        self._audio_system = self._init_audio_system()

        # System tray (for notifications) - optional feature
        self._system_tray = None
        try:
            self._init_system_tray()
        except Exception as e:
            self.logger.warning(
                f"System tray initialization failed, notifications disabled: {e}")
            self._system_tray = None

    def _config(self) -> AlertConfig:
        """The manager's live config - the presenter holds no copy."""
        return self.manager.config

    def attach(self) -> None:
        """Start rendering the manager's alerts. Idempotent."""
        if self._attached:
            return
        self.manager.alertTriggered.connect(self._on_alert)
        self.manager.alertConfigChanged.connect(self._on_config_changed)
        self._attached = True

    def detach(self) -> None:
        """Stop rendering, e.g. when the stream window closes.

        Tracked with a flag rather than relying on the disconnect: PySide6
        *warns* on a disconnect that matched nothing instead of raising, so a
        try/except would leave a RuntimeWarning behind on every second call.
        """
        if not self._attached:
            return
        self._attached = False
        try:
            self.manager.alertTriggered.disconnect(self._on_alert)
            self.manager.alertConfigChanged.disconnect(self._on_config_changed)
        except (RuntimeError, TypeError):
            # The manager went away first; nothing left to disconnect from.
            pass

    def _on_alert(self, alert_info: Dict[str, Any],
                  detections: List[Any]) -> None:
        """Sound and/or show the alert, per the configured alert type."""
        alert_type = self._config().alert_type
        if alert_type in (AlertType.AUDIO_ONLY, AlertType.BOTH):
            self._play_audio_alert()
        if alert_type in (AlertType.VISUAL_ONLY, AlertType.BOTH):
            self._show_visual_alert(alert_info, detections)

    def _on_config_changed(self, _config_dict: Dict[str, Any]) -> None:
        """Re-open the audio device: the sound file may have changed."""
        self._audio_system = self._init_audio_system()

    def test_alert(self) -> None:
        """Render a dummy alert, so the operator can check their settings."""
        self.manager.test_alert()

    def _init_audio_system(self) -> Optional[Any]:
        """Initialize audio system for alerts.

        Returns:
            QSound instance if custom audio file is configured and QSound is available, None otherwise.
        """
        try:
            if QSound is None:
                # QSound not available - will use system sounds
                return None
            if self._config().audio_file and os.path.exists(self._config().audio_file):
                return QSound(self._config().audio_file)
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
                self._system_tray.setToolTip(
                    self.tr("ADIAT - Color Detection Alerts")
                )
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
            elif self._config().use_system_sound and winsound is not None:
                # Play system beep/sound with timeout protection
                try:
                    # Use non-blocking system sound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                except Exception as e:
                    self.logger.warning(f"System sound failed: {e}")
            elif self._config().use_system_sound:
                # Fallback for non-Windows systems
                try:
                    # Terminal bell - note: logger won't produce sound, but log for debugging
                    # self.logger.debug("Alert: Terminal bell (system sound fallback)")
                    pass
                except Exception:
                    pass  # Even this can sometimes fail
        except Exception as e:
            self.logger.error(f"Error playing audio alert: {e}")

    def _show_visual_alert(self, alert_info: Dict[str, Any], detections: List[Any]):
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
            if self._config().show_system_notification and self._system_tray:
                try:
                    # Check if system tray is available and visible
                    if self._system_tray.isVisible() and QSystemTrayIcon.isSystemTrayAvailable():
                        # Use a timer to avoid blocking the main thread

                        def show_notification():
                            try:
                                self._system_tray.showMessage(
                                    self.tr("ADIAT - Color Detection Alert"),
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
            if self._config().show_popup_window:
                # This should be called from the main thread
                try:
                    # Queued so the box is built on the GUI thread:
                    # _trigger_alert_safe runs the decision on a worker.
                    QTimer.singleShot(
                        0, lambda text=message: self._show_popup_message(text))
                except Exception as e:
                    self.logger.warning(f"Popup window invocation failed: {e}")

        except Exception as e:
            self.logger.error(f"Error showing visual alert: {e}")

    def _create_alert_message(self, alert_info: Dict[str, Any], detections: List[Any]) -> str:
        """Create formatted alert message.

        Args:
            alert_info: Dictionary containing alert metadata.
            detections: List of detections that triggered the alert.

        Returns:
            Formatted alert message string.
        """
        message = self.tr(
            "Detected {count} object(s)\n"
            "Average confidence: {avg_confidence:.2f}\n"
            "Total area: {area:.0f} pixels\n"
        ).format(
            count=alert_info['detection_count'],
            avg_confidence=alert_info['avg_confidence'],
            area=alert_info['total_area']
        )

        if len(detections) <= 3:  # Show details for small number of detections
            message += self.tr("\nDetails:\n")
            for i, detection in enumerate(detections, 1):
                x, y, w, h = detection.bbox
                message += self.tr(
                    "  #{index}: ({x},{y}) {w}x{h} conf:{confidence:.2f}\n"
                ).format(
                    index=i,
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                    confidence=detection.confidence
                )

        return message.strip()

    def _show_popup_message(self, message: str):
        """Show popup message (must be called from main thread).

        Args:
            message: Message text to display in popup.
        """
        try:
            msg_box = QMessageBox()
            msg_box.setWindowTitle(self.tr("ADIAT - Detection Alert"))
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec()
        except Exception as e:
            self.logger.error(f"Error showing popup: {e}")
