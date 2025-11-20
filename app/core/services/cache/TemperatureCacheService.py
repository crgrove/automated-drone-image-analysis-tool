"""
TemperatureCacheService - Manages in-memory caching of AOI temperature information.

This service provides:
- In-memory storage of temperature information (in Celsius) during processing
- Temperature data is stored in XML, not JSON files
"""

import hashlib
import os
from typing import Dict, Optional, Any
from core.services.LoggerService import LoggerService


class TemperatureCacheService:
    """
    Service for in-memory caching of AOI temperature information.

    Temperature data is stored in XML files, not JSON. This service only provides
    in-memory storage during processing.

    Temperature is stored in Celsius for consistency.
    """

    def __init__(self):
        """
        Initialize the temperature cache service.
        """
        self.logger = LoggerService()

        # In-memory cache: {cache_key: temperature_celsius}
        self.memory_cache: Dict[str, Optional[float]] = {}

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

    def get_temperature(self, image_path: str, aoi_data: Dict[str, Any]) -> Optional[float]:
        """
        Get cached temperature for an AOI from memory (in Celsius).

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary

        Returns:
            Temperature in Celsius, or None if not cached
        """
        cache_key = self.get_cache_key(image_path, aoi_data)
        return self.memory_cache.get(cache_key)

    def save_temperature(self, image_path: str, aoi_data: Dict[str, Any],
                         temperature: float) -> bool:
        """
        Save temperature for an AOI to memory cache (in Celsius).

        Args:
            image_path: Path to the source image
            aoi_data: AOI dictionary
            temperature: Temperature in Celsius

        Returns:
            True if saved successfully
        """
        try:
            cache_key = self.get_cache_key(image_path, aoi_data)

            # Add to memory cache
            self.memory_cache[cache_key] = float(temperature)

            return True

        except Exception as e:
            self.logger.error(f"Error saving temperature to cache: {e}")
            return False

    def bulk_save_temperatures(self, temperatures: Dict[str, float]) -> bool:
        """
        Bulk save multiple temperature entries (for batch processing).

        Args:
            temperatures: Dict of {cache_key: temperature_celsius}

        Returns:
            True if saved successfully
        """
        try:
            self.memory_cache.update(temperatures)
            self.logger.info(f"Added {len(temperatures)} temperatures to cache")
            return True

        except Exception as e:
            self.logger.error(f"Error in bulk save: {e}")
            return False

    def clear_cache(self):
        """Clear the in-memory cache."""
        self.memory_cache.clear()
        self.logger.info("Temperature cache cleared from memory")

    def get_all_cache_data(self) -> Dict[str, float]:
        """
        Get all cached temperature data for XML export.

        Returns:
            Dict of {cache_key: temperature_celsius} for all cached entries
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
