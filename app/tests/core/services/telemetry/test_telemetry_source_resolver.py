"""Tests for telemetry source resolution and embedded extraction.

Precedence under test: an explicitly chosen file (``.SRT`` or ``.csv``)
beats a sidecar, which beats a track embedded in the MP4. ffmpeg is mocked
throughout; the real-video check lives in ``test_dji_video_telemetry.py``
and skips when the sample file is absent.
"""

import os
import tempfile
from datetime import datetime, timezone

import pytest
from unittest.mock import MagicMock, patch

from core.services.telemetry.TelemetrySourceResolver import (
    SOURCE_EMBEDDED,
    SOURCE_EXPLICIT_FILE,
    SOURCE_NONE,
    SOURCE_SIDECAR,
    find_sidecar_srt,
    load_telemetry_for_video,
    read_srt_track,
)

SRT_TEXT = """\
1
00:00:00,000 --> 00:00:00,033
FrameCnt: 0 2026-07-25 14:38:26.477
[latitude: 30.648730] [longitude: -97.675867] [rel_alt: 14.885 abs_alt: 207.027]

2
00:00:00,033 --> 00:00:00,066
FrameCnt: 1 2026-07-25 14:38:26.511
[latitude: 30.648740] [longitude: -97.675877] [rel_alt: 15.885 abs_alt: 208.027]
"""

RESOLVER = "core.services.telemetry.TelemetrySourceResolver"


@pytest.fixture
def workspace():
    with tempfile.TemporaryDirectory() as tmp:
        video = os.path.join(tmp, "DJI_0001.MP4")
        with open(video, "wb") as handle:
            handle.write(b"not really a video")
        yield tmp, video


def _write(path, text=SRT_TEXT):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


class TestSidecarDiscovery:
    def test_finds_uppercase_sidecar(self, workspace):
        tmp, video = workspace
        srt = _write(os.path.join(tmp, "DJI_0001.SRT"))
        assert find_sidecar_srt(video) == srt

    def test_finds_lowercase_sidecar(self, workspace):
        tmp, video = workspace
        srt = _write(os.path.join(tmp, "DJI_0001.srt"))
        assert os.path.samefile(find_sidecar_srt(video), srt)

    def test_absent_sidecar(self, workspace):
        _tmp, video = workspace
        assert find_sidecar_srt(video) is None

    def test_none_input(self):
        assert find_sidecar_srt(None) is None


class TestReadSrtTrack:
    def test_reads_a_valid_file(self, workspace):
        tmp, _video = workspace
        srt = _write(os.path.join(tmp, "t.srt"))
        track = read_srt_track(srt, source="test")
        assert len(track) == 2
        assert track.source == "test"

    def test_empty_file_yields_none(self, workspace):
        tmp, _video = workspace
        srt = _write(os.path.join(tmp, "empty.srt"), "")
        assert read_srt_track(srt, source="test") is None

    def test_missing_file_yields_none(self, workspace):
        tmp, _video = workspace
        assert read_srt_track(os.path.join(tmp, "nope.srt"), source="test") is None

    def test_tolerates_a_bom(self, workspace):
        tmp, _video = workspace
        srt = os.path.join(tmp, "bom.srt")
        with open(srt, "w", encoding="utf-8-sig") as handle:
            handle.write(SRT_TEXT)
        assert len(read_srt_track(srt, source="test")) == 2


