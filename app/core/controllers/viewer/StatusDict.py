from collections import UserDict, OrderedDict


class StatusDict(UserDict):
    """
    Dictionary-like object that maintains a custom key order and supports
    callback execution when values are updated.

    Attributes:
        callback (Callable): Function to call when values are updated.
        key_order (list): Explicit order to maintain for dictionary keys.
    """
    def __init__(self, *args, callback=None, key_order=None, **kwargs):
        self.data = OrderedDict()  # Maintain explicit ordering
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.key_order = key_order or []  # Store explicit ordering

    def __setitem__(self, key, value):
        if key in self.data:
            del self.data[key]  # Remove existing entry to reinsert in correct order
        self.data[key] = value  # Insert the key-value pair

        self._enforce_order()  # Ensure keys are in correct order

        if self.callback:
            self.callback(key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        if self.callback:
            self.callback(f"Deleted {key}")

    def set_order(self, key_order):
        """Sets the explicit order of keys in the dictionary."""
        self.key_order = key_order
        self._enforce_order()  # Apply the new order immediately

    def _enforce_order(self):
        """Reorders the dictionary based on self.key_order."""
        new_data = OrderedDict()
        for key in self.key_order:
            if key in self.data:
                new_data[key] = self.data[key]
        self.data = new_data  # Replace existing dict with the ordered one

    def items(self):
        """Returns items in the explicitly set order."""
        return [(key, self.data[key]) for key in self.key_order if key in self.data]
