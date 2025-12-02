"""
GalleryController - Handles business logic for the AOI gallery view.

This controller manages gallery data, filtering, sorting, and interactions
for displaying AOIs from all loaded images.
"""

import colorsys
import fnmatch
import math
import numpy as np
import os
import traceback
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QProgressDialog, QApplication
from PySide6.QtCore import Qt
from core.services.LoggerService import LoggerService
from core.services.image.AOIService import AOIService
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

        # Gallery column width constants (thumbnail + spacing)
        self.GALLERY_COLUMN_WIDTH = 200  # 190px thumbnail + 10px spacing
        # Gallery overhead (margins + scrollbar + padding)
        self.GALLERY_OVERHEAD = 35  # Approx. 20px scrollbar + 15px margins/padding

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
        with loading overlay.
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

            # Show loading overlay immediately
            if hasattr(self.parent, 'show_gallery_loading_overlay'):
                self.parent.show_gallery_loading_overlay()

            # Collect all AOIs from all images
            all_aois = self._collect_all_aois()
            self.logger.debug(f"Collected {len(all_aois)} AOIs")

            # Set items without triggering color calculation
            self.model.set_aoi_items(all_aois, skip_color_calc=True)
            self.logger.debug("Set AOI items in model")

            # Start color calculation in background with loading overlay
            self._start_color_calculation_with_progress(all_aois)

        except Exception as e:
            self.logger.error(f"Error loading AOIs in gallery: {e}")
            # Hide overlay on error
            if hasattr(self.parent, 'hide_gallery_loading_overlay'):
                self.parent.hide_gallery_loading_overlay()

    def _start_color_calculation_with_progress(self, all_aois):
        """
        Start color calculation with loading overlay.

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

            # Loading overlay is already shown in load_all_aois()
            # Just connect model signals (no progress updates needed for overlay)
            self.model.color_calc_complete.connect(self._on_color_calc_complete)

            # Start color calculation
            self.model._precalculate_color_info()

        except Exception as e:
            self.logger.error(f"Error starting color calculation: {e}")
            self.logger.error(traceback.format_exc())
            # Cleanup
            self._disconnect_color_calc_signals()
            if hasattr(self.parent, 'hide_gallery_loading_overlay'):
                self.parent.hide_gallery_loading_overlay()
            # Fallback: calculate synchronously without overlay
            self.model._precalculate_color_info()
            self._finalize_gallery_load()

    def _on_color_calc_progress(self, current, total):
        """Handle color calculation progress update."""
        # Progress updates no longer needed with overlay
        # Keep method for compatibility but don't do anything
        pass

    def _on_color_calc_message(self, message):
        """Handle color calculation status message."""
        # Message updates no longer needed with overlay
        # Keep method for compatibility but don't do anything
        pass

    def _disconnect_color_calc_signals(self):
        """Disconnect all color calculation signal connections."""
        try:
            # Disconnect model signals
            try:
                self.model.color_calc_progress.disconnect(self._on_color_calc_progress)
            except Exception:
                pass
            try:
                self.model.color_calc_message.disconnect(self._on_color_calc_message)
            except Exception:
                pass
            try:
                self.model.color_calc_complete.disconnect(self._on_color_calc_complete)
            except Exception:
                pass

            # Disconnect dialog signals
            if self.color_calc_progress_dialog:
                try:
                    self.color_calc_progress_dialog.canceled.disconnect(self._on_color_calc_cancelled)
                except Exception:
                    pass
        except Exception as e:
            self.logger.debug(f"Error disconnecting signals: {e}")

    def _on_color_calc_complete(self):
        """Handle color calculation completion."""
        try:
            self.logger.debug("===== _on_color_calc_complete() called =====")

            # Disconnect signals first
            self._disconnect_color_calc_signals()

            # Hide loading overlay
            if hasattr(self.parent, 'hide_gallery_loading_overlay'):
                self.parent.hide_gallery_loading_overlay()

            # Close progress dialog if it exists (for backwards compatibility)
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

        # Hide loading overlay
        if hasattr(self.parent, 'hide_gallery_loading_overlay'):
            self.parent.hide_gallery_loading_overlay()

        # Close progress dialog if it exists (for backwards compatibility)
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

                # Ensure thumbnails are loaded for the filtered results
                # The modelReset signal will trigger _on_model_changed which loads thumbnails
                # But also explicitly trigger if widget is visible
                if (self.ui_component.gallery_widget and
                        self.ui_component.gallery_widget.isVisible() and
                        len(filtered_aois) > 0):
                    self.ui_component._load_visible_thumbnails()

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

                # Connect to viewChanged signal BEFORE loading to avoid missing the signal
                # Note: viewChanged fires twice during load_image():
                # 1. From setImage() -> updateViewer() (zoom stack not reset yet)
                # 2. From resetZoom() -> updateViewer() (zoom stack cleared)
                # We need to wait for the second one (after resetZoom) to ensure zoom stack is clear
                zoom_handler = None
                zoom_executed = False
                view_changed_count = 0

                def zoom_when_ready():
                    nonlocal zoom_executed, view_changed_count
                    view_changed_count += 1

                    # Check if _recursion_guard is set - if so, updateViewer() is still running
                    # and zoomToArea() will return early. We need to wait for it to complete.
                    recursion_guard_active = False
                    if (hasattr(self.parent, 'main_image') and
                            self.parent.main_image and
                            hasattr(self.parent.main_image, '_recursion_guard')):
                        recursion_guard_active = self.parent.main_image._recursion_guard

                    # Don't try to zoom if recursion guard is active - zoomToArea() will return early
                    if recursion_guard_active:
                        return

                    # Check if zoom stack is empty (meaning resetZoom has been called)
                    # This ensures we only zoom after the resetZoom viewChanged signal
                    zoom_stack_cleared = False
                    if (hasattr(self.parent, 'main_image') and
                            self.parent.main_image and
                            hasattr(self.parent.main_image, 'zoomStack')):
                        zoom_stack_cleared = len(self.parent.main_image.zoomStack) == 0

                    # Only zoom if:
                    # 1. We haven't zoomed yet
                    # 2. Image is loaded
                    # 3. Recursion guard is not active (updateViewer completed)
                    # 4. Zoom stack is cleared (resetZoom has been called)
                    if (not zoom_executed and
                            hasattr(self.parent, 'main_image') and
                            self.parent.main_image and
                            self.parent.main_image.hasImage() and
                            not recursion_guard_active and
                            zoom_stack_cleared):
                        zoom_executed = True
                        self._zoom_to_aoi(aoi_data)
                        # Disconnect after first call
                        if zoom_handler:
                            try:
                                self.parent.main_image.viewChanged.disconnect(zoom_handler)
                            except Exception:
                                pass

                # Connect to viewChanged signal BEFORE loading (critical for race condition)
                if hasattr(self.parent, 'main_image') and self.parent.main_image:
                    try:
                        self.parent.main_image.viewChanged.connect(zoom_when_ready)
                        zoom_handler = zoom_when_ready
                    except Exception as e:
                        self.logger.debug(f"Could not connect to viewChanged: {e}")

                # Now load the image - this will emit viewChanged signals which our handler will catch
                if hasattr(self.parent, '_load_image'):
                    self.parent._load_image()

                # Check if image is ready and zoom stack is cleared but signal handler hasn't executed
                # Only check if zoom hasn't already executed via the signal
                if (not zoom_executed and
                        hasattr(self.parent, 'main_image') and
                        self.parent.main_image and
                        self.parent.main_image.hasImage()):
                    # Check if recursion guard is active - if so, wait for signal handler
                    recursion_guard_active = False
                    if hasattr(self.parent.main_image, '_recursion_guard'):
                        recursion_guard_active = self.parent.main_image._recursion_guard

                    # Check if zoom stack is cleared (resetZoom has been called)
                    zoom_stack_cleared = False
                    if hasattr(self.parent.main_image, 'zoomStack'):
                        zoom_stack_cleared = len(self.parent.main_image.zoomStack) == 0

                    # Only zoom if recursion guard is not active and zoom stack is cleared
                    if not recursion_guard_active and zoom_stack_cleared:
                        # Disconnect the signal handler to prevent double-zoom
                        if zoom_handler:
                            try:
                                self.parent.main_image.viewChanged.disconnect(zoom_handler)
                            except Exception:
                                pass
                        # Zoom directly since image is ready and zoom is reset
                        zoom_executed = True
                        self._zoom_to_aoi(aoi_data)
                elif not zoom_handler:
                    # Couldn't connect to signal, try zooming directly if image is ready and zoom is reset
                    if (hasattr(self.parent, 'main_image') and
                            self.parent.main_image and
                            self.parent.main_image.hasImage()):
                        # Check if recursion guard is active
                        recursion_guard_active = False
                        if hasattr(self.parent.main_image, '_recursion_guard'):
                            recursion_guard_active = self.parent.main_image._recursion_guard

                        # Check if zoom stack is cleared before zooming
                        zoom_stack_cleared = False
                        if hasattr(self.parent.main_image, 'zoomStack'):
                            zoom_stack_cleared = len(self.parent.main_image.zoomStack) == 0

                        if not recursion_guard_active and zoom_stack_cleared:
                            self._zoom_to_aoi(aoi_data)
            else:
                # Same image - zoom immediately
                self._zoom_to_aoi(aoi_data)

        except Exception as e:
            self.logger.error(f"Error handling AOI click: {e}")
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

    def toggle_aoi_flag(self):
        """Toggle the flag status of the currently selected AOI in the gallery."""
        self.logger.debug("===== toggle_aoi_flag() called =====")
        
        if not self.ui_component:
            self.logger.warning("toggle_aoi_flag: ui_component is None")
            return
        
        if not self.ui_component.gallery_view:
            self.logger.warning("toggle_aoi_flag: gallery_view is None")
            return

        current_index = self.ui_component.gallery_view.currentIndex()
        self.logger.debug(f"toggle_aoi_flag: current_index.isValid() = {current_index.isValid()}, row = {current_index.row() if current_index.isValid() else 'N/A'}")
        
        if not current_index.isValid():
            self.logger.warning("toggle_aoi_flag: No valid current index in gallery")
            return

        aoi_info = self.model.get_aoi_info(current_index)
        self.logger.debug(f"toggle_aoi_flag: aoi_info = {aoi_info}")
        
        if aoi_info:
            image_idx, aoi_idx, _ = aoi_info
            self.logger.info(f"Toggling flag for gallery item at row {current_index.row()}: image {image_idx}, AOI {aoi_idx}")
            self.toggle_aoi_flag_by_index(image_idx, aoi_idx)
        else:
            self.logger.error(f"Could not get AOI info for index at row {current_index.row()}")

    def toggle_aoi_flag_by_index(self, image_idx, aoi_idx):
        """
        Toggle the flag status of the specified AOI without launching dialogs.

        Args:
            image_idx: Index of the image containing the AOI
            aoi_idx: Index of the AOI within the image
        """
        if image_idx is None or image_idx < 0 or aoi_idx is None or aoi_idx < 0:
            return

        # Use the AOI controller's flagged_aois dictionary to maintain consistency
        if not hasattr(self.parent, 'aoi_controller'):
            return

        aoi_ctrl = self.parent.aoi_controller

        # Get or create flagged set for the image
        if image_idx not in aoi_ctrl.flagged_aois:
            aoi_ctrl.flagged_aois[image_idx] = set()

        flagged_set = aoi_ctrl.flagged_aois[image_idx]

        # Toggle flag status
        is_now_flagged = aoi_idx not in flagged_set
        if is_now_flagged:
            flagged_set.add(aoi_idx)
        else:
            flagged_set.remove(aoi_idx)

        # Save to XML using the AOI controller's method
        aoi_ctrl.save_flagged_aoi_to_xml(image_idx, aoi_idx, is_now_flagged)

        # Update the AOI data in the images list
        if (hasattr(self.parent, 'images') and 
                0 <= image_idx < len(self.parent.images)):
            image = self.parent.images[image_idx]
            if 'areas_of_interest' in image and 0 <= aoi_idx < len(image['areas_of_interest']):
                aoi = image['areas_of_interest'][aoi_idx]
                aoi['flagged'] = is_now_flagged

        # Check if we need to reload gallery due to filtering
        needs_reload = self.filter_flagged_only  # If filtering by flagged status, need to reload
        
        if needs_reload:
            # Save which AOI we just toggled so we can reselect it
            toggled_key = (image_idx, aoi_idx)
            # Reload the gallery with current filters
            self.load_all_aois()
            # Try to reselect the toggled item (if it's still visible after filtering)
            if toggled_key in self.model.aoi_to_row:
                row = self.model.aoi_to_row[toggled_key]
                self.ui_component.gallery_view.setCurrentIndex(self.model.index(row, 0))
        else:
            # Just refresh the flag display without reloading
            self._refresh_gallery_flag_display(image_idx, aoi_idx)

        # Update GPS map if it's open to reflect flagged status change
        if hasattr(self.parent, 'gps_map_controller') and self.parent.gps_map_controller.map_dialog:
            if self.parent.gps_map_controller.map_dialog.isVisible():
                # Re-extract GPS data to update has_flagged status
                self.parent.gps_map_controller.extract_gps_data()
                # Find the image index in GPS data
                gps_index = None
                for i, data in enumerate(self.parent.gps_map_controller.gps_data):
                    if data['index'] == image_idx:
                        gps_index = i
                        break
                # Update the map with refreshed data
                if gps_index is not None:
                    self.parent.gps_map_controller.map_dialog.update_gps_data(
                        self.parent.gps_map_controller.gps_data,
                        gps_index
                    )

        # Always refresh the AOI display if we're viewing this image (regardless of mode)
        # This ensures flags are visible when switching back to single-image mode
        if (hasattr(self.parent, 'current_image') and
                self.parent.current_image == image_idx):
            if hasattr(self.parent, 'aoi_controller') and self.parent.aoi_controller.ui_component:
                self.parent.aoi_controller.ui_component.refresh_aoi_display()

    def _refresh_gallery_flag_display(self, image_idx, aoi_idx):
        """Refresh the gallery display for a specific AOI's flag status."""
        try:
            if not self.model or not self.ui_component or not self.ui_component.gallery_view:
                return

            # Save the current selection to restore it after update
            current_index = self.ui_component.gallery_view.currentIndex()
            current_row = current_index.row() if current_index.isValid() else -1
            
            # Update the AOI data in the model's items list
            cache_key = (image_idx, aoi_idx)
            if cache_key in self.model.aoi_to_row:
                row = self.model.aoi_to_row[cache_key]
                self.logger.debug(f"Refreshing flag display for image {image_idx}, AOI {aoi_idx} at row {row} (current selection: row {current_row})")
                
                # Update the aoi_data in the model's items list
                if 0 <= row < len(self.model.aoi_items):
                    _, _, aoi_data = self.model.aoi_items[row]
                    # Get the current flagged status from the images list
                    if (hasattr(self.parent, 'images') and 
                            0 <= image_idx < len(self.parent.images)):
                        image = self.parent.images[image_idx]
                        if 'areas_of_interest' in image and 0 <= aoi_idx < len(image['areas_of_interest']):
                            aoi_data['flagged'] = image['areas_of_interest'][aoi_idx].get('flagged', False)

                index = self.model.index(row, 0)
                # Block signals temporarily to prevent selection changes
                self.ui_component.gallery_view.blockSignals(True)
                # Emit dataChanged to trigger repaint
                self.model.dataChanged.emit(index, index, [Qt.UserRole, Qt.DecorationRole])
                # Restore the selection
                if current_index.isValid():
                    self.ui_component.gallery_view.setCurrentIndex(current_index)
                    self.logger.debug(f"Restored selection to row {current_index.row()}")
                # Re-enable signals
                self.ui_component.gallery_view.blockSignals(False)
                # Also update the viewport
                self.ui_component.gallery_view.viewport().update()
            else:
                self.logger.warning(f"Could not find row for image {image_idx}, AOI {aoi_idx} in model")

        except Exception as e:
            self.logger.error(f"Error refreshing gallery flag display: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def setup_gallery_mode_ui(self):
        """Set up the gallery mode UI."""
        try:
            # Check that required UI elements exist
            if not hasattr(self.parent, 'aoiFrame') or not self.parent.aoiFrame:
                self.logger.error("aoiFrame not found, cannot set up gallery")
                return None

            if not hasattr(self.parent, 'aoiListWidget') or not self.parent.aoiListWidget:
                self.logger.error("aoiListWidget not found, cannot set up gallery")
                return None

            # Check if the parent widget is visible - if not, defer creation
            if not self.parent.isVisible():
                self.logger.debug("Parent widget not visible yet, deferring gallery widget creation")
                return None

            # Create gallery widget with aoiFrame as parent (safer than layout manipulation)
            gallery_widget = self.create_gallery_widget(self.parent.aoiFrame)

            # Start hidden - will be sized when shown
            gallery_widget.setVisible(False)
            gallery_widget.hide()

            # Raise aoiListWidget to front initially (single-image mode)
            self.parent.aoiListWidget.raise_()

            self.logger.info("Gallery mode UI setup complete")
            return gallery_widget

        except Exception as e:
            self.logger.error(f"Error setting up gallery mode UI: {e}")
            self.logger.error(traceback.format_exc())
            return None

    def update_gallery_geometry(self, gallery_widget):
        """Update gallery widget geometry to fill aoiFrame."""
        try:
            if (gallery_widget and gallery_widget.isVisible() and
                    hasattr(self.parent, 'gallery_mode') and
                    self.parent.gallery_mode):

                # Fill frame width for responsive grid display
                frame_rect = self.parent.aoiFrame.rect()
                aoi_list_rect = self.parent.aoiListWidget.geometry()

                gallery_widget.setGeometry(
                    5,
                    aoi_list_rect.y(),
                    frame_rect.width() - 10,
                    aoi_list_rect.height()
                )

                # Force the gallery view to update its layout
                if self.ui_component and self.ui_component.gallery_view:
                    gallery_view = self.ui_component.gallery_view
                    # Update the view's geometry and force layout recalculation
                    gallery_view.updateGeometry()
                    gallery_view.scheduleDelayedItemsLayout()
                    gallery_view.viewport().update()

                # Update loading overlay position if visible
                if hasattr(self.parent, '_update_gallery_overlay_position'):
                    self.parent._update_gallery_overlay_position()

        except Exception as e:
            self.logger.debug(f"Error updating gallery geometry: {e}")

    def set_splitter_to_single_column(self, splitter):
        """Set the splitter to show exactly 1 column in the gallery."""
        try:
            total_width = sum(splitter.sizes())
            # Calculate width for 1 column + overhead
            single_column_width = self.GALLERY_COLUMN_WIDTH + self.GALLERY_OVERHEAD
            image_width = total_width - single_column_width

            splitter.setSizes([image_width, single_column_width])
            self.logger.debug(f"Set splitter to single column: [{image_width}, {single_column_width}]")
        except Exception as e:
            self.logger.debug(f"Error setting splitter to single column: {e}")

    def _set_splitter_cursor(self, splitter, cursor):
        """Set the cursor on the splitter and its handle to prevent drag cursor when disabled."""
        try:
            # Set cursor on the splitter widget itself
            splitter.setCursor(cursor)
            # Also set cursor on the handle if it exists
            # For a horizontal splitter with 2 widgets, the handle is at index 1
            try:
                handle = splitter.handle(1)
                if handle:
                    handle.setCursor(cursor)
            except Exception:
                # Handle might not exist if width is 0, that's okay
                pass
        except Exception as e:
            self.logger.debug(f"Error setting splitter cursor: {e}")

    def save_splitter_position(self, splitter):
        """Save current splitter position to settings based on current view mode."""
        try:
            if not hasattr(self.parent, 'settings_service'):
                return

            sizes = splitter.sizes()
            # Save as comma-separated string
            position_str = f"{sizes[0]},{sizes[1]}"

            # Save to different settings key based on mode
            if hasattr(self.parent, 'gallery_mode') and self.parent.gallery_mode:
                # Save gallery mode position
                self.parent.settings_service.set_setting('viewer/splitter_position_gallery', position_str)
            else:
                # Save single-image mode position
                self.parent.settings_service.set_setting('viewer/splitter_position_single', position_str)
        except Exception as e:
            self.logger.debug(f"Could not save splitter position: {e}")

    def on_splitter_moved(self, pos, index, splitter, gallery_widget):
        """Handle splitter movement with snapping to column widths."""
        try:
            # Check if we're in single-image mode (not gallery mode)
            # If so, lock the splitter to the default single-column width
            if not hasattr(self.parent, 'gallery_mode') or not self.parent.gallery_mode:
                # Single-image mode: lock to default width
                self.set_splitter_to_single_column(splitter)
                # Resize main image and reposition overlay
                if hasattr(self.parent, '_resize_main_image_and_reposition_overlay'):
                    self.parent._resize_main_image_and_reposition_overlay()
                return

            # Gallery mode: allow resizing with snapping to column widths
            # Get current sizes
            sizes = splitter.sizes()
            if len(sizes) != 2:
                return

            image_width = sizes[0]
            gallery_width = sizes[1]
            total_width = image_width + gallery_width

            # Calculate usable width for columns (subtract overhead for margins/scrollbar)
            usable_width = gallery_width - self.GALLERY_OVERHEAD

            # Calculate number of columns that fit in the usable space
            # Use floor to ensure we only count columns that fully fit
            num_columns = max(1, math.floor(usable_width / self.GALLERY_COLUMN_WIDTH))

            # Calculate the ideal gallery width for this number of columns
            # This ensures no extra space on the right
            snapped_gallery_width = (num_columns * self.GALLERY_COLUMN_WIDTH) + self.GALLERY_OVERHEAD

            # Apply minimum and maximum constraints
            min_gallery_width = self.GALLERY_COLUMN_WIDTH + self.GALLERY_OVERHEAD  # 1 column + overhead
            max_gallery_width = total_width - 400  # Minimum 400px for image

            snapped_gallery_width = max(min_gallery_width, min(snapped_gallery_width, max_gallery_width))
            snapped_image_width = total_width - snapped_gallery_width

            # Only update if changed significantly (avoid infinite loop)
            if abs(gallery_width - snapped_gallery_width) > 5:
                splitter.setSizes([snapped_image_width, snapped_gallery_width])

            # Update gallery widget geometry to match new aoiFrame size
            if gallery_widget:
                self.update_gallery_geometry(gallery_widget)

            # Save the position
            self.save_splitter_position(splitter)

            # Resize main image and reposition overlay when splitter moves
            if hasattr(self.parent, '_resize_main_image_and_reposition_overlay'):
                self.parent._resize_main_image_and_reposition_overlay()

        except Exception as e:
            self.logger.error(f"Error handling splitter movement: {e}")

    def setup_splitter_layout(self, splitter):
        """Configure splitter layout for gallery mode."""
        try:
            # Start in single-image mode, so disable handle initially
            splitter.setHandleWidth(0)  # Disabled in single-image mode
            # Set cursor to arrow to prevent drag cursor from appearing
            self._set_splitter_cursor(splitter, Qt.ArrowCursor)
            splitter.setChildrenCollapsible(False)

            # Set stretch factors (image expands, gallery stays preferred size)
            splitter.setStretchFactor(0, 1)
            splitter.setStretchFactor(1, 0)

            # Connect splitter moved signal for snapping behavior
            # We'll use a lambda to pass the splitter and gallery_widget
            def on_splitter_moved_handler(pos, index):
                gallery_widget = getattr(self.parent, 'gallery_widget', None)
                self.on_splitter_moved(pos, index, splitter, gallery_widget)

            splitter.splitterMoved.connect(on_splitter_moved_handler)

            # Load saved splitter position for single-image mode (default starting mode)
            if hasattr(self.parent, 'settings_service'):
                saved_position = self.parent.settings_service.get_setting('viewer/splitter_position_single', None)
                if saved_position:
                    try:
                        positions = [int(p) for p in str(saved_position).split(',')]
                        if len(positions) == 2:
                            splitter.setSizes(positions)
                            self.logger.debug(f"Restored single-image splitter position: {positions}")
                    except Exception as e:
                        self.logger.debug(f"Could not restore splitter position: {e}")
                else:
                    # Default to 1-column width for single-image mode
                    self.set_splitter_to_single_column(splitter)

        except Exception as e:
            self.logger.error(f"Error setting up splitter layout: {e}")

    def _restore_single_image_header(self):
        """Restore the single-image mode header title."""
        try:
            # Trigger update of AOI list to restore the header
            if (hasattr(self.parent, 'aoi_controller') and
                    hasattr(self.parent, 'current_image') and
                    hasattr(self.parent, 'images') and
                    self.parent.current_image < len(self.parent.images)):
                image = self.parent.images[self.parent.current_image]
                areas_of_interest = image.get('areas_of_interest', [])

                # Use the AOI controller's UI component to update the header
                if hasattr(self.parent.aoi_controller, 'ui_component'):
                    # Get filtered count for display
                    filtered_aois = self.parent.aoi_controller.filter_aois_with_indices(
                        list(enumerate(areas_of_interest)),
                        self.parent.current_image
                    )
                    total_count = len(areas_of_interest)
                    filtered_count = len(filtered_aois)

                    # Update the header using the AOI UI component's method
                    self.parent.aoi_controller.ui_component._update_count_label(filtered_count, total_count)
        except Exception as e:
            self.logger.debug(f"Error restoring single-image header: {e}")

    def toggle_gallery_mode(self):
        """Toggle between single-image and gallery view modes."""
        try:
            # Make sure gallery is set up - try to create it if it doesn't exist
            if not hasattr(self.parent, 'gallery_widget') or not self.parent.gallery_widget:
                # Ensure we're visible before creating widgets
                if not self.parent.isVisible():
                    self.logger.warning("Cannot create gallery widget - viewer not visible")
                    return

                gallery_widget = self.setup_gallery_mode_ui()

                # Check if it was created successfully
                if not gallery_widget:
                    self.logger.error("Failed to create gallery widget")
                    return

                self.parent.gallery_widget = gallery_widget
                if hasattr(self.parent, '_gallery_setup_pending'):
                    self.parent._gallery_setup_pending = False

            if not hasattr(self.parent, 'gallery_widget') or not self.parent.gallery_widget:
                self.logger.warning("Gallery widget not available")
                return

            # Save current position BEFORE toggling mode (so we know which mode we're leaving)
            was_in_gallery_mode = getattr(self.parent, 'gallery_mode', False)
            if was_in_gallery_mode and hasattr(self.parent, 'image_gallery_splitter'):
                # We're about to exit gallery mode, save the current gallery position
                self.save_splitter_position(self.parent.image_gallery_splitter)

            self.parent.gallery_mode = not self.parent.gallery_mode

            if self.parent.gallery_mode:
                # Switch to gallery view
                # Enable splitter handle for resizing
                if hasattr(self.parent, 'image_gallery_splitter'):
                    self.parent.image_gallery_splitter.setHandleWidth(4)
                    # Explicitly set resize cursor on the handle for gallery mode
                    try:
                        handle = self.parent.image_gallery_splitter.handle(1)
                        if handle:
                            # Set the resize cursor explicitly
                            handle.setCursor(Qt.SplitHCursor)  # Horizontal resize cursor
                    except Exception:
                        pass

                # Remove fixed width constraints - splitter handles sizing
                self.parent.aoiFrame.setMinimumWidth(250)  # Just ensure minimum
                self.parent.aoiFrame.setMaximumWidth(16777215)  # Remove max constraint

                # Restore saved gallery splitter position or set default to 4 columns
                if hasattr(self.parent, 'settings_service'):
                    saved_gallery_position = self.parent.settings_service.get_setting('viewer/splitter_position_gallery', None)
                    if saved_gallery_position:
                        try:
                            positions = [int(p) for p in str(saved_gallery_position).split(',')]
                            if len(positions) == 2:
                                # Temporarily disconnect splitter signal to avoid saving during restore
                                splitter = self.parent.image_gallery_splitter
                                splitter.blockSignals(True)
                                splitter.setSizes(positions)
                                splitter.blockSignals(False)
                                self.logger.debug(f"Restored gallery splitter position: {positions}")
                                # Force update of gallery geometry after restoring position
                                QApplication.processEvents()  # Ensure sizes are applied
                                self.update_gallery_geometry(self.parent.gallery_widget)
                                # Resize main image and reposition overlay
                                if hasattr(self.parent, '_resize_main_image_and_reposition_overlay'):
                                    self.parent._resize_main_image_and_reposition_overlay()
                        except Exception as e:
                            self.logger.debug(f"Could not restore gallery splitter position: {e}")
                    else:
                        # Default to 4 columns
                        total_width = sum(self.parent.image_gallery_splitter.sizes())
                        four_column_width = (4 * self.GALLERY_COLUMN_WIDTH) + self.GALLERY_OVERHEAD
                        image_width = total_width - four_column_width
                        splitter = self.parent.image_gallery_splitter
                        splitter.blockSignals(True)
                        splitter.setSizes([image_width, four_column_width])
                        splitter.blockSignals(False)
                        self.logger.debug(f"Set gallery to default 4 columns: [{image_width}, {four_column_width}]")
                        # Force update of gallery geometry
                        QApplication.processEvents()  # Ensure sizes are applied
                        self.update_gallery_geometry(self.parent.gallery_widget)
                        # Resize main image and reposition overlay
                        if hasattr(self.parent, '_resize_main_image_and_reposition_overlay'):
                            self.parent._resize_main_image_and_reposition_overlay()

                # Gallery widget fills the frame width
                frame_rect = self.parent.aoiFrame.rect()
                aoi_list_rect = self.parent.aoiListWidget.geometry()

                self.parent.gallery_widget.setGeometry(
                    5,  # Small margin
                    aoi_list_rect.y(),
                    frame_rect.width() - 10,
                    aoi_list_rect.height()
                )

                # Show gallery and raise it to front
                self.parent.gallery_widget.setVisible(True)
                self.parent.gallery_widget.show()
                self.parent.gallery_widget.raise_()
                
                # Give focus to gallery view so keyboard shortcuts work
                if self.ui_component and self.ui_component.gallery_view:
                    self.ui_component.gallery_view.setFocus()

                # Only sync if filters have changed
                if hasattr(self.parent, '_last_filter_sync'):
                    # Check if filters have changed since last sync
                    current_filters = (
                        self.parent.aoi_controller.filter_flagged_only,
                        self.parent.aoi_controller.filter_color_hue,
                        self.parent.aoi_controller.filter_color_range,
                        self.parent.aoi_controller.filter_area_min,
                        self.parent.aoi_controller.filter_area_max,
                        self.parent.aoi_controller.sort_method,
                        self.parent.aoi_controller.sort_color_hue
                    )
                    if current_filters != self.parent._last_filter_sync:
                        self.sync_filters_from_aoi_controller()
                        self.load_all_aois()
                        self.parent._last_filter_sync = current_filters
                else:
                    # First time - do sync
                    self.sync_filters_from_aoi_controller()
                    self.load_all_aois()
                    self.parent._last_filter_sync = (
                        self.parent.aoi_controller.filter_flagged_only,
                        self.parent.aoi_controller.filter_color_hue,
                        self.parent.aoi_controller.filter_color_range,
                        self.parent.aoi_controller.filter_area_min,
                        self.parent.aoi_controller.filter_area_max,
                        self.parent.aoi_controller.sort_method,
                        self.parent.aoi_controller.sort_color_hue
                    )

                # Ensure thumbnail loading is triggered after everything is set up
                # The model signals are already connected in set_model, so just trigger if model has data
                if self.ui_component and self.model:
                    # If model already has data, trigger thumbnail loading
                    if self.model.rowCount() > 0:
                        self.ui_component._load_visible_thumbnails()

                # Update header immediately if gallery model already has data (for subsequent opens)
                # The model signals are already connected in set_model via _on_model_changed
                if (self.model and self.model.rowCount() > 0 and
                        hasattr(self.parent, 'gallery_mode') and
                        self.parent.gallery_mode):
                    self.ui_component._update_count_label(self.model.rowCount())

                self.logger.info("Switched to gallery view mode")

            else:
                # Switch to single-image view
                # Disable splitter handle to prevent dragging
                if hasattr(self.parent, 'image_gallery_splitter'):
                    self.parent.image_gallery_splitter.setHandleWidth(0)  # Disable handle
                    # Set cursor to arrow to prevent drag cursor from appearing
                    self._set_splitter_cursor(self.parent.image_gallery_splitter, Qt.ArrowCursor)
                    self.set_splitter_to_single_column(self.parent.image_gallery_splitter)
                    # Resize main image and reposition overlay
                    if hasattr(self.parent, '_resize_main_image_and_reposition_overlay'):
                        self.parent._resize_main_image_and_reposition_overlay()

                # Reset to reasonable single-column width
                self.parent.aoiFrame.setMinimumWidth(250)
                self.parent.aoiFrame.setMaximumWidth(400)  # Reasonable max for single column

                # Raise single-image list to front, keep gallery in background
                self.parent.aoiListWidget.raise_()

                # Don't destroy gallery widget - keep it cached for fast switching
                # Just hide it
                self.parent.gallery_widget.hide()

                # Restore single-image mode header title
                self._restore_single_image_header()
                
                # Refresh AOI display to show any flag changes made in gallery mode
                if hasattr(self.parent, 'aoi_controller') and self.parent.aoi_controller.ui_component:
                    self.parent.aoi_controller.ui_component.refresh_aoi_display()

                self.logger.info("Switched to single-image view mode")

        except Exception as e:
            self.logger.error(f"Error toggling gallery mode: {e}")
            self.logger.error(traceback.format_exc())
