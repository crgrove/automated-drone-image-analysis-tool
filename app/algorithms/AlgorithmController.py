class AlgorithmController:
    """Base class for algorithm controllers that manages algorithm options and validation."""

    def __init__(self, config):
        """
        Initializes the AlgorithmController with the given name and thermal flag.

        Args:
            config (dict): Algorithm config information.
        """
        self.name = config['name']
        self.is_thermal = (config['type'] == 'Thermal')

    def get_options(self):
        """
        Populates and returns options based on user-selected values.

        Returns:
            dict: A dictionary of option names and their values.
        """
        raise NotImplementedError

    def validate(self):
        """
        Validates that the required values have been provided.

        Returns:
            str: An error message if validation fails, else None.
        """
        raise NotImplementedError

    def load_options(self, options):
        """
        Sets UI elements based on provided options.

        Args:
            options (dict): Dictionary of options to set.
        """
        raise NotImplementedError