class TestDatumLookupIsLazy:
    """Identifying the aircraft costs an ffprobe spawn (~130 ms measured), and
    only a legacy single-``altitude`` track can use the answer. A track that
    states both datums must not pay for it — that was 5/6 of the load time on
    a real 2985-cue Mavic 3T sidecar.
    """

    MODERN = (
        "1\n00:00:00,000 --> 00:00:00,033\n"
        "FrameCnt: 0 2026-07-25 14:38:26.477\n"
        "[latitude: 30.6] [longitude: -97.6] [rel_alt: 14.885 abs_alt: 207.027]\n"
    )
    LEGACY = (
        "1\n00:00:00,000 --> 00:00:00,033\n"
        '<font size="36">SrtCnt : 1, DiffTime : 33ms\n2024-03-22 16:51:55,597,864\n'
        "[latitude: 30.6] [longitude: -97.9] [altitude: 9.8] </font>\n"
    )

    def test_a_modern_track_never_calls_the_provider(self, workspace):
        tmp, _video = workspace
        srt = _write(os.path.join(tmp, "modern.srt"), self.MODERN)
        calls = []
        read_srt_track(srt, source="test",
                       datum_provider=lambda: calls.append(1))
        assert calls == []

    def test_a_legacy_track_does_call_it(self, workspace):
        tmp, _video = workspace
        srt = _write(os.path.join(tmp, "legacy.srt"), self.LEGACY)
        calls = []

        def provider():
            calls.append(1)
            return "msl"

        track = read_srt_track(srt, source="test", datum_provider=provider)
        assert calls == [1]
        # And the recorded datum was actually applied.
        assert track.points[0].altitude_msl_m == pytest.approx(9.8)

    def test_a_failing_provider_falls_back_to_inference(self, workspace):
        tmp, _video = workspace
        srt = _write(os.path.join(tmp, "legacy.srt"), self.LEGACY)

        def provider():
            raise OSError("ffprobe exploded")

        track = read_srt_track(srt, source="test", datum_provider=provider)
        # Inference ran: 9.8 m is below the ceiling, so relative.
        assert track.points[0].altitude_ato_m == pytest.approx(9.8)

    def test_an_explicit_datum_short_circuits_the_provider(self, workspace):
        tmp, _video = workspace
        srt = _write(os.path.join(tmp, "legacy.srt"), self.LEGACY)
        calls = []
        read_srt_track(srt, source="test", altitude_datum="msl",
                       datum_provider=lambda: calls.append(1))
        assert calls == []


class TestPrecedence:
    def test_explicit_file_wins_over_embedded(self, workspace):
        tmp, video = workspace
        chosen = _write(os.path.join(tmp, "chosen.srt"))

        with patch(f"{RESOLVER}.find_embedded_telemetry_stream") as find_embedded:
            resolution = load_telemetry_for_video(video, chosen)

        assert resolution.source == SOURCE_EXPLICIT_FILE
        assert resolution.found
        # The embedded route must not even be probed.
        find_embedded.assert_not_called()

    def test_sidecar_used_when_no_explicit_file(self, workspace):
        tmp, video = workspace
        _write(os.path.join(tmp, "DJI_0001.SRT"))

        with patch(f"{RESOLVER}.find_embedded_telemetry_stream") as find_embedded:
            resolution = load_telemetry_for_video(video, None)

        assert resolution.source == SOURCE_SIDECAR
        assert len(resolution.track) == 2
        find_embedded.assert_not_called()

    def test_embedded_used_when_nothing_else_exists(self, workspace):
        tmp, video = workspace
        extracted = _write(os.path.join(tmp, "extracted.srt"))

        with patch(f"{RESOLVER}.find_embedded_telemetry_stream", return_value=3), \
                patch(f"{RESOLVER}.extract_embedded_subtitles", return_value=extracted):
            resolution = load_telemetry_for_video(video, None)

        assert resolution.source == SOURCE_EMBEDDED
        assert len(resolution.track) == 2
        assert "embedded" in resolution.detail

    def test_extracted_temp_file_is_deleted(self, workspace):
        """The parsed track is what we keep; the temp file must not linger."""
        tmp, video = workspace
        extracted = _write(os.path.join(tmp, "extracted.srt"))

        with patch(f"{RESOLVER}.find_embedded_telemetry_stream", return_value=3), \
                patch(f"{RESOLVER}.extract_embedded_subtitles", return_value=extracted):
            load_telemetry_for_video(video, None)

        assert not os.path.exists(extracted)

    def test_no_telemetry_anywhere(self, workspace):
        _tmp, video = workspace
        with patch(f"{RESOLVER}.find_embedded_telemetry_stream", return_value=None):
            resolution = load_telemetry_for_video(video, None)
        assert resolution.source == SOURCE_NONE
        assert not resolution.found
        assert resolution.track is None

    def test_unparseable_explicit_file_is_reported(self, workspace):
        tmp, video = workspace
        bad = _write(os.path.join(tmp, "bad.srt"), "not an srt at all")
        resolution = load_telemetry_for_video(video, bad)
        assert resolution.source == SOURCE_EXPLICIT_FILE
        assert not resolution.found
        assert "no usable telemetry" in resolution.detail

    def test_extraction_failure_degrades_gracefully(self, workspace):
        _tmp, video = workspace
        with patch(f"{RESOLVER}.find_embedded_telemetry_stream", return_value=3), \
                patch(f"{RESOLVER}.extract_embedded_subtitles", return_value=None):
            resolution = load_telemetry_for_video(video, None)
        assert resolution.source == SOURCE_NONE

    def test_missing_explicit_file_is_reported(self, workspace):
        tmp, video = workspace
        resolution = load_telemetry_for_video(video, os.path.join(tmp, "gone.srt"))
        assert resolution.source == SOURCE_EXPLICIT_FILE
        assert not resolution.found
        assert "could not be found" in resolution.detail

    def test_unsupported_extension_is_reported(self, workspace):
        """A .txt is neither format; say so instead of falling back silently."""
        tmp, video = workspace
        other = _write(os.path.join(tmp, "notes.txt"))
        resolution = load_telemetry_for_video(video, other)
        assert resolution.source == SOURCE_EXPLICIT_FILE
        assert not resolution.found
        assert "not a supported metadata format" in resolution.detail

    def test_explicit_choice_suppresses_the_embedded_fallback(self, workspace):
        """Geotagging from a source the operator didn't pick would be worse
        than telling them their file failed."""
        tmp, video = workspace
        bad = _write(os.path.join(tmp, "bad.srt"), "not an srt at all")

        with patch(f"{RESOLVER}.find_embedded_telemetry_stream") as find_embedded:
            load_telemetry_for_video(video, bad)
        find_embedded.assert_not_called()


