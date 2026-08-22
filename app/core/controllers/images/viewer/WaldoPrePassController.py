"""
WaldoPrePassController - Orchestrates the one-time WALDO metadata synthesis pass.

Hooks into the viewer's image-load sequence: detects WALDO folders by filename
prefix, builds a TerrainService configured against the user's preferred DEM
provider, opens a modal WaldoPrePassDialog and blocks until the synthesis
finishes (or the user cancels). After this returns, the standard ImageService
metadata path will read the synthesised drone-dji XMP fields written to disk.

Also drives the operator-confirmed camera clock correction: when the pre-pass
audit detects the known clock-fault signature, a confirmation dialog offers a
non-destructive corrected capture time (stamped in the waldo XMP namespace).
The per-folder decision is remembered in settings.
"""

import os
from typing import List, Optional

from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.waldo import WaldoMetadataService
from core.services.waldo import WaldoClockDecisions
from core.services.waldo import WaldoFlightLogDecisions
from core.services.waldo.WaldoClockDecisions import CLOCK_DECISIONS_SETTING
from core.services.waldo.WaldoFlightLog import WaldoFlightLogService
from core.views.images.viewer.dialogs.WaldoPrePassDialog import WaldoPrePassDialog
from core.views.images.viewer.dialogs.WaldoClockCorrectionDialog import WaldoClockCorrectionDialog
from core.views.images.viewer.dialogs.WaldoFlightLogDialog import WaldoFlightLogDialog


