"""Loading, scaling and sampling an operator-supplied filter mask.

An operator can hand ADIAT a black-and-white image marking where a detection
counts - the search area drawn over a map export, say - and have AOIs outside
it hidden. Answering "is this AOI inside the mask?" means reading the file,
resizing it to each image's dimensions and thresholding it, none of which is
UI orchestration; it lived in ``AOIController`` alongside the filter loop
that consumes it (CLAUDE.md 2.1).

The scaling cache is the reason this is a class and not a function. A mission
folder is one mask against many images, most of them the same size, and
re-resizing a full-resolution mask per AOI per image is the difference
between a filter that applies instantly and one that stalls the viewer.
"""

from typing import Optional, Tuple

import cv2
import numpy as np

from core.services.LoggerService import LoggerService


class MaskFilterService:
    """Samples a binary mask at image coordinates, scaled and cached."""

    def __init__(self, logger=None):
        """
        Args:
            logger: Optional LoggerService; one is created when omitted.
        """
        self.logger = logger or LoggerService()
        self._path: Optional[str] = None
        # Raw grayscale mask, read once per path.
        self._raw: Optional[np.ndarray] = None
        # {(width, height): thresholded mask} - one entry per image size.
        self._scaled: dict = {}

    @property
    def path(self) -> Optional[str]:
        """The mask file currently in use, or None."""
        return self._path

    def set_mask_path(self, path: Optional[str]) -> None:
        """Point at a mask file, dropping any cache for a previous one.

        A no-op when the path is unchanged, so a caller can set it on every
        filter pass without throwing the cache away each time.
        """
        if path == self._path:
            return
        self._path = path
        self.invalidate()

    def invalidate(self) -> None:
        """Forget the loaded mask and every scaled copy of it."""
        self._raw = None
        self._scaled = {}

    def get_scaled_mask(self, width: int, height: int) -> Optional[np.ndarray]:
        """Binary mask at ``width`` x ``height``, or None.

        Returns:
            numpy.ndarray: ``(height, width)`` of 0 and 255, or None when no
            mask is set or the file could not be read. None means "do not
            filter" rather than "nothing passes" - an unreadable mask must
            not silently hide every AOI.
        """
        if self._path is None:
            return None

        if self._raw is None:
            self._raw = cv2.imread(self._path, cv2.IMREAD_GRAYSCALE)
            if self._raw is None:
                self.logger.warning(f"Could not load mask image: {self._path}")
                return None

        key = (width, height)
        if key in self._scaled:
            return self._scaled[key]

        scaled = cv2.resize(self._raw, (width, height),
                            interpolation=cv2.INTER_LINEAR)
        _, binary = cv2.threshold(scaled, 127, 255, cv2.THRESH_BINARY)
        self._scaled[key] = binary
        return binary

    def contains(self, center: Tuple[int, int], width: int,
                 height: int) -> Optional[bool]:
        """Is ``center`` inside the mask, for an image of these dimensions?

        Args:
            center: ``(x, y)`` in image pixels. Clamped into range - an AOI's
                centre can sit a pixel outside the frame after expansion, and
                that must not raise.
            width: Image width in pixels.
            height: Image height in pixels.

        Returns:
            bool, or None when there is no usable mask - which the caller
            must read as "no opinion", not as False.
        """
        mask = self.get_scaled_mask(width, height)
        if mask is None:
            return None
        x = max(0, min(int(center[0]), width - 1))
        y = max(0, min(int(center[1]), height - 1))
        return bool(mask[y, x] > 0)
