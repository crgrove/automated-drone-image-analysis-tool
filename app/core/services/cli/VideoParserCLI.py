"""
VideoParserCLI.py -- command-line entry point for ADIAT video frame extraction.

Runs the same VideoParserService the Video Parser dialog uses, with no GUI:
point it at a video and an output folder and it writes a still every N seconds,
stamping each frame with GPS metadata when a DJI SRT or a Skydio CSV flight log
is supplied. It is invoked from __main__.py as:

    python app parse-video --video <file> --output <dir> [options]

or through the convenience wrapper:

    python scripts/parse_video.py --video <file> --output <dir> [options]
"""

import argparse
import os
import signal
import sys

from core.services.VideoParserService import VideoParserService


# Defaults mirror the Video Parser dialog's interval spin box, so a run started
# from the command line captures the same frames as one started from the GUI.
DEFAULT_INTERVAL = 5.0
MIN_INTERVAL = 0.1

# Metadata formats VideoParserService knows how to read.
METADATA_EXTENSIONS = ('.srt', '.csv')


def _interval(text):
    """argparse type for --interval.

    Args:
        text: The raw flag value.

    Returns:
        float: Seconds between captured frames.

    Raises:
        argparse.ArgumentTypeError: If the value is not a number of at least
            MIN_INTERVAL seconds.
    """
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"interval must be a number of seconds, got '{text}'")
    if value < MIN_INTERVAL:
        raise argparse.ArgumentTypeError(
            f"interval must be at least {MIN_INTERVAL} seconds, got {value}"
        )
    return value


def _build_parser():
    """Build the argparse parser for the parse-video subcommand.

    Returns:
        argparse.ArgumentParser: The configured parser.
    """
    parser = argparse.ArgumentParser(
        prog='app parse-video',
        description='Extract still images from a drone video at a fixed interval, '
                    'embedding GPS metadata when a flight log is supplied.'
    )
    parser.add_argument('--video', required=True,
                        help='Video file to extract frames from.')
    parser.add_argument('--output', required=True,
                        help='Directory for the extracted images (created if missing).')
    parser.add_argument('--metadata',
                        help='DJI .srt subtitle file or Skydio .csv flight log holding '
                             'the GPS track. Frames are written without GPS if omitted.')
    parser.add_argument('--interval', type=_interval, default=DEFAULT_INTERVAL,
                        metavar='SECONDS',
                        help=f'Seconds of video between captured frames (default: {DEFAULT_INTERVAL}).')
    return parser


def _validate(args):
    """Check the inputs the service cannot report on cleanly itself.

    An unreadable video is reported by the service, but a mistyped metadata
    path is not: an unrecognised extension is silently treated as "no metadata
    supplied", and the run finishes with images that have no GPS. Fail up front
    instead.

    Args:
        args: Parsed argparse namespace.

    Returns:
        str: An error message, or None when the arguments are usable.
    """
    if not os.path.isfile(args.video):
        return f"video file not found: {args.video}"
    if args.metadata:
        if not os.path.isfile(args.metadata):
            return f"metadata file not found: {args.metadata}"
        extension = os.path.splitext(args.metadata)[1].lower()
        if extension not in METADATA_EXTENSIONS:
            return (f"metadata must be a DJI .srt or a .csv flight log, "
                    f"got '{extension or args.metadata}'")
    return None


def run_video_parser_cli(argv):
    """Extract frames from a video from the command line.

    Args:
        argv: Argument list excluding the leading 'parse-video' subcommand token.

    Returns:
        int: Process exit code -- 0 when images were written, 1 on a bad
            argument, a failed run, or a run cancelled before it finished.
    """
    args = _build_parser().parse_args(argv)

    error = _validate(args)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    video = os.path.abspath(args.video)
    output = os.path.abspath(args.output)
    metadata = os.path.abspath(args.metadata) if args.metadata else ''

    # A QCoreApplication backs the QObject-based service for a headless run.
    from PySide6.QtCore import QCoreApplication
    QCoreApplication.instance() or QCoreApplication([])

    service = VideoParserService(1, video, metadata, output, args.interval)

    summary = {}
    service.sig_msg.connect(lambda text: print(text, flush=True))
    service.sig_done.connect(lambda _id, count: summary.update(count=count))

    print("ADIAT video parsing")
    print(f"  Video:    {video}")
    print(f"  Output:   {output}")
    print(f"  Metadata: {metadata or '(none)'}")
    print(f"  Interval: {args.interval} seconds")
    print('')

    # Ctrl+C asks the service to stop at the next frame, so it releases the
    # capture, deletes any remuxed temp file and reports what it wrote. Killing
    # the process instead leaves both behind.
    def _on_interrupt(_signum, _frame):
        service.process_cancel()

    previous_handler = signal.signal(signal.SIGINT, _on_interrupt)
    try:
        # Runs synchronously in this thread; the GUI is what needs the worker.
        service.process_video()
    finally:
        signal.signal(signal.SIGINT, previous_handler)

    count = summary.get('count', 0)
    print('')
    print(f"Done: {count} images written to {output}")
    if service.cancelled:
        print("Cancelled before the end of the video.")
        return 1
    return 0 if count else 1
