"""Unit tests for WaldoMetadataService."""

import importlib
import math
from datetime import datetime, timedelta

import cv2
import numpy as np
import pytest

from core.services.image.AOIService import AOIService

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

def test_optical_axis_cam_0_fallback_yaw_and_flight_axis_roll():
    # No measured orientation: yaw falls back to the mounting model
    # (image-top = plane backward = heading + 180). As of v6 the roll is
    # expressed about the FLIGHT axis: about the forward axis a positive
    # Rodrigues roll tilts LEFT, so cam 0 (right tilt) is negative.
    angles = WaldoMetadataService.compute_optical_axis_angles(45.0, 0)
    assert angles['pitch'] == -90.0
    assert angles['yaw'] == 225.0  # 45 + 180
    assert angles['roll'] == -OUTWARD_ROLL_DEG


def test_optical_axis_cam_1_fallback_yaw_and_flight_axis_roll():
    # `1_*` = LEFT pod, body mounted opposed to cam 0: its stored image-top
    # faces plane FORWARD (v9 fix - v5..v8 wrongly stamped it backward).
    # Tilt to plane LEFT = positive roll about the forward flight axis.
    angles = WaldoMetadataService.compute_optical_axis_angles(0.0, 1)
    assert angles['pitch'] == -90.0
    assert angles['yaw'] == 0.0  # image-top = heading for cam 1
    assert angles['roll'] == +OUTWARD_ROLL_DEG


def test_optical_axis_cam_1_yaw_follows_heading():
    angles = WaldoMetadataService.compute_optical_axis_angles(270.0, 1)
    assert angles['yaw'] == 270.0
    angles = WaldoMetadataService.compute_optical_axis_angles(319.67, 1)
    assert pytest.approx(angles['yaw'], abs=1e-6) == 319.67


def test_optical_axis_measured_orientation_wins_over_model():
    # A measured orientation overrides the mounting model entirely; the
    # roll stays anchored to the flight axis so the physical tilt is
    # unchanged by whatever orientation the frames are stored in.
    angles = WaldoMetadataService.compute_optical_axis_angles(
        45.0, 0, measured_orientation=('absolute', 1.5))
    assert angles['yaw'] == 1.5
    assert angles['roll'] == -OUTWARD_ROLL_DEG
    angles = WaldoMetadataService.compute_optical_axis_angles(
        45.0, 1, measured_orientation=('absolute', 359.0))
    assert angles['yaw'] == 359.0
    assert angles['roll'] == +OUTWARD_ROLL_DEG


def test_optical_axis_measured_offset_is_track_relative():
    # ('offset', d) stamps heading + d per image - serpentine-safe: the
    # same offset yields opposite absolute yaws on opposite lanes.
    angles = WaldoMetadataService.compute_optical_axis_angles(
        10.0, 0, measured_orientation=('offset', 175.0))
    assert pytest.approx(angles['yaw'], abs=1e-6) == 185.0
    angles = WaldoMetadataService.compute_optical_axis_angles(
        190.0, 0, measured_orientation=('offset', 175.0))
    assert pytest.approx(angles['yaw'], abs=1e-6) == 5.0


def test_optical_axis_invalid_orientation_mode_raises():
    with pytest.raises(ValueError):
        WaldoMetadataService.compute_optical_axis_angles(
            0.0, 0, measured_orientation=('sideways', 1.0))


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


