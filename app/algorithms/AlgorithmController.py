class AlgorithmController:
    """Base class for algorithm controllers that manages algorithm options and validation.

    Provides a common interface for algorithm configuration UI controllers.
    Subclasses must implement get_options(), validate(), and load_options().

    Attributes:
        name: Name of the algorithm.
        is_thermal: Whether this algorithm is for thermal images.
    """

    def __init__(self, config):
        """Initialize the AlgorithmController with the given name and thermal flag.

        Args:
            config: Algorithm config dictionary containing 'name' and 'type'.
        """
        self.name = config['name']
        self.is_thermal = (config['type'] == 'Thermal')

    def get_options(self):
        """Populate and return options based on user-selected values.

        Returns:
            Dictionary of option names and their values.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def validate(self):
        """Validate that the required values have been provided.

        Returns:
            Error message string if validation fails, else None.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def load_options(self, options):
        """Set UI elements based on provided options.

        Args:
            options: Dictionary of options to set.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError
