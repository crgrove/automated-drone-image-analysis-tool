"""End-to-end check against a real DJI video with embedded telemetry.

Guarded so the suite stays deterministic (CLAUDE.md §3.3): skips unless
both the sample file and ffmpeg are present. This is the test that pins
the behaviour the feature exists for — a ``.MP4`` copied off the card
with no sidecar still yields GPS.

Sample: ``DJI_20260725143826_0001_V.MP4`` — a 30 s Mavic clip whose
telemetry lives in a ``tx3g`` subtitle track at stream index 3.
"""

import os

import pytest

from core.services.telemetry import (
    SOURCE_EMBEDDED,
    load_telemetry_for_video,
)
from helpers.VideoFileHelper import (
    find_embedded_telemetry_stream,
    is_ffmpeg_available,
)

SAMPLE_VIDEO = r"C:\Users\charl\Pictures\4E\debug\DJI_20260725143826_0001_V.MP4"

pytestmark = [
    pytest.mark.skipif(
        not os.path.isfile(SAMPLE_VIDEO),
        reason="DJI sample video not present on this machine",
    ),
    pytest.mark.skipif(
        not is_ffmpeg_available(),
        reason="ffmpeg/ffprobe required to demux embedded telemetry",
    ),
]


@pytest.fixture(scope="module")
def resolution():
    return load_telemetry_for_video(SAMPLE_VIDEO)


def test_embedded_stream_is_discovered():
    assert find_embedded_telemetry_stream(SAMPLE_VIDEO) is not None


def test_resolves_from_the_embedded_track(resolution):
    """No sidecar exists for this file — it must come from the MP4."""
    assert resolution.found
    assert resolution.source == SOURCE_EMBEDDED


def test_every_cue_parses(resolution):
    """The old parser produced 0 samples for this layout."""
    assert len(resolution.track) == 890
    assert all(p.latitude is not None for p in resolution.track.points)


def test_first_fix_matches_the_file(resolution):
    first = resolution.track.points[0]
    assert first.latitude == pytest.approx(30.648730, abs=1e-6)
    assert first.longitude == pytest.approx(-97.675867, abs=1e-6)


def test_both_altitudes_are_recovered(resolution):
    """``[rel_alt: X abs_alt: Y]`` used to collapse to altitude 0."""
    first = resolution.track.points[0]
    assert first.altitude_msl_m == pytest.approx(207.027, abs=1e-3)
    assert first.altitude_ato_m == pytest.approx(14.885, abs=1e-3)


def test_track_spans_the_clip(resolution):
    assert resolution.track.duration_seconds == pytest.approx(29.66, abs=0.1)


def test_sampling_by_playback_position(resolution):
    env = resolution.track.sample_at(15.0)
    assert env is not None
    assert env["aircraft_latitude"] == pytest.approx(30.6487, abs=1e-3)
    assert env["aircraft_altitude_agl_m"] is not None


def test_sampling_beyond_the_end_returns_nothing(resolution):
    assert resolution.track.sample_at(600.0) is None


def test_path_grows_with_playback(resolution):
    early = resolution.track.path_until(5.0)
    later = resolution.track.path_until(20.0)
    assert 0 < len(early) < len(later) <= len(resolution.track)


# ----------------------------------------------------------------------
# Capture-info detection against the same real file
# ----------------------------------------------------------------------


def test_detects_the_aircraft_from_container_tags():
    """The MP4's ``encoder`` tag names the airframe."""
    from core.services.telemetry.VideoCaptureInfoService import detect_capture_info

    info = detect_capture_info(SAMPLE_VIDEO)
    assert info.has_device
    assert info.make == "DJI"
    assert info.model == "Matrice 4E"


def test_detects_the_flight_altitude():
    """Median AGL across the clip, from the embedded telemetry."""
    from core.services.telemetry.VideoCaptureInfoService import detect_capture_info

    info = detect_capture_info(SAMPLE_VIDEO)
    assert info.has_altitude
    # The aircraft hovers at ~14.9 m for this 30 s clip.
    assert info.altitude_ato_m == pytest.approx(14.9, abs=0.2)
    assert info.altitude_samples == 890
