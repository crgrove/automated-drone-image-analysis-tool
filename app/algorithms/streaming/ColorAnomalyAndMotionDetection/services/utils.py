"""
utils.py - Utility functions for color anomaly and motion detection
"""

from core.services.streaming.StreamingUtils import StageTimings


def format_timing_summary(timings: StageTimings) -> str:
    """Format timing information as readable string."""
    return (f"motion={timings.motion_detection_ms:.1f}ms, "
            f"color={timings.color_detection_ms:.1f}ms, "
            f"render={timings.render_ms:.1f}ms, "
            f"total={timings.total_ms:.1f}ms, "
            f"FPS={1000.0/timings.total_ms if timings.total_ms > 0 else 0:.1f}")

