"""
USGS3DEPProvider - Local GeoTIFF elevation provider for USGS 3DEP 1m tiles.

Reads a per-folder dem_manifest.csv (filename, minX, minY, maxX, maxY, ...)
to build an in-memory bounding-box index over local GeoTIFFs, then samples
elevations directly via rasterio. Designed for high-resolution use cases
(WALDO airplane imagery over the Sierra) where the global Terrarium tiles
are not precise enough.

Vertical datum: NAVD88 (GEOID18) for 3DEP. ADIAT's GeoidService is EGM96;
typical CONUS bias is <2 m which is acceptable at the resolutions involved.
"""

from collections import OrderedDict
from pathlib import Path
from typing import Optional, Tuple

from core.services.LoggerService import LoggerService
from .ElevationProvider import ElevationProvider


class USGS3DEPProvider(ElevationProvider):
    """Local-disk USGS 3DEP 1m GeoTIFF elevation provider."""

    DATASET_LRU_SIZE = 16

    def __init__(self, manifest_csv: str, tiles_dir: str):
        """
        Args:
            manifest_csv: Path to a CSV with columns
                'filename, minX, minY, maxX, maxY' (lat/lon WGS84 bboxes).
            tiles_dir: Folder containing the GeoTIFFs referenced by 'filename'.
        """
        self.logger = LoggerService()
        self.manifest_path = Path(manifest_csv)
        self.tiles_dir = Path(tiles_dir)
        self._tiles = []  # list of dicts: {filename, full_path, minX, minY, maxX, maxY}
        self._strtree = None
        self._strtree_geoms = []  # parallel list of shapely boxes
        self._open_datasets: "OrderedDict[str, object]" = OrderedDict()

        self._load_manifest()

    def _load_manifest(self):
        """Parse the manifest CSV and build a spatial bounding-box index."""
        try:
            import pandas as pd
            from shapely.geometry import box
            from shapely.strtree import STRtree
        except ImportError as e:
            self.logger.error(f"USGS3DEPProvider missing dependency: {e}")
            return

        if not self.manifest_path.is_file():
            self.logger.error(f"USGS3DEPProvider: manifest not found at {self.manifest_path}")
            return

        try:
            df = pd.read_csv(self.manifest_path)
        except Exception as e:
            self.logger.error(f"USGS3DEPProvider: failed to read manifest: {e}")
            return

        required = {'filename', 'minX', 'minY', 'maxX', 'maxY'}
        missing = required - set(df.columns)
        if missing:
            self.logger.error(
                f"USGS3DEPProvider: manifest missing required columns {missing}"
            )
            return

        for _, row in df.iterrows():
            filename = str(row['filename'])
            full_path = self.tiles_dir / filename
            self._tiles.append({
                'filename': filename,
                'full_path': str(full_path),
                'minX': float(row['minX']),
                'minY': float(row['minY']),
                'maxX': float(row['maxX']),
                'maxY': float(row['maxY']),
            })
            self._strtree_geoms.append(
                box(float(row['minX']), float(row['minY']),
                    float(row['maxX']), float(row['maxY']))
            )

        if self._strtree_geoms:
            self._strtree = STRtree(self._strtree_geoms)

        self.logger.info(
            f"USGS3DEPProvider: indexed {len(self._tiles)} tiles from {self.manifest_path}"
        )

    def get_provider_kind(self) -> str:
        return 'local_geotiff'

    def get_provider_name(self) -> str:
        return "USGS 3DEP 1m (Local GeoTIFF)"

    def get_datum_info(self) -> dict:
        return {
            'name': 'NAVD88',
            'type': 'orthometric',
            'geoid_model': 'GEOID18',
            'source': 'USGS 3DEP 1m',
            'resolution_m': 1,
            'note': 'EGM96 geoid correction in ADIAT introduces <2m bias vs GEOID18',
        }

    def lookup_tile(self, lat: float, lon: float) -> Optional[dict]:
        """Find the manifest entry whose lat/lon bbox contains the query point."""
        if self._strtree is None:
            return None
        from shapely.geometry import Point
        point = Point(lon, lat)
        # STRtree.query returns indices in shapely 2.x; geoms in 1.x.
        candidates = self._strtree.query(point)
        for c in candidates:
            if hasattr(c, 'contains'):
                geom = c
                idx = self._strtree_geoms.index(geom)
            else:
                idx = int(c)
                geom = self._strtree_geoms[idx]
            if geom.contains(point) or geom.touches(point):
                return self._tiles[idx]
        return None

    def lookup_tiles_bbox(self, min_lon: float, min_lat: float,
                          max_lon: float, max_lat: float) -> list:
        """Return all manifest entries whose lat/lon bbox intersects the query bbox.

        Unlike :meth:`lookup_tile` (a single containing tile for a point), the
        grid path needs every tile overlapping the footprint so the mosaic is
        complete.
        """
        if self._strtree is None:
            return None
        from shapely.geometry import box
        query = box(min_lon, min_lat, max_lon, max_lat)
        candidates = self._strtree.query(query)
        tiles = []
        seen = set()
        for c in candidates:
            # STRtree.query returns geoms in shapely 1.x, indices in 2.x.
            if hasattr(c, 'intersects'):
                geom = c
                idx = self._strtree_geoms.index(geom)
            else:
                idx = int(c)
                geom = self._strtree_geoms[idx]
            if idx in seen:
                continue
            if geom.intersects(query):
                seen.add(idx)
                tiles.append(self._tiles[idx])
        return tiles

    def covers(self, bounds_wgs84) -> str:
        """Coverage of a WGS84 bbox by the indexed tiles: 'full'|'partial'|'none'."""
        from .grid import bbox_coverage
        tiles = self.lookup_tiles_bbox(*bounds_wgs84)
        if not tiles:
            return 'none'
        return bbox_coverage(
            [(t['minX'], t['minY'], t['maxX'], t['maxY']) for t in tiles],
            bounds_wgs84)

    def sample_grid_spec(self, spec):
        """Windowed-reproject fast path: mosaic intersecting tiles onto ``spec``.

        Reprojects each intersecting local GeoTIFF into the requested EPSG:3857
        grid with bilinear resampling, merging first-writer-wins. Returns None
        when no tile intersects or rasterio is unavailable.
        """
        import numpy as np
        from .grid import GridSample

        tiles = self.lookup_tiles_bbox(*spec.wgs84_bounds())
        if not tiles:
            return None

        try:
            import rasterio  # noqa: F401
            from rasterio.warp import reproject, Resampling
        except ImportError as e:
            self.logger.error(f"USGS3DEPProvider: rasterio required for sample_grid_spec: {e}")
            return None

        from .grid import read_window

        dest = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
        merged_any = False
        for tile in tiles:
            ds = self._get_dataset(tile['full_path'])
            if ds is None:
                continue
            src_nodata = ds.nodatavals[0] if ds.nodatavals else None
            # Read only the footprint window so large 3DEP tiles never load in full.
            raw, win_transform = read_window(ds, spec, src_nodata)
            if raw is None:
                continue
            src = raw.astype(np.float32)
            if src_nodata is not None:
                src[src == src_nodata] = np.nan
            tmp = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
            try:
                reproject(
                    source=src,
                    destination=tmp,
                    src_transform=win_transform,
                    src_crs=ds.crs,
                    src_nodata=np.nan,
                    dst_transform=spec.transform,
                    dst_crs=spec.crs,
                    dst_nodata=np.nan,
                    resampling=Resampling.bilinear,
                )
            except Exception as e:
                self.logger.warning(
                    f"USGS3DEPProvider: reproject failed for {tile['filename']}: {e}"
                )
                continue
            dest = np.where(np.isnan(dest), tmp, dest)
            merged_any = True

        if not merged_any:
            return None

        # Mask residual 3DEP nodata sentinels that survived as finite values.
        dest[np.abs(dest) > 1e6] = np.nan

        datum = self.get_datum_info()
        datum_note = f"{datum.get('type', '')} {datum.get('name', '')} ({datum.get('geoid_model', '')})".strip()
        return GridSample(data=dest, transform=spec.transform, crs=spec.crs,
                          datum_note=datum_note)

    def _get_dataset(self, full_path: str):
        """LRU-cached rasterio dataset open."""
        if full_path in self._open_datasets:
            self._open_datasets.move_to_end(full_path)
            return self._open_datasets[full_path]

        try:
            import rasterio
        except ImportError:
            self.logger.error("USGS3DEPProvider: rasterio is required for sampling")
            return None

        try:
            ds = rasterio.open(full_path)
        except Exception as e:
            self.logger.warning(f"USGS3DEPProvider: failed to open {full_path}: {e}")
            return None

        self._open_datasets[full_path] = ds
        if len(self._open_datasets) > self.DATASET_LRU_SIZE:
            _, evicted = self._open_datasets.popitem(last=False)
            try:
                evicted.close()
            except Exception:
                pass
        return ds

    def sample_elevation(self, lat: float, lon: float) -> Optional[float]:
        """Sample orthometric elevation (NAVD88) at lat/lon. Returns None if out of coverage or nodata."""
        tile = self.lookup_tile(lat, lon)
        if tile is None:
            return None

        ds = self._get_dataset(tile['full_path'])
        if ds is None:
            return None

        try:
            from rasterio.warp import transform as rio_transform
        except ImportError:
            return None

        try:
            xs, ys = rio_transform("EPSG:4326", ds.crs, [lon], [lat])
            x, y = xs[0], ys[0]
            row, col = ds.index(x, y)
        except Exception as e:
            self.logger.warning(f"USGS3DEPProvider: reproject/index failed at ({lat},{lon}): {e}")
            return None

        if row < 0 or col < 0 or row >= ds.height or col >= ds.width:
            return None

        try:
            value = self._sample_bilinear(ds, x, y)
        except Exception as e:
            self.logger.warning(f"USGS3DEPProvider: sample failed at ({lat},{lon}): {e}")
            return None

        if value is None:
            return None

        nodata = ds.nodatavals[0] if ds.nodatavals else None
        if nodata is not None and value == nodata:
            return None
        # Common nodata sentinels for 3DEP DEMs
        if value < -1e6 or value > 1e6:
            return None

        return float(value)

    @staticmethod
    def _sample_bilinear(ds, x: float, y: float) -> Optional[float]:
        """Bilinear sample of the first band at projected coordinate (x, y)."""
        from rasterio.windows import Window
        # Convert projected (x, y) to fractional (row, col)
        col_f, row_f = ~ds.transform * (x, y)
        col_i = int(col_f)
        row_i = int(row_f)
        fx = col_f - col_i
        fy = row_f - row_i

        if row_i < 0 or col_i < 0 or row_i + 1 >= ds.height or col_i + 1 >= ds.width:
            # Fall back to nearest in-bounds pixel
            col_i = max(0, min(col_i, ds.width - 1))
            row_i = max(0, min(row_i, ds.height - 1))
            arr = ds.read(1, window=Window(col_i, row_i, 1, 1))
            if arr.size == 0:
                return None
            return float(arr[0, 0])

        arr = ds.read(1, window=Window(col_i, row_i, 2, 2))
        if arr.size == 0:
            return None

        e00 = float(arr[0, 0])
        e10 = float(arr[0, 1])
        e01 = float(arr[1, 0])
        e11 = float(arr[1, 1])
        e0 = e00 * (1 - fx) + e10 * fx
        e1 = e01 * (1 - fx) + e11 * fx
        return e0 * (1 - fy) + e1 * fy

    def close(self):
        """Close all cached open datasets."""
        for ds in self._open_datasets.values():
            try:
                ds.close()
            except Exception:
                pass
        self._open_datasets.clear()
