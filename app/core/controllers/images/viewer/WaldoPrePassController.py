"""
WaldoPrePassController - Orchestrates the one-time WALDO metadata synthesis pass.

Hooks into the viewer's image-load sequence: detects WALDO folders by filename
prefix, builds a TerrainService configured against the user's preferred DEM
provider, opens a modal WaldoPrePassDialog and blocks until the synthesis
finishes (or the user cancels). After this returns, the standard ImageService
metadata path will read the synthesised drone-dji XMP fields written to disk.
"""

from typing import List

from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.waldo import WaldoMetadataService
from core.views.images.viewer.dialogs.WaldoPrePassDialog import WaldoPrePassDialog


class WaldoPrePassController:
    """Blocking-modal driver for WaldoMetadataService.process_folder."""

    def __init__(self, parent_viewer):
        self.parent = parent_viewer
        self.logger = LoggerService()
        self.settings_service = SettingsService()

    @staticmethod
    def is_waldo_folder(images: List[dict]) -> bool:
        """True if any image in the folder has a WALDO `0_*` / `1_*` filename prefix."""
        if not images:
            return False
        for img in images:
            path = img.get('path') or ''
            if WaldoMetadataService.is_waldo_image(path) is not None:
                return True
        return False

    def run_pre_pass_if_needed(self, images: List[dict]):
        """Open the modal pre-pass dialog if any WALDO image is not yet processed.

        Returns silently if there are no WALDO images, or if every WALDO image
        already has the current waldo:Processed marker.
        """
        if not self.is_waldo_folder(images):
            return

        # Quick scan: any WALDO image that is NOT already processed?
        any_pending = False
        waldo_paths: List[str] = []
        for img in images:
            path = img.get('path') or ''
            if WaldoMetadataService.is_waldo_image(path) is None:
                continue
            waldo_paths.append(path)
            if not any_pending and not WaldoMetadataService.is_already_processed(path):
                any_pending = True

        if not any_pending:
            self.logger.info("WaldoPrePassController: all WALDO images already processed.")
            return

        # Build a TerrainService that respects the configured provider preference.
        try:
            from core.services.terrain import TerrainService
            terrain_service = TerrainService(settings_service=self.settings_service)
        except Exception as e:
            self.logger.error(f"WaldoPrePassController: failed to init TerrainService - {e}")
            terrain_service = None

        service = WaldoMetadataService(terrain_service=terrain_service)
        dialog = WaldoPrePassDialog(self.parent, service, waldo_paths)
        dialog.exec()
        result = dialog.result_data
        self.logger.info(
            "WaldoPrePassController: processed=%d already_current=%d errors=%d cancelled=%s"
            % (result.processed, result.already_current, len(result.errors), result.cancelled)
        )
