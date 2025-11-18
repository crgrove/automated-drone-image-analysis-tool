"""
Shared UI components for streaming detection.

This module contains reusable UI widgets used across all streaming detection algorithms.
"""

from .VideoTimelineWidget import VideoTimelineWidget
from .PlaybackControlBar import PlaybackControlBar

__all__ = [
    'VideoTimelineWidget',
    'PlaybackControlBar',
]
