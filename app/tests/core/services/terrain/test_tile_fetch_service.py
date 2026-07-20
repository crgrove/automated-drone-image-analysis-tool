"""Tests for TileFetchService (quadkey math + mocked 3DEP / Meta downloads)."""

import csv
import os

import pytest

from core.services.terrain.TileFetchService import TileFetchService


class _Resp:
    def __init__(self, status, content=b"TILE"):
        self.status_code = status
        self.content = content


class _Session:
    def __init__(self, handler):
        self._handler = handler
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        return self._handler(url, params, len(self.calls))


def _svc(handler):
    return TileFetchService(session=_Session(handler), backoff_ms=0)


# --- quadkey / tiling math ---

def test_quadkey_known_value():
    # Bing docs example: tile (3, 5) at z=3 -> "213".
    assert TileFetchService.tile_xy_to_quadkey(3, 5, 3) == "213"
    assert len(TileFetchService.tile_xy_to_quadkey(10, 20, 9)) == 9


def test_tiles_covering_bbox_count():
    tiles = TileFetchService.tiles_covering_bbox((-120.5, 38.7, -120.48, 38.72), 9)
    assert len(tiles) >= 1
    # A tiny AOI at z9 sits in one or two tiles.
    assert len(tiles) <= 4


def test_tile_bounds_roundtrip():
    x, y, z = 84, 202, 9
    lon0, lat0, lon1, lat1 = TileFetchService.tile_xy_to_bounds(x, y, z)
    assert lon0 < lon1 and lat0 < lat1
    xx, yy = TileFetchService.lnglat_to_tile_xy((lon0 + lon1) / 2, (lat0 + lat1) / 2, z)
    assert (xx, yy) == (x, y)


# --- 3DEP DEM ---

def test_fetch_3dep_params_and_manifest(tmp_path):
    svc = _svc(lambda url, params, n: _Resp(200))
    result = svc.fetch_3dep_dem((-120.50, 38.70, -120.49, 38.71), str(tmp_path),
                                tile_px=2048, native_res_m=1.0)
    assert result.tiles_written >= 1
    assert result.manifest_path and os.path.exists(result.manifest_path)
    # exportImage params carry the required fields.
    _, params = svc.session.calls[0]
    assert params['bboxSR'] == 4326
    assert params['pixelType'] == 'F32'
    assert params['format'] == 'tiff'
    assert 'size' in params and 'bbox' in params
    # Manifest has the USGS3DEPProvider schema (no product column).
    with open(result.manifest_path, newline="") as fh:
        header = next(csv.reader(fh))
    assert header == ['filename', 'minX', 'minY', 'maxX', 'maxY']


def test_fetch_3dep_tiles_large_aoi(tmp_path):
    svc = _svc(lambda url, params, n: _Resp(200))
    # Small tile_px + coarse res forces multiple sub-tiles.
    result = svc.fetch_3dep_dem((-120.60, 38.60, -120.50, 38.70), str(tmp_path),
                                tile_px=256, native_res_m=10.0)
    assert result.tiles_written > 1
    assert len(svc.session.calls) > 1


# --- Meta canopy ---

def test_fetch_meta_url_and_manifest(tmp_path):
    svc = _svc(lambda url, params, n: _Resp(200))
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))
    assert result.tiles_written >= 1
    url, _ = svc.session.calls[0]
    assert "dataforgood-fb-data.s3.amazonaws.com" in url
    assert url.endswith(".tif") and "/chm/" in url
    with open(result.manifest_path, newline="") as fh:
        header = next(csv.reader(fh))
    assert header == ['filename', 'product', 'minX', 'minY', 'maxX', 'maxY']


def test_fetch_meta_retry_then_success(tmp_path):
    state = {'n': 0}

    def handler(url, params, n):
        state['n'] += 1
        return _Resp(500) if state['n'] == 1 else _Resp(200)

    svc = _svc(handler)
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.499, 38.701), str(tmp_path))
    assert result.tiles_written >= 1
    assert len(svc.session.calls) >= 2   # retried after the 500


