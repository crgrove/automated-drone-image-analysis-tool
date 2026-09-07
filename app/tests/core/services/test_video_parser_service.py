"""
Comprehensive tests for VideoParserService.

Tests video parsing and frame extraction functionality.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QObject
from core.services.VideoParserService import VideoParserService


@pytest.fixture
def video_parser_service():
    """Fixture providing a VideoParserService instance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, 'test_video.mp4')
        srt_path = os.path.join(tmpdir, 'test.srt')
        output_dir = os.path.join(tmpdir, 'output')
        os.makedirs(output_dir, exist_ok=True)

        service = VideoParserService(
            id=1,
            video=video_path,
            metadata_path=srt_path,
            output=output_dir,
            interval=1.0
        )
        yield service


def test_video_parser_service_initialization(video_parser_service):
    """Test VideoParserService initialization."""
    # __id is a private attribute, access via name mangling
    assert video_parser_service._VideoParserService__id == 1
    assert video_parser_service.interval == 1.0
    assert video_parser_service.cancelled is False


def test_video_parser_service_signals(video_parser_service):
    """Test that signals are properly defined."""
    assert hasattr(video_parser_service, 'sig_msg')
    assert hasattr(video_parser_service, 'sig_done')


def test_video_parser_service_cancellation(video_parser_service):
    """Test cancellation functionality."""
    assert video_parser_service.cancelled is False
    video_parser_service.cancelled = True
    assert video_parser_service.cancelled is True


def test_process_video_invalid_file(video_parser_service):
    """Test processing invalid video file."""
    with patch('cv2.VideoCapture') as mock_capture:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_capture.return_value = mock_cap

        # This should emit error signal
        video_parser_service.process_video()

        # Verify error handling
        assert True  # If we get here, no exception was raised