def test_heading_serpentine_lane_edges_use_one_sided_bearing():
    """Lane-edge images must derive from their OWN lane, never inherit the
    previous lane's heading across the turn gap.

    Serpentine field flights showed the first image of each lane stamped
    ~180 deg flipped: the >30 s turn starved the two-sided bearing pass and
    the forward fill copied the opposite lane's heading.
    """
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    records = []
    # Lane A: northbound, captures every 2 s.
    for i in range(4):
        records.append(_make_record(0, i, 37.000 + i * 0.001, -120.000,
                                    t0 + timedelta(seconds=i * 2)))
    # 90 s turn gap (beyond MAX_NEIGHBOR_DT_S), then lane B: SOUTHBOUND.
    for i in range(4):
        records.append(_make_record(0, 10 + i, 37.003 - i * 0.001, -120.002,
                                    t0 + timedelta(seconds=90 + i * 2)))
    svc = WaldoMetadataService(terrain_service=None)
    svc.derive_headings(records)
    lane_a = records[:4]
    lane_b = records[4:]
    for r in lane_a:
        diff = min(abs(r.heading_deg), abs(360.0 - r.heading_deg))
        assert diff < 5.0, f"lane A image {r.name} heading {r.heading_deg}"
    for r in lane_b:
        assert abs(r.heading_deg - 180.0) < 5.0, \
            f"lane B image {r.name} heading {r.heading_deg} (flip regression)"


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

# --------------------------------------------------------------------------
# v5 -> v6 tilt equivalence and orientation measurement
# --------------------------------------------------------------------------


def _ground_offset_m(lat0, lon0, lat, lon):
    north = (lat - lat0) * 111320.0
    east = (lon - lon0) * 111320.0 * math.cos(math.radians(lat0))
    return north, east


def test_flight_axis_roll_reproduces_v5_tilt_direction():
    """The v6 stamping (flight-axis roll) must tilt the footprint the same
    way the v5 stamping (backward gimbal-yaw-axis roll) did.

    Projects the image-centre pixel with both parameterizations through the
    real ray-casting code: the ground point must land cross-track on the
    same side of the aircraft, in the same place.
    """
    heading = 45.0
    lat0, lon0 = 41.0, -122.0
    kwargs = dict(cx=2000.0, cy=1500.0, img_width=4000, img_height=3000,
                  focal_mm=50.0, sensor_w_mm=36.0, sensor_h_mm=24.0)

    for cam_idx, side_sign in ((0, +1), (1, -1)):  # cam0 tilts plane-RIGHT
        # v5: yaw = heading+180, roll about the (default) yaw axis
        v5_roll = (+OUTWARD_ROLL_DEG) if cam_idx == 0 else (-OUTWARD_ROLL_DEG)
        v5 = AOIService._calculate_ground_position(
            lat0, lon0, 2000.0, 1500.0,
            altitude_m=1000.0, pitch_deg=-90.0,
            yaw_deg=(heading + 180.0) % 360.0, roll_deg=v5_roll,
            **kwargs)

        # v6: measured yaw (north-up here), roll about the flight axis
        angles = WaldoMetadataService.compute_optical_axis_angles(
            heading, cam_idx, measured_orientation=('absolute', 0.0))
        v6 = AOIService._calculate_ground_position(
            lat0, lon0, 2000.0, 1500.0,
            altitude_m=1000.0, pitch_deg=angles['pitch'],
            yaw_deg=angles['yaw'], roll_deg=angles['roll'],
            roll_axis_azimuth_deg=heading,
            **kwargs)

        assert v5 is not None and v6 is not None
        n5, e5 = _ground_offset_m(lat0, lon0, *v5)
        n6, e6 = _ground_offset_m(lat0, lon0, *v6)
        # Same physical point: the centre-pixel footprint is tilt-driven and
        # identical regardless of how the stored pixels are rotated
        assert abs(n5 - n6) < 1.0 and abs(e5 - e6) < 1.0

        # And it lies cross-track on the correct side of the flight axis
        h = math.radians(heading)
        cross = -math.sin(h) * n5 + math.cos(h) * e5  # +ve = plane right
        assert cross * side_sign > 100.0  # 22.5 deg at 1000m AGL: ~414m


