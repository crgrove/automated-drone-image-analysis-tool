"""
CustomColorsService.py - Manages shared custom colors across all color pickers

This service provides a centralized way to store and retrieve custom colors
that are shared between RGB and HSV color pickers, persisting across sessions.
"""

import json
from typing import List, Tuple, Optional
from core.services.SettingsService import SettingsService


class CustomColorsService:
    """Service to manage custom colors shared across all color pickers."""

    MAX_CUSTOM_COLORS = 16  # Qt's QColorDialog supports 16 custom colors

    def __init__(self):
        """Initialize the CustomColorsService."""
        self.settings_service = SettingsService()
        self._colors: List[Optional[List[int]]] = [None] * self.MAX_CUSTOM_COLORS
        self._load_from_settings()

    def _load_from_settings(self):
        """Load custom colors from settings."""
        try:
            colors_json = self.settings_service.get_setting('custom_colors')
            if colors_json:
                colors = json.loads(colors_json)
                for i, color_rgb in enumerate(colors[:self.MAX_CUSTOM_COLORS]):
                    self._colors[i] = color_rgb
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    def _save_to_settings(self):
        """Save current colors to settings."""
        self.settings_service.set_setting('custom_colors', json.dumps(self._colors))

    def save_custom_colors(self):
        """Save current custom colors to settings (called after dialog sync)."""
        self._save_to_settings()

    def add_custom_color_rgb(self, rgb: Tuple[int, int, int]) -> int:
        """
        Add a color as an RGB tuple to the custom colors palette.

        Args:
            rgb: (r, g, b) tuple to add

        Returns:
            Index where the color was added, or -1 if invalid
        """
        r, g, b = rgb

        # Check if color already exists
        for i in range(self.MAX_CUSTOM_COLORS):
            existing = self._colors[i]
            if existing and existing[0] == r and existing[1] == g and existing[2] == b:
                return i

        # Find first empty slot
        for i in range(self.MAX_CUSTOM_COLORS):
            if not self._colors[i]:
                self._colors[i] = [r, g, b]
                self._save_to_settings()
                return i

        # No empty slots - shift down and insert at 0
        for i in range(self.MAX_CUSTOM_COLORS - 1, 0, -1):
            self._colors[i] = self._colors[i - 1]
        self._colors[0] = [r, g, b]
        self._save_to_settings()
        return 0

    def get_custom_colors(self) -> List[Optional[Tuple[int, int, int]]]:
        """
        Get all custom colors as RGB tuples.

        Returns:
            List of RGB tuples or None for empty slots
        """
        result = []
        for color_rgb in self._colors:
            if color_rgb:
                result.append((color_rgb[0], color_rgb[1], color_rgb[2]))
            else:
                result.append(None)
        return result

    def apply_to_qt_dialog(self):
        """Apply stored colors to QColorDialog's static custom colors.

        Call this from a controller/view before showing a QColorDialog.
        """
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QColorDialog

        for i, color_rgb in enumerate(self._colors[:self.MAX_CUSTOM_COLORS]):
            if color_rgb:
                color = QColor(color_rgb[0], color_rgb[1], color_rgb[2])
                QColorDialog.setCustomColor(i, color)

    def sync_from_qt_dialog(self):
        """Read custom colors from QColorDialog and save.

        Call this from a controller/view after a QColorDialog is closed.
        """
        from PySide6.QtWidgets import QColorDialog

        for i in range(self.MAX_CUSTOM_COLORS):
            color = QColorDialog.customColor(i)
            if color.isValid():
                self._colors[i] = [color.red(), color.green(), color.blue()]
            else:
                self._colors[i] = None
        self._save_to_settings()

    # Legacy aliases for backward compatibility
    def add_custom_color(self, color) -> int:
        """Add a QColor to the custom colors palette (legacy bridge)."""
        if not color.isValid():
            return -1
        return self.add_custom_color_rgb((color.red(), color.green(), color.blue()))

    def sync_with_dialog(self):
        """Synchronize after a QColorDialog has been used (legacy bridge)."""
        self.sync_from_qt_dialog()


# Global instance for sharing across the application
_custom_colors_instance = None


def get_custom_colors_service() -> CustomColorsService:
    """Get the singleton instance of CustomColorsService."""
    global _custom_colors_instance
    if _custom_colors_instance is None:
        _custom_colors_instance = CustomColorsService()
    return _custom_colors_instance
