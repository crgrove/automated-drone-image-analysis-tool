"""Tests for WaldoPrePassController clock-correction orchestration."""

import importlib
import json

from core.services.waldo import ClockCorrectionProposal, WaldoProcessResult

controller_module = importlib.import_module(
    "core.controllers.images.viewer.WaldoPrePassController")
WaldoPrePassController = controller_module.WaldoPrePassController
CLOCK_DECISIONS_SETTING = controller_module.CLOCK_DECISIONS_SETTING


class _FakeSettings:
    def __init__(self):
        self.values = {}

    def get_setting(self, name, default_value=None):
        return self.values.get(name, default_value)

    def set_setting(self, name, value):
        self.values[name] = value


class _FakeDialog:
    """Stands in for WaldoClockCorrectionDialog; scripted outcome."""

    instances = []

    # Class-level script for the next instance:
    script = {}

    def __init__(self, parent, service, image_paths, proposal, auto_apply=False):
        self.proposal = proposal
        self.auto_apply = auto_apply
        self.applied = self.script.get('applied', False)
        self.declined = self.script.get('declined', False)
        self.remember_choice = self.script.get('remember', False)
        self.accepted_face_shift_h = self.script.get('face_shift', None)
        self.accepted_tz_text = self.script.get('tz_text', None)
        self.result_data = WaldoProcessResult()
        _FakeDialog.instances.append(self)

    def exec(self):
        return None


class _StubService:
    pass


def _proposal():
    return ClockCorrectionProposal(
        face_shift_h=-12, tz_name="America/Los_Angeles", fixed_offset_h=-8,
        evidence=["e1"], sample_name="0_a.jpg",
        sample_face="2026:07:23 18:49:37",
        sample_corrected_utc="2026-07-23 13:49:37 UTC")


def _make_controller(monkeypatch):
    monkeypatch.setattr(controller_module, 'WaldoClockCorrectionDialog', _FakeDialog)
    _FakeDialog.instances = []
    _FakeDialog.script = {}
    controller = WaldoPrePassController(parent_viewer=None)
    controller.settings_service = _FakeSettings()
    return controller


def test_no_proposal_means_no_dialog(monkeypatch, tmp_path):
    controller = _make_controller(monkeypatch)
    controller._offer_clock_correction(
        [str(tmp_path / "0_a.jpg")], None, service=_StubService())
    assert _FakeDialog.instances == []


def test_accept_with_remember_persists_decision(monkeypatch, tmp_path):
    controller = _make_controller(monkeypatch)
    _FakeDialog.script = {'applied': True, 'remember': True,
                          'face_shift': -12, 'tz_text': 'America/Los_Angeles'}
    controller._offer_clock_correction(
        [str(tmp_path / "0_a.jpg")], _proposal(), service=_StubService())
    assert len(_FakeDialog.instances) == 1
    assert _FakeDialog.instances[0].auto_apply is False
    stored = json.loads(controller.settings_service.values[CLOCK_DECISIONS_SETTING])
    decision = next(iter(stored.values()))
    assert decision == {'decision': 'accepted', 'face_shift_h': -12,
                        'tz_text': 'America/Los_Angeles'}


def test_declined_with_remember_suppresses_future_offers(monkeypatch, tmp_path):
    controller = _make_controller(monkeypatch)
    _FakeDialog.script = {'declined': True, 'remember': True}
    paths = [str(tmp_path / "0_a.jpg")]
    controller._offer_clock_correction(paths, _proposal(), service=_StubService())
    assert len(_FakeDialog.instances) == 1

    # Second open: decision remembered, dialog never constructed again.
    controller._offer_clock_correction(paths, _proposal(), service=_StubService())
    assert len(_FakeDialog.instances) == 1


def test_stored_acceptance_reapplies_in_auto_mode(monkeypatch, tmp_path):
    controller = _make_controller(monkeypatch)
    paths = [str(tmp_path / "0_a.jpg")]
    import os
    folder_key = os.path.normcase(os.path.abspath(str(tmp_path)))
    controller.settings_service.values[CLOCK_DECISIONS_SETTING] = json.dumps({
        folder_key: {'decision': 'accepted', 'face_shift_h': -12,
                     'tz_text': 'America/Los_Angeles'}})
    _FakeDialog.script = {'applied': True, 'remember': False}
    controller._offer_clock_correction(paths, _proposal(), service=_StubService())
    assert len(_FakeDialog.instances) == 1
    dlg = _FakeDialog.instances[0]
    assert dlg.auto_apply is True
    assert dlg.proposal.face_shift_h == -12
    assert dlg.proposal.tz_name == 'America/Los_Angeles'


