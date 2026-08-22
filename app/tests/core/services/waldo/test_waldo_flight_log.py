"""Unit tests for WaldoFlightLogService (ForeFlight track-log calibration)."""

import math

from core.services.waldo.WaldoFlightLog import (
    CLOCK_FIT_MAX_MEAN_DIST_M,
    FEET_TO_M,
    KNOTS_TO_MPS,
    LAG_MIN_CORRELATION,
    FlightLogTrack,
    WaldoFlightLogService,
    _lerp_angle,
)


# --------------------------------------------------------------------------
# CSV synthesis helpers
# --------------------------------------------------------------------------

SUMMARY_ROWS = (
    "Pilot,Tail Number,Derived Origin,Start Latitude,Start Longitude,"
    "Derived Destination,End Latitude,End Longitude,Start Time,End Time\n"
    '"","N183CP","KBIH",37.0,-118.0,"KOAK",37.7,-122.2,1700000000000,1700000300000\n'
)

POINT_HEADER = (
    "Timestamp,Latitude,Longitude,Altitude,Course,Speed,Bank,Pitch,"
    "Horizontal Error,Vertical Error\n"
)


def _point_row(t, lat, lon, alt_ft=5000.0, course=0.0, speed_kt=97.2,
               bank=0.0, pitch=1.5, fmt="{:.6f}"):
    ts = fmt.format(t) if isinstance(fmt, str) else fmt(t)
    return f"{ts},{lat:.8f},{lon:.8f},{alt_ft:.1f},{course:.4f},{speed_kt:.4f},{bank:.4f},{pitch:.4f},1.0,1.5\n"


def _write_log(path, point_rows, summary=SUMMARY_ROWS, header=POINT_HEADER):
    path.write_text(summary + header + "".join(point_rows), encoding="utf-8")
    return str(path)


# Northbound line at ~50 m/s starting (37.0, -118.0) at epoch T0.
T0 = 1_700_000_000.0
LAT_PER_S = 50.0 / 111_320.0


def _line_lat(t):
    return 37.0 + (t - T0) * LAT_PER_S


def _line_rows(duration_s, **kwargs):
    return [_point_row(T0 + k, _line_lat(T0 + k), -118.0, **kwargs)
            for k in range(int(duration_s) + 1)]


# --------------------------------------------------------------------------
# sniff + candidate discovery
# --------------------------------------------------------------------------

def test_sniff_accepts_foreflight_and_rejects_others(tmp_path):
    good = tmp_path / "tracklog.csv"
    good.write_text(SUMMARY_ROWS, encoding="utf-8")
    bad = tmp_path / "other.csv"
    bad.write_text("Timestamp,Latitude\n1,2\n", encoding="utf-8")
    assert WaldoFlightLogService.sniff(str(good)) is True
    assert WaldoFlightLogService.sniff(str(bad)) is False
    assert WaldoFlightLogService.sniff(str(tmp_path / "missing.csv")) is False


def test_candidate_files_searches_parents_and_filters(tmp_path):
    images = tmp_path / "one" / "two" / "images"
    images.mkdir(parents=True)
    root_log = tmp_path / "tracklog-1.csv"
    root_log.write_text(SUMMARY_ROWS, encoding="utf-8")
    local_log = images / "tracklog-2.csv"
    local_log.write_text(SUMMARY_ROWS, encoding="utf-8")
    decoy = images / "notes.csv"
    decoy.write_text("just,a,csv\n", encoding="utf-8")

    found = WaldoFlightLogService.candidate_files(str(images))
    assert str(local_log) in found
    assert str(root_log) in found
    assert str(decoy) not in found


# --------------------------------------------------------------------------
# parse
# --------------------------------------------------------------------------

def test_parse_units_conversions_and_tolerance(tmp_path):
    rows = [
        # scientific-notation timestamp like real exports
        _point_row(T0, 37.0, -118.0, alt_ft=1000.0, course=90.0, speed_kt=100.0,
                   bank=5.0, pitch=2.0, fmt=lambda t: f"{t:.10E}"),
        _point_row(T0 + 1, 37.0001, -118.0, course=-1.0),      # invalid course
        "garbage,row\n",                                        # malformed: skipped
        _point_row(T0 + 0.5, 37.0, -118.0),                     # non-monotonic: skipped
        _point_row(T0 + 2, 37.0002, -118.0),
        "1.700000003E9,37.0003,-118.0,5000.0,0.0",              # truncated tail: skipped
    ]
    svc = WaldoFlightLogService()
    track = svc.parse(_write_log(tmp_path / "log.csv", rows))
    assert track is not None
    assert len(track) == 3
    assert track.t == [T0, T0 + 1, T0 + 2]
    assert math.isclose(track.alt_m[0], 1000.0 * FEET_TO_M)
    assert math.isclose(track.speed_mps[0], 100.0 * KNOTS_TO_MPS)
    assert track.course[0] == 90.0
    assert track.course[1] is None
    assert track.bank[0] == 5.0
    assert track.pitch[0] == 2.0


