"""
GPSMapController - Manages GPS map visualization for the image viewer.

This controller handles the GPS map window lifecycle, data extraction,
and coordination between the map and main viewer.
"""

from PySide6.QtCore import QObject, QThread, Signal, QTimer, QPointF
from PySide6.QtWidgets import QMenu, QMessageBox
from PySide6.QtGui import QCursor, QImage, QPixmap
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper
from core.services.LoggerService import LoggerService
from core.services.image.ImageService import ImageService
from core.services.image.AOIService import AOIService, _get_terrain_service
from core.services.image.AOINeighborService import AOINeighborService
from core.services.waldo import WaldoMetadataService
from core.views.images.viewer.dialogs.GPSMapDialog import GPSMapDialog
import piexif
from datetime import datetime
import math
import os


class _CanopyOverlayWorker(QThread):
    """Samples + colorizes the canopy overlay off the GUI thread.

    Emits result_ready(rgba_or_None, spec). Only numpy/rasterio work happens
    here; QPixmap conversion stays on the GUI thread (Qt requirement).
    """

    result_ready = Signal(object, object)

    def __init__(self, canopy_service, spec, logger):
        super().__init__()
        self._canopy = canopy_service
        self._spec = spec
        self._logger = logger

    def run(self):
        rgba = GPSMapController._build_canopy_rgba(self._canopy, self._spec, self._logger)
        self.result_ready.emit(rgba, self._spec)