def test_decline_without_remember_is_not_persisted(monkeypatch, tmp_path):
    controller = _make_controller(monkeypatch)
    _FakeDialog.script = {'declined': True, 'remember': False}
    controller._offer_clock_correction(
        [str(tmp_path / "0_a.jpg")], _proposal(), service=_StubService())
    assert CLOCK_DECISIONS_SETTING not in controller.settings_service.values


class _AmendStubService:
    """No live fault, but a stamped correction that fails the sanity check."""

    def __init__(self, suspect_reason, amend_proposal):
        self.suspect_reason = suspect_reason
        self.amend_proposal = amend_proposal

    def stamped_correction_suspect(self, paths):
        return self.suspect_reason

    def propose_amendment(self, paths):
        return self.amend_proposal


def test_suspect_stamp_triggers_amendment_despite_stored_acceptance(monkeypatch, tmp_path):
    """A physically impossible applied correction must re-ask, not silently
    re-apply the remembered (wrong) values."""
    controller = _make_controller(monkeypatch)
    paths = [str(tmp_path / "0_a.jpg")]
    import os
    folder_key = os.path.normcase(os.path.abspath(str(tmp_path)))
    controller.settings_service.values[CLOCK_DECISIONS_SETTING] = json.dumps({
        folder_key: {'decision': 'accepted', 'face_shift_h': -12,
                     'tz_text': 'America/Los_Angeles'}})
    _FakeDialog.script = {'applied': True, 'remember': True,
                          'face_shift': 0, 'tz_text': 'UTC'}
    service = _AmendStubService("0_a.jpg: sun below horizon on daylight image",
                                _proposal())
    controller._offer_clock_correction(paths, None, service=service)

    assert len(_FakeDialog.instances) == 1
    dlg = _FakeDialog.instances[0]
    assert dlg.auto_apply is False  # never silently re-apply suspect values
    assert "sun below horizon" in dlg.proposal.evidence[0]
    # The new choice replaces the stored decision.
    stored = json.loads(controller.settings_service.values[CLOCK_DECISIONS_SETTING])
    assert stored[folder_key] == {'decision': 'accepted', 'face_shift_h': 0,
                                  'tz_text': 'UTC'}


def test_no_proposal_and_healthy_stamp_stays_quiet(monkeypatch, tmp_path):
    controller = _make_controller(monkeypatch)
    service = _AmendStubService(None, None)
    controller._offer_clock_correction(
        [str(tmp_path / "0_a.jpg")], None, service=service)
    assert _FakeDialog.instances == []


# --------------------------------------------------------------------------
# Flight-log offer
# --------------------------------------------------------------------------

from core.services.waldo.WaldoFlightLog import FlightLogFit  # noqa: E402
from core.services.waldo.WaldoFlightLogDecisions import (  # noqa: E402
    FLIGHTLOG_DECISIONS_SETTING,
)


class _FakeFlightDialog:
    """Stands in for WaldoFlightLogDialog; scripted outcome."""

    instances = []
    script = {}

    def __init__(self, parent, service, flight_service, image_paths,
                 candidate_logs, auto_apply=False):
        self.image_paths = image_paths
        self.candidate_logs = candidate_logs
        self.auto_apply = auto_apply
        self.applied = self.script.get('applied', False)
        self.declined = self.script.get('declined', False)
        self.remember_choice = self.script.get('remember', False)
        self.fit = self.script.get('fit', None)
        self.result_data = WaldoProcessResult()
        _FakeFlightDialog.instances.append(self)

    def exec(self):
        return None


def _accepted_fit(log_path="E:/logs/tracklog.csv"):
    return FlightLogFit(log_path=log_path, log_sha256="ab" * 32, accepted=True,
                        clock_offset_s=-17.0, mean_track_dist_m=15.0,
                        matched_fraction=1.0, attitude_reliable=True,
                        attitude_lag_s=4.0, lag_correlation=0.95)


