"""Tests for the flight-log attitude stage: composition, exact inversion, stamping."""

import importlib
import math

import numpy as np
import pytest

from core.services.image.AOIService import AOIService
from core.services.waldo.WaldoFlightLog import FlightLogFit, FlightLogTrack
from core.services.waldo.WaldoMetadataService import (
    ATTITUDE_SOURCE_CONSTANTS,
    ATTITUDE_SOURCE_TRACKLOG,
    FLIGHTLOG_MAX_ROLL_DEG,
    FlightLogImageRecord,
    OUTWARD_ROLL_DEG,
    WaldoMetadataService,
)

waldo_module = importlib.import_module("core.services.waldo.WaldoMetadataService")


# --------------------------------------------------------------------------
# Composition + inversion round trips
# --------------------------------------------------------------------------

def test_invert_zero_attitude_reproduces_v9_constants():
    svc = WaldoMetadataService
    for cam_idx, level_roll in ((0, -OUTWARD_ROLL_DEG), (1, +OUTWARD_ROLL_DEG)):
        level_yaw = (123.0 + 180.0 * (cam_idx == 0)) % 360.0
        r_true = svc.compose_attitude_rotation(level_yaw, level_roll, 123.0, 0.0, 0.0)
        pitch, yaw, roll = svc.invert_to_gimbal_angles(r_true, 123.0)
        assert math.isclose(pitch, -90.0, abs_tol=1e-9)
        assert math.isclose(yaw, level_yaw, abs_tol=1e-9)
        assert math.isclose(roll, level_roll, abs_tol=1e-9)


def test_compose_invert_round_trip_grid():
    svc = WaldoMetadataService
    for flight_yaw in (0.0, 87.3, 214.6):
        for cam_idx, level_roll in ((0, -OUTWARD_ROLL_DEG), (1, +OUTWARD_ROLL_DEG)):
            level_yaw = (flight_yaw + (180.0 if cam_idx == 0 else 0.0)) % 360.0
            for bank in (-35.0, -6.2, 0.0, 4.9, 30.0):
                for ac_pitch in (-9.5, 0.0, 7.8):
                    r_true = svc.compose_attitude_rotation(
                        level_yaw, level_roll, flight_yaw, ac_pitch, bank)
                    pitch, yaw, roll = svc.invert_to_gimbal_angles(r_true, flight_yaw)
                    recomposed = (svc._rodrigues_horizontal(flight_yaw, roll)
                                  @ svc._base_rotation(pitch, yaw))
                    assert np.allclose(recomposed, r_true, atol=1e-9), (
                        f"yaw={flight_yaw} cam={cam_idx} bank={bank} pitch={ac_pitch}")


def test_bank_right_tilts_cam0_boresight_toward_nadir():
    # Right bank (+) rotates the right-tilted cam 0 boresight TOWARD nadir:
    # at bank = +22.5 it looks straight down. The docstring's "positive
    # Rodrigues roll tilts the optical axis plane LEFT" implies exactly this.
    svc = WaldoMetadataService
    r_true = svc.compose_attitude_rotation(180.0, -OUTWARD_ROLL_DEG, 0.0, 0.0, +6.0)
    pitch, yaw, roll = svc.invert_to_gimbal_angles(r_true, 0.0)
    assert math.isclose(roll, -16.5, abs_tol=1e-9)
    assert math.isclose(pitch, -90.0, abs_tol=1e-9)
    r_nadir = svc.compose_attitude_rotation(180.0, -OUTWARD_ROLL_DEG, 0.0, 0.0, +OUTWARD_ROLL_DEG)
    assert math.isclose(abs(float(r_nadir[2, 2])), 1.0, abs_tol=1e-9)


