"""Unit tests for WaldoMetadataService."""

from datetime import datetime, timedelta

import pytest

from core.services.waldo.WaldoMetadataService import (
    WaldoMetadataService,
    WaldoImageRecord,
    OUTWARD_ROLL_DEG,
)


# --------------------------------------------------------------------------
# is_waldo_image
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name,expected", [
    ("0_000_00_002.jpg", 0),
    ("1_000_00_002.jpg", 1),
    ("0_001.JPG", 0),
    ("1_999_99_999.jpeg", 1),
    ("/abs/path/0_a.jpg", 0),
    ("DJI_0001.JPG", None),
    ("IMG_0001.jpg", None),
    ("2_001.jpg", None),
    ("", None),
    (None, None),
])
def test_is_waldo_image(name, expected):
    assert WaldoMetadataService.is_waldo_image(name) == expected


# --------------------------------------------------------------------------
# compute_optical_axis_angles
# --------------------------------------------------------------------------

def test_optical_axis_cam_0_right_pod_image_flipped_180():
    # `0_*` = RIGHT pod, body top forward, but WALDO software rotates the
    # saved JPEG 180° so stored image-top = plane backward. GimbalYaw
    # therefore points backward (heading + 180°). Positive roll about
    # that flipped heading axis tilts the optical axis to plane RIGHT.
    angles = WaldoMetadataService.compute_optical_axis_angles(45.0, 0)
    assert angles['pitch'] == -90.0
    assert angles['yaw'] == 225.0  # 45 + 180
    assert angles['roll'] == +OUTWARD_ROLL_DEG


def test_optical_axis_cam_1_left_pod_top_backward():
    # `1_*` = LEFT pod, body top backward, no software rotation. Stored
    # image-top = plane backward as well, so GimbalYaw = heading + 180°.
    # Negative roll about the flipped heading axis tilts west (LEFT).
    angles = WaldoMetadataService.compute_optical_axis_angles(0.0, 1)
    assert angles['pitch'] == -90.0
    assert angles['yaw'] == 180.0
    assert angles['roll'] == -OUTWARD_ROLL_DEG


def test_optical_axis_cam_1_yaw_wraps_past_360():
    # heading 270°, cam 1 → 270 + 180 = 450 → 90° after mod-360 normalisation.
    angles = WaldoMetadataService.compute_optical_axis_angles(270.0, 1)
    assert angles['yaw'] == 90.0


def test_optical_axis_yaw_normalised_to_360():
    # heading 370.5 → 370.5 + 180 = 550.5 → 190.5 after mod-360.
    angles = WaldoMetadataService.compute_optical_axis_angles(370.5, 0)
    assert 0.0 <= angles['yaw'] < 360.0
    assert pytest.approx(angles['yaw'], abs=1e-6) == 190.5


def test_optical_axis_invalid_cam_raises():
    with pytest.raises(ValueError):
        WaldoMetadataService.compute_optical_axis_angles(0.0, 2)


# --------------------------------------------------------------------------
# Heading derivation: helper
# --------------------------------------------------------------------------

def _make_record(cam: int, idx: int, lat: float, lon: float, t: datetime) -> WaldoImageRecord:
    return WaldoImageRecord(
        path=f"{cam}_{idx:03}.jpg",
        name=f"{cam}_{idx:03}.jpg",
        cam_idx=cam,
        lat=lat,
        lon=lon,
        gps_alt_ellipsoidal=3000.0,
        timestamp=t,
    )


def test_heading_straight_line_north():
    """Five captures heading due north should produce ~0° headings everywhere."""
    base_lat = 37.0
    base_lon = -120.0
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    records = [
        _make_record(0, i, base_lat + i * 0.001, base_lon, t0 + timedelta(seconds=i * 2))
        for i in range(5)
    ]
    svc = WaldoMetadataService(terrain_service=None)
    svc.derive_headings(records)
    for r in records:
        assert r.heading_deg is not None
        # Should be close to 0 (or 360); allow small floating drift.
        diff = min(abs(r.heading_deg), abs(360.0 - r.heading_deg))
        assert diff < 1.0, f"Heading {r.heading_deg} too far from 0"


