"""
Shared UI components for streaming detection.

This module contains reusable UI widgets used across all streaming detection algorithms.
"""

from .VideoTimelineWidget import VideoTimelineWidget
from .PlaybackControlBar import PlaybackControlBar
from .InputProcessingTab import InputProcessingTab
from .RenderingTab import RenderingTab
from .ColorWheelWidget import ColorWheelWidget

__all__ = [
    'VideoTimelineWidget',
    'PlaybackControlBar',
    'InputProcessingTab',
    'RenderingTab',
    'ColorWheelWidget',
]