def test_fetch_meta_404_is_skipped(tmp_path):
    svc = _svc(lambda url, params, n: _Resp(404))
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))
    assert result.tiles_written == 0
    assert result.tiles_skipped >= 1
    assert result.manifest_path is None   # nothing written


def test_fetch_cancel(tmp_path):
    svc = _svc(lambda url, params, n: _Resp(200))
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.40, 38.80), str(tmp_path),
                                   cancel_check=lambda: True)
    assert result.cancelled is True


# --- manifest merge / dedupe (incremental fetches accumulate, not clobber) ---

def test_fetch_meta_manifest_merges_existing_rows(tmp_path):
    """A pre-existing manifest row survives a later canopy fetch into the same dir."""
    manifest = tmp_path / "chm_manifest.csv"
    fields = ['filename', 'product', 'minX', 'minY', 'maxX', 'maxY']
    # Seed a manifest as if a prior AOI had already been fetched here.
    with open(manifest, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerow({'filename': 'chm_SEED.tif', 'product': 'meta_chm',
                    'minX': -121.0, 'minY': 39.0, 'maxX': -120.9, 'maxY': 39.1})

    svc = _svc(lambda url, params, n: _Resp(200))
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))

    assert result.tiles_written >= 1
    assert result.manifest_path and os.path.exists(result.manifest_path)
    assert os.path.basename(result.manifest_path) == "chm_manifest.csv"

    with open(result.manifest_path, newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == fields          # restricted to declared fields
        names = [row['filename'] for row in reader]

    # Pre-existing row preserved AND newly fetched tile(s) appended.
    assert 'chm_SEED.tif' in names
    assert any(n != 'chm_SEED.tif' for n in names)
    assert len(names) >= 2
    assert len(names) == len(set(names))            # deduped by filename


def test_write_manifest_dedupes_by_filename_on_refetch(tmp_path):
    """Re-writing the same filename updates the row instead of duplicating it."""
    manifest = str(tmp_path / "chm_manifest.csv")
    TileFetchService._write_manifest(
        [{'filename': 'chm_X.tif', 'product': 'meta_chm',
          'minX': 1, 'minY': 2, 'maxX': 3, 'maxY': 4}],
        manifest, include_product=True)
    # Second (incremental) write re-fetches chm_X.tif with new bounds and adds chm_Y.tif.
    TileFetchService._write_manifest(
        [{'filename': 'chm_X.tif', 'product': 'meta_chm',
          'minX': 10, 'minY': 20, 'maxX': 30, 'maxY': 40},
         {'filename': 'chm_Y.tif', 'product': 'meta_chm',
          'minX': 5, 'minY': 6, 'maxX': 7, 'maxY': 8}],
        manifest, include_product=True)

    with open(manifest, newline="") as fh:
        rows = list(csv.DictReader(fh))
    by_name = {r['filename']: r for r in rows}
    assert len(rows) == 2                            # no duplicate chm_X row
    assert set(by_name) == {'chm_X.tif', 'chm_Y.tif'}
    assert by_name['chm_X.tif']['minX'] == '10'      # newest values win


def test_write_manifest_restricts_to_declared_fields(tmp_path):
    """Unexpected columns in an existing manifest are dropped on merge."""
    manifest = str(tmp_path / "dem_manifest.csv")
    with open(manifest, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['filename', 'minX', 'minY', 'maxX', 'maxY', 'extra'])
        w.writerow(['dem_0_0.tif', '1', '2', '3', '4', 'junk'])

    TileFetchService._write_manifest(
        [{'filename': 'dem_1_1.tif', 'minX': 5, 'minY': 6, 'maxX': 7, 'maxY': 8}],
        manifest, include_product=False)

    with open(manifest, newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == ['filename', 'minX', 'minY', 'maxX', 'maxY']
        rows = list(reader)
    names = {r['filename'] for r in rows}
    assert names == {'dem_0_0.tif', 'dem_1_1.tif'}   # existing row preserved
    assert all('extra' not in r for r in rows)       # unexpected column dropped


# --- download-failure accounting ---

def test_fetch_3dep_http_500_accounts_failure(tmp_path):
    """A single-tile AOI that always 500s records a download-failed error."""
    svc = _svc(lambda url, params, n: _Resp(500))
    result = svc.fetch_3dep_dem((-120.50, 38.70, -120.49, 38.71), str(tmp_path),
                                tile_px=2048, native_res_m=1.0)
    assert result.tiles_written == 0
    assert result.tiles_failed >= 1
    # Filenames carry a per-AOI digest (library-safe): dem_<digest>_0_0.tif.
    assert any(name.startswith("dem_") and name.endswith("_0_0.tif")
               and reason == "download failed" for name, reason in result.errors)
    assert result.manifest_path is None              # nothing written -> no manifest


def test_fetch_3dep_request_exception_is_swallowed(tmp_path):
    """_get_with_retry catches request exceptions and keeps going (no raise)."""
    import requests

    def handler(url, params, n):
        raise requests.exceptions.ConnectionError("boom")

    svc = _svc(handler)
    # Must not propagate the exception out of the fetch.
    result = svc.fetch_3dep_dem((-120.50, 38.70, -120.49, 38.71), str(tmp_path),
                                tile_px=2048, native_res_m=1.0)
    assert result.tiles_failed >= 1
    assert any(name.startswith("dem_") and name.endswith("_0_0.tif")
               and reason == "download failed" for name, reason in result.errors)
    # Each of the initial call and the one blind retry exhausts MAX_RETRIES attempts,
    # proving exceptions were swallowed and the loop continued rather than aborting.
    assert len(svc.session.calls) == TileFetchService.MAX_RETRIES * 2


# --- absent vs failed classification (canopy) --------------------------------
#
# Regression: a genuine download failure used to be filed as a benign "skip"
# (like a 404), so the fetch reported success with no manifest and the canopy
# source silently never registered ("CanopyServiceFactory: paths unset").

def test_fetch_meta_failure_is_counted_as_failed_not_skipped(tmp_path):
    """Exhausted retries -> tiles_failed + errors entry, NOT tiles_skipped."""
    svc = _svc(lambda url, params, n: _Resp(500))
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))
    assert result.tiles_written == 0
    assert result.tiles_failed >= 1
    assert result.tiles_skipped == 0
    assert result.errors and result.errors[0][1] == "download failed"
    assert result.manifest_path is None


