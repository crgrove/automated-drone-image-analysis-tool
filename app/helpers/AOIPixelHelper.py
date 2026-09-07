"""AOIPixelHelper - shared geometry for reading an AOI's pixels back out of an image.

Two operations recur everywhere an AOI is measured: turning its
``detected_pixels`` list into in-bounds index arrays, and enumerating the
pixels inside its circle. Both were originally written as per-pixel Python
loops, and both were then vectorized independently in six places - so the
same operation existed six times, and the six copies did not agree on what
to do with malformed input.

They agree here instead. In particular:

**Ragged input must not raise.** ``np.asarray([(1, 2), (3, 4, 5)], dtype=...)``
raises ``ValueError`` on numpy >= 1.24, where the per-pixel loops it replaced
skipped the odd entry and carried on. Every producer in ADIAT currently emits
homogeneous ``(x, y)`` pairs, so nothing reaches this path today - but
``detected_pixels`` also arrives from ``ADIAT_Data.xml`` through
``literal_eval`` (CLAUDE.md 2.5 requires old files stay readable), and a
vectorized fast path that turns one malformed row into a failed image is a
worse trade than one that drops the row. The fast path is tried first and the
tolerant path picks up whatever it rejects.

**The scale factor is applied exactly as the loops applied it** - multiply,
then truncate toward zero - so moving to array arithmetic cannot shift a
coordinate by a pixel. Detected pixels are stored at original resolution
while some algorithms score against a downscaled frame, which is the only
transform these coordinates ever undergo.
"""

from typing import NamedTuple, Optional, Tuple

import numpy as np


class CircleBox(NamedTuple):
    """The pixels of an AOI circle, as a slice pair plus a mask.

    ``inside`` is sized to the clipped bounding box, not the whole image:
    building a full-image mask per AOI turned a per-AOI cost into an
    O(image size) one, which is measurable on 48MP frames with hundreds of
    AOIs.

    Callers index the target array through the slices::

        box = circle_box(aoi['center'], aoi['radius'], img.shape)
        if box is not None:
            img[box.y_slice, box.x_slice][box.inside] = value
    """

    y_slice: slice
    x_slice: slice
    inside: np.ndarray


def _coordinates_pixel_by_pixel(detected_pixels):
    """Extract (x, y) from entries the vectorized path could not parse.

    Deliberately duck-typed rather than ``isinstance(p, (list, tuple))``:
    an entry may be a numpy array or any other 2-sequence, and the point of
    this path is to salvage what it can. Anything that will not yield two
    ints is skipped, which is what the loops this replaced did.
    """
    xs, ys = [], []
    for pixel in detected_pixels:
        try:
            x, y = int(pixel[0]), int(pixel[1])
        except (TypeError, ValueError, IndexError, KeyError):
            continue
        xs.append(x)
        ys.append(y)
    if not xs:
        return None, None
    return np.asarray(xs, dtype=np.int64), np.asarray(ys, dtype=np.int64)


