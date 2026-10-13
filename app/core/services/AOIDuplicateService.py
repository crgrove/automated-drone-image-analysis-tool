"""
AOIDuplicateService - Links repeat detections of one object to a single primary AOI.

Overlapping drone images capture the same object several times, so one find is
often several AOIs. A reviewer marks each repeat as a *duplicate* of the AOI that
should represent the object (the *primary*). Reports then list the object once,
at the primary's position, followed by every other image/AOI it was seen in.

The link lives on the duplicate as its primary's run-wide AOI number
(``duplicate_of``). Numbers are persistent and unique across the run, so a link
survives re-sorting, filtering and AOI index shifts, and builds that predate this
feature simply ignore the attribute.

Rules, enforced here so the D key, the Find Similar dialog and the flag toggles
all agree:

- An AOI is flagged (reported), a duplicate (reported through its primary), or
  neither. Marking a duplicate clears its own flag.
- Links are one level deep. Marking an AOI as a duplicate of a duplicate links
  it to that duplicate's primary, and when a primary is itself marked as a
  duplicate its own duplicates move with it.
- A link to a number no AOI carries (the primary was deleted) is ignored.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from helpers.LocationInfo import LocationInfo
from helpers.PathHelper import cross_platform_basename

# Flag colour for a duplicate. Distinct from the flagged orange-red (#FF7043),
# the comment gold and the location green so the three states read at a glance.
DUPLICATE_FLAG_COLOR = '#B388FF'

# Candidate ranking: a candidate this far away keeps half its proximity score.
PROXIMITY_HALF_DISTANCE_M = 30.0
# Proximity (and similarity) assumed when a value cannot be computed, so an
# unlocated or unreadable candidate ranks like a mid-distance, mid-match one.
UNKNOWN_FACTOR = 0.5

AOIRef = Tuple[int, int]  # (image_idx, aoi_idx)
LatLon = Tuple[float, float]


def get_duplicate_of(aoi: Optional[Dict[str, Any]]) -> Optional[int]:
    """The primary AOI number this AOI is marked a duplicate of, or None."""
    if not aoi:
        return None
    value = aoi.get('duplicate_of')
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def parse_duplicate_of(value: Any) -> Optional[int]:
    """Parse a persisted ``duplicate_of`` attribute; None when absent or malformed."""
    if value is None or value == '':
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def image_display_name(image: Dict[str, Any]) -> str:
    """The name reports use for an image."""
    return image.get('name') or cross_platform_basename(image.get('path', '') or '')


def index_by_number(images: Sequence[Dict[str, Any]]) -> Dict[int, AOIRef]:
    """Map every run-wide AOI number to its (image_idx, aoi_idx)."""
    index = {}
    for image_idx, image in enumerate(images or []):
        for aoi_idx, aoi in enumerate(image.get('areas_of_interest') or []):
            number = aoi.get('number')
            if isinstance(number, int) and number not in index:
                index[number] = (image_idx, aoi_idx)
    return index


def _aoi_at(images, ref: Optional[AOIRef]) -> Optional[Dict[str, Any]]:
    if ref is None:
        return None
    image_idx, aoi_idx = ref
    if image_idx is None or aoi_idx is None:
        return None
    if not (0 <= image_idx < len(images)):
        return None
    aois = images[image_idx].get('areas_of_interest') or []
    if not (0 <= aoi_idx < len(aois)):
        return None
    return aois[aoi_idx]


def resolve_primary(images: Sequence[Dict[str, Any]], aoi: Dict[str, Any],
                    numbers: Optional[Dict[int, AOIRef]] = None) -> Optional[AOIRef]:
    """
    Where the primary of a duplicate lives, or None if *aoi* is not a valid duplicate.

    A link to a missing number, or to the AOI itself, is not a valid duplicate.
    """
    target = get_duplicate_of(aoi)
    if target is None or target == aoi.get('number'):
        return None
    numbers = numbers if numbers is not None else index_by_number(images)
    return numbers.get(target)


def is_duplicate(images: Sequence[Dict[str, Any]], aoi: Dict[str, Any],
                 numbers: Optional[Dict[int, AOIRef]] = None) -> bool:
    """True when *aoi* is linked to a primary that exists."""
    return resolve_primary(images, aoi, numbers) is not None


def duplicates_by_primary(images: Sequence[Dict[str, Any]]) -> Dict[int, List[AOIRef]]:
    """Primary AOI number -> its duplicates' (image_idx, aoi_idx), in image/AOI order."""
    numbers = index_by_number(images)
    groups: Dict[int, List[AOIRef]] = {}
    for image_idx, image in enumerate(images or []):
        for aoi_idx, aoi in enumerate(image.get('areas_of_interest') or []):
            if resolve_primary(images, aoi, numbers) is not None:
                groups.setdefault(get_duplicate_of(aoi), []).append((image_idx, aoi_idx))
    return groups