def test_fetch_meta_connection_error_is_failed(tmp_path):
    import requests

    def handler(url, params, n):
        raise requests.exceptions.ConnectionError("net down")

    svc = _svc(handler)
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))
    assert result.tiles_failed >= 1
    assert result.tiles_skipped == 0


def test_fetch_meta_404_still_skipped_not_failed(tmp_path):
    """Sparse coverage (403/404) stays a benign skip with no error entry."""
    svc = _svc(lambda url, params, n: _Resp(404))
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))
    assert result.tiles_skipped >= 1
    assert result.tiles_failed == 0
    assert result.errors == []


def test_memory_error_is_not_retried(tmp_path):
    """A MemoryError (buffering a huge body) must not trigger a re-download."""
    calls = {'n': 0}

    def handler(url, params, n):
        calls['n'] += 1
        raise MemoryError("765 MB body")

    svc = _svc(handler)
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))
    assert result.tiles_failed >= 1
    # One attempt per transfer path (stream + none) -- never MAX_RETRIES loops.
    assert calls['n'] <= 2


# --- streamed fallback behavior ----------------------------------------------

class _StreamResp:
    """Response with iter_content + headers, modeling a large streamed body."""

    def __init__(self, status, chunks, content_length=None):
        self.status_code = status
        self._chunks = chunks
        self.headers = {}
        if content_length is not None:
            self.headers['Content-Length'] = str(content_length)
        self.closed = False

    def iter_content(self, chunk_size=None):
        for c in self._chunks:
            yield c

    def close(self):
        self.closed = True


