"""Tests for WaldoClockCorrectionDialog (confirm/edit/apply flow)."""

import pytest

from core.services.waldo import ClockCorrectionProposal, WaldoProcessResult
from core.views.images.viewer.dialogs.WaldoClockCorrectionDialog import (
    WaldoClockCorrectionDialog,
)


class _StubService:
    """Records apply_clock_correction calls; returns canned counts."""

    def __init__(self):
        self.calls = []

    def apply_clock_correction(self, image_paths, face_shift_h, tz_name=None,
                               fixed_offset_h=None, progress_cb=None,
                               cancel_cb=None):
        self.calls.append({
            'paths': list(image_paths),
            'face_shift_h': face_shift_h,
            'tz_name': tz_name,
            'fixed_offset_h': fixed_offset_h,
        })
        if progress_cb:
            progress_cb(1, len(image_paths), "working")
        result = WaldoProcessResult()
        result.processed = len(image_paths)
        return result


def _proposal():
    return ClockCorrectionProposal(
        face_shift_h=-12,
        tz_name="America/Los_Angeles",
        fixed_offset_h=-8,
        evidence=["Stamped timezone is UTC-6 but GPS longitude implies UTC-8.2.",
                  "Claimed capture is 7.5 h after the file was written."],
        sample_name="0_000_02_035.jpg",
        sample_face="2026:07:23 18:49:37",
        sample_corrected_utc="2026-07-23 13:49:37 UTC",
    )


def test_dialog_preview_uses_proposal_defaults(qtbot):
    dlg = WaldoClockCorrectionDialog(None, _StubService(), ["0_a.jpg"], _proposal())
    qtbot.addWidget(dlg)
    assert dlg._shift_spin.value() == -12
    assert dlg._tz_edit.text() == "America/Los_Angeles"
    # 18:49 face - 12h in PDT -> 13:49 UTC
    assert "13:49:37 UTC" in dlg._preview_label.text()
    assert dlg._apply_button.isEnabled()


def test_dialog_invalid_timezone_disables_apply(qtbot):
    dlg = WaldoClockCorrectionDialog(None, _StubService(), ["0_a.jpg"], _proposal())
    qtbot.addWidget(dlg)
    dlg._tz_edit.setText("garbage/zone!!")
    assert not dlg._apply_button.isEnabled()
    dlg._tz_edit.setText("-7")  # numeric offsets are accepted too
    assert dlg._apply_button.isEnabled()


def test_dialog_apply_runs_worker_and_records_choice(qtbot):
    service = _StubService()
    dlg = WaldoClockCorrectionDialog(None, service, ["0_a.jpg", "0_b.jpg"], _proposal())
    qtbot.addWidget(dlg)
    dlg._on_apply()
    qtbot.waitUntil(lambda: dlg.applied, timeout=5000)
    assert service.calls and service.calls[0]['face_shift_h'] == -12.0
    assert service.calls[0]['tz_name'] == "America/Los_Angeles"
    assert dlg.accepted_face_shift_h == -12
    assert dlg.accepted_tz_text == "America/Los_Angeles"
    assert dlg.remember_choice is True
    assert dlg.result_data.processed == 2


def test_dialog_decline_sets_flags_without_applying(qtbot):
    service = _StubService()
    dlg = WaldoClockCorrectionDialog(None, service, ["0_a.jpg"], _proposal())
    qtbot.addWidget(dlg)
    dlg._remember_check.setChecked(False)
    dlg._on_decline()
    assert dlg.declined is True
    assert dlg.remember_choice is False
    assert dlg.applied is False
    assert service.calls == []


def test_dialog_auto_mode_applies_on_show(qtbot):
    service = _StubService()
    dlg = WaldoClockCorrectionDialog(None, service, ["0_a.jpg"], _proposal(),
                                     auto_apply=True)
    qtbot.addWidget(dlg)
    dlg.show()
    qtbot.waitUntil(lambda: dlg.applied, timeout=5000)
    assert service.calls
    dlg.close()


def test_dialog_fixed_offset_input_reaches_service(qtbot):
    service = _StubService()
    proposal = _proposal()
    proposal.tz_name = None
    proposal.fixed_offset_h = -7.0
    dlg = WaldoClockCorrectionDialog(None, service, ["0_a.jpg"], proposal)
    qtbot.addWidget(dlg)
    assert dlg._tz_edit.text() == "-7.0"
    dlg._on_apply()
    qtbot.waitUntil(lambda: dlg.applied, timeout=5000)
    assert service.calls[0]['tz_name'] is None
    assert service.calls[0]['fixed_offset_h'] == pytest.approx(-7.0)
