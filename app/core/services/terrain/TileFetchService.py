"""
TileFetchService - download DEM / canopy tiles for an AOI and write the manifest.

* USGS 3DEP DEM  - ArcGIS ImageServer exportImage, tiled to keep each request
  under a pixel cap; writes GeoTIFF tiles + the manifest the USGS3DEPProvider
  reads. (No API key.)
* Meta/WRI CHM   - Bing-quadkey z9 COG tiles from the public S3 bucket. A whole
  z9 COG is enormous (~765 MB for a populated tile), so the fetch prefers a
  **windowed** rasterio ``/vsicurl`` read that clips just the AOI (KB-MB moved,
  not the whole file) and writes a small local GeoTIFF whose manifest bbox is
  the clip's true extent. If GDAL range reads are unavailable the fetch falls
  back to a **streamed** whole-file download with chunked byte progress and
  mid-transfer cancellation -- never a blocking whole-body ``resp.content``.

Outcome semantics: HTTP 403/404 means the tile legitimately does not exist
(sparse coverage) and is counted as *skipped*; every other failure (timeouts,
resets, exhausted retries) is counted as *failed* with an ``errors`` entry so
callers can tell "no data there" from "the download broke".

Network / file I/O only; no Qt. A ``requests.Session`` may be injected for
tests (an injected session also forces the HTTP path so tests never touch
GDAL's network stack).
"""

import csv
import hashlib
import math
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from core.services.LoggerService import LoggerService

# Outcome constants for a single tile transfer.
OUTCOME_OK = 'ok'
OUTCOME_ABSENT = 'absent'        # confirmed 403/404 -> sparse coverage, benign
OUTCOME_FAILED = 'failed'        # anything else -> a real failure to surface
OUTCOME_CANCELLED = 'cancelled'


def _platform_data_root() -> Path:
    """Per-user application-data folder following each OS's convention."""
    import sys
    if sys.platform == 'win32':
        base = os.environ.get('LOCALAPPDATA')
        if base:
            return Path(base) / 'ADIAT'
    elif sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'ADIAT'
    else:
        xdg = os.environ.get('XDG_DATA_HOME')
        base = Path(xdg) if xdg else Path.home() / '.local' / 'share'
        return base / 'adiat'
    return Path.home() / '.adiat'


# Central tile library: the default download destination. Unlike a mission's
# results folder it is stable and mission-independent, so downloads accumulate
# (manifests merge) instead of each mission's registration replacing the last.
# Lives in the platform's standard per-user app-data location.
DEFAULT_LIBRARY_ROOT = _platform_data_root() / 'terrain_library'

# Pre-standard-paths location; still served if it already holds tiles.
LEGACY_LIBRARY_ROOT = Path.home() / '.adiat' / 'terrain_library'


def library_root() -> str:
    """The central tile-library folder (created on demand by the fetch).

    An existing, non-empty legacy library keeps being used so previously
    downloaded tiles are never stranded by the default moving.
    """
    try:
        if LEGACY_LIBRARY_ROOT.is_dir() and any(LEGACY_LIBRARY_ROOT.iterdir()):
            return str(LEGACY_LIBRARY_ROOT)
    except OSError:
        pass
    return str(DEFAULT_LIBRARY_ROOT)


@dataclass
class FetchResult:
    product: str
    out_dir: str
    manifest_path: Optional[str]
    tiles_written: int = 0
    tiles_failed: int = 0
    tiles_skipped: int = 0
    errors: List[Tuple[str, str]] = field(default_factory=list)
    cancelled: bool = False


