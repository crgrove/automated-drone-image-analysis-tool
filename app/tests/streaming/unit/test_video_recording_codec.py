"""Recording encoder probe: no misleading console output, and the outcome is logged.

FFMPEG's H.264 path on Windows needs Cisco's OpenH264 DLL, which OpenCV
cannot ship. Probing it printed "Failed to load OpenH264 library ... Please
check environment" to the console - an operator read that as "configure
your system" - while the recording went on to succeed with another codec,
and nothing about any of it reached adiat_logs.txt.
"""

from unittest.mock import Mock

import cv2

from core.services.streaming import VideoRecordingService as vrs


def test_windows_never_probes_ffmpeg_h264(monkeypatch):
    monkeypatch.setattr(vrs.sys, "platform", "win32")
    candidates = [(api, fourcc) for api, fourcc, _ in vrs._codec_candidates()]
    assert candidates == [(cv2.CAP_MSMF, "H264"), (None, "mp4v")]


def test_other_platforms_keep_ffmpeg_h264(monkeypatch):
    monkeypatch.setattr(vrs.sys, "platform", "darwin")
    candidates = [(api, fourcc) for api, fourcc, _ in vrs._codec_candidates()]
    assert candidates == [(None, "avc1"), (None, "mp4v")]


def _recorder(tmp_path, monkeypatch, accepted_fourcc):
    vrs.reset_codec_cache()
    recorder = vrs.VideoRecorder(vrs.RecordingConfig(output_dir=str(tmp_path)))
    recorder.logger = Mock()
    recorder._resolution = (5472, 3078)
    recorder._current_output_path = str(tmp_path / "out.mp4")
    monkeypatch.setattr(
        recorder, "_open_writer",
        lambda api, fourcc: object() if fourcc == accepted_fourcc else None,
    )
    return recorder


def test_fallback_codec_is_logged_as_warning(tmp_path, monkeypatch):
    recorder = _recorder(tmp_path, monkeypatch, accepted_fourcc="mp4v")
    try:
        assert recorder._init_video_writer() is True
    finally:
        vrs.reset_codec_cache()

    recorder.logger.warning.assert_called_once()
    message = recorder.logger.warning.call_args[0][0]
    assert "MPEG-4 (mp4v)" in message
    assert "5472x3078" in message
    recorder.logger.error.assert_not_called()


def test_preferred_codec_is_not_a_warning(tmp_path, monkeypatch):
    first_fourcc = vrs._codec_candidates()[0][1]
    recorder = _recorder(tmp_path, monkeypatch, accepted_fourcc=first_fourcc)
    try:
        assert recorder._init_video_writer() is True
    finally:
        vrs.reset_codec_cache()

    recorder.logger.warning.assert_not_called()
    recorder.logger.info.assert_called_once()
