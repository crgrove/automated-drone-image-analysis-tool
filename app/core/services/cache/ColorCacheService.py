"""
ColorCacheService - Manages in-memory caching of AOI color information.

This service provides:
- In-memory storage of color information (hue, hex, RGB) during processing
- Color data is stored in XML, not JSON files
"""

import hashlib
import os
from typing import Dict, Optional, Any
from core.services.LoggerService import LoggerService


class ColorCacheService:
    """
    Service for in-memory caching of AOI color information.

    Color data is stored in XML files, not JSON. This service only provides
    in-memory storage during processing.

    Color info includes:
    - rgb: [r, g, b] values (0-255)
    - hex: "#RRGGBB" hex color string
    - hue_degrees: 0-360 degree hue value
    """

    def __init__(self):
        """
        Initialize the color cache service.
        """
        self.logger = LoggerService()

        # In-memory cache: {cache_key: color_info_dict}
        self.memory_cache: Dict[str, Optional[Dict[str, Any]]] = {}

    def get_cache_key(self, image_path: str, aoi_data: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for an AOI.

        Uses only the filename and AOI coordinates to make caches fully portable
        across machines and time.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary with center and radius

        Returns:
            MD5 hash cache key
        """
        try:
            # Use only the filename to make cache portable across machines
            filename = os.path.basename(image_path)

            # Create unique identifier from filename, center, radius
            center = aoi_data.get('center', (0, 0))
            radius = aoi_data.get('radius', 0)

            identifier = f"{filename}_{center[0]}_{center[1]}_{radius}"

            # Generate hash
            return hashlib.md5(identifier.encode()).hexdigest()

        except Exception as e:
            self.logger.error(f"Error generating cache key: {e}")
            # Fallback to simple hash
            return hashlib.md5(str(aoi_data).encode()).hexdigest()

    def get_color_info(self, image_path: str, aoi_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached color information for an AOI from memory.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary

        Returns:
            Dict with 'rgb', 'hex', 'hue_degrees' keys, or None if not cached
        """
        cache_key = self.get_cache_key(image_path, aoi_data)
        return self.memory_cache.get(cache_key)

    def save_color_info(self, image_path: str, aoi_data: Dict[str, Any],
                        color_info: Dict[str, Any]) -> bool:
        """
        Save color information for an AOI to memory cache.

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary
            color_info: Dict with 'rgb', 'hex', 'hue_degrees' keys

        Returns:
            True if saved successfully
        """
        try:
            cache_key = self.get_cache_key(image_path, aoi_data)

            # Validate color info structure
            required_keys = ['rgb', 'hex', 'hue_degrees']
            if not all(key in color_info for key in required_keys):
                self.logger.warning("Invalid color info structure, missing required keys")
                return False

            # Add to memory cache
            self.memory_cache[cache_key] = color_info

            return True

        except Exception as e:
            self.logger.error(f"Error saving color info to cache: {e}")
            return False

    def bulk_save_colors(self, colors: Dict[str, Dict[str, Any]]) -> bool:
        """
        Bulk save multiple color entries (for batch processing).

        Args:
            colors: Dict of {cache_key: color_info}

        Returns:
            True if saved successfully
        """
        try:
            self.memory_cache.update(colors)
            # self.logger.info(f"Added {len(colors)} colors to cache")
            return True

        except Exception as e:
            self.logger.error(f"Error in bulk save: {e}")
            return False

    def clear_cache(self):
        """Clear the in-memory cache."""
        self.memory_cache.clear()
        # self.logger.info("Color cache cleared from memory")

    def get_all_cache_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all cached color data for XML export.

        Returns:
            Dict of {cache_key: color_info} for all cached entries
        """
        return self.memory_cache.copy()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        return {
            'memory_count': len(self.memory_cache)
        }
