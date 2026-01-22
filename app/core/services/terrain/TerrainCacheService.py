"""
TerrainCacheService - Manages caching of terrain elevation tiles.

Features:
- Download and cache PNG tiles on-demand
- Persistent cache across sessions
- Portable cache (can be copied between PCs)
- Integrity validation
- Optional LRU eviction for disk space management
"""

import json
import os
import hashlib
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from PIL import Image
import io

from core.services.LoggerService import LoggerService
from .ElevationProvider import ElevationProvider, TerrariumProvider


class TerrainCacheService:
    """
    Service for caching terrain elevation tiles.

    Tiles are stored in a hierarchical directory structure:
    cache_dir/tiles/{provider}/{z}/{x}/{y}.png
    """

    DEFAULT_CACHE_DIR = Path.home() / '.adiat' / 'terrain_cache'
    METADATA_FILE = 'metadata.json'
    MAX_CACHE_SIZE_MB = 500  # Default max cache size

    def __init__(self, cache_dir: Optional[str] = None, provider: Optional[ElevationProvider] = None):
        """
        Initialize the TerrainCacheService.

        Args:
            cache_dir: Custom cache directory. Defaults to ~/.adiat/terrain_cache
            provider: Elevation data provider. Defaults to TerrariumProvider.
        """
        self.logger = LoggerService()

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = self.DEFAULT_CACHE_DIR

        self.provider = provider or TerrariumProvider()
        self.provider_name = self.provider.get_provider_name().replace(' ', '_').replace('(', '').replace(')', '')

        # Create cache directory structure
        self.tiles_dir = self.cache_dir / 'tiles' / 'terrarium'
        self.tiles_dir.mkdir(parents=True, exist_ok=True)

        # Load or create metadata
        self._metadata = self._load_metadata()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._downloads = 0
        self._errors = 0

    def get_tile(self, z: int, x: int, y: int) -> Optional[Image.Image]:
        """
        Get a tile, from cache if available, otherwise download.

        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            PIL Image of the tile, or None if unavailable
        """
        # Try cache first
        tile_path = self._get_tile_path(z, x, y)

        if tile_path.exists():
            try:
                img = Image.open(tile_path)
                img.load()  # Force load to catch corrupt files
                self._hits += 1
                return img
            except Exception as e:
                self.logger.warning(f"Corrupt cached tile {tile_path}: {e}")
                # Remove corrupt file
                try:
                    tile_path.unlink()
                except Exception:
                    pass

        # Cache miss - try to download
        self._misses += 1
        return self._download_and_cache_tile(z, x, y)

    def get_tile_if_cached(self, z: int, x: int, y: int) -> Optional[Image.Image]:
        """
        Get a tile only if it's already cached.

        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            PIL Image of the tile, or None if not cached
        """
        tile_path = self._get_tile_path(z, x, y)

        if tile_path.exists():
            try:
                img = Image.open(tile_path)
                img.load()
                self._hits += 1
                return img
            except Exception:
                pass

        return None

    def is_tile_cached(self, z: int, x: int, y: int) -> bool:
        """Check if a tile is in the cache."""
        return self._get_tile_path(z, x, y).exists()

    def prefetch_tiles(self, lat: float, lon: float, radius_km: float = 5, zoom: int = 12) -> int:
        """
        Pre-download tiles for an area around a location.

        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Radius in kilometers
            zoom: Zoom level

        Returns:
            Number of tiles downloaded
        """
        # Calculate bounding box
        # Approximate: 1 degree ≈ 111km at equator
        dlat = radius_km / 111.0
        dlon = radius_km / (111.0 * abs(max(0.01, abs(lat))) if lat != 0 else 111.0)

        min_lat = lat - dlat
        max_lat = lat + dlat
        min_lon = lon - dlon
        max_lon = lon + dlon

        # Get tile range
        min_x, max_y = TerrariumProvider.lat_lon_to_tile(max_lat, min_lon, zoom)
        max_x, min_y = TerrariumProvider.lat_lon_to_tile(min_lat, max_lon, zoom)

        downloaded = 0
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if not self.is_tile_cached(zoom, x, y):
                    tile = self._download_and_cache_tile(zoom, x, y)
                    if tile is not None:
                        downloaded += 1

        return downloaded

    def _get_tile_path(self, z: int, x: int, y: int) -> Path:
        """Get the file path for a cached tile."""
        return self.tiles_dir / str(z) / str(x) / f"{y}.png"

    def _download_and_cache_tile(self, z: int, x: int, y: int) -> Optional[Image.Image]:
        """Download a tile and save to cache."""
        try:
            data = self.provider.download_tile(z, x, y)
            if data is None:
                return None

            # Save to cache
            tile_path = self._get_tile_path(z, x, y)
            tile_path.parent.mkdir(parents=True, exist_ok=True)

            with open(tile_path, 'wb') as f:
                f.write(data)

            self._downloads += 1
            self._update_metadata_stats()

            # Return as PIL Image
            return Image.open(io.BytesIO(data))

        except Exception as e:
            self.logger.error(f"Failed to download tile {z}/{x}/{y}: {e}")
            self._errors += 1
            return None

    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata."""
        metadata_path = self.cache_dir / self.METADATA_FILE

        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache metadata: {e}")

        return self._create_default_metadata()

    def _create_default_metadata(self) -> Dict[str, Any]:
        """Create default metadata structure."""
        return {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'provider': self.provider.get_provider_name(),
            'datum': self.provider.get_datum_info(),
            'stats': {
                'total_tiles': 0,
                'total_size_bytes': 0,
                'last_download': None,
                'hits': 0,
                'misses': 0
            }
        }

    def _save_metadata(self):
        """Save cache metadata."""
        try:
            metadata_path = self.cache_dir / self.METADATA_FILE
            with open(metadata_path, 'w') as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save metadata: {e}")

    def _update_metadata_stats(self):
        """Update metadata statistics."""
        # Count tiles
        total_tiles = 0
        total_size = 0

        for root, dirs, files in os.walk(self.tiles_dir):
            for file in files:
                if file.endswith('.png'):
                    total_tiles += 1
                    total_size += os.path.getsize(os.path.join(root, file))

        self._metadata['stats']['total_tiles'] = total_tiles
        self._metadata['stats']['total_size_bytes'] = total_size
        self._metadata['stats']['last_download'] = datetime.now().isoformat()
        self._metadata['stats']['hits'] = self._hits
        self._metadata['stats']['misses'] = self._misses

        self._save_metadata()

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the cache."""
        # Update stats
        total_tiles = 0
        total_size = 0

        for root, dirs, files in os.walk(self.tiles_dir):
            for file in files:
                if file.endswith('.png'):
                    total_tiles += 1
                    total_size += os.path.getsize(os.path.join(root, file))

        return {
            'cache_dir': str(self.cache_dir),
            'tiles_dir': str(self.tiles_dir),
            'provider': self.provider.get_provider_name(),
            'datum': self.provider.get_datum_info(),
            'total_tiles': total_tiles,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'session_stats': {
                'hits': self._hits,
                'misses': self._misses,
                'downloads': self._downloads,
                'errors': self._errors,
                'hit_rate': round(self._hits / max(1, self._hits + self._misses) * 100, 1)
            }
        }

    def clear_cache(self) -> int:
        """
        Clear all cached tiles.

        Returns:
            Number of tiles removed
        """
        count = 0
        try:
            for root, dirs, files in os.walk(self.tiles_dir, topdown=False):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                        count += 1
                    except Exception:
                        pass
                for d in dirs:
                    try:
                        os.rmdir(os.path.join(root, d))
                    except Exception:
                        pass

            self._metadata = self._create_default_metadata()
            self._save_metadata()

            self.logger.info(f"Cleared {count} cached tiles")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

        return count

    def export_cache(self, export_path: str) -> bool:
        """
        Export the cache directory for transfer to another PC.

        Args:
            export_path: Path for the exported archive

        Returns:
            True if successful
        """
        import shutil

        try:
            # Create a zip archive of the cache directory
            shutil.make_archive(
                export_path.rstrip('.zip'),
                'zip',
                self.cache_dir.parent,
                self.cache_dir.name
            )
            self.logger.info(f"Cache exported to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export cache: {e}")
            return False

    def import_cache(self, import_path: str) -> bool:
        """
        Import a cache archive from another PC.

        Args:
            import_path: Path to the cache archive

        Returns:
            True if successful
        """
        import shutil
        import zipfile

        try:
            # Extract to cache directory
            with zipfile.ZipFile(import_path, 'r') as zip_ref:
                # Extract to parent and rename if needed
                zip_ref.extractall(self.cache_dir)

            # Reload metadata
            self._metadata = self._load_metadata()

            self.logger.info(f"Cache imported from {import_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to import cache: {e}")
            return False

    def is_online(self) -> bool:
        """Check if the elevation service is accessible online."""
        try:
            # Try to download a known tile (zoom 0, tile 0,0 - always exists)
            data = self.provider.download_tile(0, 0, 0)
            return data is not None
        except Exception:
            return False