def duplicate_counts(images: Sequence[Dict[str, Any]]) -> Dict[int, int]:
    """Primary AOI number -> number of AOIs marked as its duplicates."""
    return {number: len(refs) for number, refs in duplicates_by_primary(images).items()}


@dataclass
class DuplicateChange:
    """What a mark/clear operation changed."""
    primary: Optional[AOIRef] = None                      # Effective primary (marking only)
    changed: List[AOIRef] = field(default_factory=list)   # AOIs whose link was set or cleared
    touched: List[AOIRef] = field(default_factory=list)   # Every AOI whose review state changed

    @property
    def count(self) -> int:
        return len(self.changed)


def mark_duplicates(images: Sequence[Dict[str, Any]], items: Iterable[AOIRef],
                    primary: AOIRef) -> DuplicateChange:
    """
    Mark every item as a duplicate of *primary*, updating the AOI dicts in place.

    If *primary* is itself a duplicate, its own primary is used instead - unless
    that primary is one of the items, which swaps the two. Any item that has
    duplicates of its own hands them to the new primary. The primary itself,
    invalid references and AOIs without a number are skipped.

    Returns:
        DuplicateChange; ``primary`` is None when the primary could not be used.
    """
    change = DuplicateChange()
    items = [tuple(ref) for ref in items]
    numbers = index_by_number(images)

    primary = tuple(primary)
    primary_aoi = _aoi_at(images, primary)
    if primary_aoi is None:
        return change
    root = resolve_primary(images, primary_aoi, numbers)
    if root is not None and tuple(root) not in items:
        primary, primary_aoi = tuple(root), _aoi_at(images, root)
    primary_number = primary_aoi.get('number')
    if not isinstance(primary_number, int):
        return change
    change.primary = primary

    # Snapshot each item's own duplicates before any link changes
    groups = duplicates_by_primary(images)

    touched = []
    for ref in items:
        aoi = _aoi_at(images, ref)
        if aoi is None or ref == primary:
            continue
        number = aoi.get('number')
        if not isinstance(number, int):
            continue

        if get_duplicate_of(aoi) != primary_number or aoi.get('flagged', False):
            aoi['duplicate_of'] = primary_number
            aoi['flagged'] = False
            change.changed.append(ref)
            touched.append(ref)

        # Its own duplicates follow it to the new primary (links stay one level)
        for child_ref in groups.get(number, []):
            if child_ref == primary:
                # The new primary was this item's duplicate: it is now the primary
                primary_aoi.pop('duplicate_of', None)
                touched.append(child_ref)
                continue
            child = _aoi_at(images, child_ref)
            if get_duplicate_of(child) != primary_number:
                child['duplicate_of'] = primary_number
                touched.append(child_ref)

    change.touched = _unique(touched)
    return change


def clear_duplicates(images: Sequence[Dict[str, Any]], items: Iterable[AOIRef]) -> DuplicateChange:
    """Remove the duplicate link from every item that has one."""
    change = DuplicateChange()
    for ref in items:
        aoi = _aoi_at(images, ref)
        if aoi is None or 'duplicate_of' not in aoi:
            continue
        aoi.pop('duplicate_of', None)
        change.changed.append(tuple(ref))
    change.changed = _unique(change.changed)
    change.touched = list(change.changed)
    return change


