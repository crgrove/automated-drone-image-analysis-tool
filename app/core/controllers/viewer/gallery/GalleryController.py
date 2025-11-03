"""
GalleryController - Handles business logic for the AOI gallery view.

This controller manages gallery data, filtering, sorting, and interactions
for displaying AOIs from all loaded images.
"""

import colorsys
import fnmatch
import numpy as np
from PySide6.QtCore import QThread, QTimer
from PySide6.QtWidgets import QProgressDialog, QApplication
from PySide6.QtCore import Qt
from core.services.LoggerService import LoggerService
from core.services.AOIService import AOIService
from .AOIGalleryModel import AOIGalleryModel
from .GalleryUIComponent import GalleryUIComponent


class GalleryController:
    """
    Controller for managing the AOI gallery view business logic.

    Handles global filtering, sorting, and interaction for AOIs from all images.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the gallery controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()

        # Create model and UI component
        self.model = AOIGalleryModel()
        self.model.set_viewer(parent_viewer)

        # Set dataset directory for per-dataset caches
        # Use alternative cache directory if provided, otherwise use xml_path directory
        if hasattr(parent_viewer, 'alternative_cache_dir') and parent_viewer.alternative_cache_dir:
            # User provided an alternative cache location
            import os
            self.model.set_dataset_directory(os.path.join(parent_viewer.alternative_cache_dir, 'ADIAT_Data.xml'))
        elif hasattr(parent_viewer, 'xml_path') and parent_viewer.xml_path:
            self.model.set_dataset_directory(parent_viewer.xml_path)

        self.ui_component = GalleryUIComponent(self)

        # Filter and sort state (shared with AOI controller logic)
        self.sort_method = None
        self.sort_color_hue = None
        self.filter_flagged_only = False
        self.filter_comment_pattern = None
        self.filter_color_hue = None
        self.filter_color_range = None
        self.filter_area_min = None
        self.filter_area_max = None
        self.filter_temperature_min = None
        self.filter_temperature_max = None

        # Cache for AOIService instances per image
        self._aoi_service_cache = {}

        # Progress dialog for color calculation
        self.color_calc_progress_dialog = None

    def create_gallery_widget(self, parent=None):
        """
        Create the gallery widget.

        Args:
            parent: Parent widget

        Returns:
            QWidget: The gallery widget
        """
        widget = self.ui_component.create_gallery_widget(parent)
        self.ui_component.set_model(self.model)
        return widget

    def load_all_aois(self):
        """
        Load and display AOIs from all images in the gallery.

        This flattens all AOIs from all loaded images and applies global
        filtering and sorting. Color calculation is done in background thread
        with progress dialog.
        """
        try:
            self.logger.debug("===== load_all_aois() called =====")

            if not self.parent or not hasattr(self.parent, 'images'):
                self.logger.warning("No images available to load AOIs")
                return

            # Additional safety check
            if not self.parent.images:
                self.logger.debug("Images list is empty, skipping gallery load")
                return

            # Collect all AOIs from all images
            all_aois = self._collect_all_aois()
            self.logger.debug(f"Collected {len(all_aois)} AOIs")

            # Set items without triggering color calculation
            self.model.set_aoi_items(all_aois, skip_color_calc=True)
            self.logger.debug("Set AOI items in model")

            # Start color calculation in background with progress dialog
            self._start_color_calculation_with_progress(all_aois)

        except Exception as e:
            self.logger.error(f"Error loading AOIs in gallery: {e}")

    def _start_color_calculation_with_progress(self, all_aois):
        """
        Start color calculation with progress dialog.

        Uses main thread but processEvents() to keep UI responsive.

        Args:
            all_aois: List of all AOI tuples to process
        """
        try:
            self.logger.debug("===== _start_color_calculation_with_progress() called =====")

            # Disconnect any existing signal connections first
            self._disconnect_color_calc_signals()

            # Close any existing progress dialog
            if self.color_calc_progress_dialog:
                self.logger.debug("Closing existing progress dialog")
                self.color_calc_progress_dialog.close()
                self.color_calc_progress_dialog = None

            # Get parent widget - use the main viewer window
            parent_widget = self.parent if self.parent else None

            # Create progress dialog
            self.logger.debug("Creating new progress dialog")
            self.color_calc_progress_dialog = QProgressDialog(
                "Initializing gallery view...",
                "Cancel",
                0, 100,
                parent_widget
            )

            if not self.color_calc_progress_dialog:
                raise ValueError("Failed to create progress dialog")

            self.color_calc_progress_dialog.setWindowTitle("Loading Gallery")
            self.color_calc_progress_dialog.setWindowModality(Qt.WindowModal)
            self.color_calc_progress_dialog.setMinimumDuration(0)  # Show immediately
            self.color_calc_progress_dialog.setAutoClose(True)
            self.color_calc_progress_dialog.setAutoReset(False)

            # Connect cancel button
            self.color_calc_progress_dialog.canceled.connect(self._on_color_calc_cancelled)

            # Connect model signals to progress dialog
            self.model.color_calc_progress.connect(self._on_color_calc_progress)
            self.model.color_calc_message.connect(self._on_color_calc_message)
            self.model.color_calc_complete.connect(self._on_color_calc_complete)

            # Explicitly show the dialog and process events to ensure it's visible
            self.color_calc_progress_dialog.show()
            QApplication.processEvents()

            # Use QTimer to defer color calculation to next event loop cycle
            # This allows the progress dialog to display before calculation starts
            QTimer.singleShot(50, self.model._precalculate_color_info)

        except Exception as e:
            self.logger.error(f"Error starting color calculation: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Cleanup
            self._disconnect_color_calc_signals()
            if self.color_calc_progress_dialog:
                self.color_calc_progress_dialog.close()
                self.color_calc_progress_dialog = None
            # Fallback: calculate synchronously without dialog
            self.model._precalculate_color_info()
            self._finalize_gallery_load()

    def _on_color_calc_progress(self, current, total):
        """Handle color calculation progress update."""
        if self.color_calc_progress_dialog and not self.color_calc_progress_dialog.wasCanceled():
            percent = int((current / total) * 100) if total > 0 else 0
            self.color_calc_progress_dialog.setValue(percent)
            # Process events to keep dialog responsive
            QApplication.processEvents()

    def _on_color_calc_message(self, message):
        """Handle color calculation status message."""
        if self.color_calc_progress_dialog and not self.color_calc_progress_dialog.wasCanceled():
            self.color_calc_progress_dialog.setLabelText(message)
            # Process events to keep dialog responsive
            QApplication.processEvents()

    def _disconnect_color_calc_signals(self):
        """Disconnect all color calculation signal connections."""
        try:
            # Disconnect model signals
            try:
                self.model.color_calc_progress.disconnect(self._on_color_calc_progress)
            except:
                pass
            try:
                self.model.color_calc_message.disconnect(self._on_color_calc_message)
            except:
                pass
            try:
                self.model.color_calc_complete.disconnect(self._on_color_calc_complete)
            except:
                pass

            # Disconnect dialog signals
            if self.color_calc_progress_dialog:
                try:
                    self.color_calc_progress_dialog.canceled.disconnect(self._on_color_calc_cancelled)
                except:
                    pass
        except Exception as e:
            self.logger.debug(f"Error disconnecting signals: {e}")

    def _on_color_calc_complete(self):
        """Handle color calculation completion."""
        try:
            self.logger.debug("===== _on_color_calc_complete() called =====")

            # Disconnect signals first
            self._disconnect_color_calc_signals()

            # Close progress dialog
            if self.color_calc_progress_dialog:
                self.logger.debug("Closing progress dialog (complete)")
                self.color_calc_progress_dialog.setValue(100)
                self.color_calc_progress_dialog.close()
                self.color_calc_progress_dialog = None

            # Finalize gallery load (apply sorting/filtering)
            self._finalize_gallery_load()

        except Exception as e:
            self.logger.error(f"Error completing color calculation: {e}")

    def _on_color_calc_cancelled(self):
        """Handle color calculation cancellation."""
        self.logger.info("===== Color calculation cancelled by user =====")
        self.model.cancel_color_calculation()

        # Disconnect signals
        self._disconnect_color_calc_signals()

        # Close progress dialog
        if self.color_calc_progress_dialog:
            self.logger.debug("Closing progress dialog (cancelled)")
            self.color_calc_progress_dialog.close()
            self.color_calc_progress_dialog = None

    def _finalize_gallery_load(self):
        """Finalize gallery load by applying sorting and filtering."""
        try:
            self.logger.debug("===== _finalize_gallery_load() called =====")

            # Get current items
            all_aois = list(self.model.aoi_items)

            # Apply sorting (using cached colors)
            sorted_aois = self._sort_aois_global(all_aois)

            # Apply filtering (using cached colors)
            filtered_aois = self._filter_aois_global(sorted_aois)

            # Update model with filtered results (skip color calc and preserve color cache)
            self.model.set_aoi_items(filtered_aois, skip_color_calc=True, preserve_color_cache=True)

            # Update count label in UI
            if self.ui_component:
                self.ui_component._update_count_label(len(filtered_aois))

            self.logger.info(f"Loaded {len(filtered_aois)} AOIs in gallery (from {len(all_aois)} total)")

        except Exception as e:
            self.logger.error(f"Error finalizing gallery load: {e}")

    def _collect_all_aois(self):
        """
        Collect all AOIs from all loaded images.

        Returns:
            List of (image_index, aoi_index, aoi_data) tuples
        """
        all_aois = []

        for img_idx, image in enumerate(self.parent.images):
            # Skip hidden images if desired (for now, show all)
            # if image.get('hidden', False):
            #     continue

            areas_of_interest = image.get('areas_of_interest', [])

            for aoi_idx, aoi in enumerate(areas_of_interest):
                all_aois.append((img_idx, aoi_idx, aoi))

        return all_aois

    def _sort_aois_global(self, aoi_items):
        """
        Sort AOIs globally across all images.

        Args:
            aoi_items: List of (image_idx, aoi_idx, aoi_data) tuples

        Returns:
            Sorted list of tuples
        """
        if self.sort_method is None:
            return aoi_items

        try:
            if self.sort_method == 'area_asc':
                aoi_items.sort(key=lambda x: x[2].get('area', 0))

            elif self.sort_method == 'area_desc':
                aoi_items.sort(key=lambda x: x[2].get('area', 0), reverse=True)

            elif self.sort_method == 'confidence_asc':
                aoi_items.sort(key=lambda x: x[2].get('confidence', -1))

            elif self.sort_method == 'confidence_desc':
                aoi_items.sort(key=lambda x: x[2].get('confidence', -1), reverse=True)

            elif self.sort_method == 'color':
                if self.sort_color_hue is not None:
                    def color_sort_key(item):
                        img_idx, aoi_idx, aoi = item
                        hue = self._get_aoi_hue(img_idx, aoi_idx)
                        if hue is None:
                            return 999999
                        return self._calculate_hue_distance(hue, self.sort_color_hue)
                    aoi_items.sort(key=color_sort_key)

            elif self.sort_method == 'x':
                aoi_items.sort(key=lambda x: x[2]['center'][0])

            elif self.sort_method == 'y':
                aoi_items.sort(key=lambda x: x[2]['center'][1])

            elif self.sort_method == 'temperature_asc':
                def temp_sort_key_asc(item):
                    img_idx, aoi_idx, aoi = item
                    temp = self._get_aoi_temperature(img_idx, aoi_idx)
                    # Sort None/unavailable temperatures to the end
                    if temp is None:
                        return float('inf')
                    return temp
                aoi_items.sort(key=temp_sort_key_asc)

            elif self.sort_method == 'temperature_desc':
                def temp_sort_key_desc(item):
                    img_idx, aoi_idx, aoi = item
                    temp = self._get_aoi_temperature(img_idx, aoi_idx)
                    # Sort None/unavailable temperatures to the end
                    if temp is None:
                        return float('-inf')
                    return temp
                aoi_items.sort(key=temp_sort_key_desc, reverse=True)

        except Exception as e:
            self.logger.error(f"Error sorting AOIs globally: {e}")

        return aoi_items

    def _filter_aois_global(self, aoi_items):
        """
        Filter AOIs globally across all images.

        Args:
            aoi_items: List of (image_idx, aoi_idx, aoi_data) tuples

        Returns:
            Filtered list of tuples
        """
        filtered = []

        for img_idx, aoi_idx, aoi in aoi_items:
            # Apply flag filter
            if self.filter_flagged_only:
                if not aoi.get('flagged', False):
                    continue

            # Apply comment filter
            if self.filter_comment_pattern is not None:
                comment = aoi.get('user_comment', '').strip()
                # Skip AOIs with empty comments when filter is active
                if not comment:
                    continue
                # Case-insensitive wildcard matching
                if not fnmatch.fnmatch(comment.lower(), self.filter_comment_pattern.lower()):
                    continue

            # Apply color filter
            if self.filter_color_hue is not None and self.filter_color_range is not None:
                hue = self._get_aoi_hue(img_idx, aoi_idx)
                if hue is not None:
                    distance = self._calculate_hue_distance(hue, self.filter_color_hue)
                    if distance > self.filter_color_range:
                        continue
                else:
                    continue

            # Apply area filter
            area = aoi.get('area', 0)
            if self.filter_area_min is not None and area < self.filter_area_min:
                continue
            if self.filter_area_max is not None and area > self.filter_area_max:
                continue

            # Apply temperature filter
            if self.filter_temperature_min is not None or self.filter_temperature_max is not None:
                temp = self._get_aoi_temperature(img_idx, aoi_idx)
                # Skip AOIs without temperature data when filter is active
                if temp is None:
                    continue
                # Check min/max temperature bounds (in Celsius)
                if self.filter_temperature_min is not None and temp < self.filter_temperature_min:
                    continue
                if self.filter_temperature_max is not None and temp > self.filter_temperature_max:
                    continue

            # AOI passed all filters
            filtered.append((img_idx, aoi_idx, aoi))

        return filtered

    def _get_aoi_hue(self, img_idx, aoi_idx):
        """
        Get the representative hue for an AOI using cached color information.

        Args:
            img_idx: Image index
            aoi_idx: AOI index within the image

        Returns:
            Hue value (0-360) or None
        """
        try:
            # Try to get from model's cached color info (fastest - already in memory)
            cache_key = (img_idx, aoi_idx)
            if hasattr(self.model, '_color_info_cache') and cache_key in self.model._color_info_cache:
                color_info = self.model._color_info_cache[cache_key]
                if color_info and 'hue_degrees' in color_info:
                    return color_info['hue_degrees']

            # Not found in cache - this shouldn't happen if pre-calculation worked
            # but return None rather than trying to calculate on-demand during filtering
            return None

        except Exception as e:
            self.logger.error(f"Error getting AOI hue: {e}")
            return None

    def _calculate_hue_distance(self, hue1, hue2):
        """
        Calculate the circular distance between two hues.

        Args:
            hue1: First hue (0-360)
            hue2: Second hue (0-360)

        Returns:
            Distance (0-180)
        """
        diff = abs(hue1 - hue2)
        if diff > 180:
            diff = 360 - diff
        return diff

    def _get_aoi_temperature(self, img_idx, aoi_idx):
        """
        Get the temperature for an AOI (in Celsius).

        Args:
            img_idx: Image index
            aoi_idx: AOI index within the image

        Returns:
            Temperature in Celsius or None if unavailable
        """
        try:
            # Try to get from model's cached temperature info (fastest - already in memory)
            cache_key = (img_idx, aoi_idx)
            if hasattr(self.model, '_temperature_info_cache') and cache_key in self.model._temperature_info_cache:
                return self.model._temperature_info_cache[cache_key]

            # Try to get from AOI data directly (loaded from XML)
            if self.parent and hasattr(self.parent, 'images'):
                if 0 <= img_idx < len(self.parent.images):
                    image = self.parent.images[img_idx]
                    aois = image.get('areas_of_interest', [])
                    if 0 <= aoi_idx < len(aois):
                        temp = aois[aoi_idx].get('temperature')
                        if temp is not None:
                            # Cache it for future use
                            if hasattr(self.model, '_temperature_info_cache'):
                                self.model._temperature_info_cache[cache_key] = temp
                            return temp

            return None

        except Exception as e:
            self.logger.error(f"Error getting AOI temperature: {e}")
            return None

    def set_sort_method(self, method, color_hue=None):
        """
        Set the sort method for the gallery.

        Args:
            method: Sort method ('area_asc', 'area_desc', 'confidence_asc',
                    'confidence_desc', 'color', 'x', 'y', or None)
            color_hue: Hue value (0-360) for color-based sorting (optional)
        """
        self.sort_method = method
        self.sort_color_hue = color_hue
        self.load_all_aois()  # Reload with new sort

    def set_filters(self, filters):
        """
        Set filter settings for the gallery.

        Args:
            filters: Dict with filter settings {
                'flagged_only': bool,
                'comment_filter': str or None,
                'color_hue': int or None,
                'color_range': int or None,
                'area_min': float or None,
                'area_max': float or None,
                'temperature_min': float or None,
                'temperature_max': float or None
            }
        """
        self.filter_flagged_only = filters.get('flagged_only', False)
        self.filter_comment_pattern = filters.get('comment_filter')
        self.filter_color_hue = filters.get('color_hue')
        self.filter_color_range = filters.get('color_range')
        self.filter_area_min = filters.get('area_min')
        self.filter_area_max = filters.get('area_max')
        self.filter_temperature_min = filters.get('temperature_min')
        self.filter_temperature_max = filters.get('temperature_max')

        self.load_all_aois()  # Reload with new filters

    def sync_filters_from_aoi_controller(self):
        """
        Sync filter and sort settings from the single-image AOI controller.

        This allows seamless switching between views with consistent filters.
        """
        if not hasattr(self.parent, 'aoi_controller'):
            return

        aoi_ctrl = self.parent.aoi_controller

        # Sync filter settings
        self.filter_flagged_only = aoi_ctrl.filter_flagged_only
        if hasattr(aoi_ctrl, 'filter_comment_pattern'):
            self.filter_comment_pattern = aoi_ctrl.filter_comment_pattern
        self.filter_color_hue = aoi_ctrl.filter_color_hue
        self.filter_color_range = aoi_ctrl.filter_color_range
        self.filter_area_min = aoi_ctrl.filter_area_min
        self.filter_area_max = aoi_ctrl.filter_area_max
        if hasattr(aoi_ctrl, 'filter_temperature_min'):
            self.filter_temperature_min = aoi_ctrl.filter_temperature_min
        if hasattr(aoi_ctrl, 'filter_temperature_max'):
            self.filter_temperature_max = aoi_ctrl.filter_temperature_max

        # Sync sort settings
        self.sort_method = aoi_ctrl.sort_method
        self.sort_color_hue = aoi_ctrl.sort_color_hue

        self.logger.debug("Synced filters from AOI controller")

    def on_aoi_clicked(self, image_idx, aoi_idx, aoi_data):
        """
        Handle click on an AOI in the gallery.

        Args:
            image_idx: Index of the image containing the AOI
            aoi_idx: Index of the AOI within the image
            aoi_data: AOI data dictionary
        """
        try:
            self.logger.info(f"Gallery AOI clicked: Image {image_idx}, AOI {aoi_idx}")

            # Stay in gallery mode - just load the image with the clicked AOI
            # 1. Load the parent image if it's not already loaded
            needs_load = (self.parent.current_image != image_idx)
            if needs_load:
                self.parent.current_image = image_idx
                if hasattr(self.parent, '_load_image'):
                    self.parent._load_image()

            # 2. Zoom to the AOI in the image viewer
            # Give the image more time to load if needed, then zoom
            from PySide6.QtCore import QTimer
            # Use longer delay if we just loaded a new image (500ms), shorter if same image (100ms)
            delay = 500 if needs_load else 100
            QTimer.singleShot(delay, lambda: self._zoom_to_aoi(aoi_data))

        except Exception as e:
            self.logger.error(f"Error handling AOI click: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def _zoom_to_aoi(self, aoi_data):
        """Zoom to an AOI in the image viewer and highlight it."""
        try:
            # Get AOI center
            center = aoi_data.get('center')

            self.logger.info(f"Attempting to zoom to AOI: center={center}")

            if not center:
                self.logger.warning("AOI has no center coordinate, cannot zoom")
                return

            if not hasattr(self.parent, 'main_image'):
                self.logger.warning("Parent has no main_image viewer")
                return

            viewer = self.parent.main_image

            # First, make sure AOI overlays are visible
            if hasattr(self.parent, 'showOverlayToggle'):
                if not self.parent.showOverlayToggle.isChecked():
                    self.logger.info("Enabling AOI overlay visibility")
                    self.parent.showOverlayToggle.setChecked(True)
                    # Trigger the overlay update
                    if hasattr(self.parent, '_show_overlay_change'):
                        self.parent._show_overlay_change()

            # Use the same zoom method as single-image view
            # zoomToArea(center_xy, scale) where scale 6 = 6x zoom
            if hasattr(viewer, 'zoomToArea'):
                self.logger.info(f"Calling zoomToArea with center={center}, scale=6")
                viewer.zoomToArea(center, 6)
                self.logger.info(f"Successfully zoomed to AOI at {center}")
            else:
                self.logger.warning("Viewer does not have zoomToArea method")

        except Exception as e:
            self.logger.error(f"Error zooming to AOI: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def refresh_gallery(self):
        """Refresh the gallery display."""
        self.load_all_aois()
        if self.ui_component:
            self.ui_component.refresh_gallery()

    def clear_gallery(self):
        """Clear the gallery display."""
        self.model.set_aoi_items([])
        self._aoi_service_cache.clear()
        if self.ui_component:
            self.ui_component.clear_gallery()

    def clear_cache(self):
        """Clear cached data to free memory."""
        self.model.clear_cache()
        self._aoi_service_cache.clear()

    def on_image_loaded(self, image_idx):
        """
        Called when an image is loaded in the viewer.
        This allows the gallery to generate thumbnails for the current image's AOIs.

        Args:
            image_idx: Index of the loaded image
        """
        try:
            # If not in gallery mode, nothing to do
            if not hasattr(self.parent, 'gallery_mode') or not self.parent.gallery_mode:
                return

            # Prefetch thumbnails for the current image's AOIs
            self.model.prefetch_current_image_thumbnails()

            # Trigger a refresh of the gallery view to show new thumbnails
            if self.ui_component and self.ui_component.gallery_view:
                self.ui_component.gallery_view.viewport().update()
                # Emit data changed for current image's items
                self.model.dataChanged.emit(
                    self.model.index(0, 0),
                    self.model.index(self.model.rowCount() - 1, 0)
                )

        except Exception as e:
            self.logger.error(f"Error updating gallery on image load: {e}")

    def sync_selection_from_aoi_controller(self, image_idx, aoi_idx):
        """
        Sync selection from the single-image AOI controller to the gallery.

        Args:
            image_idx: Index of the image containing the AOI
            aoi_idx: Index of the AOI within the image
        """
        try:
            if not self.ui_component or not self.ui_component.gallery_view:
                return

            # Find the corresponding item in the gallery model
            for row in range(self.model.rowCount()):
                aoi_info = self.model.get_aoi_info(self.model.index(row, 0))
                if aoi_info:
                    g_img_idx, g_aoi_idx, _ = aoi_info
                    if g_img_idx == image_idx and g_aoi_idx == aoi_idx:
                        # Select this item in the gallery
                        self.ui_component.gallery_view.setCurrentIndex(self.model.index(row, 0))
                        # Scroll to make it visible
                        self.ui_component.gallery_view.scrollTo(self.model.index(row, 0))
                        break

        except Exception as e:
            self.logger.error(f"Error syncing selection from AOI controller: {e}")
