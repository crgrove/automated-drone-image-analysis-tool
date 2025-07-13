import os
import pandas as pd
import sys
import shutil


class PickleHelper:

    _drones_df = None
    _xmp_df = None

    @classmethod
    def get_drone_sensor_info(cls):
        """
        Loads and caches drone metadata lookup table.

        Returns:
            pandas.DataFrame: A DataFrame containing drone specifications.
        """
        if cls._drones_df is None:
            cls._drones_df = cls.load_drone_info_pickle()

        if cls._drones_df is not None:
            return cls._drones_df['data']
        else:
            return None

    @classmethod
    def get_drone_sensor_file_version(cls):
        """
        Get the version of the Drone Sensor File stored in the pickle

        Returns:
            Dict: version and date of the pickle file
        """
        if cls._drones_df is None:
            cls._drones_df = cls.load_drone_info_pickle()
        if cls._drones_df is not None:
            return {'Version': cls._drones_df['version'], 'Date': cls._drones_df['date']}
        else:
            return None

    @classmethod
    def get_xmp_mapping(cls):
        """
        Loads and caches XMP attribute mapping table.

        Returns:
            pandas.DataFrame: A DataFrame mapping logical attributes to XMP keys.
        """
        if cls._xmp_df is None:
            cls._xmp_df = cls.load_xmp_mapping_pickle()
        return cls._xmp_df

    @staticmethod
    def copy_pickle(file_name):
        """Copy a pickle file from the application bundle to the user data directory.

        Args:
            file_name (str): The name of the pickle file to copy.

        Raises:
            FileNotFoundError: If the source pickle file does not exist.

        Side Effects:
            Copies the specified pickle file from the application bundle (sys._MEIPASS)
            to the destination directory returned by _get_destination_path().
        """
        if getattr(sys, 'frozen', False):
            app_root = sys._MEIPASS
        else:
            app_root = os.path.abspath((os.path.dirname(os.path.dirname(__file__))))
        source = os.path.join(app_root, file_name)
        destination = os.path.join(PickleHelper._get_destination_path(), file_name)
        if not os.path.isfile(source):
            raise FileNotFoundError(f"Source pickle file does not exist: {source}")
        shutil.copy(source, destination)
        PickleHelper.force_reload()

    @staticmethod
    def load_drone_info_pickle():
        """
        Loads drone metadata from 'drones.pkl'.

        Returns:
            pandas.DataFrame: Drone info table.
        """
        file_path = os.path.join(PickleHelper._get_destination_path(), 'drones.pkl')
        if not os.path.isfile(file_path):
            PickleHelper.copy_pickle('drones.pkl')
        if os.path.isfile(file_path):
            return pd.read_pickle(file_path)
        else:
            return None  # or pd.DataFrame() if you prefer an empty table

    @staticmethod
    def load_xmp_mapping_pickle():
        """
        Loads attribute-key mapping from 'xmp.pkl'.

        Returns:
            pandas.DataFrame: Attribute-to-XMP-key map.
        """
        file_path = os.path.join(PickleHelper._get_destination_path(), 'xmp.pkl')
        if not os.path.isfile(file_path):
            PickleHelper.copy_pickle('xmp.pkl')
        if os.path.isfile(file_path):
            return pd.read_pickle(file_path)
        else:
            return None  # or pd.DataFrame() if you prefer an empty table

    @staticmethod
    def version_to_int(version_str):
        """Convert a version string to an integer for easy comparison.

        Args:
            version_str (str): The version string to convert, e.g., "1.6.0 Beta".

        Returns:
            int: An integer representation of the version, suitable for comparison.

        Raises:
            ValueError: If the version string is invalid.
        """
        major, minor, patch, label_val = PickleHelper._version_to_tuple(version_str)
        return major * 10**6 + minor * 10**4 + patch * 10**2 + label_val

    @staticmethod
    def _version_to_tuple(version_str):
        """Convert a version string to a tuple (major, minor, patch, label_value).

        Args:
            version_str (str): The version string to convert, e.g., "1.6.0 Beta".

        Returns:
            tuple: A tuple of the form (major, minor, patch, label_value).

        Raises:
            ValueError: If the version string does not match the expected format.
        """
        import re
        # Extract version numbers and optional label
        m = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:\s*(\w+))?', version_str.strip())
        if not m:
            raise ValueError(f"Invalid version string: {version_str}")

        major, minor, patch = map(int, m.group(1, 2, 3))
        label = (m.group(4) or "").lower()

        # Define label order (lower is more stable)
        label_order = {
            '': 0,        # Release
            'rc': 1,
            'beta': 2,
            'alpha': 3,
        }
        label_val = label_order.get(label, 99)  # Unknown suffixes sort last

        # Tuple can be directly compared
        return (major, minor, patch, label_val)

    @staticmethod
    def _get_destination_path():
        """Get the destination path for storing application data based on OS conventions.

        Returns:
            str: The path to the application data directory appropriate for the OS.

        Side Effects:
            Creates the directory if it does not exist.
        """
        home_path = os.path.expanduser("~")
        if sys.platform.startswith('win'):  # Windows
            app_path = os.path.join(home_path, 'AppData', 'Roaming', 'ADIAT')
        elif sys.platform == 'darwin':  # macOS
            app_path = os.path.join(home_path, 'Library', 'Application Support', 'ADIAT')
        else:  # Linux and other
            app_path = os.path.join(home_path, '.config', 'ADIAT')
        if not os.path.exists(app_path):
            os.makedirs(app_path)
        return app_path

    @classmethod
    def force_reload(cls):
        """Forces reloading of the drone metadata pickle on next access."""
        cls._drones_df = None
        cls._xmp_df = None
