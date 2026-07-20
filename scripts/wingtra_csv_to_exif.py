"""
wingtra_csv_to_exif.py - Embed Wingtra CSV orientation data into image EXIF/XMP metadata.

Reads a Wingtra geotags CSV file and writes DJI-compatible XMP tags into matching
image files so that ADIAT can read them without loading a CSV at runtime.

Usage:
    python wingtra_csv_to_exif.py <csv_file> <image_directory> [--output-dir <dir>] [--agl <meters>] [--terrain-agl]

Arguments:
    csv_file         Path to Wingtra geotags CSV file
    image_directory  Directory containing Wingtra image files
    --output-dir     Write modified images to this directory instead of modifying originals
    --agl            Above-ground-level altitude in meters (written as RelativeAltitude)
    --terrain-agl    Compute per-image AGL from terrain elevation data
"""

import argparse
import csv
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class WingtraImageData:
    """Parsed orientation and position data for a single Wingtra image."""
    image_name: str
    latitude: float
    longitude: float
    altitude_asl: float  # meters
    omega: float         # roll (degrees)
    phi: float           # pitch (degrees)
    kappa: float         # yaw (degrees)
    accuracy_h: float
    accuracy_v: float


# Column name aliases matching WingtraDataController conventions
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

REQUIRED_COLUMNS = ['image', 'latitude', 'longitude', 'altitude', 'omega', 'phi', 'kappa']


def find_exiftool():
    """Locate exiftool executable."""
    # Check if bundled with ADIAT
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.dirname(script_dir)
    bundled = os.path.join(app_root, 'app', 'external', 'exiftool.exe')
    if os.path.exists(bundled):
        return bundled

    # Check PATH
    try:
        result = subprocess.run(['exiftool', '-ver'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'exiftool'
    except FileNotFoundError:
        pass

    return None


def build_column_map(fieldnames):
    """Map actual CSV column headers to expected column names."""
    column_map = {}
    lower_fields = {f.lower().strip(): f for f in fieldnames}

    for expected, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_fields:
                column_map[expected] = lower_fields[alias.lower()]
                break

    return column_map


def parse_csv(csv_path):
    """Parse Wingtra geotags CSV file.

    Returns:
        tuple: (dict of image_name -> WingtraImageData, list of errors)
    """
    parsed = {}
    errors = []

    try:
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                return {}, ["CSV file has no header row"]

            column_map = build_column_map(reader.fieldnames)
            missing = [col for col in REQUIRED_COLUMNS if col not in column_map]
            if missing:
                return {}, [f"Missing required columns: {', '.join(missing)}"]

            for row_num, row in enumerate(reader, start=2):
                try:
                    image_name = row[column_map['image']].strip()
                    if not image_name:
                        continue

                    accuracy_h = 0.0
                    accuracy_v = 0.0
                    if 'accuracy_h' in column_map:
                        try:
                            accuracy_h = float(row[column_map['accuracy_h']])
                        except (ValueError, KeyError):
                            pass
                    if 'accuracy_v' in column_map:
                        try:
                            accuracy_v = float(row[column_map['accuracy_v']])
                        except (ValueError, KeyError):
                            pass

                    data = WingtraImageData(
                        image_name=image_name,
                        latitude=float(row[column_map['latitude']]),
                        longitude=float(row[column_map['longitude']]),
                        altitude_asl=float(row[column_map['altitude']]),
                        omega=float(row[column_map['omega']]),
                        phi=float(row[column_map['phi']]),
                        kappa=float(row[column_map['kappa']]),
                        accuracy_h=accuracy_h,
                        accuracy_v=accuracy_v
                    )
                    parsed[image_name] = data
                except (ValueError, KeyError) as e:
                    errors.append(f"Row {row_num}: {e}")

    except FileNotFoundError:
        errors.append(f"File not found: {csv_path}")
    except Exception as e:
        errors.append(f"Error reading CSV: {e}")

    return parsed, errors


def normalize_yaw(kappa):
    """Convert photogrammetric kappa (CCW) to geographic bearing (CW from North).

    Kappa: 0=North, positive=CCW (photogrammetric right-hand rule)
    Bearing: 0=North, positive=CW (geographic/DJI convention)
    """
    yaw = (-kappa) % 360
    return yaw


def convert_pitch(phi):
    """Convert Wingtra phi (0=nadir) to DJI convention (-90=nadir).

    Wingtra: 0 degrees = camera pointing straight down (nadir)
    DJI: -90 degrees = camera pointing straight down (nadir)
    """
    return phi - 90.0


def write_tags(exiftool_path, image_path, data, agl_meters=None):
    """Write DJI-compatible XMP and EXIF tags to an image using exiftool.

    Args:
        exiftool_path: Path to exiftool executable.
        image_path: Path to image file.
        data: WingtraImageData for this image.
        agl_meters: Optional above-ground-level altitude in meters.

    Returns:
        bool: True if successful.
    """
    yaw = normalize_yaw(data.kappa)
    pitch = convert_pitch(data.phi)
    roll = data.omega

    args = [
        exiftool_path,
        '-overwrite_original',
        # DJI XMP orientation tags
        f'-XMP-drone-dji:GimbalYawDegree={yaw:.2f}',
        f'-XMP-drone-dji:GimbalPitchDegree={pitch:.2f}',
        f'-XMP-drone-dji:GimbalRollDegree={roll:.2f}',
        f'-XMP-drone-dji:FlightYawDegree={yaw:.2f}',
        f'-XMP-drone-dji:FlightPitchDegree={pitch:.2f}',
        f'-XMP-drone-dji:FlightRollDegree={roll:.2f}',
        f'-XMP-drone-dji:AbsoluteAltitude={data.altitude_asl:.2f}',
        # Update GPS from post-processed CSV values
        f'-GPSLatitude={abs(data.latitude):.10f}',
        f'-GPSLatitudeRef={"N" if data.latitude >= 0 else "S"}',
        f'-GPSLongitude={abs(data.longitude):.10f}',
        f'-GPSLongitudeRef={"E" if data.longitude >= 0 else "W"}',
        f'-GPSAltitude={data.altitude_asl:.2f}',
        '-GPSAltitudeRef=0',
        # Set Make to DJI so ADIAT recognizes the XMP namespace
        '-Make=DJI',
    ]

    if agl_meters is not None:
        args.append(f'-XMP-drone-dji:RelativeAltitude={agl_meters:.2f}')

    args.append(image_path)

    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
        return False
    return True


def compute_terrain_agl(parsed_data):
    """Compute per-image AGL using terrain elevation lookup.

    For each image: AGL = ASL altitude - geoid undulation - terrain elevation
    Same logic as WingtraDataController._compute_agl_for_images().

    Returns:
        dict of image_name -> agl_meters
    """
    # Add app directory to path for TerrainService import
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, '..', 'app')
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)

    from core.services.terrain.TerrainService import TerrainService

    terrain = TerrainService()
    agls = {}

    for name, data in parsed_data.items():
        result = terrain.get_elevation(data.latitude, data.longitude)
        if result.source == 'terrain' and result.elevation_m is not None:
            asl_orthometric = data.altitude_asl
            if result.geoid_undulation_m is not None:
                asl_orthometric -= result.geoid_undulation_m
            agls[name] = max(1.0, asl_orthometric - result.elevation_m)

    return agls


