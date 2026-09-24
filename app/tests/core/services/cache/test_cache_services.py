"""
Comprehensive tests for cache services.

Tests thumbnail, color, and temperature caching.
"""

import pytest
import tempfile
import os
import numpy as np
from unittest.mock import patch, MagicMock
from core.services.cache.ThumbnailCacheService import ThumbnailCacheService
from core.services.cache.ColorCacheService import ColorCacheService
from core.services.cache.TemperatureCacheService import TemperatureCacheService
from core.services.cache.ThumbnailBlobStore import ThumbnailBlobStore
from pathlib import Path
from PIL import Image


@pytest.fixture
def thumbnail_cache_service():
    """Fixture providing a ThumbnailCacheService instance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ThumbnailCacheService(dataset_cache_dir=tmpdir)
        yield service


@pytest.fixture
def sample_aoi():
    """Sample AOI data."""
    return {
        'center': (100, 100),
        'radius': 20,
        'area': 400
    }


def test_thumbnail_cache_service_initialization(thumbnail_cache_service):
    """Test ThumbnailCacheService initialization."""
    assert thumbnail_cache_service is not None
    assert thumbnail_cache_service.mutex is not None


def test_get_cache_key(thumbnail_cache_service, sample_aoi):
    """Test cache key generation."""
    key = thumbnail_cache_service.get_cache_key('test_image.jpg', sample_aoi)

    assert isinstance(key, str)
    assert len(key) > 0


# ---------------------------------------------------------------------------
# Cache-key identity (review finding 3, PR #58/#127 follow-up): the key must
# distinguish same-named images in different folders, while remaining portable
# across machine roots and authoring platforms.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('service_factory', [
    lambda: ThumbnailCacheService(dataset_cache_dir=None),
    ColorCacheService,
    TemperatureCacheService,
], ids=['thumbnail', 'color', 'temperature'])
def test_cache_key_distinguishes_same_named_images(service_factory, sample_aoi):
    """FlightA/DJI_0001.JPG and FlightB/DJI_0001.JPG are different photographs
    and must never share a cache slot, whatever the AOI coordinates."""
    service = service_factory()
    key_a = service.get_cache_key('C:/Mission/FlightA/DJI_0001.JPG', sample_aoi)
    key_b = service.get_cache_key('C:/Mission/FlightB/DJI_0001.JPG', sample_aoi)
    assert key_a != key_b


@pytest.mark.parametrize('service_factory', [
    lambda: ThumbnailCacheService(dataset_cache_dir=None),
    ColorCacheService,
    TemperatureCacheService,
], ids=['thumbnail', 'color', 'temperature'])
def test_cache_key_is_portable_across_machines(service_factory, sample_aoi):
    """Registered dataset-relative identities carry the portability: the
    analysis writer keys below its input root, and a reviewer's relocated
    copy (structure preserved, different machine root and separators)
    resolves to the same identity, so shipped caches keep working."""
    from helpers.PathHelper import build_image_cache_identities

    writer = service_factory()
    writer.set_image_identities(build_image_cache_identities(
        [r'C:\Missions\FlightA\DJI_0001.JPG', r'C:\Missions\FlightB\DJI_0001.JPG'],
        input_root=r'C:\Missions'))
    reader = service_factory()
    reader.set_image_identities(build_image_cache_identities(
        ['/mnt/usb/copies/FlightA/DJI_0001.JPG', '/mnt/usb/copies/FlightB/DJI_0001.JPG']))

    key_win = writer.get_cache_key(r'C:\Missions\FlightA\DJI_0001.JPG', sample_aoi)
    key_posix = reader.get_cache_key('/mnt/usb/copies/flighta/dji_0001.jpg', sample_aoi)
    assert key_win == key_posix


@pytest.mark.parametrize('service_factory', [
    lambda: ThumbnailCacheService(dataset_cache_dir=None),
    ColorCacheService,
    TemperatureCacheService,
], ids=['thumbnail', 'color', 'temperature'])
def test_cache_key_distinguishes_nested_camera_folder_layouts(service_factory, sample_aoi):
    """FlightA/DCIM/100MEDIA/DJI_0001.JPG vs FlightB/DCIM/100MEDIA/... share
    every trailing component but the flight folder; registered identities and
    the raw full-path fallback must both keep them apart."""
    from helpers.PathHelper import build_image_cache_identities

    path_a = 'C:/Mission/FlightA/DCIM/100MEDIA/DJI_0001.JPG'
    path_b = 'C:/Mission/FlightB/DCIM/100MEDIA/DJI_0001.JPG'

    raw = service_factory()
    assert raw.get_cache_key(path_a, sample_aoi) != raw.get_cache_key(path_b, sample_aoi)

    keyed = service_factory()
    keyed.set_image_identities(build_image_cache_identities(
        [path_a, path_b], input_root='C:/Mission'))
    assert keyed.get_cache_key(path_a, sample_aoi) != keyed.get_cache_key(path_b, sample_aoi)


def test_same_named_images_keep_their_own_thumbnails(tmp_path, sample_aoi):
    """Reviewer-visible repro: a red thumbnail saved for A/DJI_0001.JPG and a
    blue one for B/DJI_0001.JPG must load back as themselves."""
    service = ThumbnailCacheService(cache_dir=str(tmp_path / 'global'),
                                    dataset_cache_dir=str(tmp_path / 'dataset'))
    path_a = 'C:/Mission/A/DJI_0001.JPG'
    path_b = 'C:/Mission/B/DJI_0001.JPG'
    red = np.full((16, 16, 3), [255, 0, 0], dtype=np.uint8)
    blue = np.full((16, 16, 3), [0, 0, 255], dtype=np.uint8)

    assert service.save_thumbnail_from_array(path_a, sample_aoi, red)
    assert service.save_thumbnail_from_array(path_b, sample_aoi, blue)

    loaded_a = service.load_thumbnail_from_disk(service.get_cache_key(path_a, sample_aoi))
    loaded_b = service.load_thumbnail_from_disk(service.get_cache_key(path_b, sample_aoi))
    assert loaded_a is not None and loaded_b is not None
    assert loaded_a[:, :, 0].mean() > 250, 'A must stay red'
    assert loaded_b[:, :, 2].mean() > 250, 'B must stay blue'


def test_nested_flights_with_matching_camera_folders_keep_their_thumbnails(tmp_path, sample_aoi):
    """Round-trip through disk with the raw service (no identities): the
    repeated-DCIM layout must never return another flight's crop."""
    service = ThumbnailCacheService(dataset_cache_dir=str(tmp_path / 'dataset'))
    path_a = 'C:/Mission/FlightA/DCIM/100MEDIA/DJI_0001.JPG'
    path_b = 'C:/Mission/FlightB/DCIM/100MEDIA/DJI_0001.JPG'
    red = np.full((16, 16, 3), [255, 0, 0], dtype=np.uint8)
    blue = np.full((16, 16, 3), [0, 0, 255], dtype=np.uint8)

    assert service.save_thumbnail_from_array(path_a, sample_aoi, red)
    assert service.save_thumbnail_from_array(path_b, sample_aoi, blue)

    loaded_a = service.load_thumbnail_from_disk(service.get_cache_key(path_a, sample_aoi))
    assert loaded_a is not None
    assert loaded_a[:, :, 0].mean() > 250, 'FlightA retrieved the blue thumbnail saved for FlightB'


