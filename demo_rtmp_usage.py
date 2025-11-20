#!/usr/bin/env python3
"""
Demo script showing how to use RTMP streams with ADIAT viewers.

This script demonstrates how to programmatically connect to RTMP streams
using the Real-Time Color Detection viewer.

Usage:
    python demo_rtmp_usage.py
    python demo_rtmp_usage.py --color rtmp://your-server:1935/live/stream
"""

import sys
import os
import argparse

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from core.controllers.RTMPColorDetectionViewer import RTMPColorDetectionViewer


def demo_color_detection(rtmp_url=None):
    """Demo Real-Time Color Detection with RTMP stream."""
    app = QApplication(sys.argv)
    viewer = RTMPColorDetectionViewer()

    # Configure for RTMP stream
    viewer.stream_controls.type_combo.setCurrentText("RTMP Stream")

    if rtmp_url:
        # Set the RTMP URL
        viewer.stream_controls.url_input.setText(rtmp_url)

        # Auto-connect after a short delay to let UI initialize
        QTimer.singleShot(1000, lambda: viewer.stream_controls.request_connect())

        print(f"Connecting to RTMP stream: {rtmp_url}")
        print("Color Detection Viewer is now running...")
        print("Configure HSV color ranges in the UI to detect specific colors")
    else:
        # Set example URL
        viewer.stream_controls.url_input.setText("rtmp://example.com:1935/live/stream")
        print("Color Detection Viewer opened in RTMP mode")
        print("Enter your RTMP URL and click Connect to start")

    viewer.show()
    sys.exit(app.exec_())


def main():
    parser = argparse.ArgumentParser(
        description="Demo RTMP stream usage with ADIAT Color Detection viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Open Color Detection viewer in RTMP mode (manual connection)
  python demo_rtmp_usage.py --color

  # Auto-connect Color Detection to RTMP stream
  python demo_rtmp_usage.py --color rtmp://localhost:1935/live/stream

  # Test with HTTP stream (also supported)
  python demo_rtmp_usage.py --color http://admin:password@192.168.1.100:8080/video

Common RTMP URLs:
  - OBS Studio: rtmp://localhost:1935/live/stream_key
  - YouTube Live: rtmp://a.rtmp.youtube.com/live2/your-stream-key
  - Twitch: rtmp://live.twitch.tv/app/your-stream-key
  - Local RTMP server: rtmp://localhost:1935/live/test
  - IP Camera: rtmp://192.168.1.100:1935/live/cam1
        """
    )

    parser.add_argument(
        "--color",
        nargs='?',
        const='',
        metavar="RTMP_URL",
        help="Launch Color Detection viewer with optional RTMP URL"
    )

    args = parser.parse_args()

    # Check if no arguments provided
    if args.color is None:
        print("=" * 60)
        print("RTMP Stream Demo for ADIAT")
        print("=" * 60)
        print("\nNo viewer specified. Use --color")
        print("\nExamples:")
        print("  python demo_rtmp_usage.py --color")
        print("  python demo_rtmp_usage.py --color rtmp://localhost:1935/live/stream")
        print("\nRun with -h for more help")
        return 1

    # Launch the color detection viewer
    rtmp_url = args.color if args.color else None
    demo_color_detection(rtmp_url)

    return 0


if __name__ == "__main__":
    sys.exit(main())
