"""
ImageLoadController - Handles image loading and display logic.

Manages image loading, augmentation, metadata extraction, and view state preservation.
"""

import os
import traceback
import qimage2ndarray
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QMessageBox, QApplication

from core.services.LoggerService import LoggerService
from core.services.ImageService import ImageService
from core.services.ImageHighlightService import ImageHighlightService
from helpers.LocationInfo import LocationInfo


class ImageLoadController:
    """
    Controller for loading and displaying images with metadata.
    
    Handles image loading, augmentation (AOI circles, pixel highlighting),
    metadata extraction, and preserving zoom/pan state during reloads.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the image load controller.
        
        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()

    def load_image(self):
        """Load the image at the current index along with areas of interest and GPS data."""
        try:
            # Prevent race conditions by checking if main_image is still valid
            if not hasattr(self.parent, 'main_image') or self.parent.main_image is None or self.parent.main_image._is_destroyed:
                return

            # Clear previous status
            self.parent.messages['GPS Coordinates'] = self.parent.messages['Relative Altitude'] = self.parent.messages['Gimbal Orientation'] = None
            self.parent.messages['Estimated Average GSD'] = self.parent.messages['Temperature'] = None

            # Hide magnifying glass when loading new image
            if hasattr(self.parent, 'magnifying_glass'):
                self.parent.magnifying_glass._hide()
                # Update the enabled flag and button styling
                self.parent.magnifying_glass_enabled = self.parent.magnifying_glass.is_enabled()
                if hasattr(self.parent, 'ui_style_controller'):
                    self.parent.ui_style_controller.update_magnify_button_style()

            image = self.parent.images[self.parent.current_image]

            # Always sync the active thumbnail/index
            self._sync_thumbnail_state(image)

            # Update GPS map if it's open
            self.parent.gps_map_controller.update_current_image(self.parent.current_image)

            # Load image service
            image_path = image.get('path', '')
            mask_path = image.get('mask_path', '')
            calculated_bearing = image.get('bearing', None)  # Get calculated bearing if available

            # Check if file exists
            if not os.path.exists(image_path):
                self.logger.error(f"Image file does not exist: {image_path}")
                return

            try:
                image_service = ImageService(image_path, mask_path, calculated_bearing=calculated_bearing)
            except Exception:
                raise

            # Store reference to ImageService for later use
            self.parent.current_image_service = image_service

            # Cache the image array
            self._cache_image_array(image_service)

            # Apply image augmentations (circles, highlights)
            augmented_image = self._apply_augmentations(image_service, image, mask_path)

            # Convert to QImage
            img = QImage(qimage2ndarray.array2qimage(augmented_image))

            # Critical section: check if widget is still valid before setting image
            if not hasattr(self.parent, 'main_image') or self.parent.main_image is None or self.parent.main_image._is_destroyed:
                return

            self.parent.main_image.setImage(img)
            self.parent.fileNameLabel.setText(image['name'])

            # Load AOIs
            self.parent.aoi_controller.load_areas_of_interest(image_service.img_array, image['areas_of_interest'])

            # Notify gallery controller that image has loaded (for thumbnail generation)
            if hasattr(self.parent, 'gallery_controller'):
                self.parent.gallery_controller.on_image_loaded(self.parent.current_image)

            # Reset zoom
            self._reset_zoom_if_valid()

            self.parent.main_image.setFocus()
            self.parent.hideImageToggle.setChecked(image['hidden'])
            self.parent.indexLabel.setText(f"(Image {self.parent.current_image + 1} of {len(self.parent.images)})")

            # Update metadata displays
            self._update_metadata_displays(image_service)

            # Update overlay
            self._update_overlay(image_service)

        except Exception as e:
            self._handle_load_error(e, image)

    def reload_image_preserving_view(self):
        """
        Reload the current image while preserving zoom and pan state.
        
        Respects both the draw AOI circle and highlight pixels toggles.
        """
        if not hasattr(self.parent, 'main_image') or self.parent.main_image is None:
            return

        # Save the current zoom stack and viewport to preserve state
        saved_zoom_stack = self.parent.main_image.zoomStack.copy() if self.parent.main_image.zoomStack else []
        saved_transform = self.parent.main_image.transform()

        # Save AOI list scroll position
        aoi_scroll_pos = self.parent.aoiListWidget.verticalScrollBar().value() if hasattr(self.parent, 'aoiListWidget') else 0

        # Reload just the image content without resetting view
        image = self.parent.images[self.parent.current_image]
        image_path = image.get('path', '')
        mask_path = image.get('mask_path', '')
        calculated_bearing = image.get('bearing', None)  # Get calculated bearing if available

        # Load and process the image
        image_service = ImageService(image_path, mask_path, calculated_bearing=calculated_bearing)

        # Update the cached image array
        self.parent.current_image_service = image_service
        self.parent.current_image_array = image_service.img_array

        # Apply augmentations
        augmented_image = self._apply_augmentations(image_service, image, mask_path)

        # Update the image without resetting the view
        img = QImage(qimage2ndarray.array2qimage(augmented_image))

        # Temporarily block zoom stack updates
        self.parent.main_image.zoomStack = saved_zoom_stack

        # Set the new image
        self.parent.main_image.setImage(img)

        # Restore the transform exactly
        self.parent.main_image.setTransform(saved_transform)

        # Restore zoom stack
        self.parent.main_image.zoomStack = saved_zoom_stack

        # Force emit zoom to update any UI elements
        self.parent.main_image._emit_zoom_if_changed()

        # Restore AOI list scroll position
        if hasattr(self.parent, 'aoiListWidget') and aoi_scroll_pos > 0:
            self.parent.aoiListWidget.verticalScrollBar().setValue(aoi_scroll_pos)

    def _sync_thumbnail_state(self, image):
        """Sync the active thumbnail state."""
        if 'thumbnail' in image:
            if hasattr(self.parent.thumbnail_controller, 'ui_component') and self.parent.thumbnail_controller.ui_component:
                self.parent.thumbnail_controller.ui_component.set_active_thumbnail(image['thumbnail'])
        else:
            self.parent.thumbnail_controller.set_active_index(self.parent.current_image)

    def _cache_image_array(self, image_service):
        """Cache the image array for pixel value display."""
        has_img_array = hasattr(image_service, 'img_array')

        if has_img_array:
            try:
                img_arr = image_service.img_array
                if img_arr is not None:
                    self.parent.current_image_array = img_arr
                else:
                    self.parent.current_image_array = None
            except Exception:
                self.parent.current_image_array = None
        else:
            self.parent.current_image_array = None

    def _apply_augmentations(self, image_service, image, mask_path):
        """
        Apply image augmentations (circles, highlights).
        
        Args:
            image_service: ImageService instance
            image: Image dictionary
            mask_path: Path to mask file
            
        Returns:
            np.ndarray: Augmented image array
        """
        # Draw AOI boundaries (circles or contours) if button is enabled
        if hasattr(self.parent, 'showAOIsButton') and self.parent.showAOIsButton.isChecked():
            augmented_image = image_service.circle_areas_of_interest(
                self.parent.settings['identifier_color'],
                image['areas_of_interest']
            )
        else:
            # Use reference instead of copy to avoid crash
            augmented_image = image_service.img_array

        # Highlight pixels of interest if button is enabled
        if hasattr(self.parent, 'showPOIsButton') and self.parent.showPOIsButton.isChecked():
            if mask_path:
                # Use mask-based highlighting (new efficient approach)
                augmented_image = ImageHighlightService.apply_mask_highlight(
                    augmented_image,
                    mask_path,
                    self.parent.settings['identifier_color'],
                    image['areas_of_interest']
                )
            else:
                # Fall back to old method for backward compatibility
                augmented_image = ImageHighlightService.highlight_aoi_pixels(
                    augmented_image,
                    image['areas_of_interest']
                )

        return augmented_image

    def _reset_zoom_if_valid(self):
        """Reset zoom if main_image is valid."""
        if not hasattr(self.parent, 'main_image') or self.parent.main_image is None or getattr(self.parent.main_image, '_is_destroyed', True):
            return

        # Ensure the image is properly loaded before resetting zoom
        if not self.parent.main_image.hasImage():
            return

        # Guard resetZoom against deleted C++ object
        try:
            self.parent.main_image.resetZoom()
        except RuntimeError:
            return

    def _update_metadata_displays(self, image_service):
        """Update metadata displays in status bar."""
        # Altitude
        altitude = image_service.get_relative_altitude(self.parent.distance_unit)
        if altitude:
            self.parent.messages['Relative Altitude'] = f"{altitude} {self.parent.distance_unit}"

            # Check for negative altitude and prompt for custom AGL
            if altitude < 0 and hasattr(self.parent, 'altitude_controller'):
                if self.parent.altitude_controller.custom_agl_altitude_ft is None:
                    self.parent.altitude_controller.prompt_for_custom_altitude(auto_triggered=True)

        # Gimbal orientation
        direction = image_service.get_camera_yaw()
        if direction is not None:
            self.parent.messages['Gimbal Orientation'] = f"{direction}°"
        else:
            self.parent.messages['Gimbal Orientation'] = None

        # GSD with custom altitude if available
        custom_alt = None
        if hasattr(self.parent, 'altitude_controller'):
            custom_alt = self.parent.altitude_controller.get_effective_altitude()
        avg_gsd = image_service.get_average_gsd(custom_altitude_ft=custom_alt)
        if avg_gsd is not None:
            self.parent.messages['Estimated Average GSD'] = f"{avg_gsd}cm/px"
        else:
            self.parent.messages['Estimated Average GSD'] = None

        # GPS position
        position = image_service.get_position(self.parent.position_format)
        if position:
            self.parent.messages['GPS Coordinates'] = position

        # Update coordinate controller
        try:
            gps = LocationInfo.get_gps(exif_data=image_service.exif_data)
            if gps and 'latitude' in gps and 'longitude' in gps:
                self.parent.coordinate_controller.update_current_coordinates((gps['latitude'], gps['longitude']))
            else:
                self.parent.coordinate_controller.update_current_coordinates(None)
        except Exception:
            self.parent.coordinate_controller.update_current_coordinates(None)

        # Thermal data
        if self.parent.is_thermal and hasattr(self.parent, 'thermal_controller'):
            image = self.parent.images[self.parent.current_image]
            image_path = image.get('path', '')
            self.parent.thermal_controller.load_thermal_data(
                image_service,
                image_path,
                self.parent.temperature_unit
            )

    def _update_overlay(self, image_service):
        """Update overlay with new image data."""
        direction = image_service.get_camera_yaw()
        
        # Get custom altitude if available
        custom_alt = None
        if hasattr(self.parent, 'altitude_controller'):
            custom_alt = self.parent.altitude_controller.get_effective_altitude()
        avg_gsd = image_service.get_average_gsd(custom_altitude_ft=custom_alt)

        # Update overlay with new image data - AFTER zoom reset so scene is properly set up
        if hasattr(self.parent, 'overlay'):
            self.parent.overlay.rotate_north_icon(direction)
            self.parent.overlay.update_visibility(
                self.parent.showOverlayToggle.isChecked() if hasattr(self.parent, 'showOverlayToggle') else True,
                direction,
                avg_gsd
            )
            # Position the overlay after image is loaded and zoomed
            self.parent.overlay._place_overlay()

    def _handle_load_error(self, e, image):
        """Handle image loading errors."""
        error_msg = f"Error loading image {self.parent.current_image + 1}: {str(e)}"
        self.logger.error(error_msg)
        self.logger.error(f"Traceback:\n{traceback.format_exc()}")
        print(f"\n{'='*60}")
        print("ERROR IN VIEWER - load_image()")
        print(f"Image index: {self.parent.current_image}")
        if image:
            print(f"Image path: {image.get('path', 'N/A')}")
            print(f"Mask path: {image.get('mask_path', 'N/A')}")
        print(f"Error: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        print(f"{'='*60}\n")
        # Show error to user
        QMessageBox.critical(self.parent, "Error Loading Image", error_msg)