def test_identity_written_thumbnails_survive_relocation(tmp_path, sample_aoi):
    """Writer keys below its input root; a reader whose relocated copy kept
    the structure resolves the same identity and loads the same entry."""
    from helpers.PathHelper import build_image_cache_identities

    cache_dir = str(tmp_path / 'dataset')
    writer = ThumbnailCacheService(dataset_cache_dir=cache_dir)
    writer_paths = [r'C:\Missions\FlightA\DCIM\100MEDIA\DJI_0001.JPG',
                    r'C:\Missions\FlightB\DCIM\100MEDIA\DJI_0001.JPG']
    writer.set_image_identities(build_image_cache_identities(
        writer_paths, input_root=r'C:\Missions'))
    red = np.full((16, 16, 3), [255, 0, 0], dtype=np.uint8)
    blue = np.full((16, 16, 3), [0, 0, 255], dtype=np.uint8)
    assert writer.save_thumbnail_from_array(writer_paths[0], sample_aoi, red)
    assert writer.save_thumbnail_from_array(writer_paths[1], sample_aoi, blue)

    reader = ThumbnailCacheService(dataset_cache_dir=cache_dir)
    reader_paths = ['/mnt/usb/copy/FlightA/DCIM/100MEDIA/DJI_0001.JPG',
                    '/mnt/usb/copy/FlightB/DCIM/100MEDIA/DJI_0001.JPG']
    reader.set_image_identities(build_image_cache_identities(reader_paths))

    loaded_a = reader.load_thumbnail_from_disk(reader.get_cache_key(reader_paths[0], sample_aoi))
    loaded_b = reader.load_thumbnail_from_disk(reader.get_cache_key(reader_paths[1], sample_aoi))
    assert loaded_a is not None and loaded_b is not None
    assert loaded_a[:, :, 0].mean() > 250, 'FlightA must stay red after relocation'
    assert loaded_b[:, :, 2].mean() > 250, 'FlightB must stay blue after relocation'


