"""
AOISimilarityGroupingService - Orders every AOI so look-alike detections that sit
close together on the ground end up next to each other.

Two AOIs are linked when their estimated GPS positions are within a ground distance
of each other AND their appearance similarity (the same color-first score that
Find Similar AOIs reports) meets a threshold. Groups are then built greedily: the
AOI with the most links anchors a group holding every still-ungrouped AOI linked to
it, so every member is both near and similar to its anchor (no chaining across a
field of look-alikes).

The resulting order puts the largest groups first (anchor, then members by
similarity to the anchor), then every ungrouped AOI in its normal image/AOI order.

Thread-safety: same contract as AOISimilarityService; run from one worker thread.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from core.services.image.AOIService import AOIService
from core.services.image.ImageService import ImageService
from core.services.LoggerService import LoggerService

DEFAULT_MAX_DISTANCE_M = 15.0
DEFAULT_MIN_SIMILARITY = 70
EARTH_RADIUS_M = 6371008.8
PROGRESS_EVERY = 100

LatLon = Tuple[float, float]
AOIKey = Tuple[Any, int, int]


def aoi_sort_key(image_path: Any, aoi: Dict[str, Any]) -> AOIKey:
    """
    Content-derived identity for an AOI: (image path, center x, center y).

    Used instead of (image_idx, aoi_idx) so a computed order survives AOIs being
    added or removed (which shifts indices) for as long as the AOI itself exists.
    """
    center = aoi.get('center') or (0, 0)
    return (image_path, int(round(float(center[0]))), int(round(float(center[1]))))


def make_aoi_locator(custom_altitude_ft: Optional[float] = None,
                     use_terrain: bool = True) -> Callable[[Dict[str, Any]], List[Optional[LatLon]]]:
    """
    Build a locate_aois callable for group() from the viewer's GPS settings.

    Uses the same AOI GPS estimate as the rest of the viewer (custom AGL, terrain
    and hand-placed marker positions included). Each image gets a metadata-only
    ImageService, so no image is decoded, and it is dropped once that image's
    AOIs are located.

    Args:
        custom_altitude_ft: Operator AGL override in feet, or None.
        use_terrain: Whether to use terrain elevation data.
    """
    logger = LoggerService()
    if not custom_altitude_ft or custom_altitude_ft <= 0:
        custom_altitude_ft = None

    def locate_aois(image: Dict[str, Any]) -> List[Optional[LatLon]]:
        aois = image.get('areas_of_interest') or []
        try:
            image_service = ImageService(
                image['path'],
                image.get('mask_path', ''),
                calculated_bearing=image.get('bearing'),
                defer_load=True
            )
            aoi_service = AOIService(image, image_service=image_service)
        except Exception as e:
            logger.error(f"Similarity grouping: cannot read metadata for '{image.get('path')}': {e}")
            return [None] * len(aois)

        positions = []
        for aoi in aois:
            result = aoi_service.calculate_gps_with_metadata(image, aoi, custom_altitude_ft, use_terrain)
            positions.append((result.latitude, result.longitude) if result else None)
        return positions

    return locate_aois


@dataclass
class SimilarityGroupingResult:
    """Outcome of a grouping pass."""
    order: List[Tuple[int, int]]                   # (image_idx, aoi_idx), sorted
    ranks: Dict[AOIKey, int]                       # aoi_sort_key -> position in order
    groups: List[List[Tuple[int, int]]] = field(default_factory=list)  # 2+ member groups, in order
    unlocated_count: int = 0                       # AOIs with no GPS position
    unanalyzed_count: int = 0                      # AOIs whose thumbnail could not be read

    @property
    def total(self) -> int:
        return len(self.order)

    @property
    def grouped_count(self) -> int:
        return sum(len(group) for group in self.groups)


class AOISimilarityGroupingService:
    """Groups AOIs that look alike and are close together on the ground."""

    def __init__(self, similarity_service):
        """
        Args:
            similarity_service: AOISimilarityService supplying cached appearance
                descriptors and the descriptor distance (compare).
        """
        self.logger = LoggerService()
        self.similarity_service = similarity_service

    def group(self, images: List[Dict[str, Any]],
              locate_aois: Callable[[Dict[str, Any]], Sequence[Optional[LatLon]]],
              max_distance_m: float = DEFAULT_MAX_DISTANCE_M,
              min_similarity: int = DEFAULT_MIN_SIMILARITY,
              progress_callback: Optional[Callable[[int, int], None]] = None,
              cancel_check: Optional[Callable[[], bool]] = None) -> Optional[SimilarityGroupingResult]:
        """
        Order every AOI in the dataset into similar-and-nearby groups.

        Args:
            images: Viewer image dicts (each with 'path' and 'areas_of_interest').
            locate_aois: callable(image) -> one (lat, lon) or None per AOI of that
                image, in AOI order. Called once per image that has AOIs.
            max_distance_m: Largest ground distance between two linked AOIs.
            min_similarity: Smallest appearance similarity (0-100) between two
                linked AOIs, on the Find Similar AOIs scale.
            progress_callback: Optional callable(done, total) over AOIs analyzed.
            cancel_check: Optional callable returning True to abort.

        Returns:
            SimilarityGroupingResult, or None when cancelled.

        Raises:
            ValueError: If max_distance_m is not positive.
        """
        if not max_distance_m or max_distance_m <= 0:
            raise ValueError(f"Max distance must be positive (got {max_distance_m})")

        total = sum(len(image.get('areas_of_interest') or []) for image in images)
        # Entry index follows the default (image, AOI) order, which makes it the
        # deterministic tie-breaker everywhere below.
        entries = []  # (image_idx, aoi_idx, descriptor or None, (lat, lon) or None)
        done = 0
        for image_idx, image in enumerate(images):
            aois = image.get('areas_of_interest') or []
            if not aois:
                continue
            if cancel_check and cancel_check():
                return None
            positions = self._locate(locate_aois, image, len(aois))
            for aoi_idx, aoi in enumerate(aois):
                if cancel_check and cancel_check():
                    return None
                entries.append((image_idx, aoi_idx, self._descriptor(image, aoi_idx, aoi),
                                positions[aoi_idx]))
                done += 1
                if progress_callback and (done % PROGRESS_EVERY == 0 or done == total):
                    progress_callback(done, total)

        unlocated = sum(1 for entry in entries if entry[3] is None)
        unanalyzed = sum(1 for entry in entries if entry[2] is None)

        links = self._link(entries, max_distance_m, min_similarity, cancel_check)
        if links is None:
            return None

        groups = self._build_groups(links)
        order_entries = [index for group in groups for index in group]
        grouped = set(order_entries)
        order_entries += [index for index in range(len(entries)) if index not in grouped]

        order = [(entries[index][0], entries[index][1]) for index in order_entries]
        ranks = {}
        for rank, (image_idx, aoi_idx) in enumerate(order):
            image = images[image_idx]
            ranks.setdefault(aoi_sort_key(image.get('path'), image['areas_of_interest'][aoi_idx]), rank)

        return SimilarityGroupingResult(
            order=order,
            ranks=ranks,
            groups=[[(entries[index][0], entries[index][1]) for index in group] for group in groups],
            unlocated_count=unlocated,
            unanalyzed_count=unanalyzed,
        )

    def _locate(self, locate_aois, image, count) -> List[Optional[LatLon]]:
        """Resolve one image's AOI positions, padding/trimming to the AOI count."""
        try:
            positions = list(locate_aois(image) or [])
        except Exception as e:
            self.logger.error(f"Similarity grouping: could not locate AOIs in '{image.get('path')}': {e}")
            positions = []
        positions = positions[:count] + [None] * max(0, count - len(positions))
        return [self._valid_position(position) for position in positions]

    @staticmethod
    def _valid_position(position) -> Optional[LatLon]:
        try:
            lat, lon = float(position[0]), float(position[1])
        except (TypeError, ValueError, IndexError):
            return None
        if not (math.isfinite(lat) and math.isfinite(lon)) or abs(lat) > 90 or abs(lon) > 180:
            return None
        return lat, lon

    def _descriptor(self, image, aoi_idx, aoi):
        try:
            return self.similarity_service.get_descriptor(image.get('path'), aoi)
        except Exception as e:
            self.logger.error(
                f"Similarity grouping: descriptor failed for image '{image.get('path')}' AOI {aoi_idx}: {e}"
            )
            return None

    def _link(self, entries, max_distance_m, min_similarity, cancel_check):
        """
        Find every pair that is both near and similar.

        Positions are projected to local metres (equirectangular about the mean
        latitude, exact enough at flight scale) and bucketed into a grid of
        max_distance_m cells, so only pairs in neighbouring cells are compared.

        Returns:
            {entry index: [(other entry index, similarity, distance_m), ...]},
            or None when cancelled.
        """
        usable = [index for index, entry in enumerate(entries)
                  if entry[2] is not None and entry[3] is not None]
        links = {index: [] for index in usable}
        if len(usable) < 2:
            return links

        lat_ref = sum(entries[index][3][0] for index in usable) / len(usable)
        lon_ref = entries[usable[0]][3][1]
        cos_ref = math.cos(math.radians(lat_ref))
        metres = {}
        cells = {}
        for index in usable:
            lat, lon = entries[index][3]
            d_lon = (lon - lon_ref + 180.0) % 360.0 - 180.0  # stay continuous across the antimeridian
            x = EARTH_RADIUS_M * math.radians(d_lon) * cos_ref
            y = EARTH_RADIUS_M * math.radians(lat - lat_ref)
            metres[index] = (x, y)
            cell = (math.floor(x / max_distance_m), math.floor(y / max_distance_m))
            cells.setdefault(cell, []).append(index)

        compare = self.similarity_service.compare
        for index in usable:
            if cancel_check and cancel_check():
                return None
            x, y = metres[index]
            cell_x, cell_y = math.floor(x / max_distance_m), math.floor(y / max_distance_m)
            descriptor = entries[index][2]
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for other in cells.get((cell_x + dx, cell_y + dy), ()):
                        if other <= index:
                            continue  # each pair once
                        ox, oy = metres[other]
                        distance = math.hypot(x - ox, y - oy)
                        if distance > max_distance_m:
                            continue
                        similarity = int(max(0, min(100, round(
                            100.0 * (1.0 - compare(descriptor, entries[other][2]))))))
                        if similarity < min_similarity:
                            continue
                        links[index].append((other, similarity, distance))
                        links[other].append((index, similarity, distance))
        return links

    @staticmethod
    def _build_groups(links) -> List[List[int]]:
        """
        Greedy star clustering over the link graph.

        Anchors are taken most-linked first; each claims every still-ungrouped AOI
        linked to it. Groups of two or more are returned largest first (ties: the
        earliest AOI in the group), each as [anchor, members by similarity desc,
        distance asc].
        """
        assigned = set()
        groups = []
        anchors = sorted(links, key=lambda index: (-len(links[index]), index))
        for anchor in anchors:
            if anchor in assigned:
                continue
            members = sorted(
                (link for link in links[anchor] if link[0] not in assigned),
                # Distance compared at centimetre resolution so float noise never
                # outranks the default-order tie-break
                key=lambda link: (-link[1], round(link[2], 2), link[0])
            )
            if not members:
                continue
            group = [anchor] + [link[0] for link in members]
            assigned.update(group)
            groups.append(group)
        groups.sort(key=lambda group: (-len(group), min(group)))
        return groups
