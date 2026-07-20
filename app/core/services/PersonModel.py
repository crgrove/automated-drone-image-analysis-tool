"""PersonModel - 3D geometry for the Person Size Reference overlay.

Generates a cloud of 3D surface points for a person of a given height in an
upright pose (standing or sitting). Points are in a person-local metric
frame: x = right, y = forward, z = up, origin at the feet on the ground.

Projecting these points through a CameraModel and taking the convex hull of
the result yields a perspective-correct silhouette - a compact top-down
shape viewed from near-nadir, a foreshortened upright figure viewed
obliquely or near a frame edge.

A recumbent (lying) person is essentially flat on the ground and is rendered
separately by projecting a flat outline, so it is not produced here.

Body proportions match the top-down silhouettes in PersonReferenceDialog
(head diameter 0.135H, shoulder width 0.26H, body depth 0.19H).
"""

import math
from typing import List, Tuple

Point3D = Tuple[float, float, float]


def _ellipse_ring(semi_x: float, semi_y: float, z: float, count: int) -> List[Point3D]:
    """Return `count` points evenly spaced around an ellipse at height z."""
    ring = []
    for i in range(count):
        angle = 2.0 * math.pi * i / count
        ring.append((semi_x * math.cos(angle), semi_y * math.sin(angle), z))
    return ring


def _sphere_points(center_z: float, radius: float,
                   lat_bands: int, lon_count: int) -> List[Point3D]:
    """Return points sampled over a sphere centred on the z axis at center_z."""
    points: List[Point3D] = []
    for lat in range(1, lat_bands):
        phi = math.pi * lat / lat_bands          # 0..pi, measured from the top
        z = center_z + radius * math.cos(phi)
        r = radius * math.sin(phi)
        for lon in range(lon_count):
            angle = 2.0 * math.pi * lon / lon_count
            points.append((r * math.cos(angle), r * math.sin(angle), z))
    points.append((0.0, 0.0, center_z + radius))  # top pole
    points.append((0.0, 0.0, center_z - radius))  # bottom pole
    return points


def build_standing_points(height_m: float, ring_count: int = 24) -> List[Point3D]:
    """3D surface points for a standing person of the given height in metres.

    The body is an elliptical column (shoulder width by body depth) from the
    feet to the shoulders, topped by a spherical head.
    """
    h = float(height_m)
    head_diam = 0.135 * h
    semi_x = 0.130 * h        # half shoulder width
    semi_y = 0.095 * h        # half body depth
    body_top = max(0.0, h - head_diam)

    points: List[Point3D] = []
    points += _ellipse_ring(semi_x, semi_y, 0.0, ring_count)        # feet ring
    points += _ellipse_ring(semi_x, semi_y, body_top, ring_count)   # shoulder ring
    points += _sphere_points(h - head_diam / 2.0, head_diam / 2.0, 4, 8)
    return points


def build_sitting_points(height_m: float, ring_count: int = 24) -> List[Point3D]:
    """3D surface points for a person sitting upright.

    `height_m` is the person's standing height; the seated form is shorter
    and has a wider footprint (knees/lap).
    """
    h = float(height_m)
    head_diam = 0.135 * h
    semi_x = 0.150 * h        # wider footprint - knees and lap
    semi_y = 0.150 * h
    torso_top = 0.40 * h      # seated torso height

    points: List[Point3D] = []
    points += _ellipse_ring(semi_x, semi_y, 0.0, ring_count)
    points += _ellipse_ring(semi_x * 0.75, semi_y * 0.75, torso_top, ring_count)
    points += _sphere_points(torso_top + head_diam / 2.0, head_diam / 2.0, 4, 8)
    return points


def build_points(height_m: float, pose: str) -> List[Point3D]:
    """Return the 3D point cloud for an upright pose ('standing' or 'sitting').

    Raises:
        ValueError: if `pose` is not an upright pose handled by this module.
    """
    if pose == "standing":
        return build_standing_points(height_m)
    if pose == "sitting":
        return build_sitting_points(height_m)
    raise ValueError(f"PersonModel.build_points: unsupported pose {pose!r}")


def build_footprint_points(height_m: float, pose: str,
                           ring_count: int = 48) -> List[Point3D]:
    """Flat overhead footprint (all z = 0) of an upright person.

    This is the person's horizontal extent as seen from directly above - the
    shape a spotter actually looks for on near-nadir imagery. Projecting the
    full 3D column instead makes a standing figure 'lay over' into a long
    radial smear at any off-centre placement (layover ~= H*R/(agl-H)), which
    is geometrically correct but useless as a size reference. Keeping the
    footprint flat gives a compact, person-sized shape wherever it is placed.
    """
    h = float(height_m)
    if pose == "standing":
        return _ellipse_ring(0.130 * h, 0.095 * h, 0.0, ring_count)
    if pose == "sitting":
        return _ellipse_ring(0.150 * h, 0.150 * h, 0.0, ring_count)
    raise ValueError(
        f"PersonModel.build_footprint_points: unsupported pose {pose!r}")