class _StreamSession:
    """Session whose get() accepts stream= and returns a _StreamResp."""

    def __init__(self, resp_factory):
        self._factory = resp_factory
        self.calls = []

    def get(self, url, params=None, timeout=None, stream=False):
        self.calls.append((url, stream))
        return self._factory()


def test_stream_to_file_writes_chunks_and_reports_bytes(tmp_path):
    """A streamed body lands on disk chunk by chunk with byte progress —
    resp.content is never touched (the memory contract for ~765 MB tiles)."""
    chunks = [b"a" * (1024 * 1024), b"b" * (1024 * 1024)]
    session = _StreamSession(lambda: _StreamResp(200, chunks, content_length=2 * 1024 * 1024))
    svc = TileFetchService(session=session, backoff_ms=0)
    dest = tmp_path / "big.tif"
    updates = []

    outcome = svc._stream_to_file(
        "http://x/big.tif", str(dest),
        progress_callback=lambda c, t, m: updates.append((c, t, m)))

    assert outcome == "ok"
    assert dest.stat().st_size == 2 * 1024 * 1024
    assert session.calls == [("http://x/big.tif", True)]  # streamed, not buffered
    # Byte progress was reported during (not just after) the transfer.
    assert len(updates) >= 2
    assert "MB" in updates[0][2]


def test_stream_to_file_cancel_mid_transfer_deletes_partial(tmp_path):
    """Cancel between chunks stops the download and removes the partial file."""
    state = {'chunks': 0}

    class _CancelableResp(_StreamResp):
        def iter_content(self, chunk_size=None):
            for c in [b"x" * 1024] * 100:
                state['chunks'] += 1
                yield c

    session = _StreamSession(lambda: _CancelableResp(200, [], content_length=100 * 1024))
    svc = TileFetchService(session=session, backoff_ms=0)
    dest = tmp_path / "big.tif"

    outcome = svc._stream_to_file(
        "http://x/big.tif", str(dest),
        cancel_check=lambda: state['chunks'] >= 3)

    assert outcome == "cancelled"
    assert not dest.exists()          # partial file cleaned up
    assert state['chunks'] < 100      # transfer stopped early


def test_stream_to_file_mid_body_failure_is_failed_no_restart(tmp_path):
    """A mid-body exception fails once — no MAX_RETRIES x 765 MB restarts."""
    def bad_iter():
        yield b"x" * 1024
        raise IOError("connection reset")

    class _BadResp(_StreamResp):
        def iter_content(self, chunk_size=None):
            return bad_iter()

    session = _StreamSession(lambda: _BadResp(200, []))
    svc = TileFetchService(session=session, backoff_ms=0)
    dest = tmp_path / "big.tif"

    outcome = svc._stream_to_file("http://x/big.tif", str(dest))
    assert outcome == "failed"
    assert not dest.exists()
    assert len(session.calls) == 1    # no whole-file restart


# --- progress cadence ---------------------------------------------------------

def test_fetch_meta_emits_progress_before_transfer(tmp_path):
    """The tile is announced BEFORE the download so the UI never sits on a
    stale message during a long transfer (the frozen-dialog regression)."""
    order = []

    class _RecordingSession(_Session):
        def get(self, url, params=None, timeout=None):
            order.append('transfer')
            return _Resp(200)

    svc = TileFetchService(session=_RecordingSession(None), backoff_ms=0)
    svc.fetch_meta_canopy(
        (-120.50, 38.70, -120.499, 38.701), str(tmp_path),
        progress_callback=lambda c, t, m: order.append(f"progress:{m}"))

    first_progress = order.index(next(o for o in order if o.startswith('progress')))
    first_transfer = order.index('transfer')
    assert first_progress < first_transfer


