"""Reading a Wingtra photogrammetry CSV, and turning it into per-image data.

A Wingtra flight exports one CSV row per photo: position, absolute altitude,
and the omega/phi/kappa orientation triple. ADIAT reads it to override the
bearing and altitude it would otherwise infer from EXIF.

Parsing that file, matching its filenames against the loaded results and
turning its absolute altitudes into heights above the ground is business
logic and I/O; it lived in ``WingtraDataController`` beside the dialogs that
report the outcome (CLAUDE.md 2.1). What stays in the controller is the file
prompt, the summary dialog, and writing the results into the viewer's image
dicts.

**The altitude is the part to be careful with.** The CSV's ``altitude`` is
absolute and, for Wingtra, ellipsoidal; the terrain service answers in
orthometric metres. Differencing them directly overstates height above the
ground by the local geoid separation - -20 to -30 m across CONUS, in the one
direction an AGL must never err in - so the geoid undulation is subtracted
first wherever the terrain service reports one. The result is a genuine
terrain-referenced **AGL**, never an ATO (CLAUDE.md 2.11).
"""

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import Image

from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.terrain.TerrainService import TerrainService

METERS_TO_FEET = 3.28084

# EXIF Make written by Wingtra's own payloads (RGB61). The older WingtraOne
# payload is a stock Sony RX1R II and says SONY, so the make alone cannot
# rule an image out - a geotags CSV naming it is the stronger evidence.
WINGTRA_MAKE = 'WINGTRA'

# EXIF tag 271 (Make). Read through PIL rather than piexif: piexif drops the
# last byte of every ASCII tag, which corrupts the unterminated strings
# Wingtra payloads write.
_EXIF_MAKE_TAG = 271

# How a results file was linked to a geotags CSV, persisted in
# ADIAT_Data.xml so reopening the results neither re-asks nor forgets.
GEOTAGS_LOADED = 'loaded'
GEOTAGS_DECLINED = 'declined'

REQUIRED_COLUMNS = [
    'image', 'latitude', 'longitude', 'altitude',
    'omega', 'phi', 'kappa'
]

# Alternate column name mappings (case-insensitive, supports partial matches).
# Wingtra format: "# image name", "latitude [decimal degrees]", etc.
COLUMN_ALIASES = {
    'image': ['# image name', 'image name', 'image', 'image_name', 'filename', 'name', 'file'],
    'latitude': ['latitude [decimal degrees]', 'latitude', 'lat'],
    'longitude': ['longitude [decimal degrees]', 'longitude', 'lon', 'long'],
    'altitude': ['altitude [meter]', 'altitude [meters]', 'altitude', 'altitude_asl', 'alt', 'elevation'],
    'omega': ['omega [degrees]', 'omega [degree]', 'omega', 'roll'],
    'phi': ['phi [degrees]', 'phi [degree]', 'phi', 'pitch'],
    'kappa': ['kappa [degrees]', 'kappa [degree]', 'kappa', 'yaw', 'heading'],
    'accuracy_h': ['accuracy horizontal [meter]', 'accuracy horizontal [meters]',
                   'accuracy_h', 'accuracy_horizontal', 'h_accuracy', 'horizontal_accuracy'],
    'accuracy_v': ['accuracy vertical [meter]', 'accuracy vertical [meters]',
                   'accuracy_v', 'accuracy_vertical', 'v_accuracy', 'vertical_accuracy']
}

# Errors beyond this many are summarised rather than listed; a malformed
# export produces one per row and the operator only needs the shape of it.
MAX_REPORTED_ERRORS = 10

_terrain_service: Optional[TerrainService] = None
_terrain_attempted = False


@dataclass
class WingtraImageData:
    """Wingtra orientation and position data for a single image."""
    image_name: str
    latitude: float
    longitude: float
    altitude_asl: float  # meters (above sea level, from CSV)
    omega: float         # roll (degrees)
    phi: float           # pitch (degrees)
    kappa: float         # yaw (degrees)
    accuracy_h: float
    accuracy_v: float
    altitude_agl: Optional[float] = field(default=None)  # meters (computed)


