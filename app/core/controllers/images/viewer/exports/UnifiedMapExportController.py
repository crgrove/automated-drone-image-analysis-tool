"""
UnifiedMapExportController - Handles unified map export functionality.

This controller coordinates all map export operations, combining image locations,
flagged AOIs, and coverage extent into a single export to either KML file or CalTopo.
"""

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog, QApplication
from core.views.images.viewer.dialogs.MapExportDialog import MapExportDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.services.export.KMLGeneratorService import KMLGeneratorService
from core.services.image.CoverageExtentService import CoverageExtentService
from core.services.LoggerService import LoggerService
from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController
from PySide6.QtCore import QThread, Signal
from core.services.image.ImageService import ImageService
from core.services.image.AOIService import AOIService
from core.views.images.viewer.dialogs.CalTopoMethodDialog import CalTopoMethodDialog
from helpers.LocationInfo import LocationInfo
from helpers.TranslationMixin import TranslationMixin
import simplekml
import traceback


class UnifiedMapExportThread(QThread):
    """Thread for generating unified map exports."""

    finished = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)
    canceled = Signal()

    def __init__(self, kml_service, coverage_service, images, flagged_aois,
                 include_locations, include_images_without_flagged_aois, include_flagged_aois, include_coverage,
                 output_path, custom_altitude_ft=None, use_terrain=True):
        """
        Initialize the export thread.

        Args:
            kml_service: KMLGeneratorService instance
            coverage_service: CoverageExtentService instance
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to flagged AOI indices
            include_locations: Whether to include image locations
            include_images_without_flagged_aois: Whether to include images without flagged AOIs in location export
            include_flagged_aois: Whether to include flagged AOIs
            include_coverage: Whether to include coverage extent
            output_path: Path to save the KML file
            custom_altitude_ft: Optional custom altitude in feet
            use_terrain: Whether to use terrain elevation data
        """
        super().__init__()
        self.kml_service = kml_service
        self.coverage_service = coverage_service
        self.images = images
        self.flagged_aois = flagged_aois
        self.include_locations = include_locations
        self.include_images_without_flagged_aois = include_images_without_flagged_aois
        self.include_flagged_aois = include_flagged_aois
        self.include_coverage = include_coverage
        self.output_path = output_path
        self.custom_altitude_ft = custom_altitude_ft
        self.use_terrain = use_terrain
        self._cancelled = False

    def cancel(self):
        """Cancel the export operation."""
        self._cancelled = True

    def is_cancelled(self):
        """Check if operation is cancelled."""
        return self._cancelled

    def run(self):
        """Execute the export operation."""
        try:
            # Determine which images should be included for locations
            images_for_locations = []
            if self.include_locations:
                for img_idx, img in enumerate(self.images):
                    if img.get('hidden', False):
                        continue
                    # Check if image has flagged AOIs
                    has_flagged_aois = img_idx in self.flagged_aois and len(self.flagged_aois[img_idx]) > 0
                    # Include if: has flagged AOIs OR include_images_without_flagged_aois is True
                    if has_flagged_aois or self.include_images_without_flagged_aois:
                        images_for_locations.append(img)

            # Determine which images should be included for coverage
            # Coverage should only include images that are actually being exported
            images_for_coverage = []
            if self.include_coverage:
                # Collect all image indices that are being exported
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

            total_steps = 0
            if self.include_locations:
                total_steps += len(images_for_locations)
            if self.include_flagged_aois:
                total_steps += sum(len(aois) for aois in self.flagged_aois.values())
            if self.include_coverage:
                total_steps += len(images_for_coverage)

            current_step = 0

            # Export image locations
            if self.include_locations:
                self.progressUpdated.emit(current_step, total_steps, "Exporting image locations...")

                def location_progress(current, total, message):
                    if self.is_cancelled():
                        return
                    self.progressUpdated.emit(current_step + current, total_steps, message)

                self.kml_service.generate_image_locations_kml(
                    images_for_locations,
                    progress_callback=location_progress,
                    cancel_check=self.is_cancelled
                )

                if self.is_cancelled():
                    self.canceled.emit()
                    return

                current_step += len(images_for_locations)

            # Export flagged AOIs
            if self.include_flagged_aois:
                self.progressUpdated.emit(current_step, total_steps, "Exporting flagged AOIs...")

                # Manually add flagged AOIs to KML (without saving yet)

                total_aois = sum(len(aois) for aois in self.flagged_aois.values())
                current_aoi = 0

                for img_idx, aoi_indices in self.flagged_aois.items():
                    if self.is_cancelled():
                        self.canceled.emit()
                        return

                    if img_idx >= len(self.images):
                        continue

                    image = self.images[img_idx]

                    # Skip hidden images
                    if image.get('hidden', False):
                        continue

                    image_name = image.get('name', f'Image {img_idx + 1}')
                    image_path = image.get('path', '')

                    try:
                        # Create ImageService to extract EXIF data
                        calculated_bearing = image.get('bearing', None)
                        image_service = ImageService(image_path, image.get('mask_path', ''), calculated_bearing=calculated_bearing)

                        # Get GPS from EXIF data
                        image_gps = LocationInfo.get_gps(exif_data=image_service.exif_data)

                        if not image_gps:
                            continue

                        # Get AOI data
                        aois = image.get('areas_of_interest', [])

                        for aoi_idx in aoi_indices:
                            if self.is_cancelled():
                                self.canceled.emit()
                                return

                            if aoi_idx >= len(aois):
                                continue

                            aoi = aois[aoi_idx]

                            # Update progress
                            current_aoi += 1
                            self.progressUpdated.emit(
                                current_step + current_aoi,
                                total_steps,
                                f"Processing {image_name} - AOI {aoi_idx + 1}..."
                            )

                            center = aoi.get('center', [0, 0])
                            area = aoi.get('area', 0)

                            # Calculate AOI GPS coordinates with fallback
                            aoi_lat = image_gps['latitude']
                            aoi_lon = image_gps['longitude']
                            gps_note = ""

                            # Try to calculate precise AOI GPS
                            try:
                                aoi_service = AOIService(image)
                                result = aoi_service.calculate_gps_with_custom_altitude(
                                    image, aoi, self.custom_altitude_ft, self.use_terrain
                                )

                                if result:
                                    aoi_lat, aoi_lon = result
                                    gps_note = "Estimated AOI GPS\n"
                                else:
                                    gps_note = "Image GPS (calculation failed)\n"
                            except Exception:
                                gps_note = "Image GPS (calculation error)\n"

                            # Get color information
                            color_info = ""
                            marker_rgb = None
                            try:
                                aoi_service = AOIService(image)
                                color_result = aoi_service.get_cached_or_representative_color(aoi)
                                if color_result:
                                    marker_rgb = color_result['rgb']
                                    color_info = f"Color: Hue: {color_result['hue_degrees']}° {color_result['hex']}\n"
                            except Exception:
                                pass

                            # Create placemark name
                            placemark_name = f"{image_name} - AOI {aoi_idx + 1}"

                            # Get user comment
                            user_comment = aoi.get('user_comment', '')

                            # Build description
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

                            # Add placemark to KML
                            self.kml_service.add_aoi_placemark(
                                placemark_name,
                                aoi_lat,
                                aoi_lon,
                                description,
                                marker_rgb
                            )

                    except Exception:
                        continue

                current_step += total_aois

            # Export coverage extent
            if self.include_coverage:
                self.progressUpdated.emit(current_step, total_steps, "Calculating coverage extent...")

                def coverage_progress(current, total, message):
                    if self.is_cancelled():
                        return
                    self.progressUpdated.emit(current_step + current, total_steps, message)

                coverage_data = self.coverage_service.calculate_coverage_extents(
                    images_for_coverage,
                    progress_callback=coverage_progress,
                    cancel_check=self.is_cancelled
                )

                if self.is_cancelled():
                    self.canceled.emit()
                    return

                # Add coverage polygons to the KML
                if coverage_data and coverage_data.get('polygons'):
                    polygons = coverage_data.get('polygons', [])

                    for idx, polygon_data in enumerate(polygons):
                        coords = polygon_data['coordinates']
                        area_sqm = polygon_data['area_sqm']
                        area_sqkm = area_sqm / 1_000_000
                        area_acres = area_sqm / 4046.86

                        if len(polygons) == 1:
                            poly_name = "Coverage Extent"
                        else:
                            poly_name = f"Coverage Area {idx + 1}"

                        # Convert coordinates to KML format (lon, lat)
                        kml_coords = [(lon, lat) for lat, lon in coords]

                        # Create polygon
                        pol = self.kml_service.kml.newpolygon(name=poly_name)
                        pol.outerboundaryis = kml_coords

                        pol.description = (
                            f"Coverage area: {area_sqkm:.3f} km² ({area_acres:.2f} acres)\n"
                            f"Area in square meters: {area_sqm:.0f} m²\n"
                            f"Number of corners: {len(coords)}"
                        )

                        # Style the polygon
                        pol.style.linestyle.color = simplekml.Color.rgb(0, 100, 200)
                        pol.style.linestyle.width = 2
                        pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.rgb(0, 150, 255))
                        pol.style.polystyle.outline = 1

            # Save the combined KML file
            self.kml_service.save_kml(self.output_path)

            self.finished.emit()

        except Exception as e:
            error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.errorOccurred.emit(error_msg)