def _write_shifted_frames(out_dir, shift_xy, size=(1800, 2400), seed=5):
    """Two JPEG 'frames' of one texture, the second shifted by shift_xy.

    The texture uses blurred blobs large enough to survive the service's
    ORIENTATION_DOWNSCALE before feature matching.
    """
    import os as _os
    _os.makedirs(str(out_dir), exist_ok=True)
    rng = np.random.default_rng(seed)
    h, w = size
    dx, dy = shift_xy
    margin = max(abs(dx), abs(dy)) + 50
    canvas = rng.integers(0, 255, (h + 2 * margin, w + 2 * margin), dtype=np.uint8)
    canvas = cv2.GaussianBlur(canvas, (0, 0), 5.0)
    canvas = cv2.normalize(canvas, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    oy, ox = margin, margin
    a = canvas[oy:oy + h, ox:ox + w]
    b = canvas[oy + dy:oy + dy + h, ox + dx:ox + dx + w]
    pa = str(out_dir) + _os.sep + '0_000_00_000.jpg'
    pb = str(out_dir) + _os.sep + '0_000_00_001.jpg'
    cv2.imwrite(pa, a)
    cv2.imwrite(pb, b)
    return pa, pb


def test_pair_orientation_sample_recovers_known_rotation(tmp_path):
    """Content shifted 'up' while GPS says 'moving north' => north-up frames."""
    # Frame b crops a region 300px higher on the shared texture: the camera
    # moved 'up' in image terms between the frames.
    pa, pb = _write_shifted_frames(tmp_path, (0, -300))

    # Camera moved up in image; GPS bearing says due north
    result = WaldoMetadataService._pair_orientation_sample(pa, pb, 0.0)
    assert result is not None
    image_up, inliers = result
    assert inliers >= 20
    # image-up should be ~north (0 deg)
    assert min(image_up, 360.0 - image_up) < 6.0

    # Same imagery, but GPS says the motion was due east: the image's top
    # must then be pointing west (270)
    result = WaldoMetadataService._pair_orientation_sample(pa, pb, 90.0)
    assert result is not None
    assert abs(result[0] - 90.0) < 6.0


def _motion_records(tmp_path, heading_deg):
    """Synthetic north-up frames moving north, with the given model heading."""
    records = []
    lat = 41.0
    for i in range(5):
        pa, pb = _write_shifted_frames(tmp_path / f'p{i}', (0, -280 - 10 * i), seed=i)
        # GPS: successive frames move north by ~200m
        records.append(WaldoImageRecord(path=pa, name=f'0_000_00_{2*i:03d}.jpg',
                                        cam_idx=0, lat=lat, lon=-122.0,
                                        heading_deg=heading_deg))
        lat += 0.0018
        records.append(WaldoImageRecord(path=pb, name=f'0_000_00_{2*i+1:03d}.jpg',
                                        cam_idx=0, lat=lat, lon=-122.0,
                                        heading_deg=heading_deg))
        lat += 0.0018
    return records


def test_measurement_overrides_model_only_on_clear_contradiction(tmp_path):
    """North-up frames with a model saying 'south-up' trip the override."""
    service = WaldoMetadataService()
    # heading 0 -> cam0 model offset = 180; measurement reads offset ~0
    records = _motion_records(tmp_path, heading_deg=0.0)

    measured = service.measure_image_up_orientation(records, cam_idx=0)
    assert measured is not None
    mode, value = measured
    assert mode == 'offset'
    assert min(value, 360.0 - value) < 8.0


def test_measurement_agreeing_with_model_defers_to_it(tmp_path):
    """When measurement and model roughly agree, the model is stamped."""
    service = WaldoMetadataService()
    # heading 180 -> frames read offset (0-180)=180 = cam0 model -> agree
    records = _motion_records(tmp_path, heading_deg=180.0)

    assert service.measure_image_up_orientation(records, cam_idx=0) is None


def test_measurement_rejects_unmatchable(tmp_path):
    """Unrelated noise frames must fail closed (fall back to the model)."""
    service = WaldoMetadataService()
    rng = np.random.default_rng(9)
    records = []
    lat = 41.0
    for i in range(5):
        p = str(tmp_path / f'0_000_00_{i:03d}.jpg')
        cv2.imwrite(p, rng.integers(0, 255, (400, 500), dtype=np.uint8))
        records.append(WaldoImageRecord(path=p, name=f'0_000_00_{i:03d}.jpg',
                                        cam_idx=0, lat=lat, lon=-122.0,
                                        heading_deg=0.0))
        lat += 0.0018

    assert service.measure_image_up_orientation(records, cam_idx=0) is None


def _serpentine_records(tmp_path, cam, lane_specs, seed0=0):
    """Records for a multi-lane flight; lane_specs = [(heading, north?, dy)].

    Each lane contributes 3 synthetic frame pairs. dy is the crop shift of
    the pair's second frame: +dy makes the camera appear to move toward the
    image BOTTOM between frames, -dy toward the image TOP.
    """
    records = []
    idx = 0
    lat = 41.0
    for lane_no, (heading, north, dy) in enumerate(lane_specs):
        dlat = 0.0018 if north else -0.0018
        for i in range(3):
            pa, pb = _write_shifted_frames(
                tmp_path / f'l{lane_no}p{i}', (0, dy), seed=seed0 + idx)
            for p in (pa, pb):
                records.append(WaldoImageRecord(
                    path=p, name=f'{cam}_000_00_{idx:03d}.jpg', cam_idx=cam,
                    lat=lat, lon=-122.0, heading_deg=heading))
                lat += dlat
                idx += 1
    return records


def test_measurement_serpentine_track_relative_defers_to_model(tmp_path):
    """Serpentine cam0 storage (image-top follows the track) must NOT trip
    the override, even though the ABSOLUTE orientations alternate 0/180.

    This is the exact failure mode that hid the cam-1 bug in v5..v8: the
    absolute circular mean of alternating lanes was garbage, so the
    measurement returned None instead of validating the model.
    """
    service = WaldoMetadataService()
    # cam0 stores image-top = heading+180. Northbound lane (heading 0):
    # top faces south -> northward motion reads motion_img 180 -> dy +280.
    # Southbound lane (heading 180): top faces north -> dy +280 as well.
    records = _serpentine_records(tmp_path, 0, [
        (0.0, True, +280),
        (180.0, False, +280),
    ])
    assert service.measure_image_up_orientation(records, cam_idx=0) is None


def test_measurement_detects_normalized_absolute_on_serpentine(tmp_path):
    """North-up-normalized frames on a serpentine flight: the relative space
    scrambles (offsets 0/180) but the absolute space is tight at ~0, and a
    constant absolute orientation across mixed headings contradicts ANY
    mounting model - the override must fire in absolute mode."""
    service = WaldoMetadataService()
    records = _serpentine_records(tmp_path, 0, [
        (0.0, True, -280),    # northbound, north-up: motion toward image top
        (180.0, False, +280),  # southbound, north-up: motion toward image bottom
    ])
    measured = service.measure_image_up_orientation(records, cam_idx=0)
    assert measured is not None
    mode, value = measured
    assert mode == 'absolute'
    assert min(value, 360.0 - value) < 8.0


def test_measurement_cam1_forward_storage_matches_v9_model(tmp_path):
    """cam1 frames stored image-top = plane FORWARD (the real WALDO output,
    field-verified on two flights) must agree with the v9 model and stamp
    it. Under the v5..v8 model (top = backward) this same data was a 180 deg
    contradiction that the old absolute aggregation failed to report."""
    service = WaldoMetadataService()
    records = _serpentine_records(tmp_path, 1, [
        (0.0, True, -280),     # northbound, top=forward(north): motion toward top
        (180.0, False, -280),  # southbound, top=forward(south): motion toward top
    ])
    assert service.measure_image_up_orientation(records, cam_idx=1) is None


# --------------------------------------------------------------------------
# Capture-time audit
# --------------------------------------------------------------------------

def test_parse_offset_hours():
    assert WaldoMetadataService._parse_offset_hours(b'-06:00') == -6.0
    assert WaldoMetadataService._parse_offset_hours('+05:30') == 5.5
    assert WaldoMetadataService._parse_offset_hours(None) is None
    assert WaldoMetadataService._parse_offset_hours(b'garbage') is None


def _audit_exif(dt_bytes, offset_bytes):
    import piexif
    return {
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: dt_bytes,
            piexif.ExifIFD.OffsetTimeOriginal: offset_bytes,
        },
        'GPS': {},
    }