def invalidate_attitude_caches(viewer):
    """Best-effort invalidation of caches built from stamped attitude XMP.

    Needed after a MID-SESSION restamp (manual flight-log attach or clock
    amendment while the viewer is open): ImageService parses XMP once at
    construction, the GPS map caches per-image bearings and FOV parameters,
    and POD coverage products fingerprint only terrain settings - none of
    them notice the files changing underneath. Folder-open restamps run
    before any of these exist, so this is a no-op there.
    """
    if viewer is None:
        return
    if hasattr(viewer, 'current_image_service'):
        viewer.current_image_service = None
    pod_cache = getattr(viewer, 'pod_result_cache', None)
    if pod_cache is not None:
        try:
            pod_cache.invalidate()
        except Exception:
            pass
    map_controller = getattr(viewer, 'gps_map_controller', None)
    map_dialog = getattr(map_controller, 'map_dialog', None)
    map_view = getattr(map_dialog, 'map_view', None)
    if map_view is not None:
        try:
            map_view._fov_cache = None
            for entry in getattr(map_view, 'gps_data', None) or []:
                if isinstance(entry, dict) and 'bearing' in entry:
                    entry['bearing'] = None
        except Exception:
            pass


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

        # Detect the clock fault BEFORE any stamping: the pre-pass rewrites
        # the files, which resets their mtime and destroys the file-time
        # evidence the detection relies on.
        detect_service = WaldoMetadataService(terrain_service=None)
        proposal = None
        try:
            proposal = detect_service.propose_clock_correction(waldo_paths)
        except Exception as e:
            self.logger.error(f"WaldoPrePassController: clock-fault detection failed - {e}")

        if not any_pending:
            self.logger.info("WaldoPrePassController: all WALDO images already processed.")
            self._offer_clock_correction(waldo_paths, proposal, service=detect_service)
            # Strictly after the clock offer: the flight-log fit reads the
            # corrected capture times the offer may just have stamped.
            self._offer_flight_log(waldo_paths, service=detect_service)
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
        if not result.cancelled:
            self._offer_clock_correction(waldo_paths, proposal, service=service)
            self._offer_flight_log(waldo_paths, service=service)

    # ------------------------------------------------------------------
    # Flight-log attitude
    # ------------------------------------------------------------------

    def _offer_flight_log(self, waldo_paths: List[str],
                          service: Optional[WaldoMetadataService] = None):
        """Discover, calibrate, and offer a ForeFlight track log for the folder.

        Runs strictly AFTER the clock-correction offer in both pre-pass
        branches: the fit resolves capture times through any correction just
        stamped, and its signature records the correction it used - a later
        clock change retriggers the restamp on the next open.

        A remembered acceptance re-applies silently (auto mode); a remembered
        decline suppresses the offer. With no memory, only a candidate whose
        clock-offset fit actually matches this folder opens the dialog.
        """
        if not waldo_paths:
            return
        try:
            folder_key = WaldoClockDecisions.folder_key_for(waldo_paths[0])
            decision = WaldoFlightLogDecisions.get_decision(folder_key, self.settings_service)
            if decision and decision.get('decision') == 'declined':
                return

            flight_service = WaldoFlightLogService()
            candidates: List[str] = []
            remembered_path = (decision or {}).get('log_path')
            if remembered_path and os.path.isfile(remembered_path):
                candidates.append(remembered_path)
            auto = bool(decision and decision.get('decision') == 'accepted' and candidates)
            if not candidates:
                candidates = flight_service.candidate_files(os.path.dirname(waldo_paths[0]))
            if not candidates:
                return

            if service is None:
                service = WaldoMetadataService(terrain_service=None)
            dialog = WaldoFlightLogDialog(
                self.parent, service, flight_service, waldo_paths, candidates,
                auto_apply=auto)
            dialog.exec()

            if dialog.applied and dialog.fit is not None and dialog.remember_choice and not auto:
                WaldoFlightLogDecisions.store_decision(folder_key, {
                    'decision': 'accepted',
                    'log_path': dialog.fit.log_path,
                }, self.settings_service)
            elif dialog.declined and dialog.remember_choice:
                WaldoFlightLogDecisions.store_decision(
                    folder_key, {'decision': 'declined'}, self.settings_service)

            result = dialog.result_data
            self.logger.info(
                "WaldoPrePassController: flight log stamped=%d current=%d "
                "errors=%d declined=%s"
                % (result.processed, result.already_current, len(result.errors),
                   dialog.declined))
        except Exception as e:
            self.logger.error(f"WaldoPrePassController: flight-log offer failed - {e}")

    # ------------------------------------------------------------------
    # Clock correction
    # ------------------------------------------------------------------

    def _clock_decisions(self) -> dict:
        return WaldoClockDecisions.get_decisions(self.settings_service)

    def _store_clock_decision(self, folder_key: str, decision: dict):
        WaldoClockDecisions.store_decision(folder_key, decision, self.settings_service)

    def _offer_clock_correction(self, waldo_paths: List[str], proposal,
                                service: Optional[WaldoMetadataService] = None):
        """Drive the confirmation dialog for a pre-computed clock proposal.

        The proposal is detected by the caller BEFORE the pre-pass stamps
        anything (stamping resets mtimes and weakens detection). A remembered
        'declined' suppresses the offer; a remembered acceptance re-applies
        silently (progress only) so images added to the folder later get
        corrected without re-asking.

        When no fault proposal exists but an APPLIED correction fails the
        physical sanity check (sun below the horizon on daylight imagery),
        an amendment prefilled from the stamped values is offered instead -
        overriding any remembered decision, since the evidence contradicts
        it.
        """
        if not waldo_paths:
            return
        try:
            if service is None:
                service = WaldoMetadataService(terrain_service=None)

            amend_reason = None
            if proposal is None:
                amend_reason = service.stamped_correction_suspect(waldo_paths)
                if amend_reason is None:
                    return
                proposal = service.propose_amendment(waldo_paths)
                if proposal is None:
                    return
                proposal.evidence.insert(0, amend_reason)

            folder_key = os.path.normcase(os.path.abspath(os.path.dirname(waldo_paths[0])))
            decision = self._clock_decisions().get(folder_key)
            if amend_reason is None and decision and decision.get('decision') == 'declined':
                self.logger.info(
                    "WaldoPrePassController: clock fault detected but correction "
                    "was previously declined for this folder.")
                return

            # A failed sanity check always re-asks; never silently re-applies.
            auto = (amend_reason is None
                    and bool(decision and decision.get('decision') == 'accepted'))
            if auto:
                proposal.face_shift_h = int(decision.get('face_shift_h', proposal.face_shift_h))
                tz_text = decision.get('tz_text')
                if tz_text:
                    proposal.tz_name = None
                    proposal.fixed_offset_h = None
                    # Reuse the dialog's parser by seeding its editable field.
                    try:
                        from zoneinfo import ZoneInfo
                        ZoneInfo(tz_text)
                        proposal.tz_name = tz_text
                    except Exception:
                        try:
                            proposal.fixed_offset_h = float(tz_text)
                        except ValueError:
                            proposal.tz_name = None

            dialog = WaldoClockCorrectionDialog(
                self.parent, service, waldo_paths, proposal, auto_apply=auto)
            dialog.exec()

            if dialog.applied and dialog.remember_choice and not auto:
                self._store_clock_decision(folder_key, {
                    'decision': 'accepted',
                    'face_shift_h': dialog.accepted_face_shift_h,
                    'tz_text': dialog.accepted_tz_text,
                })
            elif dialog.declined and dialog.remember_choice:
                self._store_clock_decision(folder_key, {'decision': 'declined'})

            result = dialog.result_data
            self.logger.info(
                "WaldoPrePassController: clock correction corrected=%d current=%d "
                "errors=%d declined=%s"
                % (result.processed, result.already_current, len(result.errors),
                   dialog.declined)
            )
        except Exception as e:
            self.logger.error(f"WaldoPrePassController: clock correction failed - {e}")
