"""Controllers for the ADIAT Flight Viewer.

This package owns the desktop-side orchestration described in
``flight_viewer_plan.md``. Controllers are UI-only orchestrators per
CLAUDE.md §2.1 — services live under ``core.services.streaming``.
"""

from .FlightViewerController import FlightViewerController
from .FlightTileController import FlightTileController
from .MissionGalleryController import MissionGalleryController

__all__ = [
    "FlightTileController",
    "FlightViewerController",
    "MissionGalleryController",
]
