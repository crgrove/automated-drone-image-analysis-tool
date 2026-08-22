"""Shared fixtures for viewer controller tests."""

import pytest

from core.controllers.images.viewer.Viewer import Viewer


@pytest.fixture
def wire_pending_zoom():
    """Bind the Viewer's real pending-zoom semantics onto a test parent.

    One shared home so every suite pins the same contract: if the Viewer's
    slot semantics change, exactly one helper has to follow.

    Returns a wiring function:
        wire(parent, loaded_idx=None)

    where ``parent`` is the stand-in viewer parent (MagicMock or QObject)
    and ``loaded_idx`` selects the simulated load behavior:
      - an int: parent._load_image consumes the pending request for that
        image index the way the real ImageLoadController pipeline does
        (its final step), invoking the zoom callable on a match;
      - None: parent._load_image returns early without consuming, the
        failed/early-returning-load case.
    """
    def wire(parent, loaded_idx=None):
        parent._pending_view_zoom = None
        # The bound Viewer methods log; bare stand-ins (QObject) need one.
        if not hasattr(parent, 'logger'):
            from unittest.mock import MagicMock
            parent.logger = MagicMock()
        parent.load_image_with_zoom = (
            lambda idx, cb: Viewer.load_image_with_zoom(parent, idx, cb))
        parent.take_pending_view_zoom = (
            lambda idx: Viewer.take_pending_view_zoom(parent, idx))

        def _load_image():
            if loaded_idx is not None:
                apply_zoom = parent.take_pending_view_zoom(loaded_idx)
                if apply_zoom is not None:
                    apply_zoom()

        parent._load_image = _load_image
        return parent

    return wire
