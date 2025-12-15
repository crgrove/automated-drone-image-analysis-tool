import logging
from ast import literal_eval
import xml.etree.ElementTree as ET
import json


class ConfigService:
    """Service for parsing an ADIAT Algorithm configuration file.

    Provides functionality to load and parse algorithm configuration files
    in JSON format. Used to retrieve available algorithms and their settings.

    Attributes:
        config: Dictionary containing the parsed configuration data.
    """

    def __init__(self, path):
        """Initialize the ConfigService with a configuration file path.

        Args:
            path: Path to the configuration file in JSON format.
        """
        with open(path) as f:
            self.config = json.load(f)

    def get_algorithms(self):
        """Retrieve the list of algorithms from the configuration.

        Returns:
            A list of algorithm dictionaries specified in the configuration file.
            Each dictionary contains algorithm metadata and configuration.
        """
        return self.config['algorithms']
