"""
aoi - derive a download area-of-interest from a mission's images.

Reads each image's EXIF GPS to bound the camera positions, and sizes a buffer
that covers the image footprints (which extend past the nadir points, especially
for oblique frames) by reusing the POD kernel's flat-plane footprint projection.
Service layer only (no Qt).
"""

import math

from core.services.LoggerService import LoggerService
from core.services.coverage.params import PodParams

_logger = LoggerService()
_DEFAULT_BUFFER_M = 500.0
_MIN_BUFFER_M = 100.0


def _image_path(image):
    if isinstance(image, dict):
        return image.get('path', '')
    return str(image) if image else ''


def image_gps(path):
    """(lat, lon) from an image's EXIF GPS, or None."""
    if not path:
        return None
    try:
        from helpers.MetaDataHelper import MetaDataHelper
        from helpers.LocationInfo import LocationInfo
        exif = MetaDataHelper.get_exif_data_piexif(path)
        gps = LocationInfo.get_gps(exif_data=exif)
        if gps:
            return gps['latitude'], gps['longitude']
    except Exception:
        pass
    return None


def compute_mission_gps_bounds(images):
    """(min_lon, min_lat, max_lon, max_lat) over all image GPS, or None."""
    lons, lats = [], []
    for image in images:
        gps = image_gps(_image_path(image))
        if gps is not None:
            lats.append(gps[0])
            lons.append(gps[1])
    if not lats:
        return None
    return (min(lons), min(lats), max(lons), max(lats))


def _frame_geometry(path):
    """FrameGeometry for one image without decoding its pixels, or None."""
    try:
        import numpy as np
        from core.services.image.ImageService import ImageService
        svc = ImageService(path, '', img_array=np.zeros((1, 1, 3), dtype=np.uint8))
        svc.img_array = None
        return svc.get_frame_geometry()
    except Exception:
        return None


def suggest_buffer_m(images, params=None, sample_limit=24):
    """Suggest a buffer (meters) covering image footprints.

    Samples up to ``sample_limit`` images evenly across the mission, projects
    each footprint, and takes the largest reach (capped at ``max_range_m``).
    """
    params = params or PodParams()
    from core.services.coverage.kernel import project_footprint_corners

    paths = [p for p in (_image_path(i) for i in images) if p]
    if not paths:
        return _DEFAULT_BUFFER_M
    step = max(1, len(paths) // max(1, sample_limit))
    sampled = paths[::step][:sample_limit]

    reaches = []
    for path in sampled:
        fg = _frame_geometry(path)
        if fg is None:
            continue
        try:
            corners = project_footprint_corners(fg, params)
            reaches.append(max(math.hypot(e, n) for e, n in corners))
        except Exception:
            continue
    if not reaches:
        return _DEFAULT_BUFFER_M
    buffer_m = max(reaches)
    buffer_m = min(buffer_m, params.max_range_m)
    buffer_m = max(buffer_m, _MIN_BUFFER_M)
    # Round up to a tidy 50 m step.
    return math.ceil(buffer_m / 50.0) * 50.0


def pad_bounds(bounds_wgs84, buffer_m):
    """Expand a WGS84 bbox outward by ``buffer_m`` meters on all sides."""
    min_lon, min_lat, max_lon, max_lat = bounds_wgs84
    mid_lat = (min_lat + max_lat) / 2.0
    dlat = buffer_m / 111320.0
    dlon = buffer_m / (111320.0 * max(0.05, math.cos(math.radians(mid_lat))))
    return (min_lon - dlon, min_lat - dlat, max_lon + dlon, max_lat + dlat)


def estimate_download_aoi(images, params=None, sample_limit=24):
    """(padded_bounds, raw_bounds, buffer_m) for a mission, or None if no GPS."""
    raw = compute_mission_gps_bounds(images)
    if raw is None:
        return None
    buffer_m = suggest_buffer_m(images, params=params, sample_limit=sample_limit)
    return pad_bounds(raw, buffer_m), raw, buffer_m
