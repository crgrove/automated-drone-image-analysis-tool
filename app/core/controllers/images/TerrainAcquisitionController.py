"""Run terrain acquisition off the UI thread, from any trigger point.

The one place the app starts a terrain download. Every trigger — an
analysis pass, opening a viewer, running an export — calls
:meth:`TerrainAcquisitionController.ensure` and gets identical behaviour,
because the decision itself lives in
:class:`~core.services.terrain.TerrainAcquisitionService.TerrainAcquisitionService`
and the same gates apply regardless of who asked.

This class adds only what a service must not: a thread, cancellation tied
to the caller's lifetime, and a message for the operator. It knows nothing
about elevation sources.

**Unobtrusive by construction.** Fire-and-forget: no dialog, no modal
progress, no return value the caller has to handle. Callers do not wait,
and a caller that goes away simply cancels. A skip is reported once, in
the message pane, because "terrain got better" and "terrain is unchanged"
are worth telling apart — and the reason (offline, off, over the size
limit) is actionable.
"""

import glob
import os

from PySide6.QtCore import QObject, QThread, Signal

from core.services.LoggerService import LoggerService
from core.services.terrain.TerrainAcquisitionService import (
    TRIGGER_ANALYSIS,
    TerrainAcquisitionService,
)

# Extensions the analysis pass itself accepts. Case-variant globs because
# only Windows matches case-insensitively.
_IMAGE_GLOBS = ('*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.png', '*.PNG',
                '*.tif', '*.TIF', '*.tiff', '*.TIFF')

# Skips worth a line in the message pane. The rest - already covered,
# already attempted, a source needing no download - are the normal quiet
# case and would be noise on every viewer open and every export.
_REPORTABLE_SKIPS = ('exceeds', 'connectivity', 'offline')


class _AcquisitionWorker(QThread):
    """Downloads on its own thread; cancellable between images and tiles."""

    message = Signal(str)

    def __init__(self, service, images, bounds, trigger, parent=None):
        super().__init__(parent)
        self._service = service
        self._images = images
        self._bounds = bounds
        self._trigger = trigger
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            outcome = self._service.run(
                images=self._images, bounds=self._bounds, trigger=self._trigger,
                cancel_check=lambda: self._cancelled,
            )
        except Exception as e:  # noqa: BLE001 - a caller must never fail on this
            self.message.emit(f"Elevation download failed: {e}")
            return
        if outcome.cancelled or self._cancelled:
            return
        if outcome.acquired:
            source = outcome.plan.detail if outcome.plan else "elevation"
            self.message.emit(
                f"Downloaded {outcome.tiles_written} {source} elevation "
                f"tile(s) for this area."
            )
        elif outcome.skipped_reason and any(
                token in outcome.skipped_reason for token in _REPORTABLE_SKIPS):
            self.message.emit(
                f"Elevation download skipped: {outcome.skipped_reason}")


class TerrainAcquisitionController(QObject):
    """Starts and cancels one acquisition attempt for one caller."""

    message = Signal(str)

    def __init__(self, parent=None, settings_service=None, logger=None):
        super().__init__(parent)
        self.logger = logger or LoggerService()
        self.settings_service = settings_service
        self._worker = None

    def ensure(self, images=None, bounds=None, input_folder=None,
               trigger: str = TRIGGER_ANALYSIS) -> bool:
        """Stock elevation data for an area, if anything needs doing.

        Accepts whichever description of the area the caller happens to
        have, so no call site has to convert: image records, an explicit
        bounding box, or a folder to scan.

        Args:
            images (list[dict], optional): Records carrying ``path``.
            bounds (tuple, optional): ``(min_lon, min_lat, max_lon, max_lat)``.
            input_folder (str, optional): Folder to collect images from.
            trigger (str): One of the service's ``TRIGGER_*`` constants.

        Returns:
            bool: True when a download was started. False - quietly, with
            nothing logged as an error - when the gates said no, there is
            no area to work from, or startup failed.
        """
        self._worker = None
        try:
            service = TerrainAcquisitionService(
                settings_service=self.settings_service, logger=self.logger)
            if not service.enabled():
                return False
            if images is None and bounds is None:
                images = self._images_in(input_folder)
            if not images and bounds is None:
                return False
            worker = _AcquisitionWorker(service, images, bounds, trigger,
                                        parent=self)
            worker.message.connect(self.message)
            worker.finished.connect(self._on_finished)
            self._worker = worker
            worker.start()
            return True
        except Exception as e:  # noqa: BLE001 - never break the caller
            self.logger.warning(f"Could not start terrain acquisition: {e}")
            self._worker = None
            return False

    def cancel(self):
        """Abandon an in-flight download. Safe when none is running."""
        if self._worker is not None:
            self._worker.cancel()

    def wait(self, msecs: int = 2000):
        """Give a cancelled download a moment to unwind. Safe when idle."""
        worker = self._worker
        if worker is not None and worker.isRunning():
            worker.wait(msecs)

    @staticmethod
    def stop_all(owner):
        """Cancel every download started for ``owner`` and wait for each to end.

        For the owner's close. Qt deletes a window's children with it, and
        deleting a thread that is still running aborts the whole process, so
        the wait has no time limit. It is short: planning and downloading
        check for cancellation between images and between tiles.

        Args:
            owner (QObject): The window the controllers were parented to.
        """
        workers = owner.findChildren(_AcquisitionWorker)
        for worker in workers:
            worker.cancel()
        for worker in workers:
            worker.wait()

    @staticmethod
    def _images_in(input_folder):
        """Image records for a folder; only ``path`` is needed.

        The service reads GPS from EXIF itself, the same way the manual
        download dialog fills its area of interest.
        """
        if not input_folder or not os.path.isdir(input_folder):
            return []
        paths = []
        for pattern in _IMAGE_GLOBS:
            paths.extend(glob.glob(os.path.join(input_folder, pattern)))
        return [{'path': path} for path in sorted(set(paths))]

    def _on_finished(self):
        self._worker = None