# --- windowed /vsicurl clip path ----------------------------------------------

def test_fetch_meta_auto_uses_http_path_with_injected_session(tmp_path):
    """An injected session forces the HTTP path (tests must never touch GDAL)."""
    svc = _svc(lambda url, params, n: _Resp(200))
    result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))
    assert result.tiles_written >= 1
    assert len(svc.session.calls) >= 1  # went through the session


def test_fetch_meta_windowed_clip_writes_manifest_with_clip_bounds(tmp_path):
    """The windowed path records the CLIP's extent (not the whole z9 tile)."""
    svc = TileFetchService(backoff_ms=0)
    clip_bounds = (-120.501, 38.699, -120.489, 38.711)

    from unittest.mock import patch
    with patch.object(svc, '_probe_absent', return_value=('ok', 42)), \
         patch.object(svc, '_fetch_canopy_tile_windowed',
                      return_value=("chm_QK_clip_ab12cd34.tif", clip_bounds)) as mock_win:
        result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71),
                                       str(tmp_path), use_windowed=True)

    mock_win.assert_called_once()
    assert result.tiles_written == 1
    assert result.manifest_path
    with open(result.manifest_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]['filename'] == "chm_QK_clip_ab12cd34.tif"
    # Manifest bbox is the clip's true extent so tile lookup intersects correctly.
    assert float(rows[0]['minX']) == clip_bounds[0]
    assert float(rows[0]['maxY']) == clip_bounds[3]


def test_fetch_meta_windowed_failure_falls_back_to_stream(tmp_path):
    """If the /vsicurl clip fails (no GDAL curl), the streamed download runs."""
    svc = _svc(lambda url, params, n: _Resp(200))

    from unittest.mock import patch
    with patch.object(svc, '_probe_absent', return_value=('ok', None)), \
         patch.object(svc, '_fetch_canopy_tile_windowed',
                      side_effect=RuntimeError("vsicurl unavailable")):
        result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71),
                                       str(tmp_path), use_windowed=True)

    assert result.tiles_written >= 1               # fallback succeeded
    assert len(svc.session.calls) >= 1             # via the HTTP session


def test_windowed_survives_prior_dem_fetch(tmp_path):
    """REGRESSION: fetch_3dep_dem lazily creates the internal session; the
    canopy auto-mode must still choose the windowed clip afterwards.

    This is the exact in-app sequence (Step 1/2 DEM, Step 2/2 canopy) that
    silently fell back to the whole-~765 MB streamed download, because
    use_windowed was keyed off `_session is None` instead of injection.
    """
    from unittest.mock import patch

    svc = TileFetchService(backoff_ms=0)
    # Simulate the DEM phase having created the internal session.
    svc.session  # property access instantiates requests.Session
    assert svc._session is not None
    assert svc._session_injected is False

    clip_bounds = (-120.501, 38.699, -120.489, 38.711)
    with patch.object(svc, '_probe_absent', return_value=('ok', 42)), \
         patch.object(svc, '_fetch_canopy_tile_windowed',
                      return_value=("chm_QK_clip_ab12cd34.tif", clip_bounds)) as mock_win, \
         patch.object(svc, '_stream_to_file') as mock_stream:
        result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71), str(tmp_path))

    mock_win.assert_called_once()          # windowed path taken
    mock_stream.assert_not_called()        # NOT the 765 MB fallback
    assert result.tiles_written == 1


def test_fetch_meta_windowed_absent_probe_skips(tmp_path):
    """A 404 probe classifies the tile as absent without opening GDAL at all."""
    svc = TileFetchService(backoff_ms=0)

    from unittest.mock import patch
    with patch.object(svc, '_probe_absent', return_value=('absent', None)), \
         patch.object(svc, '_fetch_canopy_tile_windowed') as mock_win:
        result = svc.fetch_meta_canopy((-120.50, 38.70, -120.49, 38.71),
                                       str(tmp_path), use_windowed=True)

    mock_win.assert_not_called()
    assert result.tiles_skipped >= 1
    assert result.tiles_failed == 0


