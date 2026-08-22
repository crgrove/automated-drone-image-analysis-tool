"""Unit tests for the WALDO camera clock correction (detect / compute / apply)."""

import importlib
import os
from datetime import datetime, timedelta, timezone

import piexif
import pytest

from core.services.waldo.WaldoMetadataService import (
    WaldoMetadataService,
    CLOCK_CORRECTED_UTC_XMP,
    CLOCK_FACE_SHIFT_XMP,
    CLOCK_TIMEZONE_XMP,
    WALDO_NAMESPACE_URI,
)

waldo_module = importlib.import_module("core.services.waldo.WaldoMetadataService")


# --------------------------------------------------------------------------
# compute_corrected_utc
# --------------------------------------------------------------------------

def test_compute_corrected_utc_iana_zone_dst_aware():
    # July in America/Los_Angeles is PDT (UTC-7): face 18:49 - 12h = 06:49
    # local -> 13:49 UTC.
    face = datetime(2026, 7, 23, 18, 49, 37)
    out = WaldoMetadataService.compute_corrected_utc(
        face, -12, "America/Los_Angeles", None)
    assert out == datetime(2026, 7, 23, 13, 49, 37, tzinfo=timezone.utc)


def test_compute_corrected_utc_winter_uses_standard_time():
    # January is PST (UTC-8): the IANA zone handles DST per date.
    # 18:49 - 12h = 06:49 PST -> 14:49 UTC (vs 13:49 for the PDT case above).
    face = datetime(2026, 1, 23, 18, 49, 37)
    out = WaldoMetadataService.compute_corrected_utc(
        face, -12, "America/Los_Angeles", None)
    assert out == datetime(2026, 1, 23, 14, 49, 37, tzinfo=timezone.utc)


def test_compute_corrected_utc_fixed_offset_fallback():
    face = datetime(2026, 7, 23, 18, 49, 37)
    out = WaldoMetadataService.compute_corrected_utc(face, -12, None, -7.0)
    assert out == datetime(2026, 7, 23, 13, 49, 37, tzinfo=timezone.utc)
    # A bogus zone name falls back to the fixed offset instead of raising.
    out = WaldoMetadataService.compute_corrected_utc(face, -12, "Not/AZone", -7.0)
    assert out == datetime(2026, 7, 23, 13, 49, 37, tzinfo=timezone.utc)


def test_compute_corrected_utc_no_timezone_raises():
    with pytest.raises(ValueError):
        WaldoMetadataService.compute_corrected_utc(
            datetime(2026, 7, 23, 18, 0, 0), -12, None, None)


# --------------------------------------------------------------------------
# propose_clock_correction
# --------------------------------------------------------------------------

def _fault_exif(face="2026:07:23 18:49:37", offset="-06:00"):
    return {
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: face.encode(),
            piexif.ExifIFD.OffsetTimeOriginal: offset.encode(),
        },
        'GPS': {},
    }


def _make_image(tmp_path, name="0_000_02_035.jpg",
                mtime=datetime(2026, 7, 23, 17, 21, 0, tzinfo=timezone.utc)):
    p = tmp_path / name
    p.write_bytes(b"\xff\xd8\xff\xd9")
    ts = mtime.timestamp()
    os.utime(p, (ts, ts))
    return str(p)


@pytest.fixture
def fault_setup(tmp_path, monkeypatch):
    """One WALDO image exhibiting the full clock-fault signature."""
    # Claimed capture: 18:49:37 at -06:00 -> 2026-07-24 00:49:37 UTC.
    # File mtime 2026-07-23 17:21 UTC -> claimed is ~7.5 h ahead (flip window).
    path = _make_image(tmp_path)
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(waldo_module.LocationInfo, 'get_gps',
                        staticmethod(lambda exif_data: {'latitude': 41.28, 'longitude': -122.885}))
    monkeypatch.setattr(waldo_module, 'timezone_name_for_position',
                        lambda lat, lon: 'America/Los_Angeles')
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: None))
    return path


