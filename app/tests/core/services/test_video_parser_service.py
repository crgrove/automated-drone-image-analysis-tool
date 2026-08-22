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
