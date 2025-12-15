"""
Shared UI components for streaming detection.

This module contains reusable UI widgets used across all streaming detection algorithms.
"""

from .VideoTimelineWidget import VideoTimelineWidget
from .PlaybackControlBar import PlaybackControlBar
from .InputProcessingTab import InputProcessingTab
from .RenderingTab import RenderingTab
from .CleanupTab import CleanupTab
from .ColorWheelWidget import ColorWheelWidget
from .FrameTab import FrameTab
from .TrackGalleryWidget import TrackGalleryWidget

__all__ = [
    'VideoTimelineWidget',
    'PlaybackControlBar',
    'InputProcessingTab',
    'RenderingTab',
    'CleanupTab',
    'ColorWheelWidget',
    'FrameTab',
    'TrackGalleryWidget',
]