def test_propose_fires_on_full_signature(fault_setup):
    svc = WaldoMetadataService(terrain_service=None)
    proposal = svc.propose_clock_correction([fault_setup])
    assert proposal is not None
    assert proposal.face_shift_h == -12
    assert proposal.tz_name == 'America/Los_Angeles'
    assert proposal.sample_face == "2026:07:23 18:49:37"
    # 18:49 - 12h = 06:49 PDT -> 13:49 UTC
    assert proposal.sample_corrected_utc == "2026-07-23 13:49:37 UTC"
    assert len(proposal.evidence) == 2


def test_propose_fires_on_small_ahead_margin(tmp_path, fault_setup, monkeypatch):
    """The real field case: a 12 h flip offset by a ~10 h download delay
    leaves the claimed capture only ~28 min ahead of the mtime. Any
    provable ahead margin plus the timezone mismatch must still fire."""
    # Claimed capture 2026-07-24 00:49:37 UTC; file written 28 min earlier.
    path = _make_image(tmp_path, name="0_000_04_000.jpg",
                       mtime=datetime(2026, 7, 24, 0, 21, 0, tzinfo=timezone.utc))
    svc = WaldoMetadataService(terrain_service=None)
    proposal = svc.propose_clock_correction([path])
    assert proposal is not None
    assert proposal.face_shift_h == -12
    assert "min AFTER" in proposal.evidence[1]


def test_propose_fires_on_ahead_proof_alone(fault_setup, monkeypatch):
    # The stamped offset agrees with longitude but the file time proves the
    # clock runs ahead: still propose, with the AM/PM flip default.
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif(offset="-08:00")))
    svc = WaldoMetadataService(terrain_service=None)
    proposal = svc.propose_clock_correction([fault_setup])
    assert proposal is not None
    assert proposal.face_shift_h == -12
    assert len(proposal.evidence) == 1  # no timezone line


def test_propose_tz_mismatch_alone_defaults_to_zone_fix(tmp_path, fault_setup, monkeypatch):
    # A pre-pass restamp resets mtime, destroying the ahead-proof: the
    # timezone mismatch alone must still propose, but with face shift 0 and
    # a caution that a 12 h flip cannot be proven from these files.
    path = _make_image(tmp_path, name="0_000_02_036.jpg",
                       mtime=datetime(2026, 7, 24, 1, 0, 0, tzinfo=timezone.utc))
    svc = WaldoMetadataService(terrain_service=None)
    proposal = svc.propose_clock_correction([path])
    assert proposal is not None
    assert proposal.face_shift_h == 0
    assert any("cannot be proven" in e for e in proposal.evidence)


def test_propose_quiet_when_nothing_provable(tmp_path, fault_setup, monkeypatch):
    # Offset consistent with longitude AND file written after the claimed
    # capture: no provable symptom, no proposal.
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif(offset="-08:00")))
    path = _make_image(tmp_path, name="0_000_02_037.jpg",
                       mtime=datetime(2026, 7, 24, 12, 0, 0, tzinfo=timezone.utc))
    svc = WaldoMetadataService(terrain_service=None)
    assert svc.propose_clock_correction([path]) is None


def test_propose_quiet_when_already_corrected(fault_setup, monkeypatch):
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: "2026-07-23T13:49:37+00:00"))
    svc = WaldoMetadataService(terrain_service=None)
    assert svc.propose_clock_correction([fault_setup]) is None


# --------------------------------------------------------------------------
# apply_clock_correction
# --------------------------------------------------------------------------