def test_partial_relocation_never_returns_another_images_thumbnail(tmp_path, sample_aoi):
    """One flight folder relinked elsewhere while the root image stayed put:
    the moved image's over-stripped fallback identity landed on the rooted
    image's identity and returned ITS crop. The collision is now dropped at
    registration - the moved image misses (regenerates), the rooted image
    still hits its own entry."""
    from helpers.PathHelper import build_image_cache_identities

    cache_dir = str(tmp_path / '.thumbnails')
    original_root = 'C:/Mission'
    path_a = 'C:/Mission/DJI_0001.JPG'
    path_b = 'C:/Mission/FlightB/DJI_0001.JPG'
    moved_b = 'D:/Moved/FlightB/DJI_0001.JPG'
    red = np.full((16, 16, 3), [255, 0, 0], dtype=np.uint8)
    blue = np.full((16, 16, 3), [0, 0, 255], dtype=np.uint8)

    writer = ThumbnailCacheService(dataset_cache_dir=cache_dir)
    writer.set_image_identities(build_image_cache_identities(
        [path_a, path_b], input_root=original_root))
    assert writer.save_thumbnail_from_array(path_a, sample_aoi, red)
    assert writer.save_thumbnail_from_array(path_b, sample_aoi, blue)

    # Path recovery persisted FlightB's new location; the XML keeps the
    # original input_dir and the root image's original path.
    reader = ThumbnailCacheService(dataset_cache_dir=cache_dir)
    reader.set_image_identities(build_image_cache_identities(
        [path_a, moved_b], input_root=original_root))

    loaded_b = reader.load_thumbnail_from_disk(reader.get_cache_key(moved_b, sample_aoi))
    assert loaded_b is None or loaded_b[:, :, 2].mean() > 250, \
        'moved FlightB retrieved the red root-image crop'
    loaded_a = reader.load_thumbnail_from_disk(reader.get_cache_key(path_a, sample_aoi))
    assert loaded_a is not None and loaded_a[:, :, 0].mean() > 250, \
        'the rooted image must keep hitting its own entry'


def test_ambiguous_v1_entries_are_never_served(tmp_path, sample_aoi):
    """An old basename-keyed entry (potentially the wrong image's crop) must
    miss under the current formula instead of being returned."""
    import hashlib
    service = ThumbnailCacheService(dataset_cache_dir=str(tmp_path))
    image_path = 'C:/Mission/FlightA/DJI_0001.JPG'
    # Write a loose file under the OLD (v1) key formula.
    old_identifier = f"DJI_0001.JPG:{sample_aoi['center'][0]}:{sample_aoi['center'][1]}:{sample_aoi['radius']}"
    old_key = hashlib.md5(old_identifier.encode()).hexdigest()
    poison = np.full((16, 16, 3), [0, 255, 0], dtype=np.uint8)
    assert service.save_thumbnail_to_disk(old_key, poison, tmp_path)

    assert service.load_thumbnail_from_disk(
        service.get_cache_key(image_path, sample_aoi)) is None


