from typing import Optional

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog

from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.UpdateService import UpdateRelease, UpdateService
from helpers.FormatHelper import FormatHelper


class UpdateController(QObject):
    """UI orchestration for startup update checks and manual installer download."""

    STARTUP_CHECK_PROPERTY = "adiat_update_check_completed"

    def __init__(
        self,
        parent,
        update_service: Optional[UpdateService] = None,
        settings_service: Optional[SettingsService] = None
    ):
        super().__init__(parent)
        self.parent = parent
        self.logger = LoggerService()
        self.settings_service = settings_service or getattr(parent, "settings_service", SettingsService())
        self.update_service = update_service or UpdateService(
            app_version=getattr(parent, "app_version", "")
        )
        self.action: Optional[QAction] = None

    def bind_action(self, action: QAction) -> None:
        """Attach the manual update-check action."""
        self.action = action
        # QAction.triggered emits a `checked` bool; connecting check_for_updates
        # directly would pass that False into `interactive` and suppress every
        # user-facing dialog (incl. "No Updates Available"). Wrap it so the
        # manual menu check always runs interactively.
        self.action.triggered.connect(lambda _checked=False: self.check_for_updates(interactive=True))
        self.refresh_action_state()

    def refresh_action_state(self) -> None:
        """Enable or disable the action based on Offline Only mode."""
        if not self.action:
            return

        offline_only = self._is_offline_only()
        self.action.setEnabled(not offline_only)
        if offline_only:
            self.action.setToolTip(
                self.tr("Disabled while Offline Only mode is enabled.")
            )
        else:
            self.action.setToolTip(
                self.tr("Check the update feed for a newer ADIAT installer.")
            )

    def schedule_startup_check(self) -> bool:
        """Queue a single update check for this application session."""
        self.refresh_action_state()

        if not self._is_auto_check_enabled() or self._is_offline_only():
            return False

        app = QApplication.instance()
        if app is None:
            return False

        if bool(app.property(self.STARTUP_CHECK_PROPERTY)):
            return False

        app.setProperty(self.STARTUP_CHECK_PROPERTY, True)
        QTimer.singleShot(0, lambda: self.check_for_updates(interactive=False))
        return True

    def check_for_updates(self, interactive: bool = True):
        """Check the feed, prompt for an update, and optionally launch the installer."""
        self.refresh_action_state()

        if self._is_offline_only():
            if interactive:
                QMessageBox.information(
                    self.parent,
                    self.tr("Updates Disabled"),
                    self.tr(
                        "Update checks are disabled while Offline Only mode is enabled."
                    ),
                )
            return None

        current_version = getattr(self.parent, "app_version", None) or self.settings_service.get_setting("app_version", "0.0.0")

        try:
            release = self.update_service.get_latest_available_release(current_version)
        except Exception as exc:
            self.logger.warning(f"Error checking for updates: {exc}")
            if interactive:
                QMessageBox.warning(
                    self.parent,
                    self.tr("Update Check Failed"),
                    self.tr("Unable to check for updates:\n{error}").format(error=str(exc)),
                )
            return None

        if release is None:
            if interactive:
                QMessageBox.information(
                    self.parent,
                    self.tr("No Updates Available"),
                    self.tr(
                        "You are already running the latest available version of ADIAT."
                    ),
                )
            return None

        if not self._prompt_to_install(release, current_version):
            return None

        installer_path = self._download_release(release)
        if not installer_path:
            return None

        try:
            self.update_service.launch_installer(installer_path)
        except Exception as exc:
            self.logger.error(f"Error launching installer: {exc}")
            QMessageBox.warning(
                self.parent,
                self.tr("Installer Launch Failed"),
                self.tr("The installer was downloaded but could not be launched:\n{error}").format(error=str(exc)),
            )
            return None

        QMessageBox.information(
            self.parent,
            self.tr("Installer Started"),
            self.tr(
                "The installer has been launched. Close ADIAT when you are ready to continue the update."
            ),
        )
        return installer_path

    def _prompt_to_install(self, release: UpdateRelease, current_version: str) -> bool:
        """Prompt the user to download and install the new release."""
        dialog = QMessageBox(self.parent)
        dialog.setIcon(QMessageBox.Information)
        dialog.setWindowTitle(self.tr("Update Available"))
        dialog.setText(
            self.tr("ADIAT {new_version} is available. You are running {current_version}.").format(
                new_version=release.version,
                current_version=current_version,
            )
        )

        details = release.notes.strip() or self.tr("Do you want to download and launch the installer now?")
        dialog.setInformativeText(details)

        install_button = dialog.addButton(self.tr("Download and Install"), QMessageBox.AcceptRole)
        dialog.addButton(QMessageBox.Cancel)
        dialog.exec()

        return dialog.clickedButton() is install_button

    def _download_release(self, release: UpdateRelease) -> Optional[str]:
        """Download the installer while updating an indeterminate/modal progress dialog."""
        progress = QProgressDialog(
            self.tr("Downloading ADIAT {version}...").format(version=release.version),
            self.tr("Cancel"),
            0,
            0,
            self.parent,
        )
        progress.setWindowTitle(self.tr("Downloading Update"))
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.show()
        QApplication.processEvents()

        last_total = {"value": 0}

        def _on_progress(downloaded: int, total: int) -> None:
            if total > 0 and total != last_total["value"]:
                last_total["value"] = total
                progress.setRange(0, total)
            if total > 0:
                progress.setValue(downloaded)
            downloaded_display = self.tr("{value} MB").format(value=FormatHelper.format_megabytes(downloaded))
            total_display = (
                self.tr("{value} MB").format(value=FormatHelper.format_megabytes(total))
                if total > 0 else self.tr("unknown")
            )
            progress.setLabelText(
                self.tr("Downloading ADIAT {version}...\n{downloaded} of {total}").format(
                    version=release.version,
                    downloaded=downloaded_display,
                    total=total_display,
                )
            )
            QApplication.processEvents()
            if progress.wasCanceled():
                raise RuntimeError(self.tr("Update download canceled."))

        try:
            installer_path = self.update_service.download_release(release, progress_callback=_on_progress)
        except Exception as exc:
            progress.close()
            if str(exc) == self.tr("Update download canceled."):
                return None
            self.logger.error(f"Error downloading update: {exc}")
            QMessageBox.warning(
                self.parent,
                self.tr("Download Failed"),
                self.tr("Unable to download the update installer:\n{error}").format(error=str(exc)),
            )
            return None

        progress.setValue(progress.maximum())
        progress.close()
        return installer_path

    def _is_offline_only(self) -> bool:
        """Return whether Offline Only mode is enabled."""
        return self.settings_service.get_bool_setting("OfflineOnly", False)

    def _is_auto_check_enabled(self) -> bool:
        """Return whether startup update checks are enabled."""
        return self.settings_service.get_bool_setting("AutoCheckForUpdates", False)
