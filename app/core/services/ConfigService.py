import logging
from ast import literal_eval
from importlib import import_module
import xml.etree.ElementTree as ET
import json

# Legacy misspelling that reached shipped configs and saved results files.
# Kept in one place so the controller resolver below and
# ``AnalyzeService._resolve_algorithm_service_class`` cannot drift apart.
ALGORITHM_NAME_ALIASES = {
    'AIPersonDetetor': 'AIPersonDetector',
}


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
        return self.config.get('algorithms', [])

    @staticmethod
    def resolve_image_algorithm_class(algorithm, key='controller'):
        """Import an image algorithm's controller class by dotted path.

        The controllers twin of
        ``AnalyzeService._resolve_algorithm_service_class``, and the reason
        neither orchestration file needs to import every algorithm up front
        just to look one up in ``globals()``. A routing table built out of
        module globals means a new entry in ``algorithms.conf`` is not
        actually enough to add an algorithm, which is what CLAUDE.md 2.3
        rules out.

        The dotted path comes from an explicit ``module`` /
        ``wizard_module`` key when the config carries one - the same
        escape hatch the ``streaming_algorithms`` entries already use -
        and otherwise from the convention every image algorithm follows:
        ``algorithms.images.<name>.controllers.<class>``.

        Args:
            algorithm: Algorithm configuration dictionary.
            key: Which class to resolve - ``'controller'`` or
                ``'wizard_controller'``.

        Returns:
            The resolved class.

        Raises:
            ValueError: If the config is incomplete, or the module or class
                cannot be resolved. Raised rather than returned as None so
                a misconfigured algorithm fails where it is named instead
                of somewhere downstream.
        """
        class_name = algorithm.get(key)
        name = algorithm.get('name')
        if not class_name or not name:
            raise ValueError(
                f"Algorithm config missing required fields: 'name' and '{key}'"
            )

        module_key = 'module' if key == 'controller' else 'wizard_module'
        explicit = algorithm.get(module_key)

        candidates = []
        if explicit:
            candidates.append(explicit)
        else:
            for candidate_name in (name, ALGORITHM_NAME_ALIASES.get(name)):
                if candidate_name:
                    candidates.append(
                        f'algorithms.images.{candidate_name}.controllers.{class_name}')

        last_error = None
        for module_name in candidates:
            try:
                module = import_module(module_name)
            except Exception as exc:
                last_error = exc
                continue
            resolved = getattr(module, class_name, None)
            if isinstance(resolved, type):
                return resolved
            last_error = AttributeError(
                f"Class '{class_name}' not found in module '{module_name}'")

        raise ValueError(
            f"Could not resolve {key} '{class_name}' for algorithm '{name}'"
        ) from last_error

    def get_streaming_algorithms(self):
        """Retrieve the list of streaming algorithms from the configuration.

        Returns:
            A list of streaming algorithm dictionaries specified in the configuration.
            Returns an empty list when the key is missing.
        """
        return self.config.get('streaming_algorithms', [])
