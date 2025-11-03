"""
UnifiedMapExportController - Handles unified map export functionality.

This controller coordinates all map export operations, combining image locations,
flagged AOIs, and coverage extent into a single export to either KML file or CalTopo.
"""

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog, QApplication
from core.views.viewer.dialogs.MapExportDialog import MapExportDialog
from core.views.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.services.KMLGeneratorService import KMLGeneratorService
from core.services.CoverageExtentService import CoverageExtentService
from core.services.LoggerService import LoggerService
from core.controllers.viewer.exports.CalTopoExportController import CalTopoExportController
from PySide6.QtCore import QThread, Signal


class UnifiedMapExportThread(QThread):
    """Thread for generating unified map exports."""
    
    finished = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)
    canceled = Signal()
    
    def __init__(self, kml_service, coverage_service, images, flagged_aois, 
                 include_locations, include_flagged_aois, include_coverage, 
                 output_path, custom_altitude_ft=None):
        """
        Initialize the export thread.
        
        Args:
            kml_service: KMLGeneratorService instance
            coverage_service: CoverageExtentService instance
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to flagged AOI indices
            include_locations: Whether to include image locations
            include_flagged_aois: Whether to include flagged AOIs
            include_coverage: Whether to include coverage extent
            output_path: Path to save the KML file
            custom_altitude_ft: Optional custom altitude in feet
        """
        super().__init__()
        self.kml_service = kml_service
        self.coverage_service = coverage_service
        self.images = images
        self.flagged_aois = flagged_aois
        self.include_locations = include_locations
        self.include_flagged_aois = include_flagged_aois
        self.include_coverage = include_coverage
        self.output_path = output_path
        self.custom_altitude_ft = custom_altitude_ft
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
            total_steps = 0
            if self.include_locations:
                total_steps += sum(1 for img in self.images if not img.get('hidden', False))
            if self.include_flagged_aois:
                total_steps += sum(len(aois) for aois in self.flagged_aois.values())
            if self.include_coverage:
                total_steps += len(self.images)
            
            current_step = 0
            
            # Export image locations
            if self.include_locations:
                self.progressUpdated.emit(current_step, total_steps, "Exporting image locations...")
                
                def location_progress(current, total, message):
                    if self.is_cancelled():
                        return
                    self.progressUpdated.emit(current_step + current, total_steps, message)
                
                self.kml_service.generate_image_locations_kml(
                    self.images,
                    progress_callback=location_progress,
                    cancel_check=self.is_cancelled
                )
                
                if self.is_cancelled():
                    self.canceled.emit()
                    return
                    
                current_step += sum(1 for img in self.images if not img.get('hidden', False))
            
            # Export flagged AOIs
            if self.include_flagged_aois:
                self.progressUpdated.emit(current_step, total_steps, "Exporting flagged AOIs...")
                
                # Manually add flagged AOIs to KML (without saving yet)
                from core.services.ImageService import ImageService
                from core.services.AOIService import AOIService
                from helpers.LocationInfo import LocationInfo
                
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
                                    image, aoi, self.custom_altitude_ft
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
                                color_result = aoi_service.get_aoi_representative_color(aoi)
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
                    self.images,
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
                        import simplekml
                        pol.style.linestyle.color = simplekml.Color.rgb(0, 100, 200)
                        pol.style.linestyle.width = 2
                        pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.rgb(0, 150, 255))
                        pol.style.polystyle.outline = 1
            
            # Save the combined KML file
            self.kml_service.save_kml(self.output_path)
            
            self.finished.emit()
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.errorOccurred.emit(error_msg)


