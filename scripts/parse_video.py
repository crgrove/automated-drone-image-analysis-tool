"""Extract still images from a drone video, without opening ADIAT.

Runs the same VideoParserService the Video Parser dialog uses: a frame every N
seconds, each one stamped with GPS from the flight log when one is supplied
(DJI .srt subtitles or a Skydio .csv log). The images land in a folder ready to
be pointed at by an analysis run.

Usage:
    python scripts/parse_video.py --video <file> --output <dir>
    python scripts/parse_video.py --video <file> --output <dir> --metadata <file.srt>
    python scripts/parse_video.py --video <file> --output <dir> --interval 2.5
    python scripts/parse_video.py --help

This is a wrapper: it puts app/ on the import path and hands over to
core.services.cli.VideoParserCLI, which is also reachable as
"python app parse-video ..." (and "ADIAT.exe parse-video ..." in a packaged
build). Ctrl+C stops at the next frame and keeps what was already written.

Exit code 0 when images were written, 1 on a bad argument, a failed run, or a
run cancelled before the end of the video.
"""

import os
import sys


def main():
    """Bootstrap the app package and run the video parser CLI."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, '..', 'app')
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)

    from core.services.cli.VideoParserCLI import run_video_parser_cli
    return run_video_parser_cli(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