def test_apply_stamps_corrected_fields(tmp_path, monkeypatch):
    path = _make_image(tmp_path)
    written = {}
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'add_xmp_fields',
                        staticmethod(lambda p, fields: written.update({p: fields})))
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: None))

    svc = WaldoMetadataService(terrain_service=None)
    result = svc.apply_clock_correction(
        [path], -12, tz_name="America/Los_Angeles")

    assert result.processed == 1 and not result.errors
    fields = {name: value for ns, name, value in written[path]}
    assert fields[CLOCK_CORRECTED_UTC_XMP] == "2026-07-23T13:49:37+00:00"
    assert fields[CLOCK_FACE_SHIFT_XMP] == "-12"
    assert fields[CLOCK_TIMEZONE_XMP] == "America/Los_Angeles"
    assert all(ns == WALDO_NAMESPACE_URI for ns, _, _ in written[path])


def test_apply_is_idempotent(tmp_path, monkeypatch):
    path = _make_image(tmp_path)
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: "2026-07-23T13:49:37+00:00"))
    calls = []
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'add_xmp_fields',
                        staticmethod(lambda p, fields: calls.append(p)))

    svc = WaldoMetadataService(terrain_service=None)
    result = svc.apply_clock_correction([path], -12, tz_name="America/Los_Angeles")
    assert result.already_current == 1 and result.processed == 0
    assert calls == []


def test_apply_stays_idempotent_with_refined_stamp_present(tmp_path, monkeypatch):
    # The flight-log stage writes waldo:CaptureUtcRefined ALONGSIDE the
    # corrected stamp. The remembered clock auto-apply must keep seeing its
    # own stamp as current, or every folder open would rewrite every image
    # and clobber the refinement (the two-rewrite loop).
    path = _make_image(tmp_path)
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_xmp_data_merged',
                        staticmethod(lambda p: {
                            'waldo:CaptureUtcCorrected': '2026-07-23T13:49:37+00:00',
                            'waldo:CaptureUtcRefined': '2026-07-23T13:49:20+00:00',
                        }))
    calls = []
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'add_xmp_fields',
                        staticmethod(lambda p, fields: calls.append(p)))

    svc = WaldoMetadataService(terrain_service=None)
    assert svc.get_corrected_utc_stamp(path) == '2026-07-23T13:49:37+00:00'
    result = svc.apply_clock_correction([path], -12, tz_name="America/Los_Angeles")
    assert result.already_current == 1 and result.processed == 0
    assert calls == []


def test_apply_skips_non_waldo_and_reports_missing_exif(tmp_path, monkeypatch):
    waldo = _make_image(tmp_path, name="0_000_02_035.jpg")
    other = _make_image(tmp_path, name="DJI_0001.jpg")
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: {'Exif': {}, 'GPS': {}}))
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: None))

    svc = WaldoMetadataService(terrain_service=None)
    result = svc.apply_clock_correction([waldo, other], -12, fixed_offset_h=-7.0)
    assert result.skipped == 1
    assert len(result.errors) == 1
    assert "DateTimeOriginal" in result.errors[0][1]


def test_apply_cancel_stops_early(tmp_path, monkeypatch):
    paths = [_make_image(tmp_path, name=f"0_000_02_{i:03d}.jpg") for i in range(5)]
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'add_xmp_fields',
                        staticmethod(lambda p, fields: None))
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: None))

    seen = []

    def cancel_after_two():
        return len(seen) >= 2

    svc = WaldoMetadataService(terrain_service=None)
    result = svc.apply_clock_correction(
        paths, -12, fixed_offset_h=-7.0,
        progress_cb=lambda i, n, s: seen.append(i),
        cancel_cb=cancel_after_two)
    assert result.cancelled
    assert result.processed < 5


# --------------------------------------------------------------------------
# audit softening
# --------------------------------------------------------------------------

def test_audit_quiet_when_correction_stamped(fault_setup, monkeypatch):
    """The audit must stop warning once the operator has repaired the clock."""
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: "2026-07-23T13:49:37+00:00"))
    svc = WaldoMetadataService(terrain_service=None)
    assert svc.audit_capture_times([fault_setup]) == []


