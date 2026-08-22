"""
Tests for the VideoParserCLI command-line interface.

Covers interval parsing, the input validation the service cannot report on
itself, what gets handed to VideoParserService, and the exit codes.
"""

import argparse
import signal

import pytest
from unittest.mock import patch

from core.services.cli.VideoParserCLI import (
    _build_parser, _interval, _validate, run_video_parser_cli,
    DEFAULT_INTERVAL, MIN_INTERVAL
)


class _FakeSignal:
    """Minimal stand-in for a Qt signal: connect, then emit to the slots."""

    def __init__(self):
        self._slots = []

    def connect(self, slot):
        self._slots.append(slot)

    def emit(self, *args):
        for slot in self._slots:
            slot(*args)


class _FakeService:
    """Stand-in for VideoParserService that replays a finished run."""

    instances = []
    image_count = 3
    cancel_on_run = False

    def __init__(self, id, video, metadata_path, output, interval):
        self.init_args = (id, video, metadata_path, output, interval)
        self.cancelled = False
        self.sig_msg = _FakeSignal()
        self.sig_done = _FakeSignal()
        _FakeService.instances.append(self)

    def process_video(self):
        self.sig_msg.emit("Capturing images")
        if _FakeService.cancel_on_run:
            self.process_cancel()
        self.sig_done.emit(1, _FakeService.image_count)

    def process_cancel(self):
        self.cancelled = True


@pytest.fixture
def fake_service():
    """Patch the CLI's VideoParserService with the fake and reset its state."""
    _FakeService.instances = []
    _FakeService.image_count = 3
    _FakeService.cancel_on_run = False
    with patch('core.services.cli.VideoParserCLI.VideoParserService', _FakeService):
        yield _FakeService


@pytest.fixture
def video_file(tmp_path):
    """A path that exists, so validation gets past the video check."""
    path = tmp_path / 'flight.mp4'
    path.write_bytes(b'not really a video')
    return path


# --- interval parsing -------------------------------------------------------

def test_interval_accepts_fractions():
    """Sub-second intervals are valid; the dialog allows them too."""
    assert _interval('2.5') == 2.5
    assert _interval(str(MIN_INTERVAL)) == MIN_INTERVAL


def test_interval_rejects_non_numbers():
    with pytest.raises(argparse.ArgumentTypeError):
        _interval('every-so-often')


def test_interval_rejects_values_below_the_minimum():
    """Below the dialog's floor the run would try to capture every frame."""
    with pytest.raises(argparse.ArgumentTypeError):
        _interval('0')
    with pytest.raises(argparse.ArgumentTypeError):
        _interval('0.05')


def test_parser_defaults_match_the_dialog():
    """A CLI run with no --interval captures the same frames as the GUI."""
    args = _build_parser().parse_args(['--video', 'v.mp4', '--output', 'out'])
    assert args.interval == DEFAULT_INTERVAL
    assert args.metadata is None


# --- validation -------------------------------------------------------------

def test_validate_reports_a_missing_video(tmp_path):
    args = _build_parser().parse_args([
        '--video', str(tmp_path / 'nope.mp4'), '--output', str(tmp_path / 'out')
    ])
    assert 'video file not found' in _validate(args)


def test_validate_reports_a_missing_metadata_file(tmp_path, video_file):
    args = _build_parser().parse_args([
        '--video', str(video_file), '--output', str(tmp_path / 'out'),
        '--metadata', str(tmp_path / 'nope.srt')
    ])
    assert 'metadata file not found' in _validate(args)


def test_validate_rejects_an_unsupported_metadata_extension(tmp_path, video_file):
    """The service treats an unknown extension as 'no metadata supplied'.

    Left to run, a mistyped log finishes successfully with images that have no
    GPS - the failure only shows up later, in the analysis.
    """
    log = tmp_path / 'flightlog.txt'
    log.write_text('lat,lon')
    args = _build_parser().parse_args([
        '--video', str(video_file), '--output', str(tmp_path / 'out'),
        '--metadata', str(log)
    ])
    assert 'DJI .srt or a .csv flight log' in _validate(args)


@pytest.mark.parametrize('name', ['track.srt', 'flight.csv', 'TRACK.SRT'])
def test_validate_accepts_supported_metadata(tmp_path, video_file, name):
    log = tmp_path / name
    log.write_text('data')
    args = _build_parser().parse_args([
        '--video', str(video_file), '--output', str(tmp_path / 'out'),
        '--metadata', str(log)
    ])
    assert _validate(args) is None


# --- run_video_parser_cli ---------------------------------------------------

def test_run_hands_absolute_paths_and_interval_to_the_service(tmp_path, video_file, fake_service):
    """Relative paths are resolved before the service (which never chdirs) sees them."""
    log = tmp_path / 'track.srt'
    log.write_text('data')
    output = tmp_path / 'frames'

    code = run_video_parser_cli([
        '--video', str(video_file), '--output', str(output),
        '--metadata', str(log), '--interval', '2.5'
    ])

    assert code == 0
    _id, video, metadata, out, interval = fake_service.instances[0].init_args
    assert video == str(video_file.resolve())
    assert metadata == str(log.resolve())
    assert out == str(output.resolve())
    assert interval == 2.5


def test_run_without_metadata_passes_an_empty_path(tmp_path, video_file, fake_service):
    """VideoParserService reads '' as 'no metadata provided'."""
    run_video_parser_cli(['--video', str(video_file), '--output', str(tmp_path / 'frames')])

    assert fake_service.instances[0].init_args[2] == ''


def test_run_succeeds_when_images_were_written(tmp_path, video_file, fake_service, capsys):
    code = run_video_parser_cli(['--video', str(video_file), '--output', str(tmp_path / 'frames')])

    assert code == 0
    output = capsys.readouterr().out
    # Service progress is relayed, not swallowed.
    assert 'Capturing images' in output
    assert '3 images written' in output


def test_run_fails_when_no_images_were_written(tmp_path, video_file, fake_service):
    """An unreadable video reports zero captures; the exit code must say so."""
    fake_service.image_count = 0

    code = run_video_parser_cli(['--video', str(video_file), '--output', str(tmp_path / 'frames')])

    assert code == 1


def test_run_fails_when_cancelled_partway(tmp_path, video_file, fake_service, capsys):
    """A partial extraction is not a successful run, even with images on disk."""
    fake_service.cancel_on_run = True

    code = run_video_parser_cli(['--video', str(video_file), '--output', str(tmp_path / 'frames')])

    assert code == 1
    assert 'Cancelled' in capsys.readouterr().out


def test_run_rejects_a_missing_video_before_starting(tmp_path, fake_service, capsys):
    code = run_video_parser_cli([
        '--video', str(tmp_path / 'nope.mp4'), '--output', str(tmp_path / 'frames')
    ])

    assert code == 1
    assert fake_service.instances == []
    assert 'video file not found' in capsys.readouterr().err


def test_run_restores_the_previous_interrupt_handler(tmp_path, video_file, fake_service):
    """Ctrl+C is only redirected for the duration of the extraction."""
    before = signal.getsignal(signal.SIGINT)

    run_video_parser_cli(['--video', str(video_file), '--output', str(tmp_path / 'frames')])

    assert signal.getsignal(signal.SIGINT) is before