CSV_TEXT = """\
Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)
2026-07-25T14:38:26Z,30.648730,-97.675867,679.2
2026-07-25T14:38:27Z,30.648740,-97.675877,682.5
2026-07-25T14:38:28Z,30.648750,-97.675887,685.8
"""

VIDEO_START = datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)


def _timing(start, duration=120.0):
    """Stand in for the container's creation_time + duration."""
    return patch("helpers.VideoFileHelper.get_video_timing",
                 return_value=(start, duration))


class TestExplicitCsv:
    """A CSV flight log is a first-class secondary metadata file."""

    def _csv(self, tmp, text=CSV_TEXT, name="flight.csv"):
        return _write(os.path.join(tmp, name), text)

    def test_csv_resolves_to_a_track(self, workspace):
        tmp, video = workspace
        csv_path = self._csv(tmp)
        with _timing(VIDEO_START):
            resolution = load_telemetry_for_video(video, csv_path)

        assert resolution.source == SOURCE_EXPLICIT_FILE
        assert resolution.found
        assert len(resolution.track) == 3
        assert resolution.path == csv_path
        assert "flight log" in resolution.detail

    def test_times_are_relative_to_the_video(self, workspace):
        """CSV rows are absolute UTC; the track must be video-relative."""
        tmp, video = workspace
        csv_path = self._csv(tmp)
        with _timing(VIDEO_START):
            track = load_telemetry_for_video(video, csv_path).track

        assert [p.time_seconds for p in track.points] == [0.0, 1.0, 2.0]
        assert track.point_at(1.0).latitude == pytest.approx(30.648740)

    def test_feet_are_converted_to_metres(self, workspace):
        tmp, video = workspace
        csv_path = self._csv(tmp)
        with _timing(VIDEO_START):
            track = load_telemetry_for_video(video, csv_path).track

        assert track.points[0].altitude_msl_m == pytest.approx(679.2 * 0.3048)

    def test_csv_beats_an_embedded_track(self, workspace):
        tmp, video = workspace
        csv_path = self._csv(tmp)
        with patch("helpers.VideoFileHelper.get_video_creation_time",
                   return_value=VIDEO_START), \
                patch(f"{RESOLVER}.find_embedded_telemetry_stream") as find_embedded:
            load_telemetry_for_video(video, csv_path)
        find_embedded.assert_not_called()

    def test_missing_columns_are_named(self, workspace):
        tmp, video = workspace
        csv_path = self._csv(tmp, "Time,Altitude\n1,2\n")
        resolution = load_telemetry_for_video(video, csv_path)

        assert resolution.source == SOURCE_EXPLICIT_FILE
        assert not resolution.found
        assert "Latitude" in resolution.detail
        assert "Longitude" in resolution.detail

    def test_video_without_creation_time_is_reported(self, workspace):
        """Aligning absolute timestamps needs the video's start time; there
        is no defensible guess, so this must fail loudly."""
        tmp, video = workspace
        csv_path = self._csv(tmp)
        with _timing(None):
            resolution = load_telemetry_for_video(video, csv_path)

        assert resolution.source == SOURCE_EXPLICIT_FILE
        assert not resolution.found
        assert "creation_time" in resolution.detail

    def test_log_from_a_different_flight_is_reported(self, workspace):
        tmp, video = workspace
        csv_path = self._csv(tmp)
        with _timing(datetime(2020, 1, 1, tzinfo=timezone.utc)):
            resolution = load_telemetry_for_video(video, csv_path)

        # Every row predates the video, so nothing lands in its window.
        assert not resolution.found
        assert "recording window" in resolution.detail


