"""
CanopyService - local-GeoTIFF canopy provider for the Coverage/POD pipeline.

Clones the USGS3DEPProvider structure (manifest CSV -> STRtree bbox index ->
LRU of open rasterio datasets) but returns a two-band ``CanopySample`` (canopy
height + cover fraction) co-registered to the DEM's GridSpec so the ray-march
kernel indexes DEM/CHM/cover identically.

Supported tile products (a per-tile ``product`` column in the manifest):
  * landfire_evh    - LANDFIRE Existing Vegetation Height class codes -> meters
  * landfire_evc    - LANDFIRE Existing Vegetation Cover class codes -> fraction
  * landfire_cc_pct - plain percent canopy cover (0-100) -> fraction
  * meta_chm        - Meta/WRI continuous canopy height (meters); cover derived

Class codes are decoded to physical units on the source tile FIRST, then
bilinearly resampled (interpolating raw categorical codes would be meaningless).
Canopy height is above-ground by construction, so no geoid/datum handling.
"""

from collections import OrderedDict
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import numpy as np

from core.services.LoggerService import LoggerService

KIND_LANDFIRE = 'landfire'
KIND_META = 'meta'

PRODUCT_EVH = 'landfire_evh'
PRODUCT_EVC = 'landfire_evc'
PRODUCT_CC_PCT = 'landfire_cc_pct'
PRODUCT_META_CHM = 'meta_chm'

_HEIGHT_PRODUCTS = {PRODUCT_EVH, PRODUCT_META_CHM}
_COVER_PRODUCTS = {PRODUCT_EVC, PRODUCT_CC_PCT}


@dataclass
class CanopySample:
    chm: np.ndarray        # (rows, cols) float32, canopy height above ground in meters
    cover: np.ndarray      # (rows, cols) float32, cover fraction 0-1
    transform: object      # affine.Affine (== spec.transform)
    crs: str
    cover_derived: bool    # True when cover was synthesized from CHM (stopgap)
    source_name: str
    # (rows, cols) bool: cells the tiles actually provided data for. Captured
    # BEFORE uncovered cells are filled with 0 height, so callers can tell
    # "no canopy tile here" (overstates POD -> no attenuation) from a genuine
    # bare-ground 0. None on legacy samples.
    covered: object = None


def evh_code_to_meters(codes: np.ndarray) -> np.ndarray:
    """LANDFIRE EVH class codes -> canopy height (meters), NaN for fill/nodata.

    Tree 101-199 -> code-100; shrub 201-299 -> (code-200)*0.1;
    herb 301-310 -> (code-300)*0.1; non-veg/sparse -> 0; 99 or <0 -> NaN.
    """
    c = codes.astype(np.float64)
    out = np.zeros(c.shape, dtype=np.float32)
    tree = (c >= 101) & (c <= 199)
    shrub = (c >= 201) & (c <= 299)
    herb = (c >= 301) & (c <= 310)
    out[tree] = (c[tree] - 100.0).astype(np.float32)
    out[shrub] = ((c[shrub] - 200.0) * 0.1).astype(np.float32)
    out[herb] = ((c[herb] - 300.0) * 0.1).astype(np.float32)
    out[(c == 99) | (c < 0)] = np.nan
    return out


def evc_code_to_fraction(codes: np.ndarray) -> np.ndarray:
    """LANDFIRE EVC class codes -> cover fraction 0-1, NaN for fill/nodata.

    Tree 110-199, shrub 210-299, herb 310-399 encode cover percent as
    (code - lifeform_base); non-veg/sparse -> 0; fill/<100 sentinels -> NaN.
    """
    c = codes.astype(np.float64)
    out = np.zeros(c.shape, dtype=np.float32)
    tree = (c >= 110) & (c <= 199)
    shrub = (c >= 210) & (c <= 299)
    herb = (c >= 310) & (c <= 399)
    out[tree] = ((c[tree] - 100.0) / 100.0).astype(np.float32)
    out[shrub] = ((c[shrub] - 200.0) / 100.0).astype(np.float32)
    out[herb] = ((c[herb] - 300.0) / 100.0).astype(np.float32)
    out = np.clip(out, 0.0, 1.0)
    out[(c == 99) | (c < 0)] = np.nan
    return out


