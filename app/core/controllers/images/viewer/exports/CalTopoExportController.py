"""
CalTopoExportController - Handles CalTopo export functionality.

This controller coordinates the authentication, map selection, and export
of flagged AOIs to CalTopo maps.
"""

import os
from pathlib import Path

import cv2

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QThread, QEventLoop, Signal
from core.services.export.CalTopoService import CalTopoService
from core.services.export.CalTopoAPIService import CalTopoAPIService
from core.services.export.CalTopoCredentialHelper import CalTopoCredentialHelper
from core.services.export.CalTopoPublishers import CalTopoApiPublisher, CalTopoBrowserPublisher
from core.services.export.AOIThumbnailService import AOIThumbnailService
from core.views.images.viewer.dialogs.CalTopoAuthDialog import CalTopoAuthDialog
from core.views.images.viewer.dialogs.CalTopoCredentialDialog import CalTopoCredentialDialog
from core.views.images.viewer.dialogs.CalTopoAPIMapDialog import CalTopoAPIMapDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.services.LoggerService import LoggerService
from core.services.image.ImageService import ImageService
from core.services.image.AOIService import AOIService
from core.services.image.AOICompositeService import AOICompositeService
from core.services.image.CoverageExtentService import CoverageExtentService
from helpers.FormatHelper import FormatHelper
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper
from helpers.TranslationMixin import TranslationMixin


class CalTopoAccountDataThread(QThread):
    """Thread for fetching CalTopo account data."""

    finished = Signal(bool, dict)  # success, account_data
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)

    def __init__(self, api_service, team_id, credential_id, credential_secret):
        """
        Initialize the account data thread.

        Args:
            api_service: CalTopoAPIService instance
            team_id: Team ID
            credential_id: Credential ID
            credential_secret: Credential Secret
        """
        super().__init__()
        self.api_service = api_service
        self.team_id = team_id
        self.credential_id = credential_id
        self.credential_secret = credential_secret

    def run(self):
        """
        Execute the account data fetch.

        Fetches account data from the CalTopo API using the provided credentials.
        Emits progress updates and signals completion or error.
        """
        try:
            self.progressUpdated.emit(0, 100, "Connecting to CalTopo API...")
            success, account_data = self.api_service.get_account_data(
                self.team_id, self.credential_id, self.credential_secret
            )
            if success and account_data:
                self.progressUpdated.emit(100, 100, "Account data loaded")
                self.finished.emit(True, account_data)
            else:
                # Report the failure too; leaving the bar at 0% "Connecting..."
                # made a refusal look like a stall.
                self.progressUpdated.emit(100, 100, "CalTopo rejected the request")
                self.finished.emit(False, {})
        except Exception as e:
            self.errorOccurred.emit(str(e))


class CalTopoDataPreparationThread(QThread):
    """Thread for preparing CalTopo export data (markers and polygons)."""

    finished = Signal(list, list)  # markers, polygons
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)
    canceled = Signal()

    def __init__(self, controller, images, flagged_aois, include_flagged_aois,
                 include_locations, include_images_without_flagged_aois, include_coverage_area, include_images,
                 aoi_photo_mode='full'):
        """
        Initialize the data preparation thread.

        Args:
            controller: CalTopoExportController instance (for accessing preparation methods)
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_flagged_aois: Whether to include flagged AOIs
            include_locations: Whether to include locations
            include_images_without_flagged_aois: Whether to include images without flagged AOIs in location export
            include_coverage_area: Whether to include coverage area
            include_images: Whether to include images
            aoi_photo_mode: Photo(s) to attach to flagged AOI markers ('full', 'thumbnail', or 'both')
        """
        super().__init__()
        self.controller = controller
        self.images = images
        self.flagged_aois = flagged_aois
        self.include_flagged_aois = include_flagged_aois
        self.include_locations = include_locations
        self.include_images_without_flagged_aois = include_images_without_flagged_aois
        self.include_coverage_area = include_coverage_area
        self.include_images = include_images
        self.aoi_photo_mode = aoi_photo_mode
        self._cancelled = False

    def cancel(self):
        """
        Cancel the preparation operation.

        Sets the cancellation flag to stop the thread execution.
        """
        self._cancelled = True

    def is_cancelled(self):
        """
        Check if operation is cancelled.

        Returns:
            bool: True if the operation has been cancelled, False otherwise.
        """
        return self._cancelled

    def run(self):
        """
        Execute the data preparation.

        Prepares markers and polygons for CalTopo export based on the configured
        options. Emits progress updates and signals completion or error.
        """
        try:
            markers = []
            polygons = []

            if self.include_flagged_aois:
                if self.is_cancelled():
                    self.canceled.emit()
                    return
                self.progressUpdated.emit(0, 100, "Preparing flagged AOI markers...")
                markers.extend(self.controller._prepare_markers(
                    self.images, self.flagged_aois, include_images=self.include_images,
                    aoi_photo_mode=self.aoi_photo_mode
                ))

            if self.include_locations and not self.is_cancelled():
                self.progressUpdated.emit(33, 100, "Preparing location markers...")
                # Filter images for locations based on flag
                images_for_locations = []
                for img_idx, img in enumerate(self.images):
                    if img.get('hidden', False):
                        continue
                    has_flagged_aois = img_idx in self.flagged_aois and len(self.flagged_aois[img_idx]) > 0
                    if has_flagged_aois or self.include_images_without_flagged_aois:
                        images_for_locations.append(img)
                markers.extend(self.controller._prepare_location_markers(
                    images_for_locations, include_images=self.include_images
                ))

            if self.include_coverage_area and not self.is_cancelled():
                self.progressUpdated.emit(66, 100, "Calculating coverage polygons...")
                # Determine which images should be included for coverage
                # Coverage should only include images that are actually being exported
                exported_image_indices = set()

                # Add images with flagged AOIs if flagged AOIs are included
                if self.include_flagged_aois:
                    exported_image_indices.update(self.flagged_aois.keys())

                # Add images for locations if locations are included
                if self.include_locations:
                    for img_idx, img in enumerate(self.images):
                        if img.get('hidden', False):
                            continue
                        has_flagged_aois = img_idx in self.flagged_aois and len(self.flagged_aois[img_idx]) > 0
                        if has_flagged_aois or self.include_images_without_flagged_aois:
                            exported_image_indices.add(img_idx)

                # Filter images to only those being exported
                images_for_coverage = [self.images[idx] for idx in exported_image_indices if idx < len(self.images)]
                polygons.extend(self.controller._prepare_coverage_polygons(images_for_coverage))

            if self.is_cancelled():
                self.canceled.emit()
                return

            self.progressUpdated.emit(100, 100, "Data preparation complete")
            self.finished.emit(markers, polygons)

        except Exception as e:
            self.errorOccurred.emit(str(e))