def test_parse_rejects_non_foreflight_and_tiny_logs(tmp_path):
    svc = WaldoFlightLogService()
    not_ff = tmp_path / "plain.csv"
    not_ff.write_text(POINT_HEADER + _point_row(T0, 37.0, -118.0), encoding="utf-8")
    assert svc.parse(str(not_ff)) is None
    tiny = _write_log(tmp_path / "tiny.csv", [_point_row(T0, 37.0, -118.0)])
    assert svc.parse(tiny) is None


# --------------------------------------------------------------------------
# interpolation
# --------------------------------------------------------------------------

def test_interpolate_position_midpoint_bounds_and_gaps(tmp_path):
    track = FlightLogTrack(path="x", t=[0.0, 1.0, 10.0], lat=[37.0, 37.001, 37.002],
                           lon=[-118.0, -118.0, -118.0], alt_m=[0, 0, 0],
                           course=[0.0, 0.0, 0.0], speed_mps=[50, 50, 50],
                           bank=[0, 0, 0], pitch=[0, 0, 0])
    lat, lon = WaldoFlightLogService.interpolate_position(track, 0.5)
    assert math.isclose(lat, 37.0005)
    assert WaldoFlightLogService.interpolate_position(track, -0.1) is None
    assert WaldoFlightLogService.interpolate_position(track, 10.5) is None
    # 9-second spacing exceeds MAX_INTERP_GAP_S
    assert WaldoFlightLogService.interpolate_position(track, 5.0) is None


def test_sample_attitude_lag_shift_and_circular_course():
    track = FlightLogTrack(path="x", t=[float(k) for k in range(11)],
                           lat=[37.0] * 11, lon=[-118.0] * 11, alt_m=[0] * 11,
                           course=[350.0, 10.0] + [10.0] * 9,
                           speed_mps=[50] * 11,
                           bank=[float(k) for k in range(11)],
                           pitch=[float(k) / 2 for k in range(11)])
    s = WaldoFlightLogService.sample_attitude(track, 5.0, lag_s=2.0)
    assert s.in_coverage
    assert math.isclose(s.bank_deg, 7.0)
    assert math.isclose(s.pitch_deg, 3.5)
    # course read at t (not lagged), circularly across north
    s0 = WaldoFlightLogService.sample_attitude(track, 0.5, lag_s=0.0)
    assert math.isclose(s0.course_deg, 0.0, abs_tol=1e-9)
    # outside coverage after lag shift
    far = WaldoFlightLogService.sample_attitude(track, 10.5, lag_s=2.0)
    assert far.in_coverage is False
    assert far.bank_deg is None


def test_lerp_angle_wraps():
    assert math.isclose(_lerp_angle(350.0, 10.0, 0.5), 0.0, abs_tol=1e-9)
    assert math.isclose(_lerp_angle(10.0, 350.0, 0.25), 5.0, abs_tol=1e-9)


# --------------------------------------------------------------------------
# clock-offset fit
# --------------------------------------------------------------------------

def test_fit_clock_offset_recovers_known_offset(tmp_path):
    svc = WaldoFlightLogService()
    track = svc.parse(_write_log(tmp_path / "log.csv", _line_rows(240)))
    # Pod clock 17 s FAST: face time = true + 17, so the image taken at true
    # time (t_face - 17) carries GPS from there; the fit must find -17.
    images = []
    for t_face in range(int(T0) + 40, int(T0) + 200, 10):
        t_true = t_face - 17.0
        images.append((float(t_face), _line_lat(t_true), -118.0))
    offset, mean_dist, matched = svc.fit_clock_offset(track, images)
    assert math.isclose(offset, -17.0, abs_tol=0.2)
    assert mean_dist < 2.0
    assert matched == 1.0


