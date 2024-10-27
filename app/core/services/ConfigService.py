import logging
from ast import literal_eval
import xml.etree.ElementTree as ET
import json


class ConfigService:
    """Service used to parse an ADIAT Algorithm config file"""

    def __init__(self, path):
        """
                __init__ constructor for the service

        :String path: path to the config file.
                """
        with open(path) as f:
            self.config = json.load(f)

    def getAlgorithms(self):
        return self.config['algorithms']