class CoveragePodExportThread(QThread):
    """Thread for the Probability-of-Detection pass (compute + write outputs).

    Runs independently of the KML/CalTopo export so the existing export path is
    untouched. Emits ``podCompleted`` with the CoverageResult on success.
    """

    finished = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)
    canceled = Signal()
    podCompleted = Signal(object)

    def __init__(self, pod_service, images, output_dir):
        super().__init__()
        self.pod_service = pod_service
        self.images = images
        self.output_dir = output_dir
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self):
        return self._cancelled

    def run(self):
        try:
            from core.services.coverage.writers import write_all_outputs
            result = self.pod_service.calculate(
                self.images,
                progress_callback=lambda c, t, m: self.progressUpdated.emit(c, t, m),
                cancel_check=self.is_cancelled,
            )
            if result.cancelled or self.is_cancelled():
                self.canceled.emit()
                return
            self.progressUpdated.emit(1, 1, "Writing POD outputs...")
            write_all_outputs(result, self.output_dir)
            self.podCompleted.emit(result)
            self.finished.emit()
        except Exception as e:
            self.errorOccurred.emit(f"{str(e)}\n\n{traceback.format_exc()}")


class UnifiedMapExportController(TranslationMixin):
    """
    Controller for managing unified map export functionality.

    Handles showing the export dialog and coordinating exports based on user selections.
    """

    def __init__(self, parent_viewer, logger=None):
        """
        Initialize the unified map export controller.

        Args:
            parent_viewer: The main Viewer instance
            logger: Optional LoggerService instance
        """
        self.parent = parent_viewer
        self.logger = logger or LoggerService()
        self.export_thread = None
        self.progress_dialog = None
        self.pod_thread = None
        self.pod_progress_dialog = None
        self._pending_pod_result = None
        # KML/KMZ path a completed POD pass should embed its overlay into
        # (None outside a KML export with POD selected), plus the service
        # holding that document and the folder the POD products landed in.
        self._kml_pod_target = None
        self._last_kml_service = None
        self._pod_last_output_dir = None

    def show_export_dialog(self):
        """Show the unified map export dialog and handle export based on selections."""
        try:
            # Show export options dialog
            dialog = MapExportDialog(self.parent)

            if dialog.exec() != QDialog.Accepted:
                return  # User cancelled

            # Get user selections
            export_type = dialog.get_export_type()
            include_locations = dialog.should_include_locations()
            include_images_without_flagged_aois = dialog.should_include_images_without_flagged_aois()
            include_flagged_aois = dialog.should_include_flagged_aois()
            include_coverage = dialog.should_include_coverage()
            include_images = dialog.should_include_images() if export_type == 'caltopo' else False
            include_pod = dialog.should_include_pod()
            show_pod_on_map = dialog.should_show_pod_on_map()

            # Validate selections (POD is a valid stand-alone selection).
            if not (include_locations or include_flagged_aois or include_coverage or include_pod):
                QMessageBox.warning(
                    self.parent,
                    self.tr("No Data Selected"),
                    self.tr("Please select at least one type of data to export.")
                )
                return

            # Handle export based on type
            if export_type == 'kml':
                self._kml_pod_target = None
                kml_path = self._export_to_kml(include_locations, include_images_without_flagged_aois,
                                               include_flagged_aois, include_coverage)
                if include_pod and kml_path:
                    # Embed the heatmap into the just-saved document when the
                    # POD pass completes (see _embed_pod_overlay_in_kml).
                    self._kml_pod_target = kml_path
                    self._run_pod_export(self._pod_dir_for_kml(kml_path), show_pod_on_map)
            else:  # caltopo
                # Show method selection dialog
                method_dialog = CalTopoMethodDialog(self.parent)

                if method_dialog.exec() != QDialog.Accepted:
                    return  # User cancelled method selection

                method = method_dialog.get_selected_method()
                if method == 'api':
                    self._export_to_caltopo_via_api(include_locations, include_images_without_flagged_aois,
                                                    include_flagged_aois, include_coverage, include_images)
                else:  # browser
                    self._export_to_caltopo(include_locations, include_images_without_flagged_aois, include_flagged_aois, include_coverage, include_images)
                if include_pod:
                    pod_dir = QFileDialog.getExistingDirectory(
                        self.parent, self.tr("Select folder for POD coverage files"))
                    if pod_dir:
                        self._run_pod_export(pod_dir, show_pod_on_map)

        except Exception as e:
            self.logger.error(f"Error in unified map export: {str(e)}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Error"),
                self.tr("An error occurred during export:\n{error}").format(error=str(e))
            )

    def _export_to_kml(self, include_locations, include_images_without_flagged_aois, include_flagged_aois, include_coverage):
        """
        Export to KML file.

        Args:
            include_locations: Whether to include image locations
            include_images_without_flagged_aois: Whether to include images without flagged AOIs in location export
            include_flagged_aois: Whether to include flagged AOIs
            include_coverage: Whether to include coverage extent
        """
        try:
            # Show file save dialog (KMZ packs the POD overlay image into a
            # single self-contained file; plain KML references it as a sidecar).
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                self.tr("Save Map Export"),
                "",
                self.tr("KML files (*.kml);;KMZ files (*.kmz)")
            )

            if not file_name:  # User cancelled
                return None

            # Get custom altitude if available
            custom_alt = None
            if hasattr(self.parent, 'altitude_controller'):
                custom_alt = self.parent.altitude_controller.get_effective_altitude()

            # Get terrain preference
            use_terrain = getattr(self.parent, 'use_terrain_elevation', True)

            # Create services
            kml_service = KMLGeneratorService(custom_altitude_ft=custom_alt, use_terrain=use_terrain)
            coverage_service = CoverageExtentService(custom_altitude_ft=custom_alt, logger=self.logger, use_terrain=use_terrain)
            # Keep the document so a following POD pass can embed its overlay
            # and re-save (see _embed_pod_overlay_in_kml).
            self._last_kml_service = kml_service

            # Calculate total items for progress (will be recalculated in thread, but estimate here)
            total_items = 0
            if include_locations:
                # Count images that will be included
                for img_idx, img in enumerate(self.parent.images):
                    if img.get('hidden', False):
                        continue
                    has_flagged_aois = img_idx in self.parent.aoi_controller.flagged_aois and len(self.parent.aoi_controller.flagged_aois[img_idx]) > 0
                    if has_flagged_aois or include_images_without_flagged_aois:
                        total_items += 1
            if include_flagged_aois:
                total_items += sum(len(aois) for aois in self.parent.aoi_controller.flagged_aois.values())
            if include_coverage:
                # Coverage will use filtered images, estimate with all for now
                total_items += len(self.parent.images)

            # Create progress dialog
            self.progress_dialog = ExportProgressDialog(
                self.parent,
                title="Generating Map Export",
                total_items=total_items
            )
            self.progress_dialog.set_title("Exporting map data...")

            # Create export thread
            self.export_thread = UnifiedMapExportThread(
                kml_service,
                coverage_service,
                self.parent.images,
                self.parent.aoi_controller.flagged_aois,
                include_locations,
                include_images_without_flagged_aois,
                include_flagged_aois,
                include_coverage,
                file_name,
                custom_alt,
                use_terrain
            )

            # Connect signals
            self.export_thread.finished.connect(self._on_export_finished)
            self.export_thread.errorOccurred.connect(self._on_export_error)
            self.export_thread.progressUpdated.connect(self._on_progress_updated)
            self.export_thread.canceled.connect(self._on_export_cancelled)

            # Connect cancel button
            self.progress_dialog.cancel_requested.connect(self.export_thread.cancel)

            # Start the thread
            self.export_thread.start()

            # Show progress dialog
            self.progress_dialog.show()
            QApplication.processEvents()

            # Block until finished
            if self.progress_dialog.exec() == QDialog.Rejected:
                self.export_thread.cancel()

            return file_name

        except Exception as e:
            self.logger.error(f"Error exporting to KML: {str(e)}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Error"),
                self.tr("Failed to export to KML:\n{error}").format(error=str(e))
            )
            return None

    @staticmethod
    def _pod_dir_for_kml(kml_path):
        """Sibling subfolder next to the KML for the POD product set."""
        import os
        base = os.path.splitext(os.path.basename(kml_path))[0]
        return os.path.join(os.path.dirname(kml_path), f"{base}_coverage_pod")

    def _build_pod_service(self):
        """Construct a CoveragePodService from settings (fresh TerrainService for
        thread safety; canopy factory is optional until it ships)."""
        from core.services.terrain.TerrainService import TerrainService
        from core.services.coverage.params import PodParams
        from core.services.coverage.CoveragePodService import CoveragePodService

        settings = getattr(self.parent, 'settings_service', None)
        terrain = TerrainService(settings_service=settings)
        canopy = None
        try:
            from core.services.terrain.CanopyServiceFactory import create_canopy_service
            canopy = create_canopy_service(settings)
        except Exception:
            canopy = None

        custom_alt = None
        if hasattr(self.parent, 'altitude_controller'):
            custom_alt = self.parent.altitude_controller.get_effective_altitude()
        params = PodParams.from_settings(settings)
        return CoveragePodService(terrain, canopy, params,
                                  custom_altitude_ft=custom_alt, logger=self.logger)

    def run_pod(self, output_dir, show_on_map=True):
        """Public entry point for a standalone POD calculation (no KML/CalTopo
        export required) — used by the GPS Map View's Calculate POD button."""
        self._run_pod_export(output_dir, show_on_map)

    def _pod_image_set(self):
        """The image set POD coverage is computed over: the FULL flight capture
        set (every image the drone took), not just the AOI-flagged subset the
        result XML carries. Coverage/POD answers "how well was this area
        searched", which depends on every frame, whether or not it flagged an
        AOI.

        AOI images keep their richer dicts (bearing, mask, hidden, wingtra AGL)
        so POD reuses any computed geometry hints; source-only captures become
        minimal {path, name} entries (pose/GSD come from their EXIF/XMP). Falls
        back to the AOI subset when the full set is unavailable (e.g. the source
        folder is offline)."""
        source = getattr(self.parent, 'source_images', None)
        images = getattr(self.parent, 'images', None) or []
        if not source:
            return images
        by_path = {img.get('path'): img for img in images if img.get('path')}
        return [by_path.get(e.get('path')) or {'path': e.get('path'), 'name': e.get('name')}
                for e in source]

    def _run_pod_export(self, output_dir, show_on_map):
        """Run the POD pass on the full flight capture set (see _pod_image_set),
        write outputs, cache the result, and optionally show it on the map."""
        try:
            pod_service = self._build_pod_service()
        except Exception as e:
            self.logger.error(f"Failed to build POD service: {e}")
            QMessageBox.critical(
                self.parent, self.tr("POD Error"),
                self.tr("Could not start the POD calculation:\n{error}").format(error=str(e)))
            return

        self._pending_pod_result = None
        self._show_pod_on_map_requested = show_on_map
        self._pod_last_output_dir = output_dir

        pod_images = self._pod_image_set()
        self.pod_progress_dialog = ExportProgressDialog(
            self.parent, title="Coverage / POD", total_items=len(pod_images) + 2)
        self.pod_progress_dialog.set_title("Calculating probability of detection...")

        self.pod_thread = CoveragePodExportThread(pod_service, pod_images, output_dir)
        self.pod_thread.podCompleted.connect(self._on_pod_completed)
        self.pod_thread.finished.connect(self._on_pod_finished)
        self.pod_thread.errorOccurred.connect(self._on_pod_error)
        self.pod_thread.progressUpdated.connect(self._on_pod_progress)
        self.pod_thread.canceled.connect(self._on_pod_cancelled)
        self.pod_progress_dialog.cancel_requested.connect(self.pod_thread.cancel)

        self.pod_thread.start()
        self.pod_progress_dialog.show()
        QApplication.processEvents()
        if self.pod_progress_dialog.exec() == QDialog.Rejected:
            self.pod_thread.cancel()

    def _on_pod_progress(self, current, total, message):
        if self.pod_progress_dialog:
            self.pod_progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()

    def _on_pod_completed(self, result):
        self._pending_pod_result = result
        cache = getattr(self.parent, 'pod_result_cache', None)
        if cache is not None:
            # Record the terrain/canopy config so a later source change can
            # mark this result stale instead of silently re-rendering it.
            from core.services.coverage.CoverageResultCache import config_fingerprint
            fingerprint = config_fingerprint(getattr(self.parent, 'settings_service', None))
            cache.set_result(result, fingerprint)

    def _pod_completion_summary(self, result):
        """(message, color) telling the truth about a finished POD pass.

        A run where frames were skipped (beyond user-hidden ones) must not
        read identically to a clean run: it reports the skip count, singling
        out missing elevation data since that is user-fixable (download tiles).
        Fallback-served frames are surfaced as information, not a warning.
        """
        if result is None:
            return self.tr("POD coverage complete"), "#00C853"
        from core.services.coverage.contracts import (
            SKIP_HIDDEN, SKIP_NO_DEM, SKIP_NO_DEM_AT_NADIR)

        skipped = [s for s in (result.skipped or []) if s[1] != SKIP_HIDDEN]
        fallback = getattr(result, 'dem_fallback_frames', 0)
        if not skipped:
            if fallback:
                msg = self.tr(
                    "POD coverage complete — {count} frame(s) used online "
                    "elevation (outside local DEM)").format(count=fallback)
            else:
                msg = self.tr("POD coverage complete")
            color = "#00C853"
        else:
            attempted = result.image_count + len(skipped)
            no_dem = sum(1 for _, r in skipped if r in (SKIP_NO_DEM, SKIP_NO_DEM_AT_NADIR))
            msg = self.tr("POD complete — {skipped} of {total} frames skipped").format(
                skipped=len(skipped), total=attempted)
            if no_dem:
                msg += " " + self.tr("({count} without elevation data)").format(count=no_dem)
            color = "#FFA726"

        # Canopy that didn't cover the whole searched area silently overstates
        # POD there (no attenuation on bare-treated ground), so surface it.
        frac = getattr(result, 'canopy_coverage_fraction', None)
        if frac is not None and frac < 0.99:
            msg += " " + self.tr(
                "(canopy data covered {pct}% of the searched area)").format(
                    pct=int(round(frac * 100)))
        return msg, color

    def _on_pod_finished(self):
        if self.pod_progress_dialog:
            self.pod_progress_dialog.accept()
        # Embed the heatmap into the exported KML/KMZ before anything else so
        # the file on disk is complete by the time the user is told about it.
        if self._pending_pod_result is not None and self._kml_pod_target:
            self._embed_pod_overlay_in_kml(self._pending_pod_result)
        if hasattr(self.parent, 'status_controller'):
            message, color = self._pod_completion_summary(self._pending_pod_result)
            self.parent.status_controller.show_toast(message, 5000, color=color)
        # Show on the viewer map if requested and the overlay is available.
        if self._pending_pod_result is not None and getattr(self, '_show_pod_on_map_requested', False):
            controller = getattr(self.parent, 'gps_map_controller', None)
            if controller is not None and hasattr(controller, 'enable_pod_overlay'):
                try:
                    controller.show_map()
                    controller.enable_pod_overlay()
                except Exception as e:
                    self.logger.warning(f"Could not show POD overlay: {e}")
        self._pending_pod_result = None

    def _embed_pod_overlay_in_kml(self, result):
        """Embed the POD heatmap into the exported document as a GroundOverlay.

        The plain export was already saved (crash-safe); this re-saves it with
        the overlay added. A ``.kmz`` target packs the PNG into the archive
        (self-contained); a ``.kml`` target references the PNG written into the
        sibling POD products folder. Failure leaves the original export intact
        and is surfaced as a warning, not an error.
        """
        kml_path = self._kml_pod_target
        self._kml_pod_target = None
        kml_service = self._last_kml_service
        if kml_service is None:
            return
        try:
            import os
            from core.services.coverage.writers import write_pod_overlay_png

            os.makedirs(self._pod_last_output_dir, exist_ok=True)
            png_path = os.path.join(self._pod_last_output_dir, "pod_overlay.png")
            box = write_pod_overlay_png(result, png_path)

            packed = str(kml_path).lower().endswith('.kmz')
            href = None
            if not packed:
                href = os.path.relpath(
                    png_path, os.path.dirname(os.path.abspath(kml_path))
                ).replace(os.sep, '/')

            description = self.tr(
                "Terrain and canopy aware probability-of-detection heatmap.")
            mean_pod = (result.stats or {}).get('mean_pod_covered')
            if mean_pod is not None:
                description += "\n" + self.tr(
                    "Mean POD over covered area: {pod}%").format(pod=round(mean_pod * 100))

            kml_service.add_pod_overlay(
                png_path, box, name=self.tr("POD Coverage"),
                description=description, packed=packed, href=href)
            kml_service.save_kml(kml_path)
            self.logger.info(f"POD overlay embedded into {kml_path}")
        except Exception as e:
            # The GeoTIFF products still exist; only the KML embedding failed.
            self.logger.error(f"Failed to embed POD overlay into {kml_path}: {e}")
            QMessageBox.warning(
                self.parent, self.tr("POD Overlay"),
                self.tr("The POD coverage was computed, but embedding it into the "
                        "exported file failed:\n{error}\n\nThe POD GeoTIFF products "
                        "were still written next to the export.").format(error=str(e)))

    def _on_pod_cancelled(self):
        self._kml_pod_target = None
        if self.pod_thread and self.pod_thread.isRunning():
            self.pod_thread.terminate()
            self.pod_thread.wait()
        if self.pod_progress_dialog and self.pod_progress_dialog.isVisible():
            self.pod_progress_dialog.reject()
        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast(
                self.tr("POD calculation cancelled"), 3000, color="#FFA726")

    def _on_pod_error(self, error_message):
        self._kml_pod_target = None
        if self.pod_progress_dialog and self.pod_progress_dialog.isVisible():
            self.pod_progress_dialog.reject()
        self.logger.error(f"POD export error: {error_message}")
        QMessageBox.critical(
            self.parent, self.tr("POD Error"),
            self.tr("POD calculation failed:\n{error}").format(error=error_message))

    def _export_to_caltopo(self, include_locations, include_images_without_flagged_aois, include_flagged_aois, include_coverage, include_images=True):
        """
        Export to CalTopo using browser-based authentication.

        Args:
            include_locations: Whether to include image locations
            include_images_without_flagged_aois: Whether to include images without flagged AOIs in location export
            include_flagged_aois: Whether to include flagged AOIs
            include_coverage: Whether to include coverage extent polygons
            include_images: Whether to upload photos to CalTopo markers
        """
        try:
            # Use the existing CalTopo export controller
            caltopo_controller = CalTopoExportController(self.parent, self.logger)

            # Export markers and polygons based on selections
            caltopo_controller.export_to_caltopo(
                self.parent.images,
                self.parent.aoi_controller.flagged_aois,
                include_flagged_aois=include_flagged_aois,
                include_locations=include_locations,
                include_images_without_flagged_aois=include_images_without_flagged_aois,
                include_coverage_area=include_coverage,
                include_images=include_images
            )

        except Exception as e:
            self.logger.error(f"Error exporting to CalTopo: {str(e)}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Error"),
                self.tr("Failed to export to CalTopo:\n{error}").format(error=str(e))
            )

    def _export_to_caltopo_via_api(self, include_locations, include_images_without_flagged_aois, include_flagged_aois, include_coverage, include_images=True):
        """
        Export to CalTopo using API-based authentication.

        Args:
            include_locations: Whether to include image locations
            include_images_without_flagged_aois: Whether to include images without flagged AOIs in location export
            include_flagged_aois: Whether to include flagged AOIs
            include_coverage: Whether to include coverage extent polygons
            include_images: Whether to upload photos to CalTopo markers
        """
        try:
            # Use the CalTopo export controller with API method
            caltopo_controller = CalTopoExportController(self.parent, self.logger)

            # Export markers and polygons based on selections using API
            caltopo_controller.export_to_caltopo_via_api(
                self.parent.images,
                self.parent.aoi_controller.flagged_aois,
                include_flagged_aois=include_flagged_aois,
                include_locations=include_locations,
                include_images_without_flagged_aois=include_images_without_flagged_aois,
                include_coverage_area=include_coverage,
                include_images=include_images
            )

        except Exception as e:
            self.logger.error(f"Error exporting to CalTopo via API: {str(e)}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Error"),
                self.tr("Failed to export to CalTopo:\n{error}").format(error=str(e))
            )

    def _on_progress_updated(self, current, total, message):
        """Handle progress updates from the export thread."""
        if self.progress_dialog:
            self.progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()

    def _on_export_finished(self):
        """Handle successful completion of export."""
        if self.progress_dialog:
            self.progress_dialog.accept()

        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast(
                self.tr("Map export completed successfully!"),
                3000,
                color="#00C853"
            )

    def _on_export_cancelled(self):
        """Handle cancellation of export."""
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.terminate()
            self.export_thread.wait()
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()

        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast(
                self.tr("Map export cancelled"),
                3000,
                color="#FFA726"
            )

    def _on_export_error(self, error_message):
        """Handle errors during export."""
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()

        self.logger.error(f"Map export error: {error_message}")
        QMessageBox.critical(
            self.parent,
            self.tr("Export Error"),
            self.tr("Map export failed:\n{error}").format(error=error_message)
        )