class TestEmbeddedHelpers:
    """``VideoFileHelper`` stream discovery + demux, with ffmpeg mocked."""

    def test_finds_a_mov_text_stream(self):
        from helpers.VideoFileHelper import find_embedded_telemetry_stream

        probe = MagicMock(returncode=0, stdout=(
            '{"streams": ['
            '{"index": 0, "codec_type": "video", "codec_name": "hevc"},'
            '{"index": 3, "codec_type": "subtitle", "codec_name": "mov_text"}'
            ']}'
        ))
        with patch("helpers.VideoFileHelper._find_ffprobe", return_value="ffprobe"), \
                patch("helpers.VideoFileHelper.subprocess.run", return_value=probe):
            assert find_embedded_telemetry_stream("v.mp4") == 3

    def test_ignores_non_telemetry_subtitle_codecs(self):
        from helpers.VideoFileHelper import find_embedded_telemetry_stream

        probe = MagicMock(returncode=0, stdout=(
            '{"streams": [{"index": 2, "codec_type": "subtitle", '
            '"codec_name": "dvd_subtitle"}]}'
        ))
        with patch("helpers.VideoFileHelper._find_ffprobe", return_value="ffprobe"), \
                patch("helpers.VideoFileHelper.subprocess.run", return_value=probe):
            assert find_embedded_telemetry_stream("v.mp4") is None

    def test_no_subtitle_stream(self):
        from helpers.VideoFileHelper import find_embedded_telemetry_stream

        probe = MagicMock(returncode=0, stdout='{"streams": [{"index": 0, '
                                               '"codec_type": "video"}]}')
        with patch("helpers.VideoFileHelper._find_ffprobe", return_value="ffprobe"), \
                patch("helpers.VideoFileHelper.subprocess.run", return_value=probe):
            assert find_embedded_telemetry_stream("v.mp4") is None

    def test_missing_ffprobe_is_not_an_error(self):
        from helpers.VideoFileHelper import find_embedded_telemetry_stream

        with patch("helpers.VideoFileHelper._find_ffprobe", return_value=None):
            assert find_embedded_telemetry_stream("v.mp4") is None

    def test_extraction_returns_a_temp_file(self, workspace):
        from helpers.VideoFileHelper import extract_embedded_subtitles

        tmp, video = workspace

        def fake_run(cmd, **_kwargs):
            # Write to whatever output path ffmpeg was handed.
            _write(cmd[-1])
            return MagicMock(returncode=0, stderr="")

        with patch("helpers.VideoFileHelper._find_ffmpeg", return_value="ffmpeg"), \
                patch("helpers.VideoFileHelper.subprocess.run", side_effect=fake_run):
            out = extract_embedded_subtitles(video, stream_index=3)

        assert out is not None
        assert os.path.getsize(out) > 0
        os.unlink(out)

    def test_empty_extraction_is_treated_as_failure(self, workspace):
        """A track that demuxes to nothing must not look like success."""
        from helpers.VideoFileHelper import extract_embedded_subtitles

        _tmp, video = workspace
        with patch("helpers.VideoFileHelper._find_ffmpeg", return_value="ffmpeg"), \
                patch("helpers.VideoFileHelper.subprocess.run",
                      return_value=MagicMock(returncode=0, stderr="")):
            assert extract_embedded_subtitles(video, stream_index=3) is None

    def test_ffmpeg_failure_cleans_up(self, workspace):
        from helpers.VideoFileHelper import extract_embedded_subtitles

        _tmp, video = workspace
        with patch("helpers.VideoFileHelper._find_ffmpeg", return_value="ffmpeg"), \
                patch("helpers.VideoFileHelper.subprocess.run",
                      return_value=MagicMock(returncode=1, stderr="boom")):
            assert extract_embedded_subtitles(video, stream_index=3) is None