def test_inverted_angles_reproduce_ground_position_through_consumer():
    """The stamped triple must land the consumer raycast on the true ground point."""
    svc = WaldoMetadataService
    flight_yaw = 42.0
    level_yaw = (flight_yaw + 180.0) % 360.0
    r_true = svc.compose_attitude_rotation(level_yaw, -OUTWARD_ROLL_DEG,
                                           flight_yaw, 3.5, -8.0)
    pitch, yaw, roll = svc.invert_to_gimbal_angles(r_true, flight_yaw)

    alt = 500.0
    drone_lat, drone_lon = 37.0, -118.0
    result = AOIService._calculate_ground_position(
        drone_lat, drone_lon, 2000.0, 1500.0, 2000.0, 1500.0, 4000, 3000,
        50.0, 36.0, 24.0, alt, pitch, yaw, roll,
        roll_axis_azimuth_deg=flight_yaw)
    assert result is not None
    got_north = (result[0] - drone_lat) * 111_320.0
    got_east = (result[1] - drone_lon) * 111_320.0 * math.cos(math.radians(drone_lat))

    ray = r_true[:, 2]
    t = alt / float(ray[2])
    want_north = float(ray[0]) * t
    want_east = float(ray[1]) * t
    assert math.isclose(got_north, want_north, abs_tol=1.0)
    assert math.isclose(got_east, want_east, abs_tol=1.0)


# --------------------------------------------------------------------------
# apply_flight_log_attitude
# --------------------------------------------------------------------------

T0 = 1_700_000_000.0


def _track(n=101, bank=6.0, pitch=2.0):
    return FlightLogTrack(
        path="log.csv", t=[T0 + k for k in range(n)],
        lat=[37.0] * n, lon=[-118.0] * n, alt_m=[1500.0] * n,
        course=[0.0] * n, speed_mps=[50.0] * n,
        bank=[bank] * n, pitch=[pitch] * n)


def _fit(**kwargs):
    defaults = dict(log_path="log.csv", log_sha256="ab" * 32, accepted=True,
                    clock_offset_s=-17.0, mean_track_dist_m=15.0,
                    matched_fraction=1.0, attitude_reliable=True,
                    attitude_lag_s=4.0, lag_correlation=0.95)
    defaults.update(kwargs)
    return FlightLogFit(**defaults)


def _record(**kwargs):
    defaults = dict(path="E:/img/0_000_00_010.jpg", name="0_000_00_010.jpg",
                    cam_idx=0, capture_epoch=T0 + 50.0 + 17.0, lat=37.0, lon=-118.0,
                    flight_yaw_deg=0.0, gimbal_yaw_deg=180.0,
                    processor_version="9")
    defaults.update(kwargs)
    return FlightLogImageRecord(**defaults)


@pytest.fixture
def captured_writes(monkeypatch):
    writes = []
    monkeypatch.setattr(
        waldo_module.MetaDataHelper, 'add_xmp_fields',
        staticmethod(lambda path, fields: writes.append((path, list(fields)))))
    return writes


def _field(writes, tag):
    for _path, fields in writes:
        for _ns, name, value in fields:
            if name == tag:
                return value
    return None


def test_apply_composes_and_stamps(captured_writes):
    svc = WaldoMetadataService()
    result = svc.apply_flight_log_attitude([_record()], _fit(), _track())
    assert result.processed == 1
    assert not result.errors
    assert _field(captured_writes, "AttitudeSource") == ATTITUDE_SOURCE_TRACKLOG
    # bank +6 on cam0 (-22.5) with zero pitch: exact composed roll -16.5
    assert math.isclose(float(_field(captured_writes, "GimbalRollDegree")), -16.5, abs_tol=0.01)
    assert math.isclose(float(_field(captured_writes, "FlightRollDegree")), 6.0, abs_tol=1e-6)
    assert math.isclose(float(_field(captured_writes, "FlightPitchDegree")), 2.0, abs_tol=1e-6)
    # capture (face-resolved) T0+67, offset -17 -> refined T0+50
    assert _field(captured_writes, "CaptureUtcRefined") == "2023-11-14T22:14:10+00:00"
    assert _field(captured_writes, "ClockOffsetSeconds") == "-17.00"
    assert _field(captured_writes, "LevelYawDegree") is not None
    assert result.notes and "clock -17.0 s" in result.notes[0]


