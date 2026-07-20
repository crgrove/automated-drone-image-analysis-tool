"""
TerrainProviderFactory - Construct an ElevationProvider from a string id + settings.

Used by TerrainService to swap between Terrarium (online tiled) and
USGS 3DEP local-GeoTIFF backends without leaking provider-specific
configuration into TerrainService itself.
"""

from typing import Optional, List

from core.services.LoggerService import LoggerService
from .ElevationProvider import ElevationProvider, TerrariumProvider


PROVIDER_TERRARIUM = 'terrarium'
PROVIDER_USGS_3DEP_LOCAL = 'usgs_3dep_local'

DEFAULT_PROVIDER_ID = PROVIDER_TERRARIUM


class TerrainProviderFactory:
    """Factory for ElevationProvider instances driven by SettingsService."""

    @staticmethod
    def create(provider_id: Optional[str], settings_service) -> ElevationProvider:
        """Construct a provider for the given id, falling back to Terrarium on failure."""
        logger = LoggerService()
        provider_id = provider_id or DEFAULT_PROVIDER_ID

        if provider_id == PROVIDER_USGS_3DEP_LOCAL:
            import os
            manifest = settings_service.get_setting('Terrain3DEPManifestPath', '')
            tiles_dir = settings_service.get_setting('Terrain3DEPTilesDir', '')
            if not manifest or not tiles_dir:
                logger.warning(
                    "TerrainProviderFactory: 3DEP paths not set in Preferences; "
                    "falling back to Terrarium."
                )
                return TerrariumProvider()
            if not os.path.isfile(manifest) or not os.path.isdir(tiles_dir):
                logger.warning(
                    f"TerrainProviderFactory: registered 3DEP data is missing on "
                    f"disk (manifest: {manifest}); falling back to Terrarium. "
                    "Re-download or fix the paths in Preferences."
                )
                return TerrariumProvider()
            try:
                from .USGS3DEPProvider import USGS3DEPProvider
                return USGS3DEPProvider(manifest, tiles_dir)
            except Exception as e:
                logger.error(f"TerrainProviderFactory: 3DEP provider failed ({e}); falling back to Terrarium.")
                return TerrariumProvider()

        if provider_id != PROVIDER_TERRARIUM:
            logger.warning(f"TerrainProviderFactory: unknown provider '{provider_id}', using Terrarium.")
        return TerrariumProvider()

    @staticmethod
    def available_providers() -> List[dict]:
        """List of providers exposed in the Preferences UI."""
        return [
            {
                'id': PROVIDER_TERRARIUM,
                'label': 'AWS Terrain Tiles (online, ~30 m global)',
                'requires_paths': False,
            },
            {
                'id': PROVIDER_USGS_3DEP_LOCAL,
                'label': 'USGS 3DEP 1 m local tiles (AWS fallback outside coverage)',
                'requires_paths': True,
            },
        ]
