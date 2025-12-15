"""
Service for tracking recently used colors/ranges for color-based detection algorithms.

Stores the last 10 colors for each algorithm type (HSV, RGB, MatchedFilter) with their
associated parameters (ranges, thresholds, etc.). Uses persistent storage in settings.
"""

from typing import List, Dict, Any, Optional
from core.services.SettingsService import SettingsService
from core.services.LoggerService import LoggerService


class RecentColorsService:
    """Singleton service for managing recently used colors across algorithms."""

    _instance = None
    MAX_RECENT_COLORS = 10

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.settings_service = SettingsService()
        self.logger = LoggerService()

    def add_hsv_color(self, color_data: Dict[str, Any]) -> None:
        """
        Add an HSV color configuration to recent history.

        Args:
            color_data: Dict with keys:
                - selected_color: tuple (r, g, b)
                - hsv_ranges: dict with h, s, v, h_minus, h_plus, s_minus, s_plus, v_minus, v_plus
        """
        recent = self._get_recent_list('RecentHSVColors')

        # Remove duplicate if exists (compare by selected_color)
        color_tuple = tuple(color_data['selected_color'])
        recent = [c for c in recent if tuple(c.get('selected_color', [])) != color_tuple]

        # Add to front
        recent.insert(0, color_data)

        # Keep only last 10
        recent = recent[:self.MAX_RECENT_COLORS]

        self.settings_service.set_setting('RecentHSVColors', recent)

    def add_rgb_color(self, color_data: Dict[str, Any]) -> None:
        """
        Add an RGB color configuration to recent history.

        Args:
            color_data: Dict with keys:
                - selected_color: tuple (r, g, b)
                - range_values: tuple (r_range, g_range, b_range)
                - color_range: [[r_min, g_min, b_min], [r_max, g_max, b_max]]
        """
        recent = self._get_recent_list('RecentRGBColors')

        # Remove duplicate if exists (compare by selected_color)
        color_tuple = tuple(color_data['selected_color'])
        recent = [c for c in recent if tuple(c.get('selected_color', [])) != color_tuple]

        # Add to front
        recent.insert(0, color_data)

        # Keep only last 10
        recent = recent[:self.MAX_RECENT_COLORS]

        # self.logger.info(f"Saving {len(recent)} RGB color(s) to recent colors")
        self.settings_service.set_setting('RecentRGBColors', recent)

    def add_matched_filter_color(self, color_data: Dict[str, Any]) -> None:
        """
        Add a Matched Filter color configuration to recent history.

        Args:
            color_data: Dict with keys:
                - selected_color: tuple (r, g, b)
                - match_filter_threshold: float
        """
        recent = self._get_recent_list('RecentMatchedFilterColors')

        # Remove duplicate if exists (compare by selected_color)
        color_tuple = tuple(color_data['selected_color'])
        recent = [c for c in recent if tuple(c.get('selected_color', [])) != color_tuple]

        # Add to front
        recent.insert(0, color_data)

        # Keep only last 10
        recent = recent[:self.MAX_RECENT_COLORS]

        self.settings_service.set_setting('RecentMatchedFilterColors', recent)

    def get_recent_hsv_colors(self) -> List[Dict[str, Any]]:
        """Get list of recent HSV colors."""
        return self._get_recent_list('RecentHSVColors')

    def get_recent_rgb_colors(self) -> List[Dict[str, Any]]:
        """Get list of recent RGB colors."""
        return self._get_recent_list('RecentRGBColors')

    def get_recent_matched_filter_colors(self) -> List[Dict[str, Any]]:
        """Get list of recent Matched Filter colors."""
        return self._get_recent_list('RecentMatchedFilterColors')

    def _get_recent_list(self, setting_key: str) -> List[Dict[str, Any]]:
        """Helper to get recent list from settings."""
        recent = self.settings_service.get_setting(setting_key)

        if not isinstance(recent, list):
            # self.logger.info(f"No recent colors found for {setting_key}")
            return []

        # self.logger.info(f"Loaded {len(recent)} recent color(s) from {setting_key}")
        return recent


def get_recent_colors_service() -> RecentColorsService:
    """Get or create the singleton RecentColorsService instance."""
    return RecentColorsService()