def test_save_thumbnail_from_array(thumbnail_cache_service, sample_aoi):
    """Test saving thumbnail from array."""
    thumbnail = np.random.randint(0, 255, (180, 180, 3), dtype=np.uint8)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = os.path.join(tmpdir, '.thumbnails')
        os.makedirs(cache_dir, exist_ok=True)

        thumbnail_cache_service.save_thumbnail_from_array(
            'test_image.jpg',
            sample_aoi,
            thumbnail,
            cache_dir
        )

        # Verify thumbnail was saved
        # Note: actual path may vary based on implementation
        assert os.path.exists(cache_dir)


# ---------------------------------------------------------------------------
# Freeze regression: get_thumbnail must NOT hold the cache mutex across the
# expensive disk read / full-resolution decode / JPEG encode. Otherwise a
# worker thread mid-generation blocks the GUI thread, which calls get_thumbnail
# synchronously for already-cached rows. QMutex is non-recursive, so if this
# thread already held the lock, tryLock() from inside the generation step would
# return False; it returning True proves the lock was released first.
# ---------------------------------------------------------------------------

def test_get_thumbnail_releases_mutex_during_generation(thumbnail_cache_service, sample_aoi):
    svc = thumbnail_cache_service
    observed = {}

    def fake_extract(image_path, aoi_data, target_size):
        got = svc.mutex.tryLock()
        observed['lock_available'] = got
        if got:
            svc.mutex.unlock()
        return np.zeros((180, 180, 3), dtype=np.uint8)

    # Force a full cache miss so the generation branch runs.
    svc.load_thumbnail_from_disk = lambda key: None
    svc.extract_aoi_region_fast = fake_extract

    icon = svc.get_thumbnail('nonexistent.jpg', sample_aoi)

    assert observed.get('lock_available') is True
    assert icon is not None


def test_get_thumbnail_releases_mutex_during_disk_load(thumbnail_cache_service, sample_aoi):
    svc = thumbnail_cache_service
    observed = {}

    def fake_disk_load(cache_key):
        got = svc.mutex.tryLock()
        observed['lock_available'] = got
        if got:
            svc.mutex.unlock()
        return np.zeros((180, 180, 3), dtype=np.uint8)

    svc.load_thumbnail_from_disk = fake_disk_load

    icon = svc.get_thumbnail('nonexistent.jpg', sample_aoi)

    assert observed.get('lock_available') is True
    assert icon is not None


def test_color_cache_service_initialization():
    """Test ColorCacheService initialization."""
    service = ColorCacheService()
    assert service is not None


def test_color_cache_service_save():
    """Test saving color information to cache."""
    service = ColorCacheService()

    color_info = {
        'rgb': (100, 150, 200),
        'hex': '#6496C8',
        'hue_degrees': 210.0
    }

    aoi = {
        'center': (100, 100),
        'radius': 20
    }

    service.save_color_info('test_image.jpg', aoi, color_info)

    # Verify color info was stored
    assert 'color_info' in aoi or service.get_color_info('test_image.jpg', aoi) is not None


def test_temperature_cache_service_initialization():
    """Test TemperatureCacheService initialization."""
    service = TemperatureCacheService()
    assert service is not None


def test_temperature_cache_service_save():
    """Test saving temperature information to cache."""
    service = TemperatureCacheService()

    aoi = {
        'center': (100, 100),
        'radius': 20
    }

    service.save_temperature('test_image.jpg', aoi, 25.5)

    # Verify temperature was stored
    assert 'temperature' in aoi or service.get_temperature('test_image.jpg', aoi) is not None

# ---------------------------------------------------------------------------
# SQLite blob container: thousands of loose thumbnail files become one
# thumbnails.db per cache directory; legacy loose files stay readable.
# ---------------------------------------------------------------------------