def test_apply_pitch_only_changes_composed_pitch(captured_writes):
    svc = WaldoMetadataService()
    svc.apply_flight_log_attitude([_record()], _fit(), _track(bank=0.0, pitch=5.0))
    pitch = float(_field(captured_writes, "GimbalPitchDegree"))
    roll = float(_field(captured_writes, "GimbalRollDegree"))
    # Nose-up 5 deg tilts the boresight AHEAD of the aircraft - away from
    # cam 0's backward image-top azimuth, so the composed pitch goes BEYOND
    # nadir (< -90) while roll keeps roughly the mount value.
    assert -96.0 < pitch < -90.0
    assert math.isclose(roll, -OUTWARD_ROLL_DEG, abs_tol=0.5)


def test_apply_signature_idempotence(captured_writes):
    svc = WaldoMetadataService()
    fit = _fit()
    rec = _record()
    sig = svc._flight_log_signature(rec, fit)
    rec.existing_signature = sig
    result = svc.apply_flight_log_attitude([rec], fit, _track())
    assert result.already_current == 1
    assert result.processed == 0
    assert captured_writes == []

    # A changed clock decision must break the signature and restamp.
    rec2 = _record(clock_face_shift="-12", clock_tz="America/Los_Angeles",
                   existing_signature=sig)
    result2 = svc.apply_flight_log_attitude([rec2], fit, _track())
    assert result2.processed == 1


def test_apply_steep_bank_falls_back_to_constants(captured_writes):
    svc = WaldoMetadataService()
    # cam1 mount +22.5 plus 50 deg left-wing-down bank -> composed roll ~72.5
    rec = _record(cam_idx=1, gimbal_yaw_deg=0.0)
    svc.apply_flight_log_attitude([rec], _fit(), _track(bank=50.0))
    assert _field(captured_writes, "AttitudeSource") == ATTITUDE_SOURCE_CONSTANTS
    assert math.isclose(float(_field(captured_writes, "GimbalRollDegree")),
                        +OUTWARD_ROLL_DEG, abs_tol=1e-6)
    assert math.isclose(float(_field(captured_writes, "GimbalPitchDegree")), -90.0, abs_tol=1e-6)
    assert _field(captured_writes, "FlightRollDegree") is None
    # sanity: the guard bound itself
    assert 50.0 + OUTWARD_ROLL_DEG > FLIGHTLOG_MAX_ROLL_DEG


def test_apply_out_of_coverage_falls_back_to_constants(captured_writes):
    svc = WaldoMetadataService()
    rec = _record(capture_epoch=T0 + 500.0)  # past the 100 s track
    svc.apply_flight_log_attitude([rec], _fit(), _track())
    assert _field(captured_writes, "AttitudeSource") == ATTITUDE_SOURCE_CONSTANTS
    # the clock refinement still applies
    assert _field(captured_writes, "CaptureUtcRefined") is not None


def test_apply_unreliable_attitude_keeps_constants_but_refines_clock(captured_writes):
    svc = WaldoMetadataService()
    result = svc.apply_flight_log_attitude(
        [_record()], _fit(attitude_reliable=False, attitude_lag_s=0.0, lag_correlation=0.2),
        _track())
    assert result.processed == 1
    assert _field(captured_writes, "AttitudeSource") == ATTITUDE_SOURCE_CONSTANTS
    assert _field(captured_writes, "CaptureUtcRefined") == "2023-11-14T22:14:10+00:00"
    assert result.notes and "unreliable" in result.notes[0]


def test_apply_rejected_fit_stamps_nothing(captured_writes):
    svc = WaldoMetadataService()
    result = svc.apply_flight_log_attitude(
        [_record()], _fit(accepted=False, reason="images do not lie on this log's track"),
        _track())
    assert result.processed == 0
    assert captured_writes == []
    assert result.warnings and "rejected" in result.warnings[0]


def test_apply_restores_constants_over_stale_composition(captured_writes):
    # Image previously composed with another log (LevelYaw stamped, gimbal
    # values composed): with the new fit unable to cover it, the constants
    # restamp must rebuild from the LEVEL baseline, not the composed yaw.
    svc = WaldoMetadataService()
    rec = _record(capture_epoch=T0 + 500.0, gimbal_yaw_deg=171.2,
                  level_yaw_deg=180.0, existing_signature="v1|stale")
    svc.apply_flight_log_attitude([rec], _fit(), _track())
    assert math.isclose(float(_field(captured_writes, "GimbalYawDegree")), 180.0, abs_tol=1e-6)