class UnifiedMapExportController:
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
            include_flagged_aois = dialog.should_include_flagged_aois()
            include_coverage = dialog.should_include_coverage()
            
            # Validate selections
            if not (include_locations or include_flagged_aois or include_coverage):
                QMessageBox.warning(
                    self.parent,
                    "No Data Selected",
                    "Please select at least one type of data to export."
                )
                return
            
            # Handle export based on type
            if export_type == 'kml':
                self._export_to_kml(include_locations, include_flagged_aois, include_coverage)
            else:  # caltopo
                self._export_to_caltopo(include_locations, include_flagged_aois, include_coverage)
                
        except Exception as e:
            self.logger.error(f"Error in unified map export: {str(e)}")
            QMessageBox.critical(
                self.parent,
                "Export Error",
                f"An error occurred during export:\n{str(e)}"
            )
    
    def _export_to_kml(self, include_locations, include_flagged_aois, include_coverage):
        """
        Export to KML file.
        
        Args:
            include_locations: Whether to include image locations
            include_flagged_aois: Whether to include flagged AOIs
            include_coverage: Whether to include coverage extent
        """
        try:
            # Show file save dialog
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save Map Export",
                "",
                "KML files (*.kml)"
            )
            
            if not file_name:  # User cancelled
                return
            
            # Get custom altitude if available
            custom_alt = None
            if hasattr(self.parent, 'altitude_controller'):
                custom_alt = self.parent.altitude_controller.get_effective_altitude()
            
            # Create services
            kml_service = KMLGeneratorService(custom_altitude_ft=custom_alt)
            coverage_service = CoverageExtentService(custom_altitude_ft=custom_alt, logger=self.logger)
            
            # Calculate total items for progress
            total_items = 0
            if include_locations:
                total_items += sum(1 for img in self.parent.images if not img.get('hidden', False))
            if include_flagged_aois:
                total_items += sum(len(aois) for aois in self.parent.aoi_controller.flagged_aois.values())
            if include_coverage:
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
                include_flagged_aois,
                include_coverage,
                file_name,
                custom_alt
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
                
        except Exception as e:
            self.logger.error(f"Error exporting to KML: {str(e)}")
            QMessageBox.critical(
                self.parent,
                "Export Error",
                f"Failed to export to KML:\n{str(e)}"
            )
    
    def _export_to_caltopo(self, include_locations, include_flagged_aois, include_coverage):
        """
        Export to CalTopo.
        
        Args:
            include_locations: Whether to include image locations
            include_flagged_aois: Whether to include flagged AOIs
            include_coverage: Whether to include coverage extent (not yet supported for CalTopo)
        """
        try:
            # CalTopo export currently only supports markers, not polygons
            # So we can export locations and flagged AOIs, but not coverage extent
            if include_coverage and not (include_locations or include_flagged_aois):
                QMessageBox.warning(
                    self.parent,
                    "CalTopo Export Limitation",
                    "CalTopo export currently only supports point markers (image locations and flagged AOIs).\n\n"
                    "Coverage extent polygons are not yet supported for CalTopo export.\n"
                    "Please also select image locations or flagged AOIs, or export to KML instead."
                )
                return
            
            if include_coverage:
                # Warn user that coverage extent won't be included
                reply = QMessageBox.question(
                    self.parent,
                    "Coverage Extent Not Supported",
                    "CalTopo export does not support coverage extent polygons.\n\n"
                    "Only image locations and flagged AOIs will be exported.\n\n"
                    "Continue with export?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # Use the existing CalTopo export controller
            # We'll need to prepare the markers based on selections
            caltopo_controller = CalTopoExportController(self.parent, self.logger)
            
            # For now, we'll use the existing CalTopo export which handles flagged AOIs
            # We need to enhance it to also support image locations
            # For the initial implementation, let's just call the existing export
            # and show a message about which data will be included
            
            if include_locations and not include_flagged_aois:
                QMessageBox.information(
                    self.parent,
                    "Coming Soon",
                    "Image location export to CalTopo is coming soon.\n\n"
                    "For now, please select 'Flagged Areas of Interest' for CalTopo export."
                )
                return
            
            # Export flagged AOIs using existing functionality
            if include_flagged_aois:
                caltopo_controller.export_to_caltopo(
                    self.parent.images,
                    self.parent.aoi_controller.flagged_aois
                )
            
        except Exception as e:
            self.logger.error(f"Error exporting to CalTopo: {str(e)}")
            QMessageBox.critical(
                self.parent,
                "Export Error",
                f"Failed to export to CalTopo:\n{str(e)}"
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
                "Map export completed successfully!",
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
                "Map export cancelled",
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
            "Export Error",
            f"Map export failed:\n{error_message}"
        )