def test_audit_still_warns_without_correction(fault_setup):
    svc = WaldoMetadataService(terrain_service=None)
    warnings = svc.audit_capture_times([fault_setup])
    assert warnings  # timezone mismatch + AM/PM flip both present


# --------------------------------------------------------------------------
# Amendment: propose_amendment / stamped_correction_suspect
# --------------------------------------------------------------------------

def test_propose_amendment_prefills_from_stamp(tmp_path, monkeypatch):
    path = _make_image(tmp_path)
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(WaldoMetadataService, 'get_correction_stamp_details',
                        staticmethod(lambda p: (-12.0, 'America/Los_Angeles')))
    svc = WaldoMetadataService(terrain_service=None)
    proposal = svc.propose_amendment([path])
    assert proposal is not None
    assert proposal.face_shift_h == -12
    assert proposal.tz_name == 'America/Los_Angeles'
    assert "already stamped" in proposal.evidence[0]
    assert proposal.sample_corrected_utc == "2026-07-23 13:49:37 UTC"


def test_propose_amendment_fixed_offset_stamp(tmp_path, monkeypatch):
    path = _make_image(tmp_path)
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(WaldoMetadataService, 'get_correction_stamp_details',
                        staticmethod(lambda p: (0.0, 'UTC+0.0')))
    svc = WaldoMetadataService(terrain_service=None)
    proposal = svc.propose_amendment([path])
    assert proposal is not None
    assert proposal.face_shift_h == 0
    assert proposal.tz_name is None
    assert proposal.fixed_offset_h == pytest.approx(0.0)
    # face 18:49:37 interpreted as UTC with no shift
    assert proposal.sample_corrected_utc == "2026-07-23 18:49:37 UTC"


def test_propose_amendment_none_without_stamp(tmp_path, monkeypatch):
    path = _make_image(tmp_path)
    monkeypatch.setattr(WaldoMetadataService, 'get_correction_stamp_details',
                        staticmethod(lambda p: None))
    svc = WaldoMetadataService(terrain_service=None)
    assert svc.propose_amendment([path]) is None


def test_suspect_flags_below_horizon_daylight(tmp_path, monkeypatch):
    """A stamped correction placing a bright image before sunrise is wrong."""
    import numpy as np
    path = _make_image(tmp_path)
    # 04:21 PDT = 11:21 UTC on Aug 7 at Inyo: sun well below the horizon.
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: "2026-08-07T11:21:28+00:00"))
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(waldo_module.LocationInfo, 'get_gps',
                        staticmethod(lambda exif_data: {'latitude': 37.04, 'longitude': -117.63}))
    monkeypatch.setattr(waldo_module.cv2, 'imdecode',
                        lambda buf, flags: np.full((400, 500), 150, dtype=np.uint8))
    svc = WaldoMetadataService(terrain_service=None)
    reason = svc.stamped_correction_suspect([path])
    assert reason is not None
    assert "below the horizon" in reason


def test_suspect_quiet_on_plausible_correction(tmp_path, monkeypatch):
    """A corrected time with the sun up is not second-guessed."""
    path = _make_image(tmp_path)
    # 09:21 PDT = 16:21 UTC: sun up.
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: "2026-08-07T16:21:28+00:00"))
    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        staticmethod(lambda p: _fault_exif()))
    monkeypatch.setattr(waldo_module.LocationInfo, 'get_gps',
                        staticmethod(lambda exif_data: {'latitude': 37.04, 'longitude': -117.63}))
    svc = WaldoMetadataService(terrain_service=None)
    assert svc.stamped_correction_suspect([path]) is None


def test_suspect_quiet_without_stamp(tmp_path, monkeypatch):
    path = _make_image(tmp_path)
    monkeypatch.setattr(WaldoMetadataService, 'get_corrected_utc_stamp',
                        staticmethod(lambda p: None))
    svc = WaldoMetadataService(terrain_service=None)
    assert svc.stamped_correction_suspect([path]) is None
