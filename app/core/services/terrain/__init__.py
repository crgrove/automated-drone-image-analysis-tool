"""
Terrain services module for DTM/DSM elevation data.

Provides elevation lookup, caching, and geoid correction for accurate AOI positioning.
"""

from .TerrainService import TerrainService
from .TerrainCacheService import TerrainCacheService
from .GeoidService import GeoidService
from .ElevationProvider import ElevationProvider, TerrariumProvider
from .TerrainProviderFactory import (
    TerrainProviderFactory,
    PROVIDER_TERRARIUM,
    PROVIDER_USGS_3DEP_LOCAL,
    DEFAULT_PROVIDER_ID,
)
from .USGS3DEPProvider import USGS3DEPProvider
from .CanopyService import CanopyService, CanopySample
from .CanopyServiceFactory import (
    CanopyServiceFactory,
    create_canopy_service,
    CANOPY_KIND_NONE,
    CANOPY_KIND_LANDFIRE,
    CANOPY_KIND_META,
)
from .TileFetchService import TileFetchService, FetchResult
from .grid import (
    GridSpec,
    GridSample,
    make_lattice_spec,
    spec_for_bounds_wgs84,
    integer_offset,
    lonlat_to_mercator,
    mercator_to_lonlat,
    mercator_units_per_meter,
    WEB_MERCATOR_CRS,
    WEB_MERCATOR_ORIGIN_SHIFT,
)

__all__ = [
    'TerrainService',
    'TerrainCacheService',
    'GeoidService',
    'ElevationProvider',
    'TerrariumProvider',
    'TerrainProviderFactory',
    'USGS3DEPProvider',
    'PROVIDER_TERRARIUM',
    'PROVIDER_USGS_3DEP_LOCAL',
    'DEFAULT_PROVIDER_ID',
    'CanopyService',
    'CanopySample',
    'CanopyServiceFactory',
    'create_canopy_service',
    'CANOPY_KIND_NONE',
    'CANOPY_KIND_LANDFIRE',
    'CANOPY_KIND_META',
    'TileFetchService',
    'FetchResult',
    'GridSpec',
    'GridSample',
    'make_lattice_spec',
    'spec_for_bounds_wgs84',
    'integer_offset',
    'lonlat_to_mercator',
    'mercator_to_lonlat',
    'mercator_units_per_meter',
    'WEB_MERCATOR_CRS',
    'WEB_MERCATOR_ORIGIN_SHIFT',
]