def release_duplicates_of(images: Sequence[Dict[str, Any]], number: Optional[int]) -> DuplicateChange:
    """Clear every link that points at *number* (used when that AOI is deleted)."""
    if not isinstance(number, int):
        return DuplicateChange()
    refs = [(image_idx, aoi_idx)
            for image_idx, image in enumerate(images or [])
            for aoi_idx, aoi in enumerate(image.get('areas_of_interest') or [])
            if get_duplicate_of(aoi) == number]
    return clear_duplicates(images, refs)


def _unique(refs: Iterable[AOIRef]) -> List[AOIRef]:
    seen = set()
    ordered = []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            ordered.append(ref)
    return ordered


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

@dataclass
class Sighting:
    """One other image/AOI where a reported object was also detected."""
    image_name: str
    number: Optional[int]
    image_idx: int
    aoi_idx: int


def sightings_by_primary(images: Sequence[Dict[str, Any]]) -> Dict[int, List[Sighting]]:
    """
    Primary AOI number -> where its duplicates were seen.

    Built from the full image list (not a report's filtered copy), so every
    duplicate is found wherever it lives.
    """
    result = {}
    for number, refs in duplicates_by_primary(images).items():
        result[number] = [
            Sighting(image_display_name(images[image_idx]),
                     images[image_idx]['areas_of_interest'][aoi_idx].get('number'),
                     image_idx, aoi_idx)
            for image_idx, aoi_idx in refs
        ]
    return result


def sightings_for(aoi: Dict[str, Any], by_primary: Optional[Dict[int, List[Sighting]]]) -> List[Sighting]:
    """The other sightings of a reported AOI, from a sightings_by_primary map."""
    if not by_primary or not aoi:
        return []
    number = aoi.get('number')
    if not isinstance(number, int):
        return []
    return by_primary.get(number, [])


def format_sightings(sightings: Sequence[Sighting]) -> str:
    """'IMG_0043.JPG (AOI #46), IMG_0044.JPG (AOI #47)' for report text."""
    parts = []
    for sighting in sightings:
        if sighting.number is not None:
            parts.append(f"{sighting.image_name} (AOI #{sighting.number})")
        else:
            parts.append(sighting.image_name)
    return ", ".join(parts)


def sightings_line(aoi: Dict[str, Any], by_primary: Optional[Dict[int, List[Sighting]]]) -> str:
    """'Also seen in: ...' for plain-text export descriptions, or '' when none."""
    sightings = sightings_for(aoi, by_primary)
    if not sightings:
        return ""
    return f"Also seen in: {format_sightings(sightings)}"


# ---------------------------------------------------------------------------
# Picking a primary
# ---------------------------------------------------------------------------

def candidate_primaries(images: Sequence[Dict[str, Any]], exclude: Optional[AOIRef] = None) -> List[AOIRef]:
    """
    AOIs an AOI can be marked a duplicate of: flagged AOIs and AOIs that already
    have duplicates. Duplicates themselves, AOIs without a number and *exclude*
    are left out.
    """
    numbers = index_by_number(images)
    with_duplicates = set(duplicates_by_primary(images))
    candidates = []
    for image_idx, image in enumerate(images or []):
        for aoi_idx, aoi in enumerate(image.get('areas_of_interest') or []):
            if exclude is not None and (image_idx, aoi_idx) == tuple(exclude):
                continue
            number = aoi.get('number')
            if not isinstance(number, int):
                continue
            if resolve_primary(images, aoi, numbers) is not None:
                continue
            if aoi.get('flagged', False) or number in with_duplicates:
                candidates.append((image_idx, aoi_idx))
    return candidates


@dataclass
class DuplicateCandidate:
    """A possible primary for an AOI, with why it ranks where it does."""
    image_idx: int
    aoi_idx: int
    number: Optional[int]
    image_name: str
    similarity: Optional[int]      # 0-100 on the Find Similar AOIs scale, None if unreadable
    distance_m: Optional[float]    # Ground distance between the two AOIs, None if unlocated
    duplicate_count: int
    score: float