def test_heading_forward_fill_first_image():
    """First image's heading is forward-filled from the next valid image."""
    base_lat = 37.0
    base_lon = -120.0
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    records = [
        _make_record(0, i, base_lat + i * 0.001, base_lon, t0 + timedelta(seconds=i * 2))
        for i in range(3)
    ]
    svc = WaldoMetadataService(terrain_service=None)
    svc.derive_headings(records)
    # First image had no prior neighbour; expect forward fill from records[1].
    assert records[0].heading_deg is not None
    assert pytest.approx(records[0].heading_deg, abs=1.0) == records[1].heading_deg


def test_heading_stationary_cluster_skipped():
    """A stationary cluster in the middle of the path inherits the surrounding bearing."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    # Three real captures heading north, with two duplicates wedged in between.
    records = [
        _make_record(0, 0, 37.000, -120.0, t0 + timedelta(seconds=0)),
        _make_record(0, 1, 37.001, -120.0, t0 + timedelta(seconds=2)),
        # stationary
        _make_record(0, 2, 37.001, -120.0, t0 + timedelta(seconds=4)),
        _make_record(0, 3, 37.001, -120.0, t0 + timedelta(seconds=6)),
        # back to motion
        _make_record(0, 4, 37.002, -120.0, t0 + timedelta(seconds=8)),
        _make_record(0, 5, 37.003, -120.0, t0 + timedelta(seconds=10)),
    ]
    svc = WaldoMetadataService(terrain_service=None)
    svc.derive_headings(records)
    for r in records:
        assert r.heading_deg is not None
        # All headings should be ~0° (straight north).
        diff = min(abs(r.heading_deg), abs(360.0 - r.heading_deg))
        assert diff < 5.0, f"Stationary cluster heading {r.heading_deg} drifted too far"


def test_heading_cross_cam_fallback():
    """A lone cam-1 image picks up cam-0's nearest-timestamp heading."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    records = [
        _make_record(0, 0, 37.000, -120.0, t0 + timedelta(seconds=0)),
        _make_record(0, 1, 37.001, -120.0, t0 + timedelta(seconds=2)),
        _make_record(0, 2, 37.002, -120.0, t0 + timedelta(seconds=4)),
        _make_record(1, 0, 37.001, -120.001, t0 + timedelta(seconds=2)),
    ]
    svc = WaldoMetadataService(terrain_service=None)
    svc.derive_headings(records)
    cam1 = next(r for r in records if r.cam_idx == 1)
    assert cam1.heading_deg is not None  # filled from cam 0


# --------------------------------------------------------------------------
# process_folder progress phasing
# --------------------------------------------------------------------------

def test_process_folder_emits_indeterminate_phases_before_per_image(tmp_path):
    """The pre-pass dialog must show phase status before any per-image work
    happens — otherwise the dialog freezes at 'Starting' / 0% while the EGM96
    geoid grid loads. This test asserts an indeterminate phase (total == 0)
    fires before any determinate per-image emission."""
    # Stub a tiny "WALDO" file — process_folder should reach the metadata-read
    # phase even though the file isn't a real JPEG. Errors during EXIF read
    # are recorded per-image and are fine for this signal-only test.
    waldo_jpg = tmp_path / "0_test.jpg"
    waldo_jpg.write_bytes(b"\xff\xd8\xff\xd9")  # SOI + EOI, minimal JPEG

    events = []  # list of (current, total, status)

    def progress_cb(current, total, status):
        events.append((current, total, status))

    svc = WaldoMetadataService(terrain_service=None)
    svc.process_folder([str(waldo_jpg)], progress_cb=progress_cb)

    assert events, "process_folder did not emit any progress events"
    # The first event must be indeterminate (total=0) — that's how the dialog
    # knows to show a busy spinner instead of 0%.
    first_total = events[0][1]
    assert first_total == 0, (
        f"First emission must be indeterminate phase, got total={first_total}: {events[0]}"
    )
    # And at least one of the early events should advertise reading metadata.
    assert any("metadata" in e[2].lower() for e in events[:3]), \
        f"Expected an early 'metadata' phase status, got {events[:3]}"