class CalTopoExportThread(QThread):
    """Thread that publishes markers and polygons to CalTopo.

    Transport-agnostic: it drives a publisher (Team API or captured browser
    session), so both authentication modes share one export loop.
    """

    finished = Signal(dict)  # summary produced by _summary()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)
    canceled = Signal()

    def __init__(self, publisher, controller, images, flagged_aois,
                 include_flagged_aois, include_locations,
                 include_images_without_flagged_aois, include_coverage_area, include_images,
                 aoi_photo_mode='full', markers=None, polygons=None):
        """
        Initialize the CalTopo export thread.

        Args:
            publisher: Object exposing add_marker/add_polygon/upload_photo.
            controller: CalTopoExportController instance (for preparation methods)
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_flagged_aois: Whether to include flagged AOIs
            include_locations: Whether to include locations
            include_images_without_flagged_aois: Whether to include images without flagged AOIs in location export
            include_coverage_area: Whether to include coverage area
            include_images: Whether to include images
            aoi_photo_mode: Photo(s) to attach to flagged AOI markers ('full', 'thumbnail', or 'both')
            markers: Pre-prepared markers; prepared in-thread when None.
            polygons: Pre-prepared polygons; prepared in-thread when None.
        """
        super().__init__()
        self.publisher = publisher
        self.controller = controller
        self.images = images
        self.flagged_aois = flagged_aois
        self.include_flagged_aois = include_flagged_aois
        self.include_locations = include_locations
        self.include_images_without_flagged_aois = include_images_without_flagged_aois
        self.include_coverage_area = include_coverage_area
        self.include_images = include_images
        self.aoi_photo_mode = aoi_photo_mode
        self.markers = markers
        self.polygons = polygons
        self._cancelled = False

    def cancel(self):
        """
        Cancel the export operation.

        Sets the cancellation flag to stop the thread execution.
        """
        self._cancelled = True

    def is_cancelled(self):
        """
        Check if operation is cancelled.

        Returns:
            bool: True if the operation has been cancelled, False otherwise.
        """
        return self._cancelled

    def run(self):
        """Execute the export operation (preparation and export both happen in thread)."""
        try:
            markers, polygons = self._collect()
            if markers is None:
                return
            self._publish(markers, polygons)
        except Exception as e:
            self.errorOccurred.emit(str(e))

    def _collect(self):
        """Gather the markers and polygons to publish.

        Returns:
            tuple: (markers, polygons), or (None, None) if cancelled.
        """
        if self.markers is not None or self.polygons is not None:
            # Already prepared before authentication so the user could be told
            # there was nothing to export before being asked to log in.
            return list(self.markers or []), list(self.polygons or [])

        markers = []
        polygons = []

        if self.include_flagged_aois:
            if self.is_cancelled():
                self.canceled.emit()
                return None, None
            self.progressUpdated.emit(0, 100, "Preparing flagged AOI markers...")
            markers.extend(self.controller._prepare_markers(
                self.images, self.flagged_aois, include_images=self.include_images,
                aoi_photo_mode=self.aoi_photo_mode
            ))

        if self.include_locations and not self.is_cancelled():
            self.progressUpdated.emit(20, 100, "Preparing location markers...")
            # Filter images for locations based on flag
            images_for_locations = []
            for img_idx, img in enumerate(self.images):
                if img.get('hidden', False):
                    continue
                has_flagged_aois = img_idx in self.flagged_aois and len(self.flagged_aois[img_idx]) > 0
                if has_flagged_aois or self.include_images_without_flagged_aois:
                    images_for_locations.append(img)
            markers.extend(self.controller._prepare_location_markers(
                images_for_locations, include_images=self.include_images
            ))

        if self.include_coverage_area and not self.is_cancelled():
            self.progressUpdated.emit(40, 100, "Calculating coverage polygons...")
            # Determine which images should be included for coverage
            # Coverage should only include images that are actually being exported
            exported_image_indices = set()

            # Add images with flagged AOIs if flagged AOIs are included
            if self.include_flagged_aois:
                exported_image_indices.update(self.flagged_aois.keys())

            # Add images for locations if locations are included
            if self.include_locations:
                for img_idx, img in enumerate(self.images):
                    if img.get('hidden', False):
                        continue
                    has_flagged_aois = img_idx in self.flagged_aois and len(self.flagged_aois[img_idx]) > 0
                    if has_flagged_aois or self.include_images_without_flagged_aois:
                        exported_image_indices.add(img_idx)

            # Filter images to only those being exported
            images_for_coverage = [self.images[idx] for idx in exported_image_indices if idx < len(self.images)]
            polygons.extend(self.controller._prepare_coverage_polygons(images_for_coverage))

        if self.is_cancelled():
            self.canceled.emit()
            return None, None

        return markers, polygons

    def _publish(self, markers, polygons):
        """Create every marker and polygon, then emit a summary.

        Args:
            markers (list): Marker dictionaries.
            polygons (list): Polygon dictionaries.
        """
        marker_success = 0
        polygon_success = 0
        photos_total = 0
        photos_uploaded = 0
        total = len(markers) + len(polygons)

        for index, marker in enumerate(markers, start=1):
            if self.is_cancelled():
                self.canceled.emit()
                return

            progress = 50 + int((index / len(markers)) * 40)
            self.progressUpdated.emit(
                progress,
                100,
                f"Exporting marker {index} of {len(markers)}: {marker.get('title', 'Unknown')[:40]}..."
            )

            success, marker_id = self.publisher.add_marker(marker)
            if not success:
                continue
            marker_success += 1

            if not marker_id:
                continue

            # A marker can carry several photos (e.g. close-up plus overview);
            # _get_marker_photos also handles fallbacks for missing files
            for photo in self.controller._get_marker_photos(marker):
                if self.is_cancelled():
                    self.canceled.emit()
                    return

                photos_total += 1
                self.progressUpdated.emit(
                    progress,
                    100,
                    f"Uploading photo {photos_total}: {os.path.basename(photo['path'])}..."
                )
                photo_ok, _ = self.publisher.upload_photo(
                    marker, marker_id, photo_path=photo['path'], title=photo['title']
                )
                if photo_ok:
                    photos_uploaded += 1

        for index, polygon in enumerate(polygons, start=1):
            if self.is_cancelled():
                self.canceled.emit()
                return

            progress = 90 + int((index / len(polygons)) * 10)
            self.progressUpdated.emit(
                progress,
                100,
                f"Exporting polygon {index} of {len(polygons)}: {polygon.get('title', 'Unknown')[:40]}..."
            )

            success, _ = self.publisher.add_polygon(polygon)
            if success:
                polygon_success += 1

        if self.is_cancelled():
            self.canceled.emit()
            return

        objects_created = marker_success + polygon_success
        self.finished.emit({
            'success': objects_created > 0,
            'objects_created': objects_created,
            'objects_total': total,
            'photos_uploaded': photos_uploaded,
            'photos_total': photos_total,
        })