def test_audit_flags_timezone_longitude_mismatch(tmp_path, monkeypatch):
    """A camera set to -06:00 at longitude -122.9 must be flagged."""
    waldo_module = importlib.import_module('core.services.waldo.WaldoMetadataService')
    p = str(tmp_path / '0_000_00_000.jpg')
    open(p, 'wb').write(b'x')

    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        lambda path: _audit_exif(b'2026:07:25 09:00:00', b'-06:00'))
    monkeypatch.setattr(waldo_module.LocationInfo, 'get_gps',
                        lambda exif_data: {'latitude': 41.3, 'longitude': -122.9})

    warnings = WaldoMetadataService().audit_capture_times([p])
    assert any('timezone' in w for w in warnings)


def test_audit_flags_capture_after_file_write(tmp_path, monkeypatch):
    """A claimed capture hours after the file's mtime means the clock is ahead."""
    import os as _os
    waldo_module = importlib.import_module('core.services.waldo.WaldoMetadataService')
    from datetime import datetime, timedelta, timezone as tz

    p = str(tmp_path / '0_000_00_000.jpg')
    open(p, 'wb').write(b'x')
    # Claimed capture: 10 hours after the file's mtime
    claimed_local = datetime.fromtimestamp(
        _os.path.getmtime(p), tz=tz.utc) + timedelta(hours=10) - timedelta(hours=8)
    dt_bytes = claimed_local.strftime('%Y:%m:%d %H:%M:%S').encode()

    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        lambda path: _audit_exif(dt_bytes, b'-08:00'))
    monkeypatch.setattr(waldo_module.LocationInfo, 'get_gps',
                        lambda exif_data: {'latitude': 41.3, 'longitude': -122.9})

    warnings = WaldoMetadataService().audit_capture_times([p])
    assert any('AFTER' in w for w in warnings)