@dataclass
class WingtraCsvCandidate:
    """A CSV near the source imagery that is shaped like Wingtra geotags and
    names at least one of the loaded results."""
    path: str
    row_count: int       # image rows in the CSV
    matched_count: int   # result images the CSV names


def wingtra_agl_ft(image: Optional[dict]) -> Optional[float]:
    """The per-image AGL a loaded geotags CSV wrote into *image*, in feet, or
    None when there is none (not Wingtra, no CSV, or no DEM answer)."""
    if not image:
        return None
    agl_ft = image.get('wingtra_agl_ft')
    if agl_ft is not None and agl_ft > 0:
        return agl_ft
    return None


def resolve_altitude_ft(image: Optional[dict], override_ft: Optional[float]) -> Optional[float]:
    """The altitude, in feet above the ground, to size *image* with.

    The operator override wins, as it does everywhere; otherwise the image's
    Wingtra per-image AGL. Wingtra imagery carries no RelativeAltitude, so
    without this fallback it has no GSD, no footprint and no AOI position.
    The order matches AOI geolocation in the GPS map, so every surface
    agrees on where an AOI is and how big it is.

    Returns:
        Feet, or None to let the image's own metadata decide.
    """
    if override_ft is not None and override_ft > 0:
        return override_ft
    return wingtra_agl_ft(image)


def get_terrain_service(logger=None) -> Optional[TerrainService]:
    """The shared terrain service, or None when it cannot be constructed.

    A module-level lazy singleton, mirroring
    :mod:`core.services.image.AOIService`. Construction is attempted once: a
    missing DEM cache fails the same way every time, and retrying per call
    turns one warning into one per image.
    """
    global _terrain_service, _terrain_attempted
    if _terrain_service is None and not _terrain_attempted:
        _terrain_attempted = True
        try:
            _terrain_service = TerrainService()
        except Exception as e:  # noqa: BLE001 - terrain is optional
            (logger or LoggerService()).warning(
                f"Could not initialize terrain service: {e}")
    return _terrain_service


def kappa_to_bearing(kappa: float) -> float:
    """Convert Wingtra's kappa to a geographic bearing.

    Kappa is counter-clockwise in the photogrammetric convention; a bearing
    is clockwise from north. One function, because getting it the wrong way
    round mirrors every heading through north and the two conventions agree
    at 0 and 180.
    """
    return (-float(kappa)) % 360


def build_column_map(fieldnames: Sequence[str]) -> Dict[str, str]:
    """Map ADIAT's field names onto whatever headers this export used."""
    column_map = {}
    lower_fields = {f.lower().strip(): f for f in fieldnames}

    for expected, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_fields:
                column_map[expected] = lower_fields[alias.lower()]
                break

    return column_map