def _make_flight_controller(monkeypatch, candidates):
    controller = _make_controller(monkeypatch)
    monkeypatch.setattr(controller_module, 'WaldoFlightLogDialog', _FakeFlightDialog)
    monkeypatch.setattr(controller_module.WaldoFlightLogService, 'candidate_files',
                        staticmethod(lambda image_dir: list(candidates)))
    _FakeFlightDialog.instances = []
    _FakeFlightDialog.script = {}
    return controller


def test_flight_log_no_candidates_stays_quiet(monkeypatch, tmp_path):
    controller = _make_flight_controller(monkeypatch, candidates=[])
    controller._offer_flight_log([str(tmp_path / "0_a.jpg")], service=_StubService())
    assert _FakeFlightDialog.instances == []


def test_flight_log_accept_with_remember_persists_log_path(monkeypatch, tmp_path):
    log = tmp_path / "tracklog.csv"
    controller = _make_flight_controller(monkeypatch, candidates=[str(log)])
    _FakeFlightDialog.script = {'applied': True, 'remember': True,
                                'fit': _accepted_fit(str(log))}
    controller._offer_flight_log([str(tmp_path / "0_a.jpg")], service=_StubService())
    assert len(_FakeFlightDialog.instances) == 1
    assert _FakeFlightDialog.instances[0].auto_apply is False
    stored = json.loads(controller.settings_service.values[FLIGHTLOG_DECISIONS_SETTING])
    decision = next(iter(stored.values()))
    assert decision == {'decision': 'accepted', 'log_path': str(log)}


def test_flight_log_declined_with_remember_suppresses_future_offers(monkeypatch, tmp_path):
    log = tmp_path / "tracklog.csv"
    controller = _make_flight_controller(monkeypatch, candidates=[str(log)])
    _FakeFlightDialog.script = {'declined': True, 'remember': True}
    paths = [str(tmp_path / "0_a.jpg")]
    controller._offer_flight_log(paths, service=_StubService())
    assert len(_FakeFlightDialog.instances) == 1

    controller._offer_flight_log(paths, service=_StubService())
    assert len(_FakeFlightDialog.instances) == 1


def test_flight_log_remembered_acceptance_runs_auto_with_stored_path(monkeypatch, tmp_path):
    log = tmp_path / "tracklog.csv"
    log.write_text("Pilot,Tail Number\n", encoding="utf-8")
    controller = _make_flight_controller(monkeypatch, candidates=[])
    import os
    folder_key = os.path.normcase(os.path.abspath(str(tmp_path)))
    controller.settings_service.values[FLIGHTLOG_DECISIONS_SETTING] = json.dumps({
        folder_key: {'decision': 'accepted', 'log_path': str(log)}})
    _FakeFlightDialog.script = {'applied': True, 'remember': False,
                                'fit': _accepted_fit(str(log))}
    controller._offer_flight_log([str(tmp_path / "0_a.jpg")], service=_StubService())
    assert len(_FakeFlightDialog.instances) == 1
    dlg = _FakeFlightDialog.instances[0]
    assert dlg.auto_apply is True
    assert dlg.candidate_logs == [str(log)]


def test_flight_log_missing_remembered_file_falls_back_to_discovery(monkeypatch, tmp_path):
    fresh = tmp_path / "tracklog-2.csv"
    controller = _make_flight_controller(monkeypatch, candidates=[str(fresh)])
    import os
    folder_key = os.path.normcase(os.path.abspath(str(tmp_path)))
    controller.settings_service.values[FLIGHTLOG_DECISIONS_SETTING] = json.dumps({
        folder_key: {'decision': 'accepted', 'log_path': str(tmp_path / 'gone.csv')}})
    _FakeFlightDialog.script = {'applied': False}
    controller._offer_flight_log([str(tmp_path / "0_a.jpg")], service=_StubService())
    assert len(_FakeFlightDialog.instances) == 1
    dlg = _FakeFlightDialog.instances[0]
    # The remembered file is gone: not auto mode, discovery candidates offered.
    assert dlg.auto_apply is False
    assert dlg.candidate_logs == [str(fresh)]