class TestTelemetryResolution:
    """Location data now resolves without an explicit metadata file.

    Newer DJI aircraft embed telemetry in the MP4 rather than writing a
    ``.SRT`` sidecar, so a card-pull of just the video used to lose all
    GPS. These cover the resolution paths and the status reporting the
    dialog shows the operator.
    """

    RESOLVER = 'core.services.VideoParserService.load_telemetry_for_video'

    def _service(self, tmpdir, metadata_path=''):
        return VideoParserService(
            id=1,
            video=os.path.join(tmpdir, 'v.mp4'),
            metadata_path=metadata_path,
            output=tmpdir,
            interval=1.0,
        )

    def _resolution(self, source, count=3, detail=''):
        from core.services.telemetry.DjiSrtParser import DjiSrtSample
        from core.services.telemetry.TelemetrySourceResolver import TelemetryResolution
        from core.services.telemetry.TelemetryTrack import TelemetryTrack

        track = TelemetryTrack.from_dji_samples([
            DjiSrtSample(
                start_seconds=float(i), end_seconds=float(i) + 0.03,
                latitude=30.0 + i, longitude=-97.0 - i,
                altitude_msl_m=200.0 + i, altitude_ato_m=15.0,
            )
            for i in range(count)
        ])
        return TelemetryResolution(
            track=track, source=source, path='/tmp/x.SRT',
            detail=detail or f'{count} fixes',
        )

    def test_embedded_source_is_reported(self):
        from core.services.telemetry.TelemetrySourceResolver import SOURCE_EMBEDDED

        with tempfile.TemporaryDirectory() as tmpdir:
            service = self._service(tmpdir)
            messages = []
            service.sig_msg.connect(messages.append)

            with patch(self.RESOLVER,
                       return_value=self._resolution(SOURCE_EMBEDDED)):
                track = service._resolve_telemetry()

            assert track is not None
            assert any('embedded' in m.lower() for m in messages)

    def test_sidecar_source_is_reported(self):
        from core.services.telemetry.TelemetrySourceResolver import SOURCE_SIDECAR

        with tempfile.TemporaryDirectory() as tmpdir:
            service = self._service(tmpdir)
            messages = []
            service.sig_msg.connect(messages.append)

            with patch(self.RESOLVER,
                       return_value=self._resolution(SOURCE_SIDECAR)):
                service._resolve_telemetry()

            assert any('x.SRT' in m for m in messages)

    def test_missing_telemetry_returns_none(self):
        from core.services.telemetry.TelemetrySourceResolver import (
            SOURCE_NONE, TelemetryResolution,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            service = self._service(tmpdir)
            with patch(self.RESOLVER, return_value=TelemetryResolution(
                    track=None, source=SOURCE_NONE)):
                assert service._resolve_telemetry() is None

    def test_unreadable_explicit_file_warns(self):
        from core.services.telemetry.TelemetrySourceResolver import (
            SOURCE_EXPLICIT_FILE, TelemetryResolution,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            service = self._service(tmpdir, metadata_path='chosen.srt')
            messages = []
            service.sig_msg.connect(messages.append)

            with patch(self.RESOLVER, return_value=TelemetryResolution(
                    track=None, source=SOURCE_EXPLICIT_FILE,
                    detail='selected SRT contained no usable telemetry')):
                assert service._resolve_telemetry() is None

            assert any('Warning' in m for m in messages)

    def test_resolver_failure_is_survivable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = self._service(tmpdir)
            service.logger = MagicMock()
            with patch(self.RESOLVER, side_effect=OSError('boom')):
                assert service._resolve_telemetry() is None


class TestLegacySrtDelegate:
    """``_parse_srt_file`` keeps its historical dict shape for callers."""

    CLASSIC = (
        '1\n'
        '00:00:00,000 --> 00:00:00,033\n'
        '<font size="28">FrameCnt: 1, DiffTime: 33ms\n'
        '2023-05-01 10:00:00,000\n'
        '[latitude: 30.100000] [longtitude: -97.200000] [altitude: 210.5] </font>\n'
    )

    def test_returns_datetime_anchored_dicts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            srt = os.path.join(tmpdir, 'a.srt')
            with open(srt, 'w') as handle:
                handle.write(self.CLASSIC)

            service = VideoParserService(1, 'v.mp4', srt, tmpdir, 1.0)
            rows = service._parse_srt_file(srt)

            assert len(rows) == 1
            row = rows[0]
            assert set(row) == {'start', 'end', 'timestamp', 'latitude',
                                'longitude', 'altitude', 'relative_altitude'}
            assert row['start'].year == 1900
            # start/end stay anchored to the fake 1900 epoch (they are offsets
            # into the video); 'timestamp' is the cue's real wall clock.
            assert row['timestamp'] == datetime(2023, 5, 1, 10, 0, 0)
            assert row['latitude'] == pytest.approx(30.1)
            assert row['longitude'] == pytest.approx(-97.2)
            assert row['altitude'] == pytest.approx(210.5)

    def test_now_parses_the_embedded_four_line_variant(self):
        """Previously returned an empty list for this layout."""
        embedded = (
            '1\n'
            '00:00:00,000 --> 00:00:00,033\n'
            'FrameCnt: 0 2026-07-25 14:38:26.477\n'
            '[latitude: 30.648730] [longitude: -97.675867] '
            '[rel_alt: 14.885 abs_alt: 207.027]\n'
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            srt = os.path.join(tmpdir, 'b.srt')
            with open(srt, 'w') as handle:
                handle.write(embedded)

            service = VideoParserService(1, 'v.mp4', srt, tmpdir, 1.0)
            rows = service._parse_srt_file(srt)

            assert len(rows) == 1
            assert rows[0]['altitude'] == pytest.approx(207.027)

    def test_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = VideoParserService(1, 'v.mp4', '', tmpdir, 1.0)
            assert service._parse_srt_file(os.path.join(tmpdir, 'nope.srt')) is None


class TestCsvFlightLog:
    """CSV reading is shared with the streaming window's metadata-file path.

    The shape this method returns is load-bearing: ``process_video`` and
    ``_find_closest_csv_entry`` have consumed ``utc_time`` /
    ``latitude`` / ``longitude`` / ``altitude_m`` since the Skydio path was
    added, so the delegation must not change it.
    """

    SKYDIO = (
        'Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n'
        '2026-07-25T14:38:26Z,30.648730,-97.675867,679.2\n'
        '2026-07-25T14:38:27Z,30.648740,-97.675877,682.5\n'
    )

    def _service(self, tmpdir, csv_path):
        return VideoParserService(1, os.path.join(tmpdir, 'v.mp4'),
                                  csv_path, tmpdir, 1.0)

    def _write(self, tmpdir, text, name='flight.csv'):
        path = os.path.join(tmpdir, name)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(text)
        return path

    def test_detects_the_csv_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = self._service(tmpdir, 'log.csv')
            assert service._detect_metadata_format('log.csv') == 'csv'
            assert service._detect_metadata_format('a.SRT') == 'srt'
            assert service._detect_metadata_format('') is None

    def test_returns_the_historical_entry_shape(self):
        from datetime import datetime, timezone

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = self._write(tmpdir, self.SKYDIO)
            service = self._service(tmpdir, csv_path)
            start = datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)

            with patch('core.services.VideoParserService.get_video_creation_time',
                       return_value=start):
                video_start, entries = service._parse_csv_flight_log(
                    csv_path, 'v.mp4')

            assert video_start == start
            assert len(entries) == 2
            entry = entries[0]
            assert {'utc_time', 'latitude', 'longitude', 'altitude_m'} <= set(entry)
            assert entry['latitude'] == pytest.approx(30.648730)
            # Feet in the log, metres in the entry.
            assert entry['altitude_m'] == pytest.approx(679.2 * 0.3048)

    def test_a_relative_only_log_yields_no_absolute_altitude(self):
        """The entry shape's 'altitude_m' feeds EXIF GPSAltitude, which is an
        absolute height. A log with only a relative column has none, and the
        relative reading is not a stand-in for one."""
        text = (
            "Datetime (UTC),Latitude,Longitude,Relative Altitude (m)\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,42.0\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = self._write(tmpdir, text)
            service = self._service(tmpdir, csv_path)
            start = datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)

            with patch('core.services.VideoParserService.get_video_creation_time',
                       return_value=start):
                _video_start, entries = service._parse_csv_flight_log(
                    csv_path, 'v.mp4')

            entry = entries[0]
            assert entry['altitude_m'] is None
            assert entry['altitude_ato_m'] == pytest.approx(42.0)
            assert entry['altitude_agl_terrain_m'] is None

    def test_a_terrain_agl_log_keeps_its_own_reference(self):
        """'Altitude (m AGL)' is above the terrain, not above the ramp."""
        text = (
            "Datetime (UTC),Latitude,Longitude,Altitude (m AGL)\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,42.0\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = self._write(tmpdir, text)
            service = self._service(tmpdir, csv_path)
            start = datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)

            with patch('core.services.VideoParserService.get_video_creation_time',
                       return_value=start):
                _video_start, entries = service._parse_csv_flight_log(
                    csv_path, 'v.mp4')

            entry = entries[0]
            assert entry['altitude_agl_terrain_m'] == pytest.approx(42.0)
            assert entry['altitude_ato_m'] is None

    def test_entries_feed_the_closest_match_lookup(self):
        """The delegated rows must still be sortable/searchable by time."""
        from datetime import datetime, timedelta, timezone

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = self._write(tmpdir, self.SKYDIO)
            service = self._service(tmpdir, csv_path)
            start = datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)

            with patch('core.services.VideoParserService.get_video_creation_time',
                       return_value=start):
                _video_start, entries = service._parse_csv_flight_log(
                    csv_path, 'v.mp4')

            match = service._find_closest_csv_entry(
                entries, start + timedelta(seconds=1))
            assert match['latitude'] == pytest.approx(30.648740)

    def test_missing_columns_are_reported_and_abort(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = self._write(tmpdir, 'Time,Alt\n1,2\n')
            service = self._service(tmpdir, csv_path)
            messages = []
            service.sig_msg.connect(messages.append)

            assert service._parse_csv_flight_log(csv_path, 'v.mp4') is None
            assert any('missing required columns' in m for m in messages)

    def test_a_zero_coordinate_is_a_real_position(self):
        """Regression: the CSV branch tested coordinates for truth, so a
        flight on the prime meridian or the equator lost its geotag. The SRT
        branch in the same method already used ``is not None``."""
        from datetime import datetime, timezone

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = self._write(tmpdir, (
                'Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n'
                '2026-07-25T14:38:26Z,0.0,0.0,679.2\n'
            ))
            service = self._service(tmpdir, csv_path)
            start = datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)

            with patch('core.services.VideoParserService.get_video_creation_time',
                       return_value=start):
                _video_start, entries = service._parse_csv_flight_log(
                    csv_path, 'v.mp4')

            entry = entries[0]
            assert entry['latitude'] == 0.0 and entry['longitude'] == 0.0
            # The guard the frame loop applies must accept this row.
            assert (entry['latitude'] is not None
                    and entry['longitude'] is not None)

    def test_unreadable_file_is_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = self._service(tmpdir, 'nope.csv')
            messages = []
            service.sig_msg.connect(messages.append)

            assert service._parse_csv_flight_log(
                os.path.join(tmpdir, 'nope.csv'), 'v.mp4') is None
            assert any('Error' in m for m in messages)


# --- SRT telemetry parsing --------------------------------------------------
#
# Two DJI subtitle layouts are in the field. Older files give every field its
# own bracket; Mavic 3-era firmware packs rel_alt and abs_alt into one. Both
# must parse - the newer one is what silently stamped altitude 0 on every
# extracted frame.

LEGACY_PAYLOAD = (
    '<font size="28">[iso : 100] [shutter : 1/500] [latitude: 39.900000] '
    '[longitude: -105.100000] [altitude: 1650.500000] </font>'
)

MODERN_PAYLOAD = (
    '<font size="28">[iso: 200] [shutter: 1/241.19] [fnum: 4.3] [ev: 0] '
    '[color_md : default] [focal_len: 480.00] [dzoom_ratio: 1.18], '
    '[latitude: 39.483487] [longitude: 73.585195] '
    '[rel_alt: 561.745 abs_alt: 4563.571] '
    '[gb_yaw: 130.6 gb_pitch: -26.5 gb_roll: 0.0] </font>'
)


def _srt_entry(payload, index=1):
    """Wrap a telemetry payload in a complete SRT entry."""
    return (
        f'{index}\n'
        f'00:00:0{index - 1},000 --> 00:00:0{index},000\n'
        f'<font size="28">FrameCnt: {index}, DiffTime: 33ms\n'
        f'2026-08-15 12:09:26.002\n'
        f'{payload}\n'
    )


def parse(service, tmp_path, payload):
    """Run one payload through the real file parser."""
    srt = tmp_path / 'track.srt'
    srt.write_text(_srt_entry(payload))
    entries = service._parse_srt_file(str(srt))
    assert entries is not None and len(entries) == 1
    return entries[0]


def test_modern_srt_reads_absolute_altitude(video_parser_service, tmp_path):
    """abs_alt shares its bracket with rel_alt; both must be read."""
    entry = parse(video_parser_service, tmp_path, MODERN_PAYLOAD)

    assert entry['altitude'] == 4563.571
    assert entry['relative_altitude'] == 561.745
    assert entry['latitude'] == 39.483487
    assert entry['longitude'] == 73.585195


def test_legacy_srt_still_reads_altitude(video_parser_service, tmp_path):
    """The one-pair-per-bracket layout keeps working unchanged."""
    entry = parse(video_parser_service, tmp_path, LEGACY_PAYLOAD)

    assert entry['altitude'] == 1650.5
    assert entry['latitude'] == 39.9
    assert entry['longitude'] == -105.1
    # Nothing to relate it to in this layout.
    assert entry['relative_altitude'] is None


def test_misspelled_longitude_key_still_parses(video_parser_service, tmp_path):
    """Some files write 'longtitude'; that fallback predates this fix."""
    payload = '[latitude: 39.9] [longtitude: -105.1] [altitude: 1650.5]'

    entry = parse(video_parser_service, tmp_path, payload)

    assert entry['longitude'] == -105.1


def test_multi_pair_brackets_do_not_swallow_neighbours(video_parser_service, tmp_path):
    """A crowded bracket must not corrupt the keys parsed around it."""
    payload = ('[gb_yaw: 130.6 gb_pitch: -26.5 gb_roll: 0.0] [latitude: 1.5] '
               '[longitude: 2.5] [rel_alt: 10.0 abs_alt: 20.0]')

    entry = parse(video_parser_service, tmp_path, payload)

    assert (entry['latitude'], entry['longitude']) == (1.5, 2.5)
    assert entry['altitude'] == 20.0


def test_absolute_altitude_wins_when_a_file_carries_both(video_parser_service, tmp_path):
    """'abs_alt' is explicitly height above sea level; prefer it."""
    payload = '[latitude: 1.0] [longitude: 2.0] [altitude: 5.0] [rel_alt: 7.0 abs_alt: 900.0]'

    entry = parse(video_parser_service, tmp_path, payload)

    assert entry['altitude'] == 900.0


def test_missing_altitude_falls_back_to_zero(video_parser_service, tmp_path):
    """No height in the file: the frame is stamped 0, as before."""
    entry = parse(video_parser_service, tmp_path, '[latitude: 1.0] [longitude: 2.0]')

    assert entry['altitude'] == 0.0


def test_unparseable_position_does_not_abandon_the_file(video_parser_service, tmp_path):
    """One junk value used to raise, losing GPS for the whole video."""
    entry = parse(video_parser_service, tmp_path, '[latitude: n/a] [longitude: 2.0] [altitude: 3.0]')

    assert entry['latitude'] is None
    assert entry['longitude'] == 2.0


# --- frame capture times ----------------------------------------------------
#
# Frames carry no date of their own, so nothing downstream could order them:
# the GPS map traces its path by timestamp and auto-bearing sorts by it. Three
# sources, in priority order - the SRT's own wall clock, and otherwise the
# container's creation_time (which the CSV path already reads) plus the frame's
# offset into the video.

def test_srt_entries_carry_their_wall_clock(video_parser_service, tmp_path):
    entry = parse(video_parser_service, tmp_path, MODERN_PAYLOAD)

    assert entry['timestamp'] == datetime(2026, 8, 15, 12, 9, 26, 2000)


@pytest.mark.parametrize('line, expected', [
    ('2026-08-15 12:09:26.002', datetime(2026, 8, 15, 12, 9, 26, 2000)),
    ('2026-08-15 12:09:26', datetime(2026, 8, 15, 12, 9, 26)),
    ('2023-05-01 12:00:00,000,000', datetime(2023, 5, 1, 12, 0, 0)),
    ('  2026-08-15 12:09:26  ', datetime(2026, 8, 15, 12, 9, 26)),
])
def test_srt_timestamp_formats(line, expected):
    assert VideoParserService._parse_srt_timestamp(line) == expected


@pytest.mark.parametrize('line', ['FrameCnt: 1, DiffTime: 33ms', '', None])
def test_srt_timestamp_rejects_non_dates(line):
    assert VideoParserService._parse_srt_timestamp(line) is None


def _drive_process_video(service, *, srt_text=None, creation_time=None, seconds=4.0):
    """Run process_video against a stubbed 30 fps capture.

    Returns:
        (patched MetaDataHelper mock, emitted messages)
    """
    import cv2

    fps = 30.0
    position = {'ms': 0.0}
    cap = MagicMock()
    cap.isOpened.return_value = True
    cap.read.return_value = (True, 'frame')

    def _get(prop):
        if prop == cv2.CAP_PROP_FPS:
            return fps
        if prop == cv2.CAP_PROP_FRAME_COUNT:
            return int(seconds * fps)
        if prop == cv2.CAP_PROP_POS_MSEC:
            return position['ms']
        return 0

    def _set(prop, value):
        if prop == cv2.CAP_PROP_POS_FRAMES:
            position['ms'] = (value / fps) * 1000.0

    cap.get.side_effect = _get
    cap.set.side_effect = _set

    if srt_text is not None:
        with open(service.metadata_path, 'w') as handle:
            handle.write(srt_text)
    else:
        service.metadata_path = ''

    messages = []
    service.sig_msg.connect(messages.append)

    with patch('cv2.VideoCapture', return_value=cap), \
         patch('cv2.imwrite'), \
         patch('core.services.VideoParserService.detect_thumbnail_track', return_value=False), \
         patch('core.services.VideoParserService.get_video_creation_time', return_value=creation_time), \
         patch('core.services.VideoParserService.MetaDataHelper') as helper:
        service.process_video()

    return helper, messages


def test_frames_are_stamped_with_the_srt_wall_clock(video_parser_service):
    """The SRT knows exactly when each frame was taken; nothing to reconstruct."""
    entry = _srt_entry(MODERN_PAYLOAD).replace(
        '00:00:00,000 --> 00:00:01,000', '00:00:00,000 --> 00:00:10,000')

    helper, messages = _drive_process_video(video_parser_service, srt_text=entry)
    add_gps, add_time = helper.add_gps_data, helper.add_capture_time

    assert add_gps.call_args_list, "GPS-bearing frames should go through add_gps_data"
    for call in add_gps.call_args_list:
        assert call.kwargs['timestamp'] == datetime(2026, 8, 15, 12, 9, 26, 2000)
    add_time.assert_not_called()
    assert any('from the SRT' in m for m in messages)


def test_frames_without_a_log_are_stamped_from_the_video_start(video_parser_service):
    """No flight log at all: the container's creation_time plus the offset."""
    start = datetime(2026, 8, 15, 3, 17, 4, tzinfo=timezone.utc)

    helper, messages = _drive_process_video(
        video_parser_service, creation_time=start, seconds=4.0)
    add_gps, add_time = helper.add_gps_data, helper.add_capture_time

    stamped = [call.args[1] for call in add_time.call_args_list]
    assert stamped, "frames with no GPS still need a capture time"
    # interval is 1.0 s in the fixture, so each frame advances one second.
    assert stamped[0] == start
    assert stamped[1] == start + timedelta(seconds=1)
    add_gps.assert_not_called()
    assert any('video start' in m for m in messages)


def test_no_clock_anywhere_leaves_frames_unstamped_and_says_so(video_parser_service):
    """ffprobe missing or creation_time absent: extract anyway, but be explicit."""
    helper, messages = _drive_process_video(video_parser_service, creation_time=None)
    add_gps, add_time = helper.add_gps_data, helper.add_capture_time

    add_time.assert_not_called()
    add_gps.assert_not_called()
    assert any('no timestamp' in m for m in messages)


# --- height above takeoff ---------------------------------------------------
#
# EXIF has no relative-altitude tag, so the SRT's rel_alt had nowhere to live
# and every AGL-based calculation downstream fell back or failed. ADIAT reads
# AGL from drone-dji:RelativeAltitude regardless of airframe.

def test_srt_frames_record_height_above_takeoff_as_xmp(video_parser_service):
    entry = _srt_entry(MODERN_PAYLOAD).replace(
        '00:00:00,000 --> 00:00:01,000', '00:00:00,000 --> 00:00:10,000')

    helper, _messages = _drive_process_video(video_parser_service, srt_text=entry)

    assert helper.add_xmp_fields.called
    _path, fields = helper.add_xmp_fields.call_args.args
    written = {tag: value for _ns, tag, value in fields}
    assert written['RelativeAltitude'] == '+561.7450'
    assert written['AbsoluteAltitude'] == '+4563.5710'
    # Readers will not look up XMP attributes without a make on the image.
    assert helper.add_gps_data.call_args.kwargs['make'] == 'DJI'


def test_frames_without_a_reported_agl_claim_no_make(video_parser_service):
    """The legacy layout has no rel_alt; nothing is synthesized for it."""
    entry = _srt_entry(LEGACY_PAYLOAD).replace(
        '00:00:00,000 --> 00:00:01,000', '00:00:00,000 --> 00:00:10,000')

    helper, _messages = _drive_process_video(video_parser_service, srt_text=entry)

    helper.add_xmp_fields.assert_not_called()
    assert helper.add_gps_data.call_args.kwargs['make'] is None


# --- which altitude goes in which tag --------------------------------------
#
# drone-dji:RelativeAltitude carries either a height above the takeoff point
# or a genuine terrain-referenced AGL, and AltitudeType is what records which.
# AbsoluteAltitude and EXIF GPSAltitude are sea-level tags, and used to be
# filled from the relative reading whenever the aircraft reported no abs_alt -
# a frame then claimed to have been shot 15 m above sea level.

REL_ONLY_PAYLOAD = (
    '<font size="28">[latitude: 39.483487] [longitude: 73.585195] '
    '[rel_alt: 15.500] </font>'
)


def test_no_absolute_altitude_means_no_absolute_tags(video_parser_service):
    """The height above takeoff still lands; nothing is invented for MSL."""
    entry = _srt_entry(REL_ONLY_PAYLOAD).replace(
        '00:00:00,000 --> 00:00:01,000', '00:00:00,000 --> 00:00:10,000')

    helper, _messages = _drive_process_video(video_parser_service, srt_text=entry)

    _path, fields = helper.add_xmp_fields.call_args.args
    written = {tag: value for _ns, tag, value in fields}
    assert written['RelativeAltitude'] == '+15.5000'
    assert 'AbsoluteAltitude' not in written
    # EXIF GPSAltitude is absolute too, so the position is written alone.
    assert helper.add_gps_data.call_args.args[3] is None
    # The frame still carries drone-dji fields, so it still needs a make.
    assert helper.add_gps_data.call_args.kwargs['make'] == 'DJI'


def test_an_unmarked_relative_altitude_stays_takeoff_relative():
    """No AltitudeType tag means ATO - what every DJI frame is."""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = VideoParserService(1, 'v.mp4', '', tmpdir, 1.0)
        with patch('core.services.VideoParserService.MetaDataHelper') as helper:
            service._stamp_relative_altitude('f.jpg', 15.5, 4563.5)
        _path, fields = helper.add_xmp_fields.call_args.args
        written = {tag: value for _ns, tag, value in fields}
        assert set(written) == {'RelativeAltitude', 'AbsoluteAltitude'}
        assert written['AbsoluteAltitude'] == '+4563.5000'


def test_a_terrain_referenced_height_is_marked_as_terrain():
    """A log that resolved its own AGL puts a different quantity in the same
    tag. Unmarked, ImageService.get_altitude_reference reads it back as ATO
    and the operator is shown the wrong plane."""
    from helpers.MetaDataHelper import XMP_ALTITUDE_TYPE_TERRAIN

    with tempfile.TemporaryDirectory() as tmpdir:
        service = VideoParserService(1, 'v.mp4', '', tmpdir, 1.0)
        with patch('core.services.VideoParserService.MetaDataHelper') as helper:
            service._stamp_relative_altitude(
                'f.jpg', 95.0, None, terrain_referenced=True)
        _path, fields = helper.add_xmp_fields.call_args.args
        written = {tag: value for _ns, tag, value in fields}
        assert written['AltitudeType'] == XMP_ALTITUDE_TYPE_TERRAIN
        assert written['RelativeAltitude'] == '+95.0000'
        assert 'AbsoluteAltitude' not in written


def test_a_terrain_agl_outranks_ato_for_the_stamped_height():
    """Clearance and image scale depend on height above the ground, so where
    the source resolved both, the terrain figure is the one stamped."""
    assert VideoParserService._height_above_ground(120.0, 95.0) == (95.0, True)
    assert VideoParserService._height_above_ground(120.0, None) == (120.0, False)
    assert VideoParserService._height_above_ground(None, None) == (None, False)


def test_a_failed_xmp_write_does_not_lose_the_frame(video_parser_service):
    """A frame with no XMP is still a usable frame."""
    video_parser_service.logger = MagicMock()

    with patch('core.services.VideoParserService.MetaDataHelper.add_xmp_fields',
               side_effect=OSError('locked')):
        video_parser_service._stamp_relative_altitude('frame.jpg', 100.0, 900.0)

    video_parser_service.logger.warning.assert_called_once()


def test_no_reported_agl_writes_nothing(video_parser_service):
    """Nothing to record is not a failure path."""
    with patch('core.services.VideoParserService.MetaDataHelper.add_xmp_fields') as write:
        video_parser_service._stamp_relative_altitude('frame.jpg', None, 900.0)

    write.assert_not_called()