def parse_wingtra_csv(file_path: str) -> Tuple[Dict[str, WingtraImageData], List[str]]:
    """Read a Wingtra CSV.

    A row that cannot be parsed is reported and skipped rather than failing
    the file: one truncated line at the end of an export must not cost the
    operator the rest of the flight.

    Returns:
        tuple: ``(data keyed by image filename, error strings)``. A non-empty
        error list beside an empty dict means the file was rejected outright
        - no header, or a required column missing.
    """
    parsed_data: Dict[str, WingtraImageData] = {}
    errors: List[str] = []

    try:
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as handle:
            reader = csv.DictReader(handle)

            if not reader.fieldnames:
                errors.append("CSV file has no header row")
                return {}, errors

            column_map = build_column_map(reader.fieldnames)

            missing = [col for col in REQUIRED_COLUMNS if col not in column_map]
            if missing:
                errors.append(f"Missing required columns: {', '.join(missing)}")
                return {}, errors

            for row_num, row in enumerate(reader, start=2):
                try:
                    image_name = row[column_map['image']].strip()
                    if not image_name:
                        continue

                    # Accuracy columns are optional; a missing or
                    # unparseable one is not worth losing the row over.
                    accuracy_h = 0.0
                    accuracy_v = 0.0
                    if 'accuracy_h' in column_map:
                        try:
                            accuracy_h = float(row[column_map['accuracy_h']])
                        except (ValueError, KeyError, TypeError):
                            pass
                    if 'accuracy_v' in column_map:
                        try:
                            accuracy_v = float(row[column_map['accuracy_v']])
                        except (ValueError, KeyError, TypeError):
                            pass

                    parsed_data[image_name] = WingtraImageData(
                        image_name=image_name,
                        latitude=float(row[column_map['latitude']]),
                        longitude=float(row[column_map['longitude']]),
                        altitude_asl=float(row[column_map['altitude']]),
                        omega=float(row[column_map['omega']]),
                        phi=float(row[column_map['phi']]),
                        kappa=float(row[column_map['kappa']]),
                        accuracy_h=accuracy_h,
                        accuracy_v=accuracy_v,
                    )

                except (ValueError, KeyError, TypeError) as e:
                    errors.append(f"Row {row_num}: {str(e)}")

    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
    except Exception as e:  # noqa: BLE001 - surfaced to the operator
        errors.append(f"Error reading CSV: {str(e)}")

    return parsed_data, errors


def match_image_names(
    parsed: Dict[str, WingtraImageData],
    image_names: Sequence[str],
) -> Tuple[Dict[str, WingtraImageData], List[str], List[str]]:
    """Pair CSV rows with loaded result images by filename.

    Exact match first, then case-insensitive: the CSV and the image folder
    come from different tools and disagree on case often enough to matter,
    but an exact match must never lose to a case-folded one.

    Args:
        parsed: Rows from :func:`parse_wingtra_csv`.
        image_names: Filenames of the loaded results.

    Returns:
        tuple: ``(matched keyed by *result* image name, unmatched CSV names,
        unmatched result names)``. The two unmatched lists are what the
        operator needs when nothing lines up.
    """
    result_names = set()
    result_name_map = {}          # lowercase -> original
    for name in image_names:
        if name:
            result_names.add(name)
            result_name_map[name.lower()] = name

    matched: Dict[str, WingtraImageData] = {}
    matched_csv_names = set()
    for csv_name, data in parsed.items():
        if csv_name in result_names:
            matched[csv_name] = data
            matched_csv_names.add(csv_name)
        else:
            result_name = result_name_map.get(csv_name.lower())
            if result_name is not None:
                matched[result_name] = data
                matched_csv_names.add(csv_name)

    unmatched_csv = [name for name in parsed if name not in matched_csv_names]
    unmatched_images = [name for name in result_names if name not in matched]

    return matched, unmatched_csv, unmatched_images