class GPSMapController(QObject):
    """
    Controller for GPS map functionality.

    Manages GPS data extraction, map window creation, and image selection
    coordination between the map and main viewer.
    """

    # Signal emitted when an image is selected from the map
    image_selected = Signal(int)

    def __init__(self, parent_viewer):
        """
        Initialize the GPS map controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        super().__init__()
        self.parent = parent_viewer
        self.logger = LoggerService()  # Create our own logger
        self.map_dialog = None
        self.gps_data = []
        self._pod_overlay_enabled = False
        self._pod_overlay_mode = 'pod'
        self._limit_labels = None
        self._max_overlay_dim = 2048
        self._canopy_svc = None
        self._canopy_svc_loaded = False
        self._canopy_svc_fp = ''           # canopy settings the service was built from
        self._canopy_overlay_cache = None  # (spec key, pixmap, transform6)
        self._canopy_worker = None
        self._canopy_pending_opacity = 70
        self._tile_fetch_controller = None
        self._canopy_prompt_shown = False  # one-time "download canopy?" prompt per session
        self._dem_coverage_prompt_shown = False  # one-time partial-DEM warning per session

        # Coalesce zoom-FOV updates. Viewer.viewChanged fires up to twice per
        # wheel notch, and each forward reruns the map's terrain-projected FOV
        # redraw synchronously on the GUI thread. A leading-edge + trailing
        # throttle bounds that to roughly one redraw per interval during a
        # continuous zoom/pan while still drawing the final position.
        self._fov_throttle = QTimer(self)
        self._fov_throttle.setSingleShot(True)
        self._fov_throttle.setInterval(100)
        self._fov_throttle.timeout.connect(self._flush_zoom_fov)
        self._pending_fov_rect = None
        self._has_pending_fov = False

    def show_map(self):
        """
        Show the GPS map window.

        Extracts GPS data from images and creates/shows the map dialog.
        """
        # Extract GPS data from all images
        self.extract_gps_data()

        if not self.gps_data:
            self.parent.status_controller.show_toast(self.tr("No GPS data found in images"), 3000, color="#F44336")
            return

        # Create and show the map dialog
        # Find the current image in the GPS data list
        current_gps_index = None
        for i, data in enumerate(self.gps_data):
            if data['index'] == self.parent.current_image:
                current_gps_index = i
                break

        offline_only = self._is_offline_only()

        if self.map_dialog is None:
            self.map_dialog = GPSMapDialog(self.parent, self.gps_data, current_gps_index, offline_only=offline_only)
            self.map_dialog.image_selected.connect(self.on_map_image_selected)
            self.map_dialog.gps_right_clicked.connect(self.on_map_gps_clicked)
            if hasattr(self.map_dialog, 'pod_display_changed'):
                self.map_dialog.pod_display_changed.connect(self.on_pod_display_changed)
            if hasattr(self.map_dialog, 'canopy_download_requested'):
                self.map_dialog.canopy_download_requested.connect(self.on_canopy_download_requested)
            if hasattr(self.map_dialog, 'pod_calculate_requested'):
                self.map_dialog.pod_calculate_requested.connect(self.on_pod_calculate_requested)
            # Connect to dialog close event to update button state
            self.map_dialog.finished.connect(self.on_map_dialog_closed)
        else:
            # Update with latest data if dialog already exists
            self.map_dialog.update_gps_data(self.gps_data, current_gps_index)
            self.map_dialog.set_offline_mode(offline_only)

        # Re-check overlay availability each open: canopy settings may have
        # changed in Preferences, or a tile download may have registered a source.
        self._canopy_svc_loaded = False
        self._refresh_overlay_availability()

        self.map_dialog.show()
        self.map_dialog.raise_()
        self.map_dialog.activateWindow()

        # Update button state to show map is open
        if hasattr(self.parent, 'gps_map_open'):
            self.parent.gps_map_open = True
            if hasattr(self.parent, 'ui_style_controller'):
                self.parent.ui_style_controller.update_gps_map_button_style()

        # Show current AOI if one is selected
        self.update_aoi_on_map()

        # Send current zoom FOV state to the map
        if hasattr(self.parent, '_on_view_changed'):
            self.parent._on_view_changed()

        # Offer a one-time download if no canopy source is configured yet.
        self._maybe_prompt_canopy_download()

    def _refresh_overlay_availability(self):
        """Gate the map's overlay controls. POD/look-count need a cached POD
        result; the canopy mode only needs a configured canopy source."""
        if self.map_dialog is None:
            return
        cache = self._pod_cache()
        self._invalidate_stale_pod_cache(cache)
        pod_available = cache is not None and cache.has_result()
        canopy_available = self._canopy_service() is not None
        if hasattr(self.map_dialog, 'set_overlay_availability'):
            self.map_dialog.set_overlay_availability(pod_available, canopy_available)
        elif hasattr(self.map_dialog, 'set_pod_available'):
            self.map_dialog.set_pod_available(pod_available)

    def _invalidate_stale_pod_cache(self, cache):
        """Drop a cached POD result computed under a different terrain/canopy
        configuration: re-rendering it would silently show data from sources
        the user has since switched away from."""
        if cache is None or not hasattr(cache, 'is_stale'):
            return
        try:
            from core.services.coverage.CoverageResultCache import config_fingerprint
            settings = getattr(self.parent, 'settings_service', None)
            if cache.is_stale(config_fingerprint(settings)):
                cache.invalidate()
                self.logger.info(
                    "POD overlay: cached result predates a terrain/canopy source "
                    "change; recalculate to refresh it.")
                if hasattr(self.parent, 'status_controller'):
                    self.parent.status_controller.show_toast(
                        self.tr("POD overlay cleared — the elevation/canopy source "
                                "changed. Recalculate to refresh it."),
                        5000, color="#FFA726")
        except Exception as e:
            self.logger.warning(f"POD staleness check failed: {e}")

    def on_canopy_download_requested(self):
        """Run the tile-fetch flow for this mission, then refresh availability so
        a freshly registered canopy source lights up the overlay immediately."""
        if self._is_offline_only():
            self.parent.status_controller.show_toast(
                self.tr("Downloading tiles is disabled in Offline Only mode"),
                3000, color="#F44336")
            return
        # Release any open canopy datasets first: on Windows an open tile file
        # cannot be overwritten, which would break a re-download into the same
        # folder. Also drop the stale overlay cache.
        self._close_canopy_service()
        self._canopy_svc_loaded = False
        self._canopy_overlay_cache = None
        if not self._run_tile_fetch():
            return
        # A download may have registered a new canopy/DEM source in settings.
        self._canopy_svc_loaded = False
        self._refresh_overlay_availability()
        self._maybe_offer_pod_calculation()

    def _maybe_offer_pod_calculation(self):
        """After a completed download, offer to compute POD right away so the
        download -> calculate -> overlay workflow chains without leaving the map.

        Only offered when the download actually finished (not dismissed or
        cancelled) and no POD result is cached yet.
        """
        fetch = self._tile_fetch_controller
        if fetch is None or getattr(fetch, 'last_results', None) is None:
            return
        cache = self._pod_cache()
        if cache is not None and cache.has_result():
            return
        resp = QMessageBox.question(
            self.map_dialog,
            self.tr("Calculate POD Coverage?"),
            self.tr("Coverage data is ready. Calculate the probability-of-detection "
                    "heatmap for this mission now? (May take several minutes.)"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        if resp == QMessageBox.StandardButton.Yes:
            self.on_pod_calculate_requested()

    def _mission_gps_bounds(self):
        """(min_lon, min_lat, max_lon, max_lat) of the mission GPS, or None."""
        lats = [d['latitude'] for d in self.gps_data if 'latitude' in d]
        lons = [d['longitude'] for d in self.gps_data if 'longitude' in d]
        if not lats or not lons:
            return None
        return (min(lons), min(lats), max(lons), max(lats))

    def _confirm_local_dem_coverage(self):
        """Once per session before a POD run: if the active local DEM only
        partially covers (or misses) the mission, say so and offer the
        download. Returns False when the user chose to download tiles first
        (the POD run is deferred), True to proceed.

        Proceeding is safe either way — uncovered frames fall back to online
        AWS Terrain Tiles — so this is an offer, not a gate.
        """
        if self._dem_coverage_prompt_shown:
            return True
        settings = getattr(self.parent, 'settings_service', None)
        bounds = self._mission_gps_bounds()
        if settings is None or bounds is None:
            return True
        try:
            provider_id = settings.get_setting('TerrainProviderId', '') or ''
            manifest = settings.get_setting('Terrain3DEPManifestPath', '')
            tiles = settings.get_setting('Terrain3DEPTilesDir', '')
        except Exception:
            return True
        if provider_id != 'usgs_3dep_local' or not (manifest and tiles):
            return True
        if not (os.path.isfile(manifest) and os.path.isdir(tiles)):
            # Dangling registration: the factory already falls back to the
            # online baseline, so a "your 3DEP doesn't cover this" prompt
            # would be misleading.
            return True

        try:
            from core.services.terrain.USGS3DEPProvider import USGS3DEPProvider
            probe = USGS3DEPProvider(manifest, tiles)
            try:
                coverage = probe.covers(bounds)
            finally:
                probe.close()
        except Exception as e:
            self.logger.warning(f"POD DEM coverage check failed: {e}")
            return True
        if coverage == 'full':
            return True

        self._dem_coverage_prompt_shown = True
        if coverage == 'partial':
            detail = self.tr("Your local USGS 3DEP tiles only partially cover "
                             "this mission.")
        else:
            detail = self.tr("Your local USGS 3DEP tiles do not cover this "
                             "mission.")
        box = QMessageBox(self.map_dialog)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle(self.tr("Local Elevation Coverage"))
        box.setText(detail + "\n\n" + self.tr(
            "Frames outside the local tiles will use online AWS Terrain Tiles "
            "(~30 m) elevation instead. You can download 1 m tiles for this "
            "area first, or continue with the fallback."))
        download_btn = box.addButton(self.tr("Download Tiles..."),
                                     QMessageBox.ButtonRole.ActionRole)
        continue_btn = box.addButton(self.tr("Continue"),
                                     QMessageBox.ButtonRole.AcceptRole)
        box.setDefaultButton(continue_btn)
        box.exec()
        if box.clickedButton() is download_btn:
            self.on_canopy_download_requested()
            return False
        return True

    def on_pod_calculate_requested(self):
        """Run the POD coverage calculation from the map view.

        Delegates to the viewer's UnifiedMapExportController (the same flow as
        Map Export's POD option) so the computation, progress dialog, result
        cache, and overlay enablement all stay in one place. Outputs land in
        ``<results>/coverage_pod``.
        """
        if not self._confirm_local_dem_coverage():
            return
        export_controller = getattr(self.parent, 'unified_map_export', None)
        if export_controller is None or not hasattr(export_controller, 'run_pod'):
            try:
                from core.controllers.images.viewer.exports.UnifiedMapExportController import (
                    UnifiedMapExportController)
                export_controller = UnifiedMapExportController(self.parent, self.logger)
                self.parent.unified_map_export = export_controller
            except Exception as e:
                self.logger.error(f"GPS map: POD controller unavailable: {e}")
                self.parent.status_controller.show_toast(
                    self.tr("POD calculation is unavailable"), 3000, color="#F44336")
                return
        export_controller.run_pod(self._pod_output_dir(), show_on_map=True)

    def _pod_output_dir(self):
        """Default POD product folder: <results dir>/coverage_pod."""
        xml_path = getattr(self.parent, 'xml_path', None)
        if isinstance(xml_path, (str, os.PathLike)) and os.fspath(xml_path):
            return os.path.join(os.path.dirname(os.fspath(xml_path)), "coverage_pod")
        return os.path.join(os.getcwd(), "coverage_pod")

    def _run_tile_fetch(self):
        """Open the Download Tiles dialog seeded with this mission's images so it
        can auto-fill the AOI. Returns False if the downloader is unavailable."""
        try:
            from core.controllers.images.viewer.exports.TileFetchController import TileFetchController
        except Exception as e:
            self.logger.error(f"GPS map: tile downloader unavailable: {e}")
            self.parent.status_controller.show_toast(
                self.tr("The tile downloader is unavailable"), 3000, color="#F44336")
            return False
        settings_service = getattr(self.parent, 'settings_service', None)
        mission_images = (getattr(self.parent, 'source_images', None)
                          or getattr(self.parent, 'images', None))
        # Default the download destination to the results folder (next to
        # ADIAT_Data.xml) so tiles land beside the analysis they support.
        # Viewer.xml_path is a pathlib.Path (see MainWindow), so accept any
        # path-like, not just str; a MagicMock parent in tests is neither.
        default_output_dir = None
        xml_path = getattr(self.parent, 'xml_path', None)
        if isinstance(xml_path, (str, os.PathLike)) and os.fspath(xml_path):
            default_output_dir = os.path.dirname(os.fspath(xml_path))
        # Keep a reference so the fetch thread is not collected mid-run.
        self._tile_fetch_controller = TileFetchController(
            self.map_dialog, settings_service, logger=self.logger)
        self._tile_fetch_controller.run_fetch(
            mission_images=mission_images, default_output_dir=default_output_dir)
        return True

    def _maybe_prompt_canopy_download(self):
        """Once per session, if no canopy source is configured (and not offline),
        offer to download elevation/canopy tiles for this mission."""
        if self._canopy_prompt_shown or self.map_dialog is None:
            return
        if self._is_offline_only() or self._canopy_service() is not None:
            return
        self._canopy_prompt_shown = True
        resp = QMessageBox.question(
            self.map_dialog,
            self.tr("Download Canopy Data?"),
            self.tr("No canopy-height data is configured for this mission.\n\n"
                    "Download elevation and canopy tiles for this area now so the "
                    "canopy overlay and terrain-aware detection coverage can use them?\n\n"
                    "This downloads Meta/WRI canopy height (1 m) and sets it as the canopy "
                    "source, replacing any LANDFIRE selection (LANDFIRE tiles must be added "
                    "manually)."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.on_canopy_download_requested()

    def _is_offline_only(self) -> bool:
        """Return whether OfflineOnly preference is enabled."""
        try:
            if hasattr(self.parent, "settings_service"):
                return self.parent.settings_service.get_bool_setting("OfflineOnly", False)
        except Exception:
            pass
        return False

    def extract_gps_data(self):
        """
        Extract GPS coordinates and timestamps from all source-folder images.

        AOI-subset images keep their viewer index so clicks on the map jump to
        the corresponding viewer slot. Source-only captures (in the original
        flight folder but not in the result XML) are appended with index=None
        and is_source_only=True so the renderer can paint them as small grey
        dots and the click handler ignores them.
        """
        self.gps_data = []

        # Index AOI subset by path so we can look up the viewer position for any
        # source-folder entry that did produce a detection.
        aoi_by_path = {img['path']: (idx, img) for idx, img in enumerate(self.parent.images) if img.get('path')}

        # Fall back to AOI-only iteration if source_images wasn't populated
        # (e.g. on legacy code paths or if Viewer.__init__ short-circuited).
        source_iterable = getattr(self.parent, 'source_images', None) or [
            {'path': img['path'], 'name': img.get('name', ''), 'has_aoi': True}
            for img in self.parent.images if img.get('path')
        ]

        for src_entry in source_iterable:
            path = src_entry.get('path')
            if not path:
                continue
            try:
                exif_data = MetaDataHelper.get_exif_data_piexif(path)
                gps_coords = LocationInfo.get_gps(exif_data=exif_data)
                if not gps_coords:
                    continue

                timestamp = self.get_image_timestamp_from_exif(exif_data)
                aoi_match = aoi_by_path.get(path)

                if aoi_match is not None:
                    idx, image = aoi_match
                    aoi_count = len(image.get('areas_of_interest', [])) if 'areas_of_interest' in image else 0
                    has_aoi = aoi_count > 0
                    has_flagged = any(aoi.get('flagged', False) for aoi in image.get('areas_of_interest', []))
                    # WALDO images: the XML's cached bearing was computed by
                    # BearingRecoveryController before WALDO synthesised the XMP,
                    # so it's stale. Force GPSMapView's lazy lookup to read the
                    # authoritative Gimbal Yaw from the now-present XMP.
                    is_waldo = WaldoMetadataService.is_waldo_image(path) is not None
                    cached_bearing = None if is_waldo else image.get('bearing')
                    self.gps_data.append({
                        'index': idx,
                        'latitude': gps_coords['latitude'],
                        'longitude': gps_coords['longitude'],
                        'timestamp': timestamp,
                        'name': image.get('name', src_entry.get('name', f'Image {idx + 1}')),
                        'has_aoi': has_aoi,
                        'aoi_count': aoi_count,
                        'hidden': image.get('hidden', False),
                        'has_flagged': has_flagged,
                        'bearing': cached_bearing,
                        'wingtra_agl_ft': image.get('wingtra_agl_ft'),
                        'fov_alignment': image.get('fov_alignment'),
                        'width': image.get('width'),
                        'height': image.get('height'),
                        'image_path': path,
                        'is_source_only': False,
                    })
                else:
                    # Source-only capture: display-only marker, no click target.
                    self.gps_data.append({
                        'index': None,
                        'latitude': gps_coords['latitude'],
                        'longitude': gps_coords['longitude'],
                        'timestamp': timestamp,
                        'name': src_entry.get('name', ''),
                        'has_aoi': False,
                        'aoi_count': 0,
                        'hidden': False,
                        'has_flagged': False,
                        'bearing': None,
                        'wingtra_agl_ft': None,
                        'image_path': path,
                        'is_source_only': True,
                    })
            except Exception as e:
                self.logger.error(f"Could not extract GPS from {path}: {str(e)}")

        # Sort by timestamp so the path line traces the actual flight order.
        self.gps_data.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min)

    def get_image_timestamp_from_exif(self, exif_data):
        """
        Extract timestamp from EXIF data.

        Args:
            exif_data: Pre-loaded EXIF data dictionary

        Returns:
            datetime object or None if timestamp not found
        """
        try:

            if exif_data and 'Exif' in exif_data:
                # Try to get DateTimeOriginal
                datetime_original = exif_data['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
                if datetime_original:
                    if isinstance(datetime_original, bytes):
                        datetime_str = datetime_original.decode('utf-8')
                    else:
                        datetime_str = datetime_original
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')

                # Fallback to DateTime
                datetime_tag = exif_data['Exif'].get(piexif.ExifIFD.DateTime)
                if datetime_tag:
                    datetime_str = datetime_tag.decode('utf-8') if isinstance(datetime_tag, bytes) else datetime_tag
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')

        except Exception as e:
            self.logger.error(f"Could not extract timestamp: {str(e)}")

        return None

    def get_image_timestamp(self, image_path):
        """
        Extract timestamp from image EXIF data (compatibility method).

        Args:
            image_path: Path to the image file

        Returns:
            datetime object or None if timestamp not found
        """
        exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
        return self.get_image_timestamp_from_exif(exif_data)

    def get_image_bearing(self, image_path, calculated_bearing=None):
        """
        Extract bearing/yaw information from image.

        Args:
            image_path: Path to the image file
            calculated_bearing: Optional calculated bearing from XML (degrees)

        Returns:
            float: Bearing in degrees (0-360), or None if not available
        """
        try:
            image_service = ImageService(image_path, '', calculated_bearing=calculated_bearing)
            # Use get_camera_yaw() which accounts for both Flight Yaw and Gimbal Yaw
            bearing = image_service.get_camera_yaw()
            return bearing
        except Exception as e:
            self.logger.error(f"Could not extract bearing: {str(e)}")
            return None

    def on_map_image_selected(self, image_index):
        """
        Handle image selection from the map.

        Args:
            image_index: Index of the selected image
        """
        if 0 <= image_index < len(self.parent.images):
            self.parent.current_image = image_index
            self.parent._load_image()

    # ---------------- POD coverage overlay ----------------

    def _pod_cache(self):
        return getattr(self.parent, 'pod_result_cache', None)

    def _limit_label(self, code):
        if self._limit_labels is None:
            from core.services.coverage.contracts import (
                LIMIT_NO_LOOKS, LIMIT_TERRAIN, LIMIT_CANOPY, LIMIT_GSD, LIMIT_NONE)
            self._limit_labels = {
                LIMIT_NO_LOOKS: self.tr("Not covered — no looks"),
                LIMIT_TERRAIN: self.tr("Terrain occlusion"),
                LIMIT_CANOPY: self.tr("Canopy"),
                LIMIT_GSD: self.tr("Image resolution (GSD)"),
                LIMIT_NONE: self.tr("None"),
            }
        return self._limit_labels.get(code, self.tr("Unknown"))

    def _rgba_to_pixmap(self, rgba, transform):
        """(QPixmap, transform6) from an RGBA grid, downsampled to a display cap."""
        import numpy as np

        a, b, c, d, e, f = tuple(transform)[:6]
        rows, cols = rgba.shape[:2]
        shrink = max(rows, cols) / float(self._max_overlay_dim)
        if shrink > 1.0:
            import cv2
            new_cols = max(1, int(cols / shrink))
            new_rows = max(1, int(rows / shrink))
            rgba = cv2.resize(rgba, (new_cols, new_rows), interpolation=cv2.INTER_NEAREST)
            a *= cols / new_cols
            e *= rows / new_rows
            rows, cols = new_rows, new_cols

        arr = np.ascontiguousarray(rgba, dtype=np.uint8)
        qimg = QImage(arr.tobytes(), cols, rows, 4 * cols, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimg), (a, b, c, d, e, f)

    def _build_pod_pixmap(self, result, mode):
        """(QPixmap, transform6) from a CoverageResult, downsampled to a display cap."""
        from core.services.coverage.colormap import pod_to_rgba, look_count_to_rgba

        if mode == 'looks':
            rgba = look_count_to_rgba(result.look_count)
        else:
            rgba = pod_to_rgba(result.pod, result.look_count, result.params)
        return self._rgba_to_pixmap(rgba, result.transform)

    @staticmethod
    def _canopy_config_fingerprint():
        """Fingerprint of the canopy settings the cached service was built from."""
        try:
            from core.services.SettingsService import SettingsService
            s = SettingsService()
            return '|'.join(
                str(s.get_setting(k, '') or '')
                for k in ('CanopyKind', 'CanopyManifestPath', 'CanopyTilesDir'))
        except Exception:
            return ''

    def _canopy_service(self):
        """Lazily build (and cache) the settings-configured CanopyService.

        The cache is fingerprinted against the canopy settings: changing the
        source in Preferences while the map is open rebuilds the service on
        next access instead of silently serving the old source's data.
        """
        fingerprint = self._canopy_config_fingerprint()
        # An empty recorded fingerprint means "unknown provenance" (e.g. a
        # directly injected service) and is trusted, mirroring
        # CoverageResultCache.is_stale's convention.
        if (self._canopy_svc_loaded and self._canopy_svc_fp
                and fingerprint != self._canopy_svc_fp):
            self._canopy_svc_loaded = False
            self._canopy_overlay_cache = None   # old source's pixels are stale too
        if not self._canopy_svc_loaded:
            self._canopy_svc_loaded = True
            self._canopy_svc_fp = fingerprint
            self._close_canopy_service()   # release the old source's datasets
            try:
                from core.services.terrain.CanopyServiceFactory import create_canopy_service
                from core.services.SettingsService import SettingsService
                self._canopy_svc = create_canopy_service(SettingsService())
            except Exception as e:
                self.logger.warning(f"Canopy overlay: service unavailable: {e}")
        return self._canopy_svc

    def _close_canopy_service(self):
        """Deterministically close the canopy service's open rasterio datasets.

        The Meta/WRI source keeps large COGs open in an LRU; leaking the
        handles blocks re-downloads on Windows (open files can't be replaced)
        and holds file mappings for the viewer's lifetime.
        """
        svc = self._canopy_svc
        self._canopy_svc = None
        if svc is not None:
            try:
                svc.close()
            except Exception:
                pass

    def _canopy_extent_spec(self):
        """EPSG:3857 GridSpec for the canopy overlay: the cached POD grid when
        one exists (pixel-aligned with the POD overlay), else the mission GPS
        bounding box padded 200 m, at a resolution capped to the display size."""
        from core.services.terrain.grid import GridSpec, spec_for_bounds_wgs84, WEB_MERCATOR_CRS

        cache = self._pod_cache()
        if cache is not None and cache.has_result():
            result = cache.get_result()
            rows, cols = result.pod.shape
            if rows and cols:
                return GridSpec(crs=WEB_MERCATOR_CRS, transform=result.transform,
                                width=int(cols), height=int(rows))

        lats = [d['latitude'] for d in self.gps_data]
        lons = [d['longitude'] for d in self.gps_data]
        if not lats:
            return None
        pad_deg = 200.0 / 111320.0
        bounds = (min(lons) - pad_deg, min(lats) - pad_deg,
                  max(lons) + pad_deg, max(lats) + pad_deg)
        span_m = max((bounds[2] - bounds[0]) * 111320.0 * math.cos(math.radians(lats[0])),
                     (bounds[3] - bounds[1]) * 111320.0)
        res_m = max(2.0, span_m / float(self._max_overlay_dim))
        return spec_for_bounds_wgs84(bounds, res_m)

    @staticmethod
    def _build_canopy_rgba(canopy, spec, logger):
        """Sample + colorize the canopy for ``spec``. Worker-thread safe: touches
        only numpy/rasterio, never QPixmap (pixmaps must be built on the GUI
        thread). Returns an RGBA ndarray or None."""
        try:
            sample = canopy.sample_grid_spec(spec)
        except Exception as e:
            logger.warning(f"Canopy overlay: sampling failed: {e}")
            return None
        if sample is None or sample.chm is None:
            return None
        from core.services.coverage.colormap import chm_to_rgba
        return chm_to_rgba(sample.chm)

    @staticmethod
    def _canopy_cache_key(spec):
        return (spec.crs, tuple(spec.transform)[:6], spec.width, spec.height)

    def _build_canopy_pixmap(self):
        """(QPixmap, transform6) of canopy height over the mission extent, or
        None when no canopy source is configured / no tile covers the area.

        Synchronous path (also the worker's core); the interactive overlay
        toggle goes through _start_canopy_overlay_build so the sampling runs
        off the GUI thread.
        """
        canopy = self._canopy_service()
        if canopy is None:
            return None
        spec = self._canopy_extent_spec()
        if spec is None:
            return None

        key = self._canopy_cache_key(spec)
        if self._canopy_overlay_cache and self._canopy_overlay_cache[0] == key:
            return self._canopy_overlay_cache[1], self._canopy_overlay_cache[2]

        rgba = self._build_canopy_rgba(canopy, spec, self.logger)
        if rgba is None:
            return None
        pixmap, transform6 = self._rgba_to_pixmap(rgba, spec.transform)
        self._canopy_overlay_cache = (key, pixmap, transform6)
        return pixmap, transform6

    def _start_canopy_overlay_build(self, opacity):
        """Build the canopy overlay on a worker thread (a full-resolution
        sample + reproject can take seconds -- it must not freeze the UI).
        Delivery lands back on the GUI thread via the worker's signal."""
        canopy = self._canopy_service()
        spec = self._canopy_extent_spec() if canopy is not None else None
        if canopy is None or spec is None:
            self._canopy_overlay_failed()
            return

        key = self._canopy_cache_key(spec)
        if self._canopy_overlay_cache and self._canopy_overlay_cache[0] == key:
            self._set_overlay(self._canopy_overlay_cache[1],
                              self._canopy_overlay_cache[2], 'canopy', opacity)
            return

        if self._canopy_worker is not None and self._canopy_worker.isRunning():
            # A build is already running; the newest request wins on delivery.
            self._canopy_pending_opacity = opacity
            return

        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast(
                self.tr("Building canopy overlay..."), 2000)
        self._canopy_pending_opacity = opacity
        self._canopy_worker = _CanopyOverlayWorker(canopy, spec, self.logger)
        self._canopy_worker.result_ready.connect(self._on_canopy_overlay_built)
        self._canopy_worker.start()

    def _on_canopy_overlay_built(self, rgba, spec):
        """GUI-thread delivery of a worker-built canopy RGBA array."""
        worker = self._canopy_worker
        self._canopy_worker = None
        if worker is not None:
            worker.wait(100)
        # The overlay may have been toggled off / switched while building.
        if not self._pod_overlay_enabled or self._pod_overlay_mode != 'canopy':
            return
        if rgba is None:
            self._canopy_overlay_failed()
            return
        pixmap, transform6 = self._rgba_to_pixmap(rgba, spec.transform)
        self._canopy_overlay_cache = (self._canopy_cache_key(spec), pixmap, transform6)
        self._set_overlay(pixmap, transform6, 'canopy', self._canopy_pending_opacity)

    def _canopy_overlay_failed(self):
        self._clear_pod_overlay()
        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast(
                self.tr("No canopy data covers this area"), 3000, color="#F44336")

    def _set_overlay(self, pixmap, transform6, mode, opacity):
        self._pod_overlay_enabled = True
        self._pod_overlay_mode = mode
        if self.map_dialog is None or not hasattr(self.map_dialog, 'map_view'):
            return
        view = self.map_dialog.map_view
        view.set_pod_overlay(pixmap, transform6)
        view.set_pod_overlay_opacity(opacity / 100.0)

    def enable_pod_overlay(self, mode='pod'):
        """Turn the overlay on from the cached result (called after an export run).

        Drive the dialog's controls (via activate_pod_overlay) rather than
        painting directly, so the POD Overlay button, mode dropdown, and
        opacity slider reflect the active overlay. The widget's
        pod_display_changed emission is what paints it (see on_pod_display_changed).
        """
        cache = self._pod_cache()
        if cache is None or not cache.has_result() or self.map_dialog is None:
            return
        if hasattr(self.map_dialog, 'activate_pod_overlay'):
            self.map_dialog.activate_pod_overlay(mode)
        else:
            # Fallback for a dialog without the widget-driven path.
            if hasattr(self.map_dialog, 'set_pod_available'):
                self.map_dialog.set_pod_available(True)
            self.on_pod_display_changed(True, mode, 70)

    def on_pod_display_changed(self, enabled, mode, opacity):
        """React to the dialog's overlay toggle / mode / opacity controls."""
        if not enabled or self.map_dialog is None:
            self._clear_pod_overlay()
            return

        if mode == 'canopy':
            # Sampling a large canopy source can take seconds; run it on a
            # worker thread and deliver the overlay when it's ready. Mark the
            # overlay as pending-enabled so delivery knows it's still wanted.
            self._pod_overlay_enabled = True
            self._pod_overlay_mode = mode
            self._start_canopy_overlay_build(opacity)
            return

        cache = self._pod_cache()
        if cache is None or not cache.has_result():
            self._clear_pod_overlay()
            return
        pixmap, transform6 = self._build_pod_pixmap(cache.get_result(), mode)
        self._set_overlay(pixmap, transform6, mode, opacity)

    def _clear_pod_overlay(self):
        self._pod_overlay_enabled = False
        if self.map_dialog is not None and hasattr(self.map_dialog, 'map_view'):
            self.map_dialog.map_view.clear_pod_overlay()

    def _show_pod_inspect_menu(self, sample, lat, lon):
        view = self.map_dialog.map_view if self.map_dialog else None
        menu = QMenu(view)
        hdr = menu.addAction(self.tr("POD: {pod}% (beta)   Looks: {looks}").format(
            pod=round(sample['pod'] * 100), looks=sample['looks']))
        hdr.setEnabled(False)
        lim = menu.addAction(self.tr("Limiting factor: {factor}").format(
            factor=self._limit_label(sample['limiting_factor'])))
        lim.setEnabled(False)
        frames = sample.get('frames', [])
        if frames:
            menu.addSeparator()
            self._add_frame_actions(menu, frames)
        menu.addSeparator()
        locate = menu.addAction(self.tr("Find location in images"))
        locate.triggered.connect(lambda checked=False: self._reverse_locate(lat, lon))
        menu.exec(QCursor.pos())

    def _add_frame_actions(self, menu, frames):
        """Add a menu entry per contributing frame (capped at 8).

        POD may have run over the full flight, so a frame id is NOT a viewer
        index. When the result carries frame_sources, resolve id -> image
        identity and map to a viewer slot by path: frames that produced an AOI
        open in the viewer; source-only captures (imaged the cell but flagged
        nothing) are shown for context but can't be opened (not in the
        gallery). Results without frame_sources are legacy — the frame id is a
        viewer index, preserved as-is.
        """
        result = None
        cache = self._pod_cache()
        if cache is not None and cache.has_result():
            result = cache.get_result()
        frame_sources = getattr(result, 'frame_sources', None)
        if not isinstance(frame_sources, list):
            frame_sources = None   # legacy / malformed result -> id is a viewer index

        if frame_sources is None:
            for fid in frames[:8]:
                if 0 <= fid < len(self.parent.images):
                    name = self.parent.images[fid].get(
                        'name', self.tr("Image {n}").format(n=fid + 1))
                    act = menu.addAction(self.tr("View {name}").format(name=name))
                    act.triggered.connect(
                        lambda checked=False, i=fid: self.on_map_image_selected(i))
            return

        viewer_index_by_path = {img.get('path'): i
                                for i, img in enumerate(self.parent.images)
                                if img.get('path')}
        for fid in frames[:8]:
            if not (0 <= fid < len(frame_sources)):
                continue
            src = frame_sources[fid]
            name = src.get('name') or self.tr("Image {n}").format(n=fid + 1)
            viewer_idx = viewer_index_by_path.get(src.get('path'))
            if viewer_idx is not None:
                act = menu.addAction(self.tr("View {name}").format(name=name))
                act.triggered.connect(
                    lambda checked=False, i=viewer_idx: self.on_map_image_selected(i))
            else:
                act = menu.addAction(self.tr("{name} (no flagged AOIs)").format(name=name))
                act.setEnabled(False)

    def update_current_image(self, image_index):
        """
        Update the map to highlight a new current image.

        Args:
            image_index: Index of the new current image in the viewer's image list
        """
        if self.map_dialog and self.map_dialog.isVisible():
            # Find the gps_data list index for this image
            for i, data in enumerate(self.gps_data):
                if data['index'] == image_index:
                    self.map_dialog.set_current_image(i)
                    break

            # Clear AOI marker when switching images (will be re-added if AOI is selected)
            self.map_dialog.update_aoi_marker(None, None)

    def update_zoom_fov(self, visible_rect):
        """
        Update the zoom FOV box on the GPS map (throttled).

        Coalesces the burst of viewChanged emissions a single wheel notch
        produces into at most one map redraw per throttle interval, so the
        terrain-projected FOV redraw cannot saturate the GUI thread.

        Args:
            visible_rect: QRectF in image pixel coordinates, or None to clear.
        """
        if not (self.map_dialog and self.map_dialog.isVisible()):
            return

        self._pending_fov_rect = visible_rect
        self._has_pending_fov = True

        if not self._fov_throttle.isActive():
            # Leading edge: draw the first update immediately for
            # responsiveness, then coalesce any that arrive during the window.
            self._flush_zoom_fov()
            self._fov_throttle.start()

    def _flush_zoom_fov(self):
        """Forward the most recent pending FOV rect to the map dialog."""
        if not self._has_pending_fov:
            return
        self._has_pending_fov = False
        if self.map_dialog and self.map_dialog.isVisible():
            self.map_dialog.update_zoom_fov(self._pending_fov_rect)

    def on_map_gps_clicked(self, lat, lon):
        """Handle a right-click on the map.

        When the POD overlay is active and the click lands on a covered cell,
        show a cell-inspect menu (POD, look count, limiting factor, contributing
        frames). Otherwise fall back to the reverse image lookup.
        """
        if self._pod_overlay_enabled:
            cache = self._pod_cache()
            result = cache.get_result() if (cache and cache.has_result()) else None
            sample = result.sample(lat, lon) if result is not None else None
            if sample is not None:
                self._show_pod_inspect_menu(sample, lat, lon)
                return
        self._reverse_locate(lat, lon)

    def _reverse_locate(self, lat, lon):
        """
        Find the image containing the coordinate and center the viewer on it.

        Args:
            lat: Clicked latitude
            lon: Clicked longitude
        """
        try:
            neighbor_service = AOINeighborService()
            terrain_service = None
            if getattr(self.parent, 'use_terrain_elevation', True):
                try:
                    terrain_service = _get_terrain_service()
                except Exception:
                    pass

            # Try current image first, then search others sorted by distance
            candidates = []
            current_idx = self.parent.current_image
            if 0 <= current_idx < len(self.parent.images):
                candidates.append(current_idx)

            # Sort other images by distance from clicked point
            other_indices = []
            for data in self.gps_data:
                idx = data['index']
                # Skip source-only entries (no AOI subset slot, so no image to open).
                if idx is None or idx == current_idx:
                    continue
                dlat = (data['latitude'] - lat) * 111320
                dlon = (data['longitude'] - lon) * 111320 * math.cos(math.radians(lat))
                dist = math.sqrt(dlat * dlat + dlon * dlon)
                other_indices.append((dist, idx))
            other_indices.sort()
            candidates.extend(idx for _, idx in other_indices[:10])

            for idx in candidates:
                if idx < 0 or idx >= len(self.parent.images):
                    continue
                image = self.parent.images[idx]
                coverage = neighbor_service.get_image_coverage_info(image)
                if not coverage:
                    continue

                # Apply terrain adjustment to altitude
                self._apply_terrain_altitude(coverage, lat, lon, terrain_service)

                pixel = neighbor_service.gps_to_pixel(lat, lon, coverage)
                if pixel is None:
                    continue
                u, v = pixel
                if not neighbor_service.is_point_in_image(u, v, coverage['width'], coverage['height']):
                    continue

                # Found a matching image — center the viewer
                if idx != current_idx:
                    self.parent.current_image = idx
                    self.parent._load_image()
                    # Defer centering until image is loaded
                    QTimer.singleShot(150, lambda px=(u, v): self._center_viewer_on_pixel(px))
                else:
                    self._center_viewer_on_pixel((u, v))
                return

            # No image contains this coordinate
            if hasattr(self.parent, 'status_controller'):
                self.parent.status_controller.show_toast(
                    self.tr("GPS coordinate not in any images"),
                    3000, color="#F44336"
                )

        except Exception as e:
            self.logger.error(f"Error handling GPS map click: {e}")

    def _apply_terrain_altitude(self, coverage, target_lat, target_lon, terrain_service):
        """Adjust coverage altitude with terrain elevation at the target location."""
        if not terrain_service or not terrain_service.enabled:
            return
        try:
            image_service = coverage.get('image_service')
            if not image_service:
                return
            absolute_alt = image_service.get_asl_altitude('m')
            if not absolute_alt:
                return
            geoid = terrain_service.get_geoid_undulation(coverage['center_lat'], coverage['center_lon'])
            drone_ortho = absolute_alt - (geoid or 0)
            click_terrain = terrain_service.get_elevation(target_lat, target_lon)
            if click_terrain.source == 'terrain' and click_terrain.elevation_m is not None:
                effective_agl = max(1.0, drone_ortho - click_terrain.elevation_m)
                coverage['altitude'] = effective_agl
        except Exception:
            pass

    def _center_viewer_on_pixel(self, pixel_xy):
        """Center the main image viewer on a pixel coordinate."""
        try:
            if self.parent.main_image and self.parent.main_image.hasImage():
                current_zoom = self.parent.main_image.getZoom()
                scale = max(current_zoom, 2.0)
                self.parent.main_image.zoomToArea(pixel_xy, scale)
        except Exception as e:
            self.logger.error(f"Error centering viewer: {e}")

    def close_map(self):
        """Close the GPS map window if it's open."""
        if self.map_dialog:
            self.map_dialog.close()
            self.map_dialog = None

    def on_map_dialog_closed(self):
        """Handle map dialog close event."""
        # Drop any queued FOV redraw so the throttle timer cannot wake after
        # the dialog is gone.
        self._fov_throttle.stop()
        self._has_pending_fov = False
        # Let an in-flight canopy build finish, then release the (potentially
        # very large) open canopy datasets deterministically.
        if self._canopy_worker is not None:
            try:
                self._canopy_worker.wait(2000)
            except Exception:
                pass
            self._canopy_worker = None
        self._close_canopy_service()
        self._canopy_svc_loaded = False
        if hasattr(self.parent, 'gps_map_open'):
            self.parent.gps_map_open = False
            if hasattr(self.parent, 'ui_style_controller'):
                self.parent.ui_style_controller.update_gps_map_button_style()

    def get_current_aoi_gps(self):
        """
        Get GPS coordinates for the currently selected AOI.

        Returns:
            Dict with AOI GPS data including coordinates and metadata, or None
        """
        try:
            # Check if we have a selected AOI
            if not hasattr(self.parent, 'aoi_controller') or self.parent.aoi_controller.selected_aoi_index < 0:
                return None

            # Get current image data
            current_image = self.parent.images[self.parent.current_image]

            # Get AOI data
            aoi_index = self.parent.aoi_controller.selected_aoi_index
            if 'areas_of_interest' not in current_image or aoi_index >= len(current_image['areas_of_interest']):
                return None

            aoi = current_image['areas_of_interest'][aoi_index]

            # Use AOIService for GPS calculation with metadata
            aoi_service = AOIService(current_image)

            # Get custom altitude if available
            custom_alt_ft = None
            if (hasattr(self.parent, 'custom_agl_altitude_ft') and
                    self.parent.custom_agl_altitude_ft and
                    self.parent.custom_agl_altitude_ft > 0):
                custom_alt_ft = self.parent.custom_agl_altitude_ft

            # Fall back to per-image AGL from Wingtra CSV data
            if custom_alt_ft is None:
                custom_alt_ft = current_image.get('wingtra_agl_ft')

            # Honor the terrain-elevation preference so the map marker matches
            # the viewer's AOI label and the exports
            use_terrain = getattr(self.parent, 'use_terrain_elevation', True)

            # Calculate AOI GPS coordinates with metadata using the convenience method
            aoi_gps = aoi_service.get_aoi_gps_with_metadata(current_image, aoi, aoi_index, custom_alt_ft, use_terrain)

            if not aoi_gps:
                return None

            # Add additional viewer-specific metadata
            aoi_gps['image_index'] = self.parent.current_image
            aoi_gps['image_name'] = current_image.get('name', 'Unknown')

            # Get color/temperature info if available
            if hasattr(self.parent.aoi_controller, 'calculate_aoi_average_info'):
                # Get temperature data from thermal controller if available
                temperature_data = None
                if hasattr(self.parent, 'thermal_controller'):
                    temperature_data = self.parent.thermal_controller.temperature_data

                avg_info, _ = self.parent.aoi_controller.calculate_aoi_average_info(
                    aoi,
                    self.parent.is_thermal,
                    temperature_data,
                    self.parent.temperature_unit
                )
                aoi_gps['avg_info'] = avg_info

            return aoi_gps

        except Exception as e:
            self.logger.error(f"Error getting current AOI GPS: {e}")
            return None

    def calculate_gsd_for_image(self, image_path, custom_altitude_ft=None):
        """
        Calculate GSD for an image if not already available.

        Args:
            image_path: Path to the image file
            custom_altitude_ft: Optional custom altitude in feet

        Returns:
            GSD in cm/px or None if calculation fails
        """
        try:
            image_service = ImageService(image_path, '')

            # Use the existing ImageService method to get average GSD
            avg_gsd = image_service.get_average_gsd(custom_altitude_ft=custom_altitude_ft)
            return avg_gsd

        except Exception:
            return None

    def update_aoi_on_map(self):
        """Update the AOI display on the map if it's open."""
        if self.map_dialog and self.map_dialog.isVisible():
            aoi_gps = self.get_current_aoi_gps()

            # Get the identifier color from settings
            identifier_color = self.parent.settings.get('identifier_color', [255, 255, 0])

            self.map_dialog.update_aoi_marker(aoi_gps, identifier_color)