class CalTopoExportController(TranslationMixin):
    """
    Controller for managing CalTopo export functionality.

    Handles authentication flow, map selection, and export of flagged AOIs
    and/or image locations to CalTopo maps as markers/waypoints.
    """

    def __init__(self, parent_widget, logger=None):
        """
        Initialize the CalTopo export controller.

        Args:
            parent_widget: The parent widget for dialogs
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()
        self.caltopo_service = CalTopoService(logger=self.logger)  # Browser-session HTTP client
        self.caltopo_api_service = CalTopoAPIService(logger=self.logger)  # API-based service
        self.credential_helper = CalTopoCredentialHelper()
        self._account_thread = None
        # Created lazily during marker preparation; generate the per-export AOI
        # photos (zoomed crops and multi-zoom composites) into a temp dir
        self.aoi_thumbnail_service = None
        self.aoi_composite_service = None

    def export_to_caltopo(
            self,
            images,
            flagged_aois,
            include_flagged_aois=True,
            include_locations=False,
            include_images_without_flagged_aois=True,
            include_coverage_area=False,
            include_images=True,
            aoi_photo_mode='full'):
        """
        Export data to CalTopo.

        Args:
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_flagged_aois (bool): Include flagged AOIs as markers
            include_locations (bool): Include drone/image locations as markers
            include_images_without_flagged_aois (bool): Include images without flagged AOIs in location export
            include_coverage_area (bool): Include coverage area as polygons
            include_images (bool): Upload photos to CalTopo markers
            aoi_photo_mode (str): Photo(s) to attach to flagged AOI markers:
                'full' (multi-zoom composite, as in the PDF report),
                'thumbnail' (zoomed AOI crop), or 'both'

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            if self._is_offline_only():
                QMessageBox.information(
                    self.parent,
                    self.tr("Offline Mode Enabled"),
                    self.tr(
                        "Offline Only is turned on in Preferences:\n\n"
                        "• Map tiles will not be retrieved.\n"
                        "• CalTopo integration is disabled.\n\n"
                        "Turn off Offline Only to export to CalTopo."
                    )
                )
                return False

            if not include_flagged_aois and not include_locations and not include_coverage_area:
                QMessageBox.information(
                    self.parent,
                    self.tr("Nothing Selected"),
                    self.tr(
                        "Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export."
                    )
                )
                return False

            # Step 1: Prepare markers and polygons in a background thread
            prep_dialog = ExportProgressDialog(
                self.parent,
                title=self.tr("Preparing Export Data"),
                total_items=100
            )
            prep_dialog.set_title(self.tr("Preparing data for export..."))
            prep_dialog.set_status(self.tr("Processing images and AOIs..."))

            markers = []
            coverage_polygons = []
            prep_error = None

            def on_prep_progress(current, total, message):
                prep_dialog.update_progress(current, total, message)
                QApplication.processEvents()

            def on_prep_finished(markers_result, polygons_result):
                nonlocal markers, coverage_polygons
                markers = markers_result
                coverage_polygons = polygons_result
                prep_dialog.accept()

            def on_prep_error(error_message):
                nonlocal prep_error
                prep_error = error_message
                prep_dialog.reject()

            def on_prep_cancelled():
                prep_dialog.reject()

            prep_thread = CalTopoDataPreparationThread(
                self, images, flagged_aois, include_flagged_aois,
                include_locations, include_images_without_flagged_aois, include_coverage_area, include_images,
                aoi_photo_mode=aoi_photo_mode
            )
            prep_thread.progressUpdated.connect(on_prep_progress)
            prep_thread.finished.connect(on_prep_finished)
            prep_thread.errorOccurred.connect(on_prep_error)
            prep_thread.canceled.connect(on_prep_cancelled)
            prep_dialog.cancel_requested.connect(prep_thread.cancel)

            prep_thread.start()
            # exec() shows the dialog itself; pumping events first can deliver
            # the worker's completion before the modal loop exists.
            prep_dialog.exec()

            prep_thread.wait()

            if prep_error:
                QMessageBox.critical(
                    self.parent,
                    self.tr("Preparation Error"),
                    self.tr(
                        "An error occurred while preparing export data:\n\n{error}"
                    ).format(error=prep_error)
                )
                return False

            if not markers and not coverage_polygons:
                # Build appropriate error message based on what was selected
                selected_types = []
                if include_flagged_aois:
                    selected_types.append(self.tr("flagged AOIs"))
                if include_locations:
                    selected_types.append(self.tr("image locations"))
                if include_coverage_area:
                    selected_types.append(self.tr("coverage area"))

                if include_flagged_aois and include_locations and include_coverage_area:
                    message = self.tr(
                        "No flagged AOIs, geotagged image locations, or coverage areas are available.\n"
                        "Flag some AOIs with the 'F' key or ensure your images have GPS metadata."
                    )
                elif include_flagged_aois:
                    total_flagged = sum(len(aois) for aois in flagged_aois.values())
                    message = self.tr(
                        "Found {count} flagged AOI(s), but could not extract GPS coordinates.\n\n"
                        "This usually means:\n"
                        "• The images don't have GPS data in their EXIF metadata\n"
                        "• The image files have been moved or renamed\n\n"
                        "Please ensure your images have GPS coordinates embedded."
                    ).format(count=total_flagged)
                elif include_locations:
                    message = self.tr(
                        "No geotagged drone/image locations were found.\n"
                        "Ensure your images contain GPS metadata and try again."
                    )
                elif include_coverage_area:
                    message = self.tr(
                        "No coverage area polygons could be calculated.\n\n"
                        "This usually means:\n"
                        "• The images don't have GPS data in their EXIF metadata\n"
                        "• The images are not nadir (gimbal pitch must be between -85° and -95°;\n"
                        "  WALDO images: boresight within 40° of nadir)\n"
                        "• GSD (ground sample distance) could not be calculated\n\n"
                        "Please ensure your images have GPS coordinates and are near-nadir shots."
                    )
                else:
                    message = self.tr(
                        "No {types} are available to export."
                    ).format(types=" or ".join(selected_types))

                QMessageBox.information(
                    self.parent,
                    self.tr("Nothing to Export"),
                    message
                )
                return False

            # Step 2: Authenticate in the embedded browser, then publish over
            # plain HTTP with the captured session. The browser is a login
            # surface only - it does not run the export.
            selected_map_id = None
            captured_cookies = None
            captured_account_id = None

            auth_dialog = CalTopoAuthDialog(self.parent)

            def on_authenticated(payload):
                nonlocal selected_map_id, captured_cookies, captured_account_id

                if isinstance(payload, dict):
                    selected_map_id = payload.get('map_id') or payload.get('__map_id')
                    captured_cookies = payload.get('cookies')
                    captured_account_id = payload.get('account_id')

                if not selected_map_id:
                    QMessageBox.warning(
                        auth_dialog,
                        self.tr("No Map Selected"),
                        self.tr(
                            "Please navigate to a CalTopo map before clicking 'I'm Logged In'.\n\n"
                            "The map URL should look like:\n"
                            "https://caltopo.com/map.html#...&id=ABC123"
                        )
                    )
                    return

                auth_dialog.accept()

            auth_dialog.authenticated.connect(on_authenticated)

            # Every bail-out below used to be a silent `return False`, so a run
            # that stopped here left no trace at all. Say which gate closed.

            # Deliberately not auth_dialog.exec(). A modal loop exits on any
            # hide of the dialog, and embedding a QWebEngineView causes one;
            # that silently aborted the export before the user could log in.
            # Waiting on finished() keys the outcome to done() alone.
            try:
                auth_dialog.show()
                wait_loop = QEventLoop()
                auth_dialog.finished.connect(lambda _result: wait_loop.quit())
                wait_loop.exec()
                dialog_result = auth_dialog.result()
            finally:
                auth_dialog.deleteLater()

            if dialog_result != CalTopoAuthDialog.Accepted:
                self.logger.warning(
                    f"CalTopo browser export cancelled: login dialog closed without "
                    f"authenticating (result={dialog_result})."
                )
                return False

            if not selected_map_id:
                self.logger.warning(
                    "CalTopo browser export stopped: the login dialog was accepted but "
                    "no map ID was captured. Navigate to a map before exporting."
                )
                QMessageBox.warning(
                    self.parent,
                    self.tr("No Map Selected"),
                    self.tr(
                        "No CalTopo map was selected, so there was nothing to export to.\n\n"
                        "Open your map in the CalTopo window before clicking "
                        "'I'm Logged In - Export Data'."
                    )
                )
                return False

            if not captured_cookies:
                self.logger.error(
                    "CalTopo browser export stopped: no session cookies were captured."
                )
                QMessageBox.critical(
                    self.parent,
                    self.tr("Authentication Failed"),
                    self.tr("No CalTopo session cookies were captured. Please log in and try again.")
                )
                return False

            # Hand the captured session to the HTTP client used for the export.
            self.caltopo_service.save_session(captured_cookies)
            self.caltopo_service.set_account_id(captured_account_id)

            # Step 3: Publish, reusing the same worker the API path uses.
            return self._run_export(
                CalTopoBrowserPublisher(self.caltopo_service, selected_map_id),
                images, flagged_aois,
                include_flagged_aois, include_locations,
                include_images_without_flagged_aois, include_coverage_area, include_images,
                aoi_photo_mode=aoi_photo_mode,
                markers=markers, polygons=coverage_polygons
            )

        except Exception as e:
            self.logger.error(f"CalTopo export error: {e}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Error"),
                self.tr(
                    "An error occurred during CalTopo export:\n\n{error}"
                ).format(error=str(e))
            )
            return False
        finally:
            # Generated AOI photos live in a temp dir; drop them once the export ends
            self._cleanup_aoi_thumbnails()

    def _is_offline_only(self) -> bool:
        """Return whether OfflineOnly is enabled on the parent settings service."""
        try:
            if hasattr(self.parent, "settings_service"):
                return self.parent.settings_service.get_bool_setting("OfflineOnly", False)
        except Exception:
            pass
        return False

    def _prepare_markers(self, images, flagged_aois, include_images=True, aoi_photo_mode='full'):
        """Prepare marker data from flagged AOIs.

        Args:
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_images (bool): Whether to include photos for upload
            aoi_photo_mode (str): Which photo(s) to attach to each AOI marker:
                'full' (multi-zoom composite, as in the PDF report),
                'thumbnail' (zoomed AOI crop), or 'both'

        Returns:
            list: List of marker dictionaries with 'lat', 'lon', 'title', 'description'
        """
        markers = []

        if include_images:
            # The mode decides what gets generated below; record it for diagnosis
            self.logger.info(f"CalTopo AOI photo mode: {aoi_photo_mode}")

        for img_idx, aoi_indices in flagged_aois.items():
            if img_idx >= len(images):
                continue

            image = images[img_idx]

            # Skip hidden images - don't export their flagged AOIs
            if image.get('hidden', False):
                continue

            image_name = image.get('name', f'Image {img_idx + 1}')
            image_path = image.get('path', '')

            # Get image GPS coordinates and metadata
            try:
                # Create ImageService to extract EXIF data
                calculated_bearing = image.get('bearing', None)
                image_service = ImageService(image_path, image.get('mask_path', ''), calculated_bearing=calculated_bearing)

                # Get GPS from EXIF data
                exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
                image_gps = LocationInfo.get_gps(exif_data=exif_data)

                if not image_gps:
                    continue

                # Get image dimensions for AOI GPS calculation
                img_array = image_service.img_array
                height, width = img_array.shape[:2]

                # Get bearing
                # Use get_drone_orientation() for nadir shots (gimbal check below ensures nadir)
                # For nadir shots, drone body orientation determines ground orientation, not gimbal yaw
                bearing = image_service.get_camera_yaw()
                if bearing is None:
                    bearing = 0  # Default to north

                # Get custom altitude if viewer has one set
                custom_alt = None
                if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                    custom_alt = self.parent.custom_agl_altitude_ft

                # Get GSD (try from parent viewer first)
                gsd_cm = None
                if hasattr(self.parent, 'messages'):
                    gsd_value = self.parent.messages.get('GSD (cm/px)', None)
                    if gsd_value:
                        try:
                            gsd_cm = float(gsd_value.split()[0])
                        except (ValueError, IndexError):
                            pass

                # Calculate GSD if not available
                if gsd_cm is None:
                    gsd_cm = image_service.get_average_gsd(custom_altitude_ft=custom_alt)

            except Exception:
                continue

            # Composites reuse this image's already-loaded pixels; build the
            # shared per-image context once, not per AOI
            composite_context = None
            if include_images and aoi_photo_mode in ('full', 'both'):
                composite_context = self._build_composite_context(image, image_path, img_array, bearing)

            # Get AOI data
            aois = image.get('areas_of_interest', [])

            for aoi_idx in aoi_indices:
                if aoi_idx >= len(aois):
                    continue

                aoi = aois[aoi_idx]
                center = aoi.get('center', [0, 0])
                area = aoi.get('area', 0)

                # Calculate AOI-specific GPS coordinates with fallback
                # Default to image GPS (always available as fallback)
                aoi_lat = image_gps['latitude']
                aoi_lon = image_gps['longitude']
                gps_note = ""

                # Try to calculate precise AOI GPS using AOIService
                try:
                    aoi_service = AOIService(image)

                    # Get custom altitude if viewer has one set
                    custom_alt_ft = None
                    if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                        custom_alt_ft = self.parent.custom_agl_altitude_ft

                    # Get terrain preference
                    use_terrain = getattr(self.parent, 'use_terrain_elevation', True)

                    # Calculate AOI GPS coordinates using the convenience method
                    result = aoi_service.calculate_gps_with_custom_altitude(image, aoi, custom_alt_ft, use_terrain)

                    if result:
                        aoi_lat, aoi_lon = result
                        gps_note = "Estimated AOI GPS\n"
                    else:
                        gps_note = "Image GPS (calculation failed)\n"
                except Exception as e:
                    gps_note = f"Image GPS (calculation error: {str(e)[:30]})\n"

                # Get color information using AOIService
                color_info = ""
                marker_rgb = None
                try:
                    color_result = aoi_service.get_cached_or_representative_color(aoi)
                    if color_result:
                        marker_rgb = color_result['rgb']
                        color_info = f"Color/Temp: Hue: {color_result['hue_degrees']}° {color_result['hex']}\n"
                except Exception:
                    # If color calculation fails, continue without color
                    pass

                # Create marker for this AOI
                marker_title = f"{image_name} - AOI {aoi_idx + 1}"

                # Get user comment if available
                user_comment = aoi.get('user_comment', '')

                # Build description with user comment at the top if present
                description = ""
                if user_comment:
                    description = f'"{user_comment}"\n\n'

                # Add confidence info if available
                confidence_info = ""
                if 'confidence' in aoi:
                    confidence = aoi['confidence']
                    score_type = aoi.get('score_type', 'unknown')
                    confidence_info = f"Confidence: {confidence:.1f}% ({score_type})\n"

                description += (
                    f"Flagged AOI from {image_name}\n"
                    f"{gps_note}"
                    f"AOI Index: {aoi_idx + 1}\n"
                    f"Center: ({center[0]}, {center[1]})\n"
                    f"Area: {area:.0f} pixels\n"
                    f"{confidence_info}"
                    f"{color_info}"
                )

                marker = {
                    'lat': aoi_lat,
                    'lon': aoi_lon,
                    'title': marker_title,
                    'description': description,
                    'rgb': marker_rgb,  # RGB tuple (R, G, B) or None
                }
                # Only include photos if they should be uploaded
                if include_images:
                    # Keep the plain image path as the last-resort fallback; the
                    # generated photo(s) for the selected mode go in 'photos'
                    marker['image_path'] = image_path
                    photos = self._build_aoi_photos(
                        image_path, image_name, aoi, aoi_idx, aoi_photo_mode,
                        composite_context=composite_context
                    )
                    if photos:
                        marker['photos'] = photos

                markers.append(marker)

            # Free the rotated-image cache for this image before moving to the next
            if composite_context is not None and self.aoi_composite_service is not None:
                self.aoi_composite_service.clear_cache_for(composite_context['cache_key'])

        return markers

    def _prepare_location_markers(self, images, include_images=True):
        """Prepare marker data for drone/image locations.

        Args:
            images: List of image data dictionaries
            include_images (bool): Whether to include image_path for photo uploads

        Returns:
            list: List of marker dictionaries with 'lat', 'lon', 'title', 'description'
        """
        markers = []

        for img_idx, image in enumerate(images):
            if image.get('hidden', False):
                continue

            image_name = image.get('name', f'Image {img_idx + 1}')
            image_path = image.get('path', '')
            if not image_path:
                continue

            try:
                image_service = ImageService(image_path, image.get('mask_path', ''))
                image_gps = LocationInfo.get_gps(exif_data=image_service.exif_data)

                if not image_gps:
                    continue

                custom_alt = None
                if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                    custom_alt = self.parent.custom_agl_altitude_ft

                # The reference plane travels with the value - see
                # KMLGeneratorService for why all three cases differ.
                # Resolved by the service, rendered by FormatHelper - see
                # KMLGeneratorService for why both planes are exported.
                readings = image_service.get_altitude_readings(
                    'ft',
                    use_terrain=getattr(self.parent, 'use_terrain_elevation', True),
                    custom_altitude_ft=custom_alt, offline_only=False)

                gimbal_pitch = image_service.get_camera_pitch()
                gimbal_yaw = image_service.get_camera_yaw()

                description = "Drone/Image Location\n"
                description += f"Image: {image_name}\n"
                description += f"GPS: {image_gps['latitude']:.6f}, {image_gps['longitude']:.6f}\n"

                for line in FormatHelper.altitude_lines(readings):
                    description += f"{line}\n"
                if gimbal_pitch is not None:
                    description += f"Gimbal Pitch: {gimbal_pitch:.1f}°\n"
                if gimbal_yaw is not None:
                    description += f"Gimbal Yaw: {gimbal_yaw:.1f}°\n"

                marker = {
                    'lat': image_gps['latitude'],
                    'lon': image_gps['longitude'],
                    'title': image_name,
                    'description': description,
                    'marker_color': '1E88E5',
                    'marker_symbol': 'info',
                }
                # Only include image_path if photos should be uploaded
                if include_images:
                    marker['image_path'] = image_path
                markers.append(marker)
            except Exception:
                continue

        return markers

    def _prepare_coverage_polygons(self, images):
        """Prepare polygon data for coverage areas.

        Args:
            images: List of image data dictionaries

        Returns:
            list: List of polygon dictionaries with 'coordinates', 'title', 'description', 'area_sqm'
        """
        polygons = []

        # Get custom altitude if viewer has one set
        custom_alt = None
        if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
            custom_alt = self.parent.custom_agl_altitude_ft

        try:
            # Filter out hidden images - only include images that would be exported
            # This matches the behavior of _prepare_markers and _prepare_location_markers
            filtered_images = [img for img in images if not img.get('hidden', False)]

            if not filtered_images:
                return polygons

            # Create coverage extent service (honor the terrain-elevation preference)
            use_terrain = getattr(self.parent, 'use_terrain_elevation', True)
            coverage_service = CoverageExtentService(custom_altitude_ft=custom_alt, logger=self.logger, use_terrain=use_terrain)

            # Calculate coverage extents using only non-hidden images
            coverage_data = coverage_service.calculate_coverage_extents(filtered_images)

            if not coverage_data or coverage_data.get('cancelled', False):
                return polygons

            coverage_polygons = coverage_data.get('polygons', [])
            if not coverage_polygons:
                return polygons

            # Convert to CalTopo polygon format
            for idx, polygon_data in enumerate(coverage_polygons):
                coords = polygon_data.get('coordinates', [])
                area_sqm = polygon_data.get('area_sqm', 0)
                area_sqkm = area_sqm / 1_000_000
                area_acres = area_sqm / 4046.86

                # Create polygon name
                if len(coverage_polygons) == 1:
                    poly_name = "Coverage Extent"
                else:
                    poly_name = f"Coverage Area {idx + 1}"

                # Build description
                description = self.tr(
                    "Coverage area: {sqkm:.3f} km² ({acres:.2f} acres)\n"
                    "Area in square meters: {sqm:.0f} m²\n"
                    "Number of corners: {count}"
                ).format(
                    sqkm=area_sqkm,
                    acres=area_acres,
                    sqm=area_sqm,
                    count=len(coords)
                )

                polygons.append({
                    'coordinates': coords,  # List of (lat, lon) tuples
                    'title': poly_name,
                    'description': description,
                    'area_sqm': area_sqm
                })

        except Exception as e:
            self.logger.error(f"Error preparing coverage polygons: {e}")

        return polygons

    def _build_composite_context(self, image, image_path, img_array, bearing):
        """Prepare the per-image inputs needed to build multi-zoom composites.

        Args:
            image (dict): Image data dictionary
            image_path (str): Path used to load img_array
            img_array: Image array already loaded for this image (RGB)
            bearing: Drone bearing in degrees

        Returns:
            dict: Context with 'img_array_bgr', 'bearing', 'identifier_color',
                  and 'cache_key' keys, or None if it could not be prepared
        """
        try:
            # Match the PDF report: use the original image pixels when available
            source_path = image.get('original_path', image_path) if 'original_path' in image else image_path
            if source_path == image_path:
                source_array = img_array
            else:
                source_array = ImageService(source_path, image.get('mask_path', '')).img_array

            # Same identifier color the PDF uses for the AOI circle
            identifier_color = (255, 255, 0)
            if hasattr(self.parent, 'settings') and isinstance(self.parent.settings, dict):
                identifier_color = self.parent.settings.get('identifier_color', identifier_color)

            return {
                'img_array_bgr': cv2.cvtColor(source_array, cv2.COLOR_RGB2BGR),
                'bearing': bearing,
                'identifier_color': identifier_color,
                'cache_key': source_path,
            }
        except Exception as e:
            self.logger.error(f"Error preparing composite source for {image_path}: {e}")
            return None

    def _build_composite_photo(self, image_path, image_name, aoi, aoi_idx, composite_context):
        """Generate the multi-zoom composite photo (same layout as the PDF report) for an AOI.

        Args:
            image_path (str): Path to the source image
            image_name (str): Display name of the source image
            aoi (dict): AOI dictionary
            aoi_idx (int): Index of the AOI within the image
            composite_context (dict): Context from _build_composite_context, or None

        Returns:
            str: Path to the generated composite image, or None if it could not be created
        """
        if composite_context is None:
            self.logger.warning(
                f"No composite source available for {image_name} - AOI {aoi_idx + 1}; "
                "the plain image will be used instead"
            )
            return None

        try:
            if self.aoi_composite_service is None:
                self.aoi_composite_service = AOICompositeService(logger=self.logger)
            if self.aoi_thumbnail_service is None:
                self.aoi_thumbnail_service = AOIThumbnailService(logger=self.logger)

            composite = self.aoi_composite_service.create_composite(
                composite_context['img_array_bgr'],
                aoi,
                composite_context['bearing'],
                composite_context['identifier_color'],
                cache_key=composite_context['cache_key']
            )
            if composite is None:
                return None

            return self.aoi_thumbnail_service.save_composite(
                composite,
                output_name=f"{Path(image_path).stem}_AOI{aoi_idx + 1}_overview"
            )
        except Exception as e:
            self.logger.error(f"Error generating composite for {image_name} - AOI {aoi_idx + 1}: {e}")
            return None

    def _build_aoi_photos(self, image_path, image_name, aoi, aoi_idx, aoi_photo_mode, composite_context=None):
        """Build the list of photos to upload for a flagged AOI marker.

        Args:
            image_path (str): Path to the source image
            image_name (str): Display name of the source image
            aoi (dict): AOI dictionary
            aoi_idx (int): Index of the AOI within the image
            aoi_photo_mode (str): 'full' (multi-zoom composite, as in the PDF report),
                'thumbnail' (zoomed AOI crop), or 'both'
            composite_context (dict, optional): Per-image context from
                _build_composite_context; required to build composites

        Returns:
            list: List of dictionaries with 'path' and 'title' keys
        """
        photos = []

        if not image_path:
            return photos

        if aoi_photo_mode in ('thumbnail', 'both'):
            try:
                if self.aoi_thumbnail_service is None:
                    self.aoi_thumbnail_service = AOIThumbnailService(logger=self.logger)

                thumbnail_path = self.aoi_thumbnail_service.generate_thumbnail(
                    image_path,
                    aoi,
                    output_name=f"{Path(image_path).stem}_AOI{aoi_idx + 1}_closeup"
                )
                if thumbnail_path:
                    photos.append({
                        'path': thumbnail_path,
                        'title': f"{image_name} - AOI {aoi_idx + 1} (close-up)"
                    })
                else:
                    self.logger.warning(f"Could not generate AOI thumbnail for {image_name} - AOI {aoi_idx + 1}")
            except Exception as e:
                self.logger.error(f"Error generating AOI thumbnail for {image_name} - AOI {aoi_idx + 1}: {e}")

        if aoi_photo_mode in ('full', 'both'):
            composite_path = self._build_composite_photo(image_path, image_name, aoi, aoi_idx, composite_context)
            if composite_path:
                photos.append({
                    'path': composite_path,
                    'title': f"{image_name} - AOI {aoi_idx + 1} (overview)"
                })
            else:
                # Fall back to the plain full image so the marker still gets a photo
                photos.append({'path': image_path, 'title': image_name})

        # Last-resort fallback: never leave the marker photo-less when photos were requested
        if not photos:
            photos.append({'path': image_path, 'title': image_name})

        return photos

    def _get_marker_photos(self, marker):
        """Return the photos that should be uploaded for a marker.

        Supports markers that carry a 'photos' list as well as legacy markers that
        only carry a single 'image_path'.

        Args:
            marker (dict): Marker dictionary

        Returns:
            list: List of dictionaries with 'path' and 'title' keys
        """
        photos = []
        missing = []
        for photo in marker.get('photos') or []:
            path = photo.get('path')
            if path and os.path.exists(path):
                photos.append({'path': path, 'title': photo.get('title') or os.path.basename(path)})
            elif path:
                missing.append(path)

        # A prepared photo that vanished before upload is a bug we need to hear about
        for path in missing:
            self.logger.warning(f"Prepared CalTopo photo is missing on disk, skipping: {path}")

        if not photos:
            image_path = marker.get('image_path')
            if image_path and os.path.exists(image_path):
                if missing:
                    self.logger.warning(
                        f"Marker '{marker.get('title', '')}': all prepared photos missing; "
                        "falling back to the original image"
                    )
                photos.append({'path': image_path, 'title': marker.get('title') or os.path.basename(image_path)})

        return photos

    def _cleanup_aoi_thumbnails(self):
        """Remove any temporary AOI photos generated for this export and free caches."""
        if self.aoi_thumbnail_service is not None:
            self.aoi_thumbnail_service.cleanup()
            self.aoi_thumbnail_service = None
        if self.aoi_composite_service is not None:
            self.aoi_composite_service.clear_cache()
            self.aoi_composite_service = None

    def logout_from_caltopo(self):
        """Log out from CalTopo by clearing session."""
        self.caltopo_service.clear_session()
        QMessageBox.information(
            self.parent,
            self.tr("Logged Out"),
            self.tr("Successfully logged out from CalTopo.")
        )

    def export_to_caltopo_via_api(self, images, flagged_aois, include_flagged_aois=True,
                                  include_locations=False, include_images_without_flagged_aois=True, include_coverage_area=False, include_images=True,
                                  aoi_photo_mode='full'):
        """
        Export data to CalTopo using the official Team API.

        This method uses the CalTopo Team API with service account credentials
        instead of browser-based authentication.

        Args:
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_flagged_aois (bool): Include flagged AOIs as markers
            include_locations (bool): Include drone/image locations as markers
            include_images_without_flagged_aois (bool): Include images without flagged AOIs in location export
            include_coverage_area (bool): Include coverage area as polygons
            include_images (bool): Upload photos to CalTopo markers
            aoi_photo_mode (str): Photo(s) to attach to flagged AOI markers:
                'full' (multi-zoom composite, as in the PDF report),
                'thumbnail' (zoomed AOI crop), or 'both'

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            if self._is_offline_only():
                QMessageBox.information(
                    self.parent,
                    self.tr("Offline Mode Enabled"),
                    self.tr(
                        "Offline Only is turned on in Preferences:\n\n"
                        "• Map tiles will not be retrieved.\n"
                        "• CalTopo integration is disabled.\n\n"
                        "Turn off Offline Only to export to CalTopo."
                    )
                )
                return False

            if not include_flagged_aois and not include_locations and not include_coverage_area:
                QMessageBox.information(
                    self.parent,
                    self.tr("Nothing Selected"),
                    self.tr(
                        "Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export."
                    )
                )
                return False

            # Steps 1-2: obtain credentials that actually work, then load the
            # account. These are one loop on purpose: a stored secret that
            # CalTopo rejects must send the user back to the credential dialog.
            # Gating the prompt on has_credentials() alone locked users out,
            # because the only other way to reach that dialog ("Update
            # Credentials") lives behind a *successful* authentication.
            account_data = None
            credentials = None
            while True:
                if credentials is None:
                    if self.credential_helper.has_credentials():
                        credentials = self.credential_helper.get_credentials()
                    else:
                        credentials = self._prompt_for_credentials()
                        if not credentials:
                            return False

                team_id, credential_id, credential_secret = credentials
                account_success, account_data, account_error = self._fetch_account_data(
                    team_id, credential_id, credential_secret
                )
                if account_success and account_data:
                    break

                credentials = self._offer_credential_retry(account_error, credentials)
                if not credentials:
                    return False

            # Show map selection dialog (pass credential helper and API service for update functionality)
            map_dialog = CalTopoAPIMapDialog(
                self.parent,
                account_data=account_data,
                credential_helper=self.credential_helper,
                api_service=self.caltopo_api_service
            )
            if map_dialog.exec() != CalTopoAPIMapDialog.Accepted:
                return False

            selected_map = map_dialog.selected_map
            if not selected_map or selected_map.get('type') != 'map':
                return False

            map_id = selected_map.get('id')
            map_team_id = selected_map.get('team_id', team_id)

            # Step 3: Export markers and polygons via API in a separate thread
            # (Data preparation happens inside the thread, just like KML export)
            return self._run_export(
                CalTopoApiPublisher(
                    self.caltopo_api_service, map_id, map_team_id, credential_id, credential_secret
                ),
                images, flagged_aois, include_flagged_aois, include_locations,
                include_images_without_flagged_aois, include_coverage_area, include_images,
                aoi_photo_mode=aoi_photo_mode
            )

        except Exception as e:
            self.logger.error(f"CalTopo API export error: {e}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Error"),
                self.tr(
                    "An error occurred during CalTopo API export:\n\n{error}"
                ).format(error=str(e))
            )
            return False
        finally:
            # Generated AOI photos live in a temp dir; drop them once the export ends
            self._cleanup_aoi_thumbnails()

    def _prompt_for_credentials(self, existing_credentials=None):
        """Show the credential dialog and persist whatever the user enters.

        Args:
            existing_credentials: Optional (team_id, credential_id, secret) to
                pre-fill, used when correcting a rejected set.

        Returns:
            tuple: (team_id, credential_id, credential_secret), or None if the
            user cancelled.
        """
        credential_dialog = CalTopoCredentialDialog(
            self.parent, existing_credentials=existing_credentials
        )
        if credential_dialog.exec() != CalTopoCredentialDialog.Accepted:
            return None

        credentials = credential_dialog.get_credentials()
        if not credentials:
            return None

        team_id, credential_id, credential_secret = credentials
        self.credential_helper.save_credentials(team_id, credential_id, credential_secret)
        return credentials

    def _fetch_account_data(self, team_id, credential_id, credential_secret):
        """Load CalTopo account data on a worker thread behind a progress dialog.

        Args:
            team_id (str): Team ID.
            credential_id (str): Credential ID.
            credential_secret (str): Credential Secret.

        Returns:
            tuple: (success: bool, account_data: dict or None, error: str or None)
        """
        loading_dialog = ExportProgressDialog(
            self.parent,
            title=self.tr("Loading CalTopo Maps"),
            total_items=100
        )
        loading_dialog.set_title(self.tr("Connecting to CalTopo..."))
        loading_dialog.set_status(self.tr("Fetching account data and maps..."))

        account_data = None
        account_success = False
        account_error = None

        def on_account_progress(current, total, message):
            loading_dialog.update_progress(current, total, message)

        def on_account_finished(success, data):
            nonlocal account_data, account_success
            account_data = data
            account_success = success
            loading_dialog.accept()

        def on_account_error(error_message):
            nonlocal account_error
            account_error = error_message
            loading_dialog.reject()

        # Held on self so the QThread cannot be garbage collected mid-run.
        self._account_thread = CalTopoAccountDataThread(
            self.caltopo_api_service, team_id, credential_id, credential_secret
        )
        self._account_thread.progressUpdated.connect(on_account_progress)
        self._account_thread.finished.connect(on_account_finished)
        self._account_thread.errorOccurred.connect(on_account_error)
        # Cancel used to be a dead button: nothing was connected to it and the
        # dialog does not close itself.
        loading_dialog.cancel_requested.connect(loading_dialog.reject)

        self._account_thread.start()
        # No show()/processEvents() before exec(): pumping events here can
        # deliver the worker's completion signal while the dialog is not yet in
        # a modal loop. ExportProgressDialog.exec() also guards against that,
        # but not creating the race is better than surviving it.
        loading_dialog.exec()
        self._account_thread.wait()

        return account_success, account_data, account_error

    def _offer_credential_retry(self, account_error, existing_credentials):
        """Report why CalTopo refused the request and offer to fix credentials.

        Args:
            account_error (str or None): Error text from the worker, if the
                attempt raised rather than simply failing.
            existing_credentials: The (team_id, credential_id, secret) that was
                just rejected, pre-filled into the retry dialog.

        Returns:
            tuple: The replacement (team_id, credential_id, credential_secret)
            to retry with, or None if the user gave up.
        """
        if account_error:
            title = self.tr("Connection Error")
            message = self.tr(
                "An error occurred while connecting to CalTopo API:\n\n{error}"
            ).format(error=account_error)
        else:
            title = self.tr("Authentication Failed")
            message = self.tr(
                "CalTopo did not accept these credentials.\n\n"
                "The reason was written to the log (adiat_logs.txt) and the console.\n\n"
                "Would you like to re-enter your Team ID, Credential ID and "
                "Credential Secret?"
            )

        choice = QMessageBox.question(
            self.parent,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if choice != QMessageBox.Yes:
            return None

        return self._prompt_for_credentials(existing_credentials=existing_credentials)

    def _run_export(self, publisher, images, flagged_aois, include_flagged_aois, include_locations,
                    include_images_without_flagged_aois, include_coverage_area, include_images,
                    aoi_photo_mode='full', markers=None, polygons=None):
        """Publish to CalTopo on a worker thread behind a progress dialog.

        Shared by both authentication modes: only the publisher differs.

        Args:
            publisher: CalTopoApiPublisher or CalTopoBrowserPublisher.
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_flagged_aois: Whether to include flagged AOIs
            include_locations: Whether to include locations
            include_images_without_flagged_aois: Whether to include images without flagged AOIs
            include_coverage_area: Whether to include coverage area
            include_images: Whether to include images
            aoi_photo_mode: Photo(s) to attach to flagged AOI markers ('full', 'thumbnail', or 'both')
            markers: Pre-prepared markers, when the caller already built them.
            polygons: Pre-prepared polygons, when the caller already built them.

        Returns:
            bool: True if anything was created, False otherwise
        """
        progress_dialog = ExportProgressDialog(
            self.parent,
            title=self.tr("Exporting to CalTopo"),
            total_items=100
        )
        progress_dialog.set_title(self.tr("Exporting to CalTopo..."))
        progress_dialog.set_status(self.tr("Preparing data and exporting..."))

        export_thread = CalTopoExportThread(
            publisher,
            self,  # Pass controller for accessing preparation methods
            images,
            flagged_aois,
            include_flagged_aois,
            include_locations,
            include_images_without_flagged_aois,
            include_coverage_area,
            include_images,
            aoi_photo_mode=aoi_photo_mode,
            markers=markers,
            polygons=polygons
        )

        # Store result for return value
        self._export_result = False

        def on_progress_updated(current, total, message):
            progress_dialog.update_progress(current, total, message)

        def on_finished(summary):
            progress_dialog.accept()
            self._export_result = summary.get('success', False)
            self._report_export_summary(summary)

        def on_error(error_message):
            progress_dialog.reject()
            self._export_result = False
            self.logger.error(f"CalTopo export error: {error_message}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Error"),
                self.tr(
                    "An error occurred during CalTopo export:\n\n{error}"
                ).format(error=error_message)
            )

        def on_cancelled():
            progress_dialog.reject()
            self._export_result = False

        export_thread.progressUpdated.connect(on_progress_updated)
        export_thread.finished.connect(on_finished)
        export_thread.errorOccurred.connect(on_error)
        export_thread.canceled.connect(on_cancelled)
        progress_dialog.cancel_requested.connect(export_thread.cancel)

        export_thread.start()
        progress_dialog.exec()

        if export_thread.isRunning():
            export_thread.wait()

        return self._export_result

    def _report_export_summary(self, summary):
        """Tell the user exactly what reached CalTopo, photos included.

        Args:
            summary (dict): Payload emitted by CalTopoExportThread.
        """
        created = summary.get('objects_created', 0)
        total = summary.get('objects_total', 0)
        photos_uploaded = summary.get('photos_uploaded', 0)
        photos_total = summary.get('photos_total', 0)

        if not summary.get('success'):
            QMessageBox.critical(
                self.parent,
                self.tr("Export Failed"),
                self.tr(
                    "Nothing could be exported to CalTopo.\n\n"
                    "The reason was written to the log (adiat_logs.txt) and the console."
                )
            )
            return

        photo_note = ""
        if photos_total:
            photo_note = "\n" + self.tr(
                "Photos uploaded: {uploaded} of {total}."
            ).format(uploaded=photos_uploaded, total=photos_total)

        if created == total and photos_uploaded == photos_total:
            QMessageBox.information(
                self.parent,
                self.tr("Export Successful"),
                self.tr(
                    "Successfully exported all {total} item(s) to CalTopo.\n\n"
                    "The items should now be visible on your map."
                ).format(total=total) + photo_note
            )
        else:
            QMessageBox.warning(
                self.parent,
                self.tr("Partial Success"),
                self.tr(
                    "Exported {created} of {total} item(s) to CalTopo.{photos}\n\n"
                    "Details for anything that failed were written to the log "
                    "(adiat_logs.txt) and the console."
                ).format(created=created, total=total, photos=photo_note)
            )