class TileFetchService:
    META_CHM_URL = ("https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/"
                    "alsgedi_global_v6_float/chm/{quadkey}.tif")
    DEP_EXPORT_URL = ("https://elevation.nationalmap.gov/arcgis/rest/services/"
                      "3DEPElevation/ImageServer/exportImage")
    MAX_RETRIES = 4
    BACKOFF_MS = 300
    METERS_PER_DEG = 111320.0

    def __init__(self, logger: Optional[LoggerService] = None, session=None,
                 timeout: float = 60.0, backoff_ms: Optional[int] = None):
        self.logger = logger or LoggerService()
        self._session = session
        # Record whether the caller supplied the session. The lazily created
        # internal session must NOT count as "injected": the DEM phase creates
        # it before the canopy phase runs, and keying windowed-vs-HTTP off
        # `_session is None` made the canopy fetch silently fall back to the
        # whole-~765 MB download whenever DEM ran first.
        self._session_injected = session is not None
        self.timeout = timeout
        self.backoff_ms = self.BACKOFF_MS if backoff_ms is None else backoff_ms

    @property
    def session(self):
        if self._session is None:
            import requests
            self._session = requests.Session()
            self._session.headers.update({'User-Agent': 'ADIAT/1.0 (Drone Image Analysis Tool)'})
        return self._session

    # ---- slippy / quadkey math ----

    @staticmethod
    def lnglat_to_tile_xy(lon: float, lat: float, z: int) -> Tuple[int, int]:
        lat_rad = math.radians(lat)
        n = 2 ** z
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        x = max(0, min(x, n - 1))
        y = max(0, min(y, n - 1))
        return x, y

    @staticmethod
    def tile_xy_to_quadkey(x: int, y: int, z: int) -> str:
        qk = []
        for i in range(z, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if x & mask:
                digit += 1
            if y & mask:
                digit += 2
            qk.append(str(digit))
        return "".join(qk)

    @staticmethod
    def tile_xy_to_bounds(x: int, y: int, z: int) -> Tuple[float, float, float, float]:
        n = 2.0 ** z
        lon0 = x / n * 360.0 - 180.0
        lon1 = (x + 1) / n * 360.0 - 180.0
        lat1 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        lat0 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
        return (lon0, lat0, lon1, lat1)

    @classmethod
    def tiles_covering_bbox(cls, bounds_wgs84, z: int) -> List[Tuple[int, int]]:
        min_lon, min_lat, max_lon, max_lat = bounds_wgs84
        x0, y0 = cls.lnglat_to_tile_xy(min_lon, max_lat, z)   # NW
        x1, y1 = cls.lnglat_to_tile_xy(max_lon, min_lat, z)   # SE
        tiles = []
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                tiles.append((x, y))
        return tiles

    # ---- HTTP ----

    def _http_get(self, url, params=None, cancel_check=None):
        """GET with linear backoff. Returns (outcome, bytes-or-None).

        Distinguishes a confirmed-absent tile (403/404 -> OUTCOME_ABSENT) from a
        genuine failure (exceptions / other statuses / exhausted retries ->
        OUTCOME_FAILED). Only network-ish exceptions are retried; a MemoryError
        from buffering a huge body must NOT trigger a re-download.
        """
        for attempt in range(self.MAX_RETRIES):
            if cancel_check and cancel_check():
                return OUTCOME_CANCELLED, None
            if attempt > 0 and self.backoff_ms:
                time.sleep(self.backoff_ms * attempt / 1000.0)
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
            except MemoryError:
                self.logger.error(f"TileFetch: out of memory buffering {url}")
                return OUTCOME_FAILED, None
            except Exception as e:
                self.logger.warning(f"TileFetch: request error {url}: {e}")
                continue
            if resp.status_code == 200:
                return OUTCOME_OK, resp.content
            if resp.status_code in (403, 404):
                return OUTCOME_ABSENT, None
            self.logger.warning(f"TileFetch: HTTP {resp.status_code} for {url}")
        return OUTCOME_FAILED, None

    def _get_with_retry(self, url, params=None):
        """Back-compat wrapper: bytes on success, None for absent OR failed."""
        _, content = self._http_get(url, params=params)
        return content

    def _stream_to_file(self, url, dest_path, progress_callback=None,
                        cancel_check=None, label=""):
        """Stream a (potentially huge) file to disk in chunks. Returns an
        OUTCOME_* constant.

        Chunked writes keep memory flat, report byte progress (MB), and honor
        cancellation between chunks -- a whole z9 canopy COG can be ~765 MB, so
        a blocking ``resp.content`` here is exactly the freeze this replaces.
        A partial file is deleted on cancel/failure.
        """
        for attempt in range(self.MAX_RETRIES):
            if cancel_check and cancel_check():
                return OUTCOME_CANCELLED
            if attempt > 0 and self.backoff_ms:
                time.sleep(self.backoff_ms * attempt / 1000.0)
            try:
                # Injected test sessions may not accept stream=; fall back to a
                # plain GET (their bodies are tiny in-memory fixtures anyway).
                try:
                    resp = self.session.get(url, timeout=self.timeout, stream=True)
                except TypeError:
                    resp = self.session.get(url, timeout=self.timeout)
            except MemoryError:
                # Buffering a huge body OOM'd; retrying would just re-download
                # hundreds of MB into the same wall.
                self.logger.error(f"TileFetch: out of memory requesting {url}")
                return OUTCOME_FAILED
            except Exception as e:
                self.logger.warning(f"TileFetch: request error {url}: {e}")
                continue

            if resp.status_code in (403, 404):
                return OUTCOME_ABSENT
            if resp.status_code != 200:
                self.logger.warning(f"TileFetch: HTTP {resp.status_code} for {url}")
                continue

            total_bytes = 0
            try:
                total_bytes = int(getattr(resp, 'headers', {}).get('Content-Length', 0))
            except (TypeError, ValueError):
                total_bytes = 0
            total_mb = max(1, round(total_bytes / (1024 * 1024))) if total_bytes else 0

            try:
                with open(dest_path, 'wb') as fh:
                    if hasattr(resp, 'iter_content'):
                        written = 0
                        for chunk in resp.iter_content(chunk_size=1024 * 1024):
                            if cancel_check and cancel_check():
                                try:
                                    resp.close()
                                except Exception:
                                    pass
                                fh.close()
                                Path(dest_path).unlink(missing_ok=True)
                                return OUTCOME_CANCELLED
                            if not chunk:
                                continue
                            fh.write(chunk)
                            written += len(chunk)
                            if progress_callback:
                                done_mb = round(written / (1024 * 1024))
                                progress_callback(
                                    min(done_mb, total_mb) if total_mb else done_mb,
                                    total_mb,
                                    f"{label} — {done_mb} of {total_mb} MB..." if total_mb
                                    else f"{label} — {done_mb} MB...")
                    else:
                        fh.write(resp.content)
                return OUTCOME_OK
            except MemoryError:
                self.logger.error(f"TileFetch: out of memory streaming {url}")
                Path(dest_path).unlink(missing_ok=True)
                return OUTCOME_FAILED
            except Exception as e:
                # Mid-body failure: do NOT restart a multi-hundred-MB transfer
                # MAX_RETRIES times; surface it as a failure.
                self.logger.warning(f"TileFetch: streaming failed for {url}: {e}")
                Path(dest_path).unlink(missing_ok=True)
                return OUTCOME_FAILED
        return OUTCOME_FAILED

    # ---- windowed COG clip (canopy) ----

    CLIP_PAD_DEG = 300.0 / 111320.0   # ~300 m so padded overlay extents stay covered

    def _fetch_canopy_tile_windowed(self, x, y, zoom, bounds_wgs84, out_dir):
        """Clip just the AOI from a remote canopy COG via rasterio /vsicurl.

        Downloads only the HTTP ranges GDAL needs (KB-MB) instead of the whole
        ~765 MB tile. Returns (filename, (minX, minY, maxX, maxY)) for the
        manifest, or raises on any failure (caller falls back to streaming).
        """
        import numpy as np
        import rasterio
        from rasterio.windows import from_bounds, Window
        from rasterio.transform import array_bounds

        qk = self.tile_xy_to_quadkey(x, y, zoom)
        url = self.META_CHM_URL.format(quadkey=qk)

        # Pad the AOI, then clamp to this tile's own extent.
        min_lon, min_lat, max_lon, max_lat = bounds_wgs84
        t_lon0, t_lat0, t_lon1, t_lat1 = self.tile_xy_to_bounds(x, y, zoom)
        w = max(min_lon - self.CLIP_PAD_DEG, t_lon0)
        e = min(max_lon + self.CLIP_PAD_DEG, t_lon1)
        s = max(min_lat - self.CLIP_PAD_DEG, t_lat0)
        n = min(max_lat + self.CLIP_PAD_DEG, t_lat1)
        if w >= e or s >= n:
            raise ValueError("AOI does not intersect tile")

        env = rasterio.Env(
            GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',
            CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',
            GDAL_HTTP_CONNECTTIMEOUT='30',
            GDAL_HTTP_TIMEOUT=str(int(self.timeout)),
        )
        with env:
            with rasterio.open('/vsicurl/' + url) as ds:
                from rasterio.warp import transform_bounds
                src_bounds = transform_bounds('EPSG:4326', ds.crs, w, s, e, n)
                win = from_bounds(*src_bounds, transform=ds.transform)
                win = win.round_offsets().round_lengths()
                # Clamp to the dataset so the clip transform is exact.
                col0 = max(0, int(win.col_off))
                row0 = max(0, int(win.row_off))
                col1 = min(ds.width, int(win.col_off + win.width))
                row1 = min(ds.height, int(win.row_off + win.height))
                if col1 <= col0 or row1 <= row0:
                    raise ValueError("window outside dataset")
                win = Window(col0, row0, col1 - col0, row1 - row0)
                data = ds.read(1, window=win)
                clip_transform = ds.window_transform(win)
                profile = {
                    'driver': 'GTiff', 'height': data.shape[0], 'width': data.shape[1],
                    'count': 1, 'dtype': data.dtype, 'crs': ds.crs,
                    'transform': clip_transform, 'compress': 'deflate',
                }
                nodata = ds.nodatavals[0] if ds.nodatavals else None
                if nodata is not None and np.isfinite(nodata):
                    profile['nodata'] = nodata

        # Deterministic per-AOI clip name: same AOI overwrites its own clip,
        # a different AOI adds a new one (manifest merges by filename).
        digest = hashlib.md5(
            f"{w:.6f}_{s:.6f}_{e:.6f}_{n:.6f}".encode()).hexdigest()[:8]
        filename = f"chm_{qk}_clip_{digest}.tif"
        with rasterio.open(os.path.join(out_dir, filename), 'w', **profile) as out:
            out.write(data, 1)

        # Manifest bbox = the clip's true extent (in the tile's CRS -> WGS84).
        from rasterio.warp import transform_bounds as tb
        cb = array_bounds(data.shape[0], data.shape[1], clip_transform)
        lon0, lat0, lon1, lat1 = tb(profile['crs'], 'EPSG:4326', *cb)
        return filename, (lon0, lat0, lon1, lat1)

    @staticmethod
    def _write_manifest(rows, manifest_path, include_product):
        fields = ['filename']
        if include_product:
            fields.append('product')
        fields += ['minX', 'minY', 'maxX', 'maxY']
        # Merge with any existing manifest (dedupe by filename) for incremental AOIs.
        existing = {}
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, newline='') as fh:
                    for r in csv.DictReader(fh):
                        existing[r['filename']] = r
            except Exception:
                existing = {}
        for r in rows:
            existing[r['filename']] = r
        with open(manifest_path, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in existing.values():
                w.writerow({k: r.get(k, '') for k in fields})

    # ---- 3DEP DEM ----

    def fetch_3dep_dem(self, bounds_wgs84, out_dir, image_sr: int = 4326,
                       tile_px: int = 2048, native_res_m: float = 1.0,
                       progress_callback=None, cancel_check=None) -> FetchResult:
        min_lon, min_lat, max_lon, max_lat = bounds_wgs84
        os.makedirs(out_dir, exist_ok=True)
        mid_lat = (min_lat + max_lat) / 2.0
        m_per_deg_lon = self.METERS_PER_DEG * max(0.05, math.cos(math.radians(mid_lat)))

        # Ground span of one sub-tile at the target resolution.
        dlat_tile = tile_px * native_res_m / self.METERS_PER_DEG
        dlon_tile = tile_px * native_res_m / m_per_deg_lon
        n_x = max(1, math.ceil((max_lon - min_lon) / dlon_tile))
        n_y = max(1, math.ceil((max_lat - min_lat) / dlat_tile))

        result = FetchResult(product='usgs_3dep_dem', out_dir=out_dir, manifest_path=None)
        rows = []
        total = n_x * n_y
        done = 0
        # Per-AOI digest in the tile names so different AOIs sharing one folder
        # (the central library) never overwrite each other's files; the same
        # AOI re-downloaded overwrites its own tiles (idempotent), mirroring
        # the canopy clip naming. Old digest-less names remain readable via
        # their manifest rows.
        aoi_digest = hashlib.md5(
            f"{min_lon:.6f}_{min_lat:.6f}_{max_lon:.6f}_{max_lat:.6f}".encode()
        ).hexdigest()[:8]
        for j in range(n_y):
            for i in range(n_x):
                if cancel_check and cancel_check():
                    result.cancelled = True
                    return result
                w = min_lon + i * dlon_tile
                e = min(max_lon, w + dlon_tile)
                s = min_lat + j * dlat_tile
                north = min(max_lat, s + dlat_tile)
                cols = max(1, min(tile_px, round((e - w) * m_per_deg_lon / native_res_m)))
                rows_px = max(1, min(tile_px, round((north - s) * self.METERS_PER_DEG / native_res_m)))
                params = {
                    'bbox': f"{w},{s},{e},{north}", 'bboxSR': 4326, 'imageSR': image_sr,
                    'size': f"{cols},{rows_px}", 'format': 'tiff', 'pixelType': 'F32',
                    'interpolation': 'RSP_BilinearInterpolation', 'f': 'image',
                }
                filename = f"dem_{aoi_digest}_{j}_{i}.tif"
                # Announce the tile BEFORE the transfer so the UI shows activity
                # while the request is in flight.
                if progress_callback:
                    progress_callback(done, total,
                                      f"Downloading DEM tile {done + 1}/{total}...")
                outcome, content = self._http_get(self.DEP_EXPORT_URL, params=params,
                                                  cancel_check=cancel_check)
                if outcome == OUTCOME_CANCELLED:
                    result.cancelled = True
                    return result
                if content is None:
                    # one blind retry (endpoint occasionally 502s)
                    outcome, content = self._http_get(self.DEP_EXPORT_URL, params=params,
                                                      cancel_check=cancel_check)
                    if outcome == OUTCOME_CANCELLED:
                        result.cancelled = True
                        return result
                if content is None:
                    result.tiles_failed += 1
                    result.errors.append((filename, "download failed"))
                else:
                    Path(out_dir, filename).write_bytes(content)
                    rows.append({'filename': filename, 'minX': w, 'minY': s,
                                 'maxX': e, 'maxY': north})
                    result.tiles_written += 1
                done += 1
                if progress_callback:
                    progress_callback(done, total, f"Downloading DEM tile {done}/{total}...")

        if rows:
            manifest = os.path.join(out_dir, "dem_manifest.csv")
            self._write_manifest(rows, manifest, include_product=False)
            result.manifest_path = manifest
        return result

    # ---- Meta/WRI canopy ----

    def fetch_meta_canopy(self, bounds_wgs84, out_dir, zoom: int = 9,
                          progress_callback=None, cancel_check=None,
                          use_windowed: Optional[bool] = None) -> FetchResult:
        """Fetch Meta/WRI canopy for the AOI.

        Prefers a windowed /vsicurl clip of just the AOI (a whole z9 COG can be
        ~765 MB; the clip moves KB-MB). Falls back to a streamed whole-file
        download with byte progress and mid-transfer cancel. ``use_windowed``
        defaults to auto: windowed unless a custom session was injected (tests
        drive the HTTP path with in-memory bodies and must not touch GDAL).
        """
        os.makedirs(out_dir, exist_ok=True)
        tiles = self.tiles_covering_bbox(bounds_wgs84, zoom)
        result = FetchResult(product='meta_chm', out_dir=out_dir, manifest_path=None)
        rows = []
        total = len(tiles)
        if use_windowed is None:
            # Keyed off *injection*, not existence: fetch_3dep_dem lazily
            # creates the internal session, and that must not disable the clip.
            use_windowed = not self._session_injected

        for done, (x, y) in enumerate(tiles, start=1):
            if cancel_check and cancel_check():
                result.cancelled = True
                return result
            qk = self.tile_xy_to_quadkey(x, y, zoom)
            url = self.META_CHM_URL.format(quadkey=qk)
            filename = f"chm_{qk}.tif"
            # Announce the tile BEFORE the transfer so the UI never sits on a
            # stale message while a long download runs.
            if progress_callback:
                progress_callback(done - 1, total,
                                  f"Downloading canopy tile {done}/{total}...")

            outcome = None
            if use_windowed:
                # Cheap absence probe first: a 403/404 is sparse coverage, and
                # probing avoids burying "absent" inside a GDAL open error.
                probe, _ = self._probe_absent(url)
                if probe == OUTCOME_ABSENT:
                    outcome = OUTCOME_ABSENT
                else:
                    try:
                        filename, clip_bounds = self._fetch_canopy_tile_windowed(
                            x, y, zoom, bounds_wgs84, out_dir)
                        rows.append({'filename': filename, 'product': 'meta_chm',
                                     'minX': clip_bounds[0], 'minY': clip_bounds[1],
                                     'maxX': clip_bounds[2], 'maxY': clip_bounds[3]})
                        result.tiles_written += 1
                        outcome = OUTCOME_OK
                    except Exception as e:
                        self.logger.warning(
                            f"TileFetch: windowed canopy clip failed for {qk} ({e}); "
                            "falling back to full-tile download")
                        outcome = None  # fall through to streaming

            if outcome is None:
                outcome = self._stream_to_file(
                    url, os.path.join(out_dir, filename),
                    progress_callback=progress_callback, cancel_check=cancel_check,
                    label=f"Downloading canopy tile {done}/{total}")
                if outcome == OUTCOME_OK:
                    lon0, lat0, lon1, lat1 = self.tile_xy_to_bounds(x, y, zoom)
                    rows.append({'filename': filename, 'product': 'meta_chm',
                                 'minX': lon0, 'minY': lat0, 'maxX': lon1, 'maxY': lat1})
                    result.tiles_written += 1

            if outcome == OUTCOME_CANCELLED:
                result.cancelled = True
                break
            if outcome == OUTCOME_ABSENT:
                result.tiles_skipped += 1
            elif outcome == OUTCOME_FAILED:
                result.tiles_failed += 1
                result.errors.append((filename, "download failed"))
            if progress_callback:
                progress_callback(done, total,
                                  f"Downloading canopy tile {done}/{total}...")

        if rows:
            manifest = os.path.join(out_dir, "chm_manifest.csv")
            self._write_manifest(rows, manifest, include_product=True)
            result.manifest_path = manifest
        return result

    def _probe_absent(self, url):
        """HEAD probe classifying a tile as absent (403/404) vs present/unknown.

        Returns (outcome, content-length-or-None). Any probe error returns
        (OUTCOME_OK, None) -- i.e. "assume present", letting the real transfer
        classify definitively.
        """
        try:
            head = getattr(self.session, 'head', None)
            if head is None:
                return OUTCOME_OK, None
            resp = head(url, timeout=min(self.timeout, 20.0))
            if resp.status_code in (403, 404):
                return OUTCOME_ABSENT, None
            length = None
            try:
                length = int(getattr(resp, 'headers', {}).get('Content-Length', 0)) or None
            except (TypeError, ValueError):
                pass
            return OUTCOME_OK, length
        except Exception:
            return OUTCOME_OK, None