def read_csv_image_names(file_path: str) -> Optional[List[str]]:
    """The image-name column of a Wingtra-shaped CSV.

    Only the header and one column are looked at, so screening every CSV in
    a folder stays cheap; the full parse waits until the operator agrees to
    load the file.

    Returns:
        The image names, or None when the file is unreadable or lacks any
        column :func:`parse_wingtra_csv` requires.
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                return None
            column_map = build_column_map(reader.fieldnames)
            if any(col not in column_map for col in REQUIRED_COLUMNS):
                return None
            image_column = column_map['image']
            names = []
            for row in reader:
                name = (row.get(image_column) or '').strip()
                if name:
                    names.append(name)
            return names
    except (OSError, UnicodeDecodeError, csv.Error):
        return None


def candidate_folders(image_paths: Sequence[str]) -> List[str]:
    """Where a geotags CSV for these images would plausibly be.

    Each source image's folder, then that folder's parent: WingtraHub exports
    the CSV beside the photos, but operators often move the photos into a
    subfolder before processing. Duplicates are dropped, first sighting kept.
    """
    folders = []
    seen = set()
    for image_path in image_paths:
        folder = os.path.dirname(os.path.abspath(image_path))
        for candidate in (folder, os.path.dirname(folder)):
            key = os.path.normcase(candidate)
            if candidate and key not in seen:
                seen.add(key)
                folders.append(candidate)
    return folders


def find_wingtra_csvs(image_paths: Sequence[str],
                      image_names: Sequence[str]) -> List[WingtraCsvCandidate]:
    """Geotags CSVs near the source imagery that name the loaded results.

    A CSV qualifies only when it has every required Wingtra column *and*
    names at least one result image (case-insensitively, as
    :func:`match_image_names` does), so an unrelated CSV in the same folder
    is never offered.

    Args:
        image_paths: Full paths of the result images' source files.
        image_names: Filenames of the loaded results.

    Returns:
        Candidates, the one naming the most result images first.
    """
    result_names = {name.lower() for name in image_names if name}
    candidates = []
    seen = set()
    for folder in candidate_folders(image_paths):
        try:
            entries = sorted(os.listdir(folder))
        except OSError:
            continue
        for entry in entries:
            if not entry.lower().endswith('.csv'):
                continue
            path = os.path.join(folder, entry)
            key = os.path.normcase(os.path.abspath(path))
            if key in seen or not os.path.isfile(path):
                continue
            seen.add(key)

            names = read_csv_image_names(path)
            if not names:
                continue
            matched_count = len({name.lower() for name in names} & result_names)
            if matched_count > 0:
                candidates.append(WingtraCsvCandidate(
                    path=path, row_count=len(names), matched_count=matched_count))

    candidates.sort(key=lambda c: (-c.matched_count, c.path.lower()))
    return candidates


def is_wingtra_image(image_path: str) -> bool:
    """True when the image's EXIF Make says it came from a Wingtra payload."""
    try:
        with Image.open(image_path) as image:
            make = image.getexif().get(_EXIF_MAKE_TAG)
    except Exception:  # noqa: BLE001 - unreadable just means "not known to be Wingtra"
        return False
    if isinstance(make, bytes):
        make = make.decode('utf-8', errors='ignore')
    if not make:
        return False
    return make.strip().rstrip('\x00').upper() == WINGTRA_MAKE


def compute_agl(image_data: Dict[str, WingtraImageData],
                terrain_service=None, logger=None) -> int:
    """Fill in each image's AGL from the terrain beneath it, in place.

    ``AGL = orthometric absolute altitude - terrain elevation``. The CSV's
    altitude is ellipsoidal, so the geoid undulation comes off first wherever
    the terrain service reports one; skipping that overstates height above
    the ground by the local geoid separation, which is the one direction an
    AGL must never err in (CLAUDE.md 2.11).

    Args:
        image_data: Rows to annotate. ``altitude_agl`` is set on each one the
            terrain service could answer for, and left alone otherwise.
        terrain_service: Injectable for tests; the shared one otherwise.
        logger: Optional logger.

    Returns:
        int: How many images got an AGL. Zero is a normal outcome - no DEM
        coverage, or no terrain service at all.
    """
    terrain = (terrain_service if terrain_service is not None
               else get_terrain_service(logger))
    if terrain is None:
        return 0

    computed = 0
    for data in image_data.values():
        result = terrain.get_elevation(data.latitude, data.longitude)
        if result.source == 'terrain' and result.elevation_m is not None:
            asl_orthometric = data.altitude_asl
            if result.geoid_undulation_m is not None:
                asl_orthometric = data.altitude_asl - result.geoid_undulation_m

            # Floored at 1 m: an aircraft cannot be below ground, and a small
            # negative is DEM resolution error rather than a subterranean
            # flight.
            data.altitude_agl = max(1.0, asl_orthometric - result.elevation_m)
            computed += 1

    return computed


def apply_geotag(image: dict, data: WingtraImageData):
    """Write one geotags row into an image dict, in the fields every consumer
    reads: ``bearing`` (rotation, footprints, AOI positions) and
    ``wingtra_agl_ft`` (GSD and AOI positions, via :func:`resolve_altitude_ft`).
    """
    image['bearing'] = kappa_to_bearing(data.kappa)
    if data.altitude_agl is not None:
        image['wingtra_agl_ft'] = data.altitude_agl * METERS_TO_FEET


