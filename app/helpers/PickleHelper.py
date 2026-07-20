"""Loader for the drone-sensor and XMP-attribute lookup tables.

Despite the legacy class name, the data is stored as plain CSV with two
header-comment lines carrying the file version and last-edit date:

    # version: 1.2.0
    # date: 2026-05-04
    Manufacturer,Model,Model (Exif),...
    DJI,...

CSV was chosen over pickle so the files diff cleanly in git, can be edited
in any tool, and don't carry pandas/numpy version coupling.
"""

import os
import sys
import re
import shutil

import pandas as pd


class PickleHelper:

    _drones_df = None
    _xmp_df = None

    @classmethod
    def get_drone_sensor_info(cls):
        """Returns the drone-spec DataFrame (cached)."""
        if cls._drones_df is None:
            cls._drones_df = cls.load_drone_info_pickle()

        if cls._drones_df is not None:
            return cls._drones_df['data']
        return None

    @classmethod
    def get_drone_sensor_file_version(cls):
        """Returns {'Version': str, 'Date': str} for the current drone-spec file."""
        if cls._drones_df is None:
            cls._drones_df = cls.load_drone_info_pickle()
        if cls._drones_df is not None:
            return {'Version': cls._drones_df['version'], 'Date': cls._drones_df['date']}
        return None

    @classmethod
    def get_xmp_mapping(cls):
        """Returns the attribute→XMP-key mapping DataFrame (cached)."""
        if cls._xmp_df is None:
            cls._xmp_df = cls.load_xmp_mapping_pickle()
        if cls._xmp_df is not None:
            return cls._xmp_df['data']
        return None

    @staticmethod
    def copy_pickle(file_name):
        """Copy a bundled data file (e.g. 'drones.csv') into the user data directory."""
        source = os.path.join(PickleHelper._bundled_root(), file_name)
        destination = os.path.join(PickleHelper._get_destination_path(), file_name)
        if not os.path.isfile(source):
            raise FileNotFoundError(f"Source data file does not exist: {source}")
        shutil.copy(source, destination)
        PickleHelper.force_reload()

    @staticmethod
    def load_drone_info_pickle():
        """Loads the drone-spec table from drones.csv and returns
        {'version': str, 'date': str, 'data': DataFrame}, or None on failure."""
        return PickleHelper._load_csv_with_meta('drones.csv')

    @staticmethod
    def load_xmp_mapping_pickle():
        """Loads the XMP-attribute mapping from xmp.csv and returns
        {'version': str, 'date': str, 'data': DataFrame}, or None on failure.

        Falls back to a minimal mapping if both the user-data and bundled
        files are unavailable so the app still starts."""
        result = PickleHelper._load_csv_with_meta('xmp.csv')
        if result is not None:
            return result
        # Defensive fallback so MetaDataHelper can still resolve the
        # core drone-dji attributes if the data files are missing entirely.
        return {
            'version': '0.0.0',
            'date': '',
            'data': pd.DataFrame({
                'Attribute': ['Flight Yaw', 'Flight Pitch', 'Flight Roll',
                              'Gimbal Yaw', 'Gimbal Pitch', 'Gimbal Roll',
                              'Relative Altitude'],
                'DJI': ['drone-dji:FlightYawDegree', 'drone-dji:FlightPitchDegree',
                        'drone-dji:FlightRollDegree', 'drone-dji:GimbalYawDegree',
                        'drone-dji:GimbalPitchDegree', 'drone-dji:GimbalRollDegree',
                        'drone-dji:RelativeAltitude']
            })
        }

    @staticmethod
    def _load_csv_with_meta(file_name):
        """Resolve a data file in the user data dir, copy/refresh from the
        bundle as needed, parse it, and return {'version','date','data'}."""
        dest_path = os.path.join(PickleHelper._get_destination_path(), file_name)
        if not os.path.isfile(dest_path):
            try:
                PickleHelper.copy_pickle(file_name)
            except FileNotFoundError:
                return None
        else:
            # A user who installed an older build keeps the stale copy
            # forever otherwise — silently breaks any row added in a new
            # revision (e.g. the WALDO Canon EOS 5DS R sensor).
            PickleHelper._refresh_if_bundle_newer(file_name, dest_path)

        if not os.path.isfile(dest_path):
            return None

        try:
            version, date = PickleHelper._read_meta_header(dest_path)
            df = pd.read_csv(dest_path, comment='#')
        except Exception:
            return None
        return {'version': version, 'date': date, 'data': df}

    @staticmethod
    def _read_meta_header(path):
        """Read leading `# key: value` comment lines and return (version, date).

        Stops at the first non-comment, non-blank line so it doesn't scan
        the whole file. Missing fields default to empty strings so callers
        can still use string equality without None checks.
        """
        version, date = '', ''
        with open(path, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                if not line.startswith('#'):
                    break
                m = re.match(r'^#\s*(version|date)\s*:\s*(.+?)\s*$', line, re.IGNORECASE)
                if m:
                    key = m.group(1).lower()
                    # A spreadsheet re-save (Excel/Sheets/Calc) pads every row,
                    # including these comment lines, with trailing commas to
                    # match the data columns. Strip them so the value stays clean.
                    value = m.group(2).rstrip(', \t')
                    if key == 'version':
                        version = value
                    elif key == 'date':
                        date = value
        return version, date

    @staticmethod
    def _refresh_if_bundle_newer(file_name, current_path):
        """Re-copy `file_name` from the app bundle into the user data dir
        when the bundled copy advertises a newer 'version' header. Failures
        are swallowed so a corrupt bundle never blocks startup."""
        source = os.path.join(PickleHelper._bundled_root(), file_name)
        if not os.path.isfile(source):
            return

        try:
            bundle_version, _ = PickleHelper._read_meta_header(source)
            current_version, _ = PickleHelper._read_meta_header(current_path)
        except Exception:
            return

        if not bundle_version or not current_version:
            return

        try:
            if PickleHelper.version_to_int(bundle_version) > PickleHelper.version_to_int(current_version):
                shutil.copy(source, current_path)
                PickleHelper.force_reload()
        except (ValueError, OSError):
            return

    @staticmethod
    def _bundled_root():
        """Directory that ships with the application (frozen build vs. source tree)."""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    @staticmethod
    def version_to_int(version_str):
        """Convert a version string like '1.6.0 Beta 3' to a comparable integer."""
        major, minor, patch, label_val, build = PickleHelper._version_to_tuple(version_str)
        # Build is capped to two digits so it occupies the least-significant slot
        # without overflowing into the label field.
        build = min(build, 99)
        return major * 10**8 + minor * 10**6 + patch * 10**4 + label_val * 10**2 + build

    @staticmethod
    def _version_to_tuple(version_str):
        """Convert a version string to (major, minor, patch, label_value, build).

        Supports an optional pre-release label and an optional trailing build
        number, e.g. '2.1.0', '2.1.0 Beta', or '2.1.0 Beta 5'. Strings without
        a build number yield build 0 for backward compatibility.
        """
        m = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:\s*([A-Za-z]+))?(?:\s*(\d+))?', version_str.strip())
        if not m:
            raise ValueError(f"Invalid version string: {version_str}")

        major, minor, patch = map(int, m.group(1, 2, 3))
        label = (m.group(4) or "").lower()
        build = int(m.group(5)) if m.group(5) else 0

        # Lower label_val == more stable. Unknown suffixes sort last.
        label_order = {
            '': 0,        # Release
            'rc': 1,
            'beta': 2,
            'alpha': 3,
        }
        label_val = label_order.get(label, 99)

        return (major, minor, patch, label_val, build)

    @staticmethod
    def _get_destination_path():
        """Return (and create) the OS-appropriate user data directory."""
        home_path = os.path.expanduser("~")
        if sys.platform.startswith('win'):
            app_path = os.path.join(home_path, 'AppData', 'Roaming', 'ADIAT')
        elif sys.platform == 'darwin':
            app_path = os.path.join(home_path, 'Library', 'Application Support', 'ADIAT')
        else:
            app_path = os.path.join(home_path, '.config', 'ADIAT')
        if not os.path.exists(app_path):
            os.makedirs(app_path)
        return app_path

    @classmethod
    def force_reload(cls):
        """Clear cached DataFrames so the next access re-reads from disk."""
        cls._drones_df = None
        cls._xmp_df = None