# --- central tile library + collision-safe DEM naming -------------------------

def test_library_root_is_stable_and_platform_standard(tmp_path, monkeypatch):
    """The library lives in the platform's per-user app-data location."""
    import importlib
    tfs = importlib.import_module('core.services.terrain.TileFetchService')
    # Point the legacy root at an empty location so the platform path wins.
    monkeypatch.setattr(tfs, 'LEGACY_LIBRARY_ROOT', tmp_path / "no_legacy")
    root = tfs.library_root()
    assert root == tfs.library_root()                # stable across calls
    assert root == str(tfs.DEFAULT_LIBRARY_ROOT)
    assert 'terrain_library' in root
    # Windows: %LOCALAPPDATA%\ADIAT; macOS: Application Support; Linux: XDG.
    assert 'ADIAT' in root or 'adiat' in root


def test_library_root_prefers_populated_legacy_location(tmp_path, monkeypatch):
    """A pre-existing legacy library (~/.adiat) keeps being served so old
    downloads are never stranded by the default moving."""
    import importlib
    tfs = importlib.import_module('core.services.terrain.TileFetchService')
    legacy = tmp_path / "legacy_lib"
    legacy.mkdir()
    (legacy / "dem").mkdir()
    monkeypatch.setattr(tfs, 'LEGACY_LIBRARY_ROOT', legacy)
    assert tfs.library_root() == str(legacy)


def test_library_root_ignores_empty_legacy_location(tmp_path, monkeypatch):
    import importlib
    tfs = importlib.import_module('core.services.terrain.TileFetchService')
    legacy = tmp_path / "legacy_lib"
    legacy.mkdir()   # exists but empty -> platform default wins
    monkeypatch.setattr(tfs, 'LEGACY_LIBRARY_ROOT', legacy)
    assert tfs.library_root() == str(tfs.DEFAULT_LIBRARY_ROOT)


def test_dem_filenames_carry_aoi_digest(tmp_path):
    """Two different AOIs downloaded into the SAME folder must not overwrite
    each other's tiles (the central-library contract)."""
    svc = _svc(lambda url, params, n: _Resp(200, b"TIFFDATA"))
    r1 = svc.fetch_3dep_dem((-120.50, 38.70, -120.49, 38.71), str(tmp_path),
                            tile_px=2048, native_res_m=1.0)
    svc2 = _svc(lambda url, params, n: _Resp(200, b"TIFFDATA"))
    r2 = svc2.fetch_3dep_dem((-97.96, 30.65, -97.95, 30.66), str(tmp_path),
                             tile_px=2048, native_res_m=1.0)

    assert r1.tiles_written >= 1 and r2.tiles_written >= 1
    with open(r2.manifest_path, newline="") as fh:
        names = {row['filename'] for row in csv.DictReader(fh)}
    # Both AOIs' tiles coexist in the merged manifest with distinct names.
    assert len(names) >= 2
    assert len({n.split('_')[1] for n in names}) == 2   # two distinct digests


def test_same_aoi_redownload_is_idempotent(tmp_path):
    """The same AOI re-downloaded reuses its filenames (overwrites, no growth)."""
    bounds = (-120.50, 38.70, -120.49, 38.71)
    svc = _svc(lambda url, params, n: _Resp(200, b"TIFFDATA"))
    r1 = svc.fetch_3dep_dem(bounds, str(tmp_path), tile_px=2048, native_res_m=1.0)
    svc2 = _svc(lambda url, params, n: _Resp(200, b"TIFFDATA"))
    r2 = svc2.fetch_3dep_dem(bounds, str(tmp_path), tile_px=2048, native_res_m=1.0)

    with open(r2.manifest_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == r1.tiles_written               # no duplicate rows
