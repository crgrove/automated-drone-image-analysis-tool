import logging
from ast import literal_eval
import xml.etree.ElementTree as ET
import json


class ConfigService:
    """Service for parsing an ADIAT Algorithm configuration file."""

    def __init__(self, path):
        """
        Initialize the ConfigService with a configuration file path.

        Args:
            path (str): Path to the configuration file in JSON format.
        """
        with open(path) as f:
            self.config = json.load(f)

    def get_algorithms(self):
        """
        Retrieve the list of algorithms from the configuration.

        Returns:
            list: A list of algorithms specified in the configuration file.
        """
        return self.config['algorithms']