def test_calibrate_rejects_wrong_area_log(tmp_path):
    svc = WaldoFlightLogService()
    log = _write_log(tmp_path / "log.csv", _line_rows(240))
    images = [(T0 + 60.0 + k, 36.5, -117.5) for k in range(0, 100, 10)]  # ~70 km away
    fit = svc.calibrate(log, images)
    assert fit.accepted is False
    assert "track" in fit.reason
    assert fit.mean_track_dist_m > CLOCK_FIT_MAX_MEAN_DIST_M


# --------------------------------------------------------------------------
# attitude-lag fit
# --------------------------------------------------------------------------

def _turning_rows(lag_s):
    """Straight flight, a coordinated right turn, straight again.

    The bank profile is SMOOTH (the aircraft rolls in/out over 6 s) so the
    correlation peak is unambiguous; a step profile would leave the discrete
    peak straddling a half-sample. Course is the integral of the turn rate a
    coordinated turn at that bank produces; the logged bank column reproduces
    the true bank of (t - lag_s), i.e. the attitude channel is recorded late.
    """
    v = 97.2 * KNOTS_TO_MPS
    max_bank = math.degrees(math.atan(v * math.radians(3.0) / 9.80665))  # ~15 deg

    def bank_true(t):
        s = t - T0
        if s < 120.0 or s >= 180.0:
            return 0.0
        if s < 126.0:
            return max_bank * (s - 120.0) / 6.0
        if s >= 174.0:
            return max_bank * (180.0 - s) / 6.0
        return max_bank

    rows = []
    lat, lon = 37.0, -118.0
    course = 0.0
    substeps = 10  # fine integration so the logged course is not Euler-biased
    for k in range(301):
        t = T0 + k
        c = math.radians(course)
        lat += (v / 111_320.0) * math.cos(c)
        lon += (v / (111_320.0 * math.cos(math.radians(lat)))) * math.sin(c)
        rows.append(_point_row(t, lat, lon, course=course % 360.0,
                               bank=bank_true(t - lag_s)))
        for j in range(substeps):
            omega = math.tan(math.radians(bank_true(t + (j + 0.5) / substeps))) * 9.80665 / v
            course += math.degrees(omega) / substeps
    return rows


def test_fit_attitude_lag_recovers_known_lag(tmp_path):
    svc = WaldoFlightLogService()
    track = svc.parse(_write_log(tmp_path / "log.csv", _turning_rows(lag_s=4.0)))
    lag, corr = svc.fit_attitude_lag(track, T0 + 20, T0 + 280)
    assert lag == 4.0
    assert corr > 0.9


def test_calibrate_flags_flat_attitude_as_unreliable(tmp_path):
    svc = WaldoFlightLogService()
    # Real turns in the course channel but a dead-flat bank column: the
    # correlation cannot reach the threshold, so attitude must be untrusted
    # while the clock fit stays accepted.
    rows = _turning_rows(lag_s=0.0)
    rows = [r.rsplit(",", 4)[0] + ",0.0000,1.5000,1.0,1.5\n" for r in rows]
    track_path = _write_log(tmp_path / "log.csv", rows)
    svc_track = svc.parse(track_path)
    images = []
    for k in range(20, 280, 10):
        pos = WaldoFlightLogService.interpolate_position(svc_track, T0 + k)
        images.append((T0 + k, pos[0], pos[1]))
    fit = svc.calibrate(track_path, images)
    assert fit.accepted is True
    assert math.isclose(fit.clock_offset_s, 0.0, abs_tol=0.2)
    assert fit.attitude_reliable is False
    assert fit.lag_correlation < LAG_MIN_CORRELATION


def test_calibrate_full_pipeline_accepts_and_reports(tmp_path):
    svc = WaldoFlightLogService()
    log = _write_log(tmp_path / "log.csv", _turning_rows(lag_s=4.0))
    track = svc.parse(log)
    images = []
    for k in range(20, 280, 10):
        t_true = T0 + k
        pos = WaldoFlightLogService.interpolate_position(track, t_true)
        images.append((t_true + 17.0, pos[0], pos[1]))  # clock 17 s fast
    fit = svc.calibrate(log, images)
    assert fit.accepted is True
    assert math.isclose(fit.clock_offset_s, -17.0, abs_tol=0.2)
    assert fit.attitude_reliable is True
    assert fit.attitude_lag_s == 4.0
    assert fit.bank_max_deg > 10.0
    assert fit.log_sha256 == WaldoFlightLogService.content_hash(log)
