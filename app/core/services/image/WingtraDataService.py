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
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from core.services.LoggerService import LoggerService
from core.services.terrain.TerrainService import TerrainService

METERS_TO_FEET = 3.28084

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


def summarize_errors(errors: Sequence[str],
                     limit: int = MAX_REPORTED_ERRORS) -> str:
    """Render parse errors for display, capped so the dialog stays readable."""
    text = "\n".join(errors[:limit])
    if len(errors) > limit:
        text += f"\n... and {len(errors) - limit} more errors"
    return text
