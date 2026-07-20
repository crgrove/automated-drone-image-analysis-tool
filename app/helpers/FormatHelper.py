"""FormatHelper.py -- small display-formatting helpers shared by the UI and services."""


class FormatHelper:
    """Static helpers for formatting values for display."""

    @staticmethod
    def format_duration(seconds):
        """Return a short, human-readable string for a duration.

        Args:
            seconds: A duration in seconds. Negative values are treated as 0.

        Returns:
            str: e.g. '45s', '5m 12s', or '1h 23m 45s'.
        """
        total = max(0, int(round(seconds)))
        hours, remainder = divmod(total, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"

    @staticmethod
    def format_megabytes(num_bytes):
        """Return a byte count formatted as megabytes with two decimal places.

        Args:
            num_bytes: A size in bytes. Negative values are treated as 0.
                One megabyte is 1024 * 1024 bytes.

        Returns:
            str: e.g. '31.25' (no unit suffix; callers add the localized unit).
        """
        megabytes = max(0, int(num_bytes)) / (1024 * 1024)
        return f"{megabytes:.2f}"