def main():
    parser = argparse.ArgumentParser(
        description='Embed Wingtra CSV orientation data into image EXIF/XMP metadata.'
    )
    parser.add_argument('csv_file', help='Path to Wingtra geotags CSV file')
    parser.add_argument('image_directory', help='Directory containing Wingtra image files')
    parser.add_argument('--output-dir', help='Write modified images here instead of modifying originals')
    parser.add_argument('--agl', type=float, help='Above-ground-level altitude in meters (RelativeAltitude)')
    parser.add_argument('--terrain-agl', action='store_true',
                        help='Compute per-image AGL from terrain elevation data')
    args = parser.parse_args()

    # Validate inputs
    if not os.path.isfile(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)
    if not os.path.isdir(args.image_directory):
        print(f"Error: Image directory not found: {args.image_directory}")
        sys.exit(1)

    # Find exiftool
    exiftool_path = find_exiftool()
    if not exiftool_path:
        print("Error: exiftool not found. Install exiftool or ensure it's in the ADIAT external directory.")
        sys.exit(1)
    print(f"Using exiftool: {exiftool_path}")

    # Parse CSV
    print(f"Parsing CSV: {args.csv_file}")
    parsed, errors = parse_csv(args.csv_file)
    if errors:
        print("CSV parse errors:")
        for err in errors[:10]:
            print(f"  {err}")
        if not parsed:
            sys.exit(1)
    print(f"  Parsed {len(parsed)} image entries from CSV")

    # Compute per-image terrain AGL if requested
    terrain_agls = {}
    if args.terrain_agl:
        print("Computing per-image terrain AGL...")
        terrain_agls = compute_terrain_agl(parsed)
        print(f"  Computed AGL for {len(terrain_agls)}/{len(parsed)} images")

    # Find matching images in directory
    image_files = {}
    for f in os.listdir(args.image_directory):
        if f.lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff', '.png')):
            image_files[f] = os.path.join(args.image_directory, f)
            image_files[f.lower()] = os.path.join(args.image_directory, f)

    matched = 0
    unmatched = 0
    failed = 0

    # Set up output directory if specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Output directory: {args.output_dir}")

    print("\nProcessing images...")
    for image_name, data in parsed.items():
        # Try exact match, then case-insensitive
        src_path = image_files.get(image_name) or image_files.get(image_name.lower())
        if not src_path:
            unmatched += 1
            continue

        # Determine target path
        if args.output_dir:
            target_path = os.path.join(args.output_dir, os.path.basename(src_path))
            shutil.copy2(src_path, target_path)
        else:
            target_path = src_path

        # Determine AGL: --agl overrides terrain-agl per-image values
        if args.agl is not None:
            agl = args.agl
        else:
            agl = terrain_agls.get(image_name)

        yaw = normalize_yaw(data.kappa)
        pitch = convert_pitch(data.phi)
        agl_str = f" agl={agl:.1f}m" if agl is not None else ""
        print(f"  {image_name}: yaw={yaw:.1f}° pitch={pitch:.1f}° alt={data.altitude_asl:.1f}m{agl_str}")

        if write_tags(exiftool_path, target_path, data, agl):
            matched += 1
        else:
            failed += 1

    # Summary
    print("\nSummary:")
    print(f"  Modified: {matched}")
    print(f"  Not found in directory: {unmatched}")
    if failed:
        print(f"  Failed: {failed}")
    print(f"  Total CSV entries: {len(parsed)}")


if __name__ == '__main__':
    main()
