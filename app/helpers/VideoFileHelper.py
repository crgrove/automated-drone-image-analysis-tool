"""
VideoFileHelper.py - Utilities for handling video files with non-standard stream layouts.

Detects and works around MP4 files that embed a thumbnail/cover image as the
first video stream (e.g. Skydio X10), which causes OpenCV to grab the wrong track.
Also provides utilities for extracting metadata from video containers.
"""

import os
import platform
import shutil
import subprocess
import tempfile
import json
import cv2
from datetime import datetime, timezone


def get_video_creation_time(video_path, logger=None):
    """Extract creation_time from MP4 container via ffprobe.

    Args:
        video_path: Path to the video file.
        logger: Optional logger for error reporting.

    Returns:
        A timezone-aware UTC datetime, or None if extraction fails.
    """
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format_tags=creation_time',
                '-of', 'json', video_path
            ],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            if logger:
                logger.error(f"ffprobe failed: {result.stderr}")
            return None

        data = json.loads(result.stdout)
        creation_time_str = data.get('format', {}).get('tags', {}).get('creation_time')
        if not creation_time_str:
            return None

        # Parse ISO 8601 UTC timestamp (e.g. "2024-02-24T19:09:57.000000Z")
        creation_time_str = creation_time_str.replace('Z', '+00:00')
        return datetime.fromisoformat(creation_time_str).astimezone(timezone.utc)

    except Exception as e:
        if logger:
            logger.error(f"Error extracting video creation time: {e}")
        return None


# Common Homebrew binary directories that may not be in PATH when the app
# is launched outside a terminal (e.g. from Finder or a .app bundle).
_HOMEBREW_BIN_DIRS = [
    '/opt/homebrew/bin',      # Apple Silicon
    '/usr/local/bin',         # Intel Mac
]


def _which_with_fallback(name):
    """Find an executable by name, checking PATH then common Homebrew locations."""
    path = shutil.which(name)
    if path:
        return path
    if platform.system() == 'Darwin':
        for d in _HOMEBREW_BIN_DIRS:
            candidate = os.path.join(d, name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    return None


def _find_ffprobe():
    """Locate the ffprobe binary.

    Checks the system PATH first, then common Homebrew locations on macOS,
    then falls back to the imageio-ffmpeg bundled binary.

    Returns:
        Absolute path to ffprobe, or None if not found.
    """
    path = _which_with_fallback('ffprobe')
    if path:
        return path
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        # imageio-ffmpeg bundles ffprobe next to ffmpeg
        ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe')
        if os.path.isfile(ffprobe_path):
            return ffprobe_path
    except (ImportError, RuntimeError):
        pass
    return None


def _find_ffmpeg():
    """Locate the ffmpeg binary.

    Checks the system PATH first, then common Homebrew locations on macOS,
    then falls back to the imageio-ffmpeg bundled binary.

    Returns:
        Absolute path to ffmpeg, or None if not found.
    """
    path = _which_with_fallback('ffmpeg')
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError):
        pass
    return None


_FFMPEG_MISSING_MSG = (
    "ffmpeg not found. Install via 'brew install ffmpeg' on macOS "
    "or add imageio-ffmpeg to your environment."
)

_FFMPEG_USER_MSG = (
    "This video requires ffmpeg to process, but ffmpeg was not found. "
    "Please install ffmpeg (on macOS: 'brew install ffmpeg') and restart the application."
)


def is_ffmpeg_available():
    """Check whether both ffmpeg and ffprobe can be found.

    Returns:
        True if both binaries are available, False otherwise.
    """
    return _find_ffprobe() is not None and _find_ffmpeg() is not None


def detect_thumbnail_track(cap) -> bool:
    """Check if OpenCV grabbed a thumbnail track instead of the real video.

    Some drones (e.g. Skydio X10) embed an MJPEG cover image as stream 0.
    OpenCV picks it up, reports an absurd FPS (the MP4 timescale), and fails
    to read a second frame. This function detects that situation.

    After calling, the capture position is reset to frame 0.

    Args:
        cap: An opened cv2.VideoCapture instance.

    Returns:
        True if the capture appears to be on a thumbnail track.
    """
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps > 1000:
        return True
    # Also check if second frame fails immediately
    ret2, _ = cap.read()
    if not ret2:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return True
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    return False


def remux_to_main_track(source_path, logger=None):
    """Remux an MP4 to select the main video track, skipping thumbnail/cover tracks.

    Uses ffprobe to identify the real video stream (highest resolution, not
    marked as attached_pic), then ffmpeg to remux with -c copy (no re-encoding).

    Args:
        source_path: Path to the source MP4 file.
        logger: Optional logger instance with .info() and .error() methods.

    Returns:
        Path to a temporary remuxed MP4 file on success, None on failure.
        Caller is responsible for deleting the temp file when done.
    """
    try:
        ffprobe = _find_ffprobe()
        ffmpeg = _find_ffmpeg()
        if not ffprobe or not ffmpeg:
            if logger:
                logger.error(_FFMPEG_MISSING_MSG)
            return None

        # Use ffprobe to find the real video stream
        probe = subprocess.run(
            [ffprobe, '-v', 'error', '-show_streams', '-of', 'json', source_path],
            capture_output=True, text=True, timeout=10
        )
        if probe.returncode != 0:
            if logger:
                logger.error(f"ffprobe failed: {probe.stderr}")
            return None

        streams = json.loads(probe.stdout).get('streams', [])

        # Find best video stream: not attached_pic, highest resolution
        best_idx = None
        best_pixels = 0
        for s in streams:
            if s.get('codec_type') != 'video':
                continue
            if s.get('disposition', {}).get('attached_pic', 0):
                continue
            pixels = int(s.get('width', 0)) * int(s.get('height', 0))
            if pixels > best_pixels:
                best_pixels = pixels
                best_idx = s['index']

        if best_idx is None:
            if logger:
                logger.error("No suitable video stream found in file")
            return None

        # Remux to temp file (copy codec, no re-encoding)
        temp_fd, temp_path = tempfile.mkstemp(suffix='.mp4')
        os.close(temp_fd)
        result = subprocess.run(
            [ffmpeg, '-y', '-i', source_path, '-map', f'0:{best_idx}', '-c', 'copy', temp_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            if logger:
                logger.error(f"ffmpeg remux failed: {result.stderr}")
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            return None

        if logger:
            logger.info(f"Remuxed video to temp file: {temp_path}")
        return temp_path

    except Exception as e:
        if logger:
            logger.error(f"Remux error: {e}")
        return None