def proximity(distance_m: Optional[float]) -> float:
    """1 at 0 m, 0.5 at PROXIMITY_HALF_DISTANCE_M, falling smoothly after."""
    if distance_m is None:
        return UNKNOWN_FACTOR
    return 1.0 / (1.0 + max(0.0, distance_m) / PROXIMITY_HALF_DISTANCE_M)


def rank_candidates(images: Sequence[Dict[str, Any]], source: AOIRef, candidates: Sequence[AOIRef],
                    similarity_service=None,
                    locate_aois: Optional[Callable[[Dict[str, Any]], Sequence[Optional[LatLon]]]] = None,
                    progress_callback: Optional[Callable[[int, int], None]] = None,
                    cancel_check: Optional[Callable[[], bool]] = None) -> Optional[List[DuplicateCandidate]]:
    """
    Rank possible primaries for the *source* AOI, most likely first.

    The same object seen in overlapping images is close on the ground and looks
    alike, so each candidate scores similarity x proximity. Either factor falls
    back to UNKNOWN_FACTOR when it cannot be computed.

    Args:
        images: Viewer image dicts.
        source: The AOI being marked.
        candidates: Possible primaries (see candidate_primaries).
        similarity_service: AOISimilarityService (get_descriptor/compare), optional.
        locate_aois: callable(image) -> one (lat, lon) or None per AOI, optional.
        progress_callback: Optional callable(done, total).
        cancel_check: Optional callable returning True to abort.

    Returns:
        Ranked candidates, or None when cancelled.
    """
    source_aoi = _aoi_at(images, source)
    if source_aoi is None:
        return []

    positions_cache: Dict[int, Sequence[Optional[LatLon]]] = {}

    def position_of(image_idx, aoi_idx):
        if locate_aois is None:
            return None
        if image_idx not in positions_cache:
            try:
                positions_cache[image_idx] = locate_aois(images[image_idx]) or []
            except Exception:
                positions_cache[image_idx] = []
        positions = positions_cache[image_idx]
        position = positions[aoi_idx] if aoi_idx < len(positions) else None
        if position is None:
            return None
        lat, lon = position
        if lat is None or lon is None or not (math.isfinite(lat) and math.isfinite(lon)):
            return None
        return (lat, lon)

    def descriptor_of(image_idx, aoi):
        if similarity_service is None:
            return None
        try:
            return similarity_service.get_descriptor(images[image_idx].get('path'), aoi)
        except Exception:
            return None

    source_position = position_of(*source)
    source_descriptor = descriptor_of(source[0], source_aoi)
    counts = duplicate_counts(images)

    ranked = []
    total = len(candidates)
    for done, (image_idx, aoi_idx) in enumerate(candidates, start=1):
        if cancel_check and cancel_check():
            return None
        aoi = _aoi_at(images, (image_idx, aoi_idx))
        if aoi is None:
            continue

        similarity = None
        if source_descriptor is not None:
            descriptor = descriptor_of(image_idx, aoi)
            if descriptor is not None:
                distance = similarity_service.compare(source_descriptor, descriptor)
                similarity = int(max(0, min(100, round(100.0 * (1.0 - distance)))))

        distance_m = None
        position = position_of(image_idx, aoi_idx)
        if source_position is not None and position is not None:
            distance_m = LocationInfo.haversine_m(source_position[0], source_position[1],
                                                  position[0], position[1])

        similarity_factor = similarity / 100.0 if similarity is not None else UNKNOWN_FACTOR
        number = aoi.get('number')
        ranked.append(DuplicateCandidate(
            image_idx=image_idx,
            aoi_idx=aoi_idx,
            number=number,
            image_name=image_display_name(images[image_idx]),
            similarity=similarity,
            distance_m=distance_m,
            duplicate_count=counts.get(number, 0),
            score=similarity_factor * proximity(distance_m),
        ))
        if progress_callback:
            progress_callback(done, total)

    ranked.sort(key=lambda c: (-c.score, c.image_idx, c.aoi_idx))
    return ranked