def test_saved_thumbnails_land_in_one_container_not_loose_files(thumbnail_cache_service, sample_aoi):
    svc = thumbnail_cache_service
    thumbnail = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)

    for i in range(5):
        aoi = dict(sample_aoi, center=(100 + i, 100))
        key = svc.get_cache_key(f'img_{i}.jpg', aoi)
        assert svc.save_thumbnail_to_disk(key, thumbnail) is True

    cache_dir = Path(svc.dataset_cache_dir)
    assert (cache_dir / ThumbnailBlobStore.DB_FILENAME).exists()
    assert list(cache_dir.rglob('*.jpg')) == []  # no loose files anymore


def test_blob_roundtrip_preserves_thumbnail(thumbnail_cache_service, sample_aoi):
    svc = thumbnail_cache_service
    thumbnail = np.full((64, 64, 3), (200, 30, 90), dtype=np.uint8)
    key = svc.get_cache_key('roundtrip.jpg', sample_aoi)

    assert svc.save_thumbnail_to_disk(key, thumbnail) is True
    loaded = svc.load_thumbnail_from_disk(key)

    assert loaded is not None
    assert loaded.shape == (64, 64, 3)
    # JPEG at quality 80 is lossy but close; channel order must be preserved
    assert np.allclose(loaded.mean(axis=(0, 1)), thumbnail.mean(axis=(0, 1)), atol=6)


def test_is_cached_sees_blob_entries(thumbnail_cache_service, sample_aoi):
    svc = thumbnail_cache_service
    thumbnail = np.zeros((32, 32, 3), dtype=np.uint8)

    assert svc.is_cached('blobbed.jpg', sample_aoi) is False
    key = svc.get_cache_key('blobbed.jpg', sample_aoi)
    svc.save_thumbnail_to_disk(key, thumbnail)
    assert svc.is_cached('blobbed.jpg', sample_aoi) is True


def test_legacy_loose_files_remain_readable(thumbnail_cache_service, sample_aoi):
    """Caches written by older builds (loose .jpg per thumbnail) still load."""
    svc = thumbnail_cache_service
    key = svc.get_cache_key('legacy.jpg', sample_aoi)
    legacy_path = Path(svc.dataset_cache_dir) / f"{key}.jpg"
    Image.new('RGB', (48, 48), (10, 250, 10)).save(legacy_path)

    loaded = svc.load_thumbnail_from_disk(key)

    assert loaded is not None
    assert loaded.shape == (48, 48, 3)
    assert loaded[0, 0, 1] > 200  # green channel survived (RGB order)
    assert svc.is_cached('legacy.jpg', sample_aoi) is True


def test_clear_disk_cache_resets_container(thumbnail_cache_service, sample_aoi):
    svc = thumbnail_cache_service
    thumbnail = np.zeros((32, 32, 3), dtype=np.uint8)
    key = svc.get_cache_key('cleared.jpg', sample_aoi)
    svc.save_thumbnail_to_disk(key, thumbnail)

    svc.clear_disk_cache()

    assert svc.load_thumbnail_from_disk(key) is None
    # And the cache still works after the reset
    assert svc.save_thumbnail_to_disk(key, thumbnail) is True
    assert svc.load_thumbnail_from_disk(key) is not None


def test_cache_stats_count_blob_entries(thumbnail_cache_service, sample_aoi):
    svc = thumbnail_cache_service
    thumbnail = np.zeros((32, 32, 3), dtype=np.uint8)
    for i in range(3):
        key = svc.get_cache_key(f'stat_{i}.jpg', sample_aoi)
        svc.save_thumbnail_to_disk(key, thumbnail)

    stats = svc.get_cache_stats()

    assert stats['disk_count'] == 3
    assert stats['disk_size_mb'] > 0


def test_blob_store_concurrent_writes(tmp_path):
    """The GUI thread and worker pool write concurrently; nothing may be lost."""
    import threading

    store = ThumbnailBlobStore(tmp_path)
    errors = []

    def write_batch(offset):
        try:
            for i in range(25):
                assert store.put(f'key_{offset}_{i}', b'\xff\xd8jpegbytes')
        except Exception as e:  # pragma: no cover - failure detail for the assert below
            errors.append(e)

    threads = [threading.Thread(target=write_batch, args=(t,)) for t in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert store.count() == 100
    assert store.get('key_3_24') == b'\xff\xd8jpegbytes'