def resolve_geotags_csv(link: Optional[dict], image_paths: Sequence[str],
                        image_names: Sequence[str]) -> Optional[str]:
    """The geotags CSV a results file should use, decided without asking.

    The viewer's order (``WingtraDataController.auto_load_on_open``) minus its
    prompts, for exports that never open a viewer: an operator's decline
    stands; a CSV they loaded is used while it is still there; otherwise the
    geotags CSV beside the images that names the most of them - the one the
    viewer would offer first.

    Args:
        link: ``XmlService.get_wingtra_geotags()`` for the results, or None.
        image_paths: Full paths of the result images.
        image_names: Their filenames.

    Returns:
        The CSV path, or None when there is none to use.
    """
    if link is not None:
        if link.get('status') == GEOTAGS_DECLINED:
            return None
        csv_path = link.get('csv_path', '')
        if link.get('status') == GEOTAGS_LOADED and csv_path and os.path.isfile(csv_path):
            return csv_path
        # A linked CSV that has since moved falls through to a fresh search.
    candidates = find_wingtra_csvs(image_paths, image_names)
    return candidates[0].path if candidates else None


def attach_geotags(images: Sequence[dict], link: Optional[dict],
                   terrain_service=None, logger=None) -> Optional[str]:
    """Apply a results file's Wingtra geotags to its image dicts, unprompted.

    Wingtra imagery carries no altitude or heading of its own; the viewer
    reads both from the geotags CSV when the results open. A collation of
    several results files never opens a viewer, so without this its Wingtra
    AOIs had no position but the camera's and its report had no GSD. Images
    are matched by file name, so dicts renamed for display still match.

    Args:
        images: Result image dicts, updated in place.
        link: ``XmlService.get_wingtra_geotags()`` for the results, or None.
        terrain_service: For the AGL lookups; one is built when None. Pass
            one per thread - its geoid transformer is PROJ state, and PROJ
            contexts are thread-affine (see TelemetryEnrichmentService).
        logger: Optional logger.

    Returns:
        The CSV applied, or None when there was none or it was unusable.
    """
    logger = logger or LoggerService()
    image_paths = [image['path'] for image in images if image.get('path')]
    if not image_paths:
        return None
    image_names = [os.path.basename(path) for path in image_paths]
    csv_path = resolve_geotags_csv(link, image_paths, image_names)
    if csv_path is None:
        return None

    parsed, errors = parse_wingtra_csv(csv_path)
    if errors:
        # The viewer refuses such a file so the operator can fix it; nobody
        # sees this path, and a truncated last line must not cost the flight.
        logger.warning(f"Wingtra geotags {csv_path}: rows skipped:\n{summarize_errors(errors)}")
    if not parsed:
        logger.warning(f"Wingtra geotags {csv_path} not applied: no usable rows")
        return None
    matched, _, _ = match_image_names(parsed, image_names)
    if not matched:
        return None

    if terrain_service is None:
        # Geoid kept on: the CSV altitude is ellipsoidal, and without the
        # undulation the AGL is overstated - the one direction it must never
        # err in. Built here so it lives on the calling thread.
        terrain_service = TerrainService(settings_service=SettingsService())
    computed = compute_agl(matched, terrain_service=terrain_service, logger=logger)

    for image in images:
        data = matched.get(os.path.basename(image.get('path', '')))
        if data is not None:
            apply_geotag(image, data)
    logger.info(
        f"Wingtra geotags {csv_path} applied: {len(matched)} images matched, "
        f"{computed} AGL computed")
    return csv_path


def summarize_errors(errors: Sequence[str],
                     limit: int = MAX_REPORTED_ERRORS) -> str:
    """Render parse errors for display, capped so the dialog stays readable."""
    text = "\n".join(errors[:limit])
    if len(errors) > limit:
        text += f"\n... and {len(errors) - limit} more errors"
    return text