class CanopyService:
    DATASET_LRU_SIZE = 16

    def __init__(self, manifest_csv: str, tiles_dir: str, kind: str = KIND_LANDFIRE,
                 h_ref_m: float = 20.0, c_max: float = 0.9,
                 logger: Optional[LoggerService] = None):
        """
        Args:
            manifest_csv: CSV with columns filename, product, minX, minY, maxX, maxY
                (WGS84 bboxes). A missing 'product' column falls back to ``kind``.
            tiles_dir: folder holding the GeoTIFFs referenced by 'filename'.
            kind: default product family ('landfire' or 'meta') when the manifest
                omits a per-tile product column.
            h_ref_m/c_max: CHM->cover stopgap (cover ~ clip(chm/h_ref,0,1)*c_max).
        """
        self.logger = logger or LoggerService()
        self.manifest_path = Path(manifest_csv)
        self.tiles_dir = Path(tiles_dir)
        self.kind = kind
        self.h_ref_m = float(h_ref_m)
        self.c_max = float(c_max)
        self._tiles = []            # {filename, full_path, product, minX..maxY}
        self._strtree = None
        self._strtree_geoms = []
        self._open_datasets: "OrderedDict[str, object]" = OrderedDict()
        self._load_manifest()

    @property
    def source_name(self) -> str:
        if self.kind == KIND_META:
            return "Meta/WRI Canopy Height 1m (cover derived)"
        return "LANDFIRE EVH+EVC 30m"

    def _default_product(self) -> str:
        return PRODUCT_META_CHM if self.kind == KIND_META else PRODUCT_EVH

    def _load_manifest(self):
        try:
            import pandas as pd
            from shapely.geometry import box
            from shapely.strtree import STRtree
        except ImportError as e:
            self.logger.error(f"CanopyService missing dependency: {e}")
            return

        if not self.manifest_path.is_file():
            self.logger.error(f"CanopyService: manifest not found at {self.manifest_path}")
            return

        try:
            df = pd.read_csv(self.manifest_path)
        except Exception as e:
            self.logger.error(f"CanopyService: failed to read manifest: {e}")
            return

        required = {'filename', 'minX', 'minY', 'maxX', 'maxY'}
        missing = required - set(df.columns)
        if missing:
            self.logger.error(f"CanopyService: manifest missing required columns {missing}")
            return

        has_product = 'product' in df.columns
        if not has_product and self.kind == KIND_LANDFIRE:
            self.logger.error(
                "CanopyService: LANDFIRE manifest missing the 'product' column; "
                "EVH and EVC tiles are indistinguishable. Refusing to load.")
            return

        for _, row in df.iterrows():
            filename = str(row['filename'])
            product = str(row['product']) if has_product else self._default_product()
            self._tiles.append({
                'filename': filename,
                'full_path': str(self.tiles_dir / filename),
                'product': product,
                'minX': float(row['minX']), 'minY': float(row['minY']),
                'maxX': float(row['maxX']), 'maxY': float(row['maxY']),
            })
            self._strtree_geoms.append(
                box(float(row['minX']), float(row['minY']),
                    float(row['maxX']), float(row['maxY'])))

        if self._strtree_geoms:
            self._strtree = STRtree(self._strtree_geoms)
        self.logger.info(
            f"CanopyService: indexed {len(self._tiles)} tiles from {self.manifest_path}")

    def lookup_tiles_bbox(self, min_lon, min_lat, max_lon, max_lat) -> list:
        if self._strtree is None:
            return None
        from shapely.geometry import box
        query = box(min_lon, min_lat, max_lon, max_lat)
        candidates = self._strtree.query(query)
        tiles = []
        seen = set()
        for c in candidates:
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

    def _get_dataset(self, full_path: str):
        if full_path in self._open_datasets:
            self._open_datasets.move_to_end(full_path)
            return self._open_datasets[full_path]
        try:
            import rasterio
        except ImportError:
            self.logger.error("CanopyService: rasterio is required for sampling")
            return None
        try:
            ds = rasterio.open(full_path)
        except Exception as e:
            self.logger.warning(f"CanopyService: failed to open {full_path}: {e}")
            return None
        self._open_datasets[full_path] = ds
        if len(self._open_datasets) > self.DATASET_LRU_SIZE:
            _, evicted = self._open_datasets.popitem(last=False)
            try:
                evicted.close()
            except Exception:
                pass
        return ds

    @staticmethod
    def _decode(product: str, raw: np.ndarray, nodata) -> np.ndarray:
        """Decode a source tile's raw band to physical units (meters or fraction)."""
        arr = raw.astype(np.float32)
        if product == PRODUCT_EVH:
            return evh_code_to_meters(arr)
        if product == PRODUCT_EVC:
            return evc_code_to_fraction(arr)
        if product == PRODUCT_CC_PCT:
            out = np.clip(arr, 0.0, 100.0) / 100.0
            out[arr < 0] = np.nan
            return out.astype(np.float32)
        # meta_chm: continuous meters, clamp and drop negatives/nodata.
        out = arr.copy()
        if nodata is not None:
            out[out == nodata] = np.nan
        out[out < 0] = np.nan
        return np.clip(out, 0.0, 60.0).astype(np.float32)

    def sample_grid_spec(self, spec) -> Optional[CanopySample]:
        """Return a CanopySample co-registered to ``spec``, or None if no tile
        intersects the footprint."""
        tiles = self.lookup_tiles_bbox(*spec.wgs84_bounds())
        if not tiles:
            return None
        try:
            import rasterio  # noqa: F401
            from rasterio.warp import reproject, Resampling
        except ImportError as e:
            self.logger.error(f"CanopyService: rasterio required for sample_grid_spec: {e}")
            return None

        chm = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
        cover = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
        covered = np.zeros((spec.height, spec.width), dtype=bool)
        got_height = got_cover = False

        for tile in tiles:
            ds = self._get_dataset(tile['full_path'])
            if ds is None:
                continue
            product = tile['product']
            nodata = ds.nodatavals[0] if ds.nodatavals else None
            try:
                # Read ONLY the window under the footprint. Meta/WRI canopy COGs
                # are ~65536x65536 (16 GB) -- a full ds.read(1) would OOM; the
                # windowed read touches only the AOI.
                from core.services.terrain.grid import read_window
                raw, win_transform = read_window(ds, spec, nodata)
                if raw is None:
                    continue
                src = self._decode(product, raw, nodata)
            except Exception as e:
                self.logger.warning(f"CanopyService: decode failed for {tile['filename']}: {e}")
                continue
            target = chm if product in _HEIGHT_PRODUCTS else cover
            tmp = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
            try:
                reproject(
                    source=src, destination=tmp,
                    src_transform=win_transform, src_crs=ds.crs, src_nodata=np.nan,
                    dst_transform=spec.transform, dst_crs=spec.crs, dst_nodata=np.nan,
                    resampling=Resampling.bilinear)
            except Exception as e:
                self.logger.warning(f"CanopyService: reproject failed for {tile['filename']}: {e}")
                continue
            merged = np.where(np.isnan(target) & ~np.isnan(tmp), tmp, target)
            covered |= np.isfinite(tmp)
            if product in _HEIGHT_PRODUCTS:
                chm = merged
                got_height = True
            else:
                cover = merged
                got_cover = True

        if not (got_height or got_cover):
            return None

        # No-canopy cells default to 0 height (L_eff == 0 -> transmittance 1).
        chm = np.where(np.isnan(chm), 0.0, chm).astype(np.float32)

        cover_derived = False
        if not got_cover or np.isnan(cover).all():
            cover = np.clip(chm / self.h_ref_m, 0.0, 1.0) * self.c_max
            cover_derived = True
        else:
            # Derive only where cover is missing but canopy is present.
            need = np.isnan(cover) & (chm > 0)
            if need.any():
                cover = cover.copy()
                cover[need] = np.clip(chm[need] / self.h_ref_m, 0.0, 1.0) * self.c_max
                cover_derived = True
            cover = np.where(np.isnan(cover), 0.0, cover)
        cover = cover.astype(np.float32)

        return CanopySample(chm=chm, cover=cover, transform=spec.transform,
                            crs=spec.crs, cover_derived=cover_derived,
                            source_name=self.source_name, covered=covered)

    def reset(self):
        self.close()

    def close(self):
        for ds in self._open_datasets.values():
            try:
                ds.close()
            except Exception:
                pass
        self._open_datasets.clear()
