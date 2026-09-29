"""GeoDataEnvHelper - Guard PROJ/GDAL data env vars against stale installs.

Third-party GIS software (VTP, old QGIS/PostGIS/FME setups) exports
machine-wide PROJ_LIB / PROJ_DATA / GDAL_DATA variables pointing at its own
data directories. rasterio and GDAL trust those variables over the data
bundled with their wheels, so a PROJ4-era directory (one with no ``proj.db``,
which PROJ 6+ requires) breaks every CRS lookup with
"proj_create_from_database: Cannot find proj.db" - and with it all DEM
sampling (observed in the field with VTP's PROJ4-data/GDAL-data).

Clearing the incompatible variable for THIS process only lets rasterio and
pyproj fall back to their own bundled, version-matched data. The system
environment is left untouched, so the third-party software that set the
variable keeps working.
"""

import os

# Variable -> file that must exist in the directory it points at for the
# directory to be usable by the PROJ 6+ / GDAL 3 our wheels bundle.
# proj.db is the PROJ 6+ database (PROJ4-era data directories lack it);
# gdalvrt.xsd ships with every GDAL 2+/3 data directory but not with the
# GDAL 1.x csv-table layout old installs carry.
_REQUIRED_MARKERS = (
    ('PROJ_LIB', 'proj.db'),
    ('PROJ_DATA', 'proj.db'),
    ('GDAL_DATA', 'gdalvrt.xsd'),
)


def sanitize_geo_data_env():
    """Remove PROJ/GDAL data environment variables that point at data our
    bundled libraries cannot use.

    Must run before the first rasterio/pyproj use (both read the variables
    when their environment initializes).

    Returns:
        list: (variable, path) pairs that were removed, for the caller to log.
    """
    removed = []
    for var, marker in _REQUIRED_MARKERS:
        path = os.environ.get(var)
        if not path:
            continue
        try:
            usable = os.path.isfile(os.path.join(path, marker))
        except (TypeError, ValueError):
            usable = False
        if not usable:
            del os.environ[var]
            removed.append((var, path))
    return removed