def in_bounds_coordinates(
    detected_pixels,
    shape,
    scale_factor: float = 1.0,
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Convert ``detected_pixels`` to in-bounds index arrays for ``shape``.

    Args:
        detected_pixels: Sequence of ``(x, y)`` pixel pairs. ``None`` and
            empty are accepted and yield ``(None, None)``.
        shape: Shape of the array the coordinates will index, ``(height,
            width, ...)``. Only the first two entries are read.
        scale_factor: Multiply coordinates by this before bounds-checking.
            Use it when ``detected_pixels`` are stored at original resolution
            but the target array is at processing resolution. ``1.0`` is a
            no-op.

    Returns:
        ``(xs, ys)`` int64 arrays holding only the in-bounds coordinates, or
        ``(None, None)`` if there are none. The order is x-first, but both
        arrays are needed together and numpy indexes rows first, so callers
        index as ``array[ys, xs]``.
    """
    if detected_pixels is None or len(detected_pixels) == 0:
        return None, None

    try:
        coords = np.asarray(detected_pixels, dtype=np.int64)
        if coords.ndim != 2 or coords.shape[1] < 2:
            raise ValueError("detected_pixels is not a sequence of (x, y) pairs")
        xs, ys = coords[:, 0], coords[:, 1]
    except (ValueError, TypeError):
        xs, ys = _coordinates_pixel_by_pixel(detected_pixels)
        if xs is None:
            return None, None

    if scale_factor != 1.0:
        xs = (xs.astype(np.float64) * scale_factor).astype(np.int64)
        ys = (ys.astype(np.float64) * scale_factor).astype(np.int64)

    max_y, max_x = shape[0], shape[1]
    in_bounds = (xs >= 0) & (xs < max_x) & (ys >= 0) & (ys < max_y)
    if not np.any(in_bounds):
        return None, None

    return xs[in_bounds], ys[in_bounds]


def sample_aoi_pixels(image, aoi) -> Optional[np.ndarray]:
    """Return the image values covered by an AOI, or ``None`` if it covers none.

    Prefers the AOI's ``detected_pixels`` - the pixels the algorithm actually
    matched - and falls back to every pixel inside its circle, which is what
    an AOI carries when it was drawn rather than detected. This is the
    sampling that ``AlgorithmService._calculate_aoi_representative_color``
    and ``AOIService.get_aoi_representative_color`` both need; they compute
    the same representative colour from it, one from an in-memory frame and
    one through ``ImageService``.

    Args:
        image: Array to sample, indexed ``[y, x]``. Channel layout is the
            caller's business - this returns whatever the array holds, so an
            RGB array yields RGB and a BGR array yields BGR.
        aoi: AOI dict with ``center``, ``radius``, and optionally
            ``detected_pixels``.

    Returns:
        An ``(N, ...)`` array of the sampled values, or ``None`` when the AOI
        selects nothing (no in-bounds detected pixel and no on-image circle).
    """
    detected_pixels = aoi.get('detected_pixels')
    if detected_pixels:
        xs, ys = in_bounds_coordinates(detected_pixels, image.shape)
        if xs is None:
            return None
        return image[ys, xs]

    box = circle_box(aoi.get('center'), aoi.get('radius', 0), image.shape)
    if box is None:
        return None
    return image[box.y_slice, box.x_slice][box.inside]


def circle_box(center, radius, shape) -> Optional[CircleBox]:
    """Return the clipped bounding box and inside-circle mask for an AOI.

    The mask is the analytic ``dx^2 + dy^2 <= r^2``, which was checked
    against ``cv2.circle``'s filled rasterization for r=1..59 and agrees on
    every pixel - so this is not an approximation of the drawn circle.

    Args:
        center: ``(cx, cy)`` in pixels. Coerced to int, so a float centre
            cannot silently turn the box into a float slice.
        radius: Circle radius in pixels.
        shape: Shape of the array being indexed, ``(height, width, ...)``.

    Returns:
        A :class:`CircleBox`, or ``None`` when the circle falls entirely
        outside the array (an empty box).
    """
    if center is None or radius is None:
        return None
    try:
        cx, cy = int(center[0]), int(center[1])
        radius = int(radius)
    except (TypeError, ValueError, IndexError):
        return None
    if radius < 0:
        return None

    max_y, max_x = shape[0], shape[1]
    y_min, y_max = max(0, cy - radius), min(max_y, cy + radius + 1)
    x_min, x_max = max(0, cx - radius), min(max_x, cx + radius + 1)
    if y_max <= y_min or x_max <= x_min:
        return None

    ys, xs = np.ogrid[y_min:y_max, x_min:x_max]
    inside = (xs - cx) ** 2 + (ys - cy) ** 2 <= radius ** 2
    return CircleBox(slice(y_min, y_max), slice(x_min, x_max), inside)