def test_audit_quiet_on_healthy_metadata(tmp_path, monkeypatch):
    """Correct offset, past capture time, sun up: no warnings."""
    import os as _os
    waldo_module = importlib.import_module('core.services.waldo.WaldoMetadataService')
    from datetime import datetime, timedelta, timezone as tz

    p = str(tmp_path / '0_000_00_000.jpg')
    open(p, 'wb').write(b'x')
    # Claimed capture: two hours before the file was written, offset -08:00
    claimed_local = datetime.fromtimestamp(
        _os.path.getmtime(p), tz=tz.utc) - timedelta(hours=2) - timedelta(hours=8)
    dt_bytes = claimed_local.strftime('%Y:%m:%d %H:%M:%S').encode()

    monkeypatch.setattr(waldo_module.MetaDataHelper, 'get_exif_data_piexif',
                        lambda path: _audit_exif(dt_bytes, b'-08:00'))
    monkeypatch.setattr(waldo_module.LocationInfo, 'get_gps',
                        lambda exif_data: {'latitude': 41.3, 'longitude': -122.9})
    # Force the solar check to a sun-up answer so no daylight warning can fire
    monkeypatch.setattr(waldo_module, 'get_solar_position', lambda lat, lon, utc: (30.0, 120.0))

    assert WaldoMetadataService().audit_capture_times([p]) == []
