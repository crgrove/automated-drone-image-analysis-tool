"""
AOIController - Handles Areas of Interest (AOI) business logic for the image viewer.

This controller manages AOI data, selection, flagging, filtering, and business logic.
UI manipulation is handled by AOIUIComponent.
"""

import colorsys
import numpy as np
import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidgetItem, QPushButton, QMenu, QApplication, QAbstractItemView, QColorDialog
try:
    from shiboken6 import isValid as _qt_is_valid
except Exception:
    def _qt_is_valid(obj):
        try:
            _ = obj.metaObject()
            return True
        except Exception:
            return False
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QCursor, QColor

from core.services.LoggerService import LoggerService
from core.services.AOIService import AOIService

class AOIController:
    """
    Controller for managing Areas of Interest (AOI) business logic.

    Handles AOI data management, selection, flagging, filtering, and business logic.
    UI manipulation is delegated to AOIUIComponent.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the AOI controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()  # Create our own logger

        # AOI state
        self.selected_aoi_index = -1
        self.flagged_aois = {}
        self.filter_flagged_only = False

        # Sort and filter state
        self.sort_method = None  # 'area_asc', 'area_desc', 'color', 'x', 'y', 'temperature_asc', 'temperature_desc'
        self.sort_color_hue = None  # Hue value (0-360) for color-based sorting
        self.filter_color_hue = None  # Hue value (0-360) for color filtering
        self.filter_color_range = None  # ± degrees for color filtering
        self.filter_area_min = None  # Minimum pixel area for filtering
        self.filter_area_max = None  # Maximum pixel area for filtering
        self.filter_comment_pattern = None  # Wildcard pattern for comment filtering
        self.filter_temperature_min = None  # Minimum temperature (Celsius) for filtering
        self.filter_temperature_max = None  # Maximum temperature (Celsius) for filtering

        # Cache for AOIService to avoid recreating for same image
        self._cached_aoi_service = None
        self._cached_image_index = None

        # Create UI component internally
        from core.controllers.viewer.aoi.AOIUIComponent import AOIUIComponent
        self.ui_component = AOIUIComponent(self)
        
        # Initialize sort combo box
        self._initialize_sort_combo()

    def _get_aoi_service(self):
        """
        Get or create a cached AOIService for the current image.
        
        Returns:
            AOIService instance for the current image, or None if no image is loaded
        """
        try:
            current_image_idx = self.parent.current_image
            
            # Check if we can use cached service
            if (self._cached_aoi_service is not None and 
                self._cached_image_index == current_image_idx):
                return self._cached_aoi_service
            
            # Create new service for current image
            if current_image_idx < len(self.parent.images):
                image = self.parent.images[current_image_idx]
                self._cached_aoi_service = AOIService(image)
                self._cached_image_index = current_image_idx
                return self._cached_aoi_service
            
            return None
        except Exception as e:
            self.logger.error(f"Error getting AOIService: {e}")
            return None

    def refresh_sort_combo(self):
        """Refresh the sort combo box options (e.g., after thermal data is loaded)."""
        self._initialize_sort_combo()

    def initialize_from_xml(self, images):
        """Load flagged AOI information from XML data.

        Args:
            images: List of image data dictionaries
        """
        self.flagged_aois = {}
        if images:
            for img_idx, image in enumerate(images):
                if 'areas_of_interest' in image:
                    for aoi_idx, aoi in enumerate(image['areas_of_interest']):
                        # Check if this AOI is flagged in the XML data
                        flagged = aoi.get('flagged', False)
                        if flagged:
                            if img_idx not in self.flagged_aois:
                                self.flagged_aois[img_idx] = set()
                            self.flagged_aois[img_idx].add(aoi_idx)



    def calculate_aoi_average_info(self, area_of_interest, is_thermal, temperature_data, temperature_unit):
        """Calculate average color or temperature for an AOI.

        Args:
            area_of_interest (dict): AOI dictionary with center, radius, and optionally detected_pixels
            is_thermal (bool): Whether this is a thermal image
            temperature_data: Temperature data array for thermal images
            temperature_unit (str): Temperature unit ('F' or 'C')

        Returns:
            tuple: (info_text, rgb_tuple) where info_text is the formatted string and
                   rgb_tuple is (r, g, b) for colors or None for temperature
        """
        try:
            # For thermal images, calculate average temperature
            if is_thermal:
                # First check if AOI has cached temperature (from analysis)
                if 'temperature' in area_of_interest and area_of_interest['temperature'] is not None:
                    temp_c = area_of_interest['temperature']
                    # Convert to user's preferred unit
                    if temperature_unit == 'F':
                        temp_display = (temp_c * 1.8) + 32.0
                        return f"Temp: {temp_display:.1f}°F", None
                    else:
                        return f"Temp: {temp_c:.1f}°C", None

                # Fall back to calculating from temperature_data array if available
                if temperature_data is None:
                    return "Temp: N/A", None

                center = area_of_interest['center']
                radius = area_of_interest.get('radius', 0)
                cx, cy = center
                shape = temperature_data.shape

                # Get temperature values for detected pixels or within the AOI circle
                temps = []

                # If we have detected pixels, use those for temperature
                if 'detected_pixels' in area_of_interest and area_of_interest['detected_pixels']:
                    for pixel in area_of_interest['detected_pixels']:
                        if isinstance(pixel, (list, tuple)) and len(pixel) >= 2:
                            px, py = int(pixel[0]), int(pixel[1])
                            if 0 <= py < shape[0] and 0 <= px < shape[1]:
                                temps.append(temperature_data[py][px])
                # Otherwise sample temperatures within the circle
                else:
                    for y in range(max(0, cy - radius), min(shape[0], cy + radius + 1)):
                        for x in range(max(0, cx - radius), min(shape[1], cx + radius + 1)):
                            # Check if pixel is within circle
                            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                                temps.append(temperature_data[y][x])

                if temps:
                    avg_temp = sum(temps) / len(temps)
                    return f"Avg Temp: {avg_temp:.1f}° {temperature_unit}", None
                else:
                    return None, None

            # For non-thermal images, calculate average color
            else:
                # Use cached AOIService for current image
                aoi_service = self._get_aoi_service()
                if not aoi_service:
                    return None, None
                
                color_result = aoi_service.get_aoi_representative_color(area_of_interest)
                if color_result:
                    # Return hue angle, hex color, and RGB tuple for the color square
                    hex_color = color_result['hex']
                    hue_degrees = color_result['hue_degrees']
                    full_sat_rgb = color_result['rgb']
                    return f"Hue: {hue_degrees}° {hex_color}", full_sat_rgb

        except Exception as e:
            self.logger.error(f"Error calculating AOI average info: {e}")
            return None, None

        return None, None

    def load_areas_of_interest(self, augmented_image, areas_of_interest):
        """Load areas of interest thumbnails for a given image (delegated to UI component).

        Args:
            augmented_image: The image array to create thumbnails from
            areas_of_interest: List of AOI dictionaries
        """
        if self.ui_component:
            self.ui_component.load_areas_of_interest(augmented_image, areas_of_interest)

    def area_of_interest_click(self, x, y, img):
        """Handles clicks on area of interest thumbnails.

        Args:
            x (int): X coordinate of the cursor.
            y (int): Y coordinate of the cursor.
            img (QtImageViewer): The clicked thumbnail image viewer.
        """
        self.parent.main_image.zoomToArea(img.center, 6)

    def select_aoi(self, aoi_index, visible_index):
        """Select an AOI and update the visual selection.

        Args:
            aoi_index (int): Index of the AOI in the full list (-1 to deselect)
            visible_index (int): Index of the AOI in the visible containers list
        """
        # Set new selection (business logic)
        self.selected_aoi_index = aoi_index

        # Delegate UI updates to UI component
        if self.ui_component:
            # Clear ALL container styles first
            for i, container in enumerate(self.ui_component.get_aoi_containers()):
                self.ui_component.update_aoi_selection_style(container, False)

            # Apply selection style to the clicked container
            if aoi_index >= 0 and visible_index >= 0 and visible_index < len(self.ui_component.get_aoi_containers()):
                container = self.ui_component.get_aoi_containers()[visible_index]
                self.ui_component.update_aoi_selection_style(container, True)
                container.update()
                container.repaint()

                # Scroll the AOI list to bring the selected item into view
                self.ui_component.scroll_to_aoi(visible_index)

        # Update AOI on GPS map if available
        if hasattr(self.parent, 'gps_map_controller') and self.parent.gps_map_controller:
            self.parent.gps_map_controller.update_aoi_on_map()

        # Sync selection to gallery (if it exists)
        if hasattr(self.parent, 'gallery_controller'):
            # Only sync if actually in gallery mode to avoid unnecessary work
            if hasattr(self.parent, 'gallery_mode') and self.parent.gallery_mode:
                self.parent.gallery_controller.sync_selection_from_aoi_controller(
                    self.parent.current_image, aoi_index
                )


    def find_aoi_at_position(self, x, y):
        """Find the AOI at the given cursor position.

        Args:
            x (int): X coordinate in image space
            y (int): Y coordinate in image space

        Returns:
            tuple: (aoi_index, visible_index) if found, (-1, -1) otherwise
        """
        # Return if cursor is outside the image
        if x < 0 or y < 0:
            return (-1, -1)

        # Get current image and its AOIs
        if not hasattr(self.parent, 'images') or not hasattr(self.parent, 'current_image'):
            return (-1, -1)

        image = self.parent.images[self.parent.current_image]
        if 'areas_of_interest' not in image:
            return (-1, -1)

        areas_of_interest = image['areas_of_interest']

        # Get flagged AOIs for filtering
        img_idx = self.parent.current_image
        flagged_set = self.flagged_aois.get(img_idx, set())

        # Track visible index (accounting for filtering)
        visible_index = 0

        # Check each AOI to see if cursor is within it
        for aoi_index, aoi in enumerate(areas_of_interest):
            # Skip if we're filtering and this AOI is not flagged
            if self.filter_flagged_only and aoi_index not in flagged_set:
                continue

            # Get AOI center and radius
            center = aoi['center']
            radius = aoi.get('radius', 0)

            # Check if cursor is within the AOI circle
            cx, cy = center
            distance_squared = (x - cx) ** 2 + (y - cy) ** 2
            if distance_squared <= radius ** 2:
                return (aoi_index, visible_index)

            visible_index += 1

        return (-1, -1)

    def save_flagged_aoi_to_xml(self, image_index, aoi_index, is_flagged):
        """Save the flagged status of an AOI to XML.

        Args:
            image_index (int): Index of the image
            aoi_index (int): Index of the AOI within the image
            is_flagged (bool): Whether the AOI is flagged
        """
        if hasattr(self.parent, 'images') and 0 <= image_index < len(self.parent.images):
            image = self.parent.images[image_index]
            if 'areas_of_interest' in image and 0 <= aoi_index < len(image['areas_of_interest']):
                aoi = image['areas_of_interest'][aoi_index]
                aoi['flagged'] = is_flagged

                # Update the XML element if it exists
                if 'xml' in aoi and aoi['xml'] is not None:
                    aoi['xml'].set('flagged', str(is_flagged))
                    # Save the XML file using the xml_service method
                    if hasattr(self.parent, 'xml_service') and self.parent.xml_service:
                        try:
                            # Use the xml_service save method
                            self.parent.xml_service.save_xml_file(self.parent.xml_path)
                        except Exception:
                            pass
                    else:
                        pass
                else:
                    pass

    def save_aoi_comment_to_xml(self, image_index, aoi_index, comment):
        """Save a user comment for an AOI to XML.

        Args:
            image_index (int): Index of the image
            aoi_index (int): Index of the AOI within the image
            comment (str): The user comment text
        """
        if hasattr(self.parent, 'images') and 0 <= image_index < len(self.parent.images):
            image = self.parent.images[image_index]
            if 'areas_of_interest' in image and 0 <= aoi_index < len(image['areas_of_interest']):
                aoi = image['areas_of_interest'][aoi_index]
                aoi['user_comment'] = comment

                # Update the XML element if it exists
                if 'xml' in aoi and aoi['xml'] is not None:
                    if comment:
                        aoi['xml'].set('user_comment', str(comment))
                    else:
                        # Remove attribute if comment is empty
                        if 'user_comment' in aoi['xml'].attrib:
                            del aoi['xml'].attrib['user_comment']

                    # Save the XML file using the xml_service method
                    if hasattr(self.parent, 'xml_service') and self.parent.xml_service:
                        try:
                            self.parent.xml_service.save_xml_file(self.parent.xml_path)
                        except Exception:
                            pass

    def edit_aoi_comment(self, aoi_index):
        """Open dialog to edit the comment for an AOI.

        Args:
            aoi_index (int): Index of the AOI to edit comment for
        """
        if aoi_index < 0:
            return

        # Get current image and AOI
        image = self.parent.images[self.parent.current_image]
        if 'areas_of_interest' not in image or aoi_index >= len(image['areas_of_interest']):
            return

        aoi = image['areas_of_interest'][aoi_index]
        current_comment = aoi.get('user_comment', '')

        # Open comment dialog
        from core.views.viewer.dialogs.AOICommentDialog import AOICommentDialog
        dialog = AOICommentDialog(self.parent, current_comment)

        if dialog.exec():
            # User clicked OK - save the comment
            new_comment = dialog.get_comment()
            self.save_aoi_comment_to_xml(self.parent.current_image, aoi_index, new_comment)

            # Refresh the AOI display to update the icon (UI component handles this)
            if self.ui_component:
                self.ui_component.refresh_aoi_display()

            # Show confirmation toast
            if hasattr(self.parent, 'status_controller'):
                if new_comment:
                    self.parent.status_controller.show_toast("Comment saved", 2000, color="#00C853")
                else:
                    self.parent.status_controller.show_toast("Comment cleared", 2000, color="#808080")

    def toggle_aoi_flag(self):
        """Toggle the flag status of the currently selected AOI."""
        if self.selected_aoi_index < 0:
            return
        # Delegate to index-based toggle (suppresses comment dialog)
        self.toggle_aoi_flag_by_index(self.selected_aoi_index)

    def toggle_aoi_flag_by_index(self, aoi_index):
        """Toggle the flag status of the specified AOI without launching dialogs.

        Args:
            aoi_index (int): Index of the AOI to toggle
        """
        if aoi_index is None or aoi_index < 0:
            return

        # Get or create flagged set for current image
        if self.parent.current_image not in self.flagged_aois:
            self.flagged_aois[self.parent.current_image] = set()

        flagged_set = self.flagged_aois[self.parent.current_image]

        # Toggle flag status
        is_now_flagged = aoi_index not in flagged_set
        if is_now_flagged:
            flagged_set.add(aoi_index)
        else:
            flagged_set.remove(aoi_index)

        # Save to XML
        self.save_flagged_aoi_to_xml(self.parent.current_image, aoi_index, is_now_flagged)

        # Refresh the AOI display to show/hide flag icon (UI component handles this)
        if self.ui_component:
            self.ui_component.refresh_aoi_display()
        
        # Update GPS map if it's open to reflect flagged status change
        if hasattr(self.parent, 'gps_map_controller') and self.parent.gps_map_controller.map_dialog:
            if self.parent.gps_map_controller.map_dialog.isVisible():
                # Re-extract GPS data to update has_flagged status
                self.parent.gps_map_controller.extract_gps_data()
                # Find the current image index in GPS data
                current_gps_index = None
                for i, data in enumerate(self.parent.gps_map_controller.gps_data):
                    if data['index'] == self.parent.current_image:
                        current_gps_index = i
                        break
                # Update the map with refreshed data
                if current_gps_index is not None:
                    self.parent.gps_map_controller.map_dialog.update_gps_data(
                        self.parent.gps_map_controller.gps_data, 
                        current_gps_index
                    )

    def show_aoi_context_menu(self, pos, label_widget, center, pixel_area, avg_info=None, aoi_index=None):
        """Show context menu for AOI coordinate label with copy option.

        Args:
            pos: Position where the context menu was requested (relative to label_widget)
            label_widget: The QLabel widget that was right-clicked
            center: Tuple of (x, y) coordinates of the AOI center
            pixel_area: The area of the AOI in pixels
            avg_info: Average color/temperature information string
            aoi_index: Index of the AOI
        """
        menu = QMenu(label_widget)

        # Style the menu to match the application theme
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                color: white;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
        """)

        # Add copy action
        copy_action = menu.addAction("Copy Data")
        copy_action.triggered.connect(lambda: self.copy_aoi_data(center, pixel_area, avg_info, aoi_index))

        # Get the current cursor position (global coordinates)
        global_pos = QCursor.pos()

        # Show menu at cursor position
        menu.exec(global_pos)

    def copy_aoi_data(self, center, pixel_area, avg_info=None, aoi_index=None):
        """Copy AOI data to clipboard including image name, coordinates, and GPS.

        Args:
            center: Tuple of (x, y) coordinates of the AOI center
            pixel_area: The area of the AOI in pixels
            avg_info: Average color/temperature information string
            aoi_index: Index of the AOI
        """
        # Get current image information
        image = self.parent.images[self.parent.current_image]
        image_name = image.get('name', 'Unknown')

        # Get image GPS coordinates if available
        image_gps_coords = self.parent.messages.get('GPS Coordinates', 'N/A')

        # Get user comment if available
        user_comment = ""
        if aoi_index is not None and 'areas_of_interest' in image:
            if aoi_index < len(image['areas_of_interest']):
                aoi = image['areas_of_interest'][aoi_index]
                user_comment = aoi.get('user_comment', '')

        # Calculate AOI GPS coordinates
        aoi_gps_coords = self.calculate_aoi_gps(aoi_index)

        # Format the data for clipboard
        clipboard_text = f"Image: {image_name}\n"

        # Add user comment if present
        if user_comment:
            clipboard_text += f"User Comment: {user_comment}\n"

        clipboard_text += (
            f"AOI Coordinates: X={center[0]}, Y={center[1]}\n"
            f"AOI Area: {pixel_area:.0f} px\n"
        )

        # Add average info if available
        if avg_info:
            clipboard_text += f"Average: {avg_info}\n"

        clipboard_text += f"Image GPS Coordinates: {image_gps_coords}\n"
        clipboard_text += f"AOI GPS Coordinates: {aoi_gps_coords}"

        # Copy to clipboard
        QApplication.clipboard().setText(clipboard_text)

        # Show confirmation toast
        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast("AOI data copied", 2000, color="#00C853")

    def calculate_aoi_gps(self, aoi_index):
        """Calculate GPS coordinates for a specific AOI.

        Args:
            aoi_index: Index of the AOI

        Returns:
            String with formatted GPS coordinates or "N/A" if calculation fails
        """
        try:
            if aoi_index is None or aoi_index < 0:
                return "N/A"

            # Get current image and AOI
            image = self.parent.images[self.parent.current_image]
            if 'areas_of_interest' not in image or aoi_index >= len(image['areas_of_interest']):
                return "N/A"

            aoi = image['areas_of_interest'][aoi_index]

            # Use AOIService for GPS calculation
            from core.services.AOIService import AOIService
            aoi_service = AOIService(image)

            # Get custom altitude if available
            custom_alt_ft = None
            if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                custom_alt_ft = self.parent.custom_agl_altitude_ft

            # Calculate AOI GPS coordinates using the convenience method
            result = aoi_service.calculate_gps_with_custom_altitude(image, aoi, custom_alt_ft)

            if result:
                lat, lon = result

                # Get position format preference
                position_format = getattr(self.parent, 'position_format', 'Decimal Degrees')

                # Use LocationInfo for formatting
                from helpers.LocationInfo import LocationInfo
                return LocationInfo.format_coordinates(lat, lon, position_format)

            return "N/A"

        except Exception as e:
            self.logger.error(f"Error calculating AOI GPS: {e}")
            return "N/A"

    def calculate_hue_distance(self, hue1, hue2):
        """Calculate the circular distance between two hue values.

        Args:
            hue1: First hue value (0-360)
            hue2: Second hue value (0-360)

        Returns:
            float: Shortest distance between hues (0-180)
        """
        # Calculate both directions around the color wheel
        direct = abs(hue1 - hue2)
        around = 360 - direct
        # Return the shorter distance
        return min(direct, around)

    def get_aoi_hue(self, aoi):
        """Get the hue value for an AOI.

        Args:
            aoi: AOI dictionary

        Returns:
            int: Hue value (0-360) or None if cannot be calculated
        """
        try:
            # Only works for non-thermal images
            if self.parent.is_thermal:
                return None
            
            # Use cached AOIService for current image
            aoi_service = self._get_aoi_service()
            if not aoi_service:
                return None
            
            color_result = aoi_service.get_aoi_representative_color(aoi)
            
            if color_result:
                return color_result['hue_degrees']
            
            return None
        except Exception as e:
            self.logger.error(f"Error getting AOI hue: {e}")
            return None

    def sort_aois_with_indices(self, areas_of_interest):
        """Sort AOIs based on current sort method, preserving original indices.

        Args:
            areas_of_interest: List of AOI dictionaries

        Returns:
            list: List of tuples (aoi, original_index) sorted by current method
        """
        # Create list of (aoi, index) tuples
        aois_with_indices = list(enumerate(areas_of_interest))

        if self.sort_method is None:
            # No sorting, return as-is
            return aois_with_indices

        try:
            if self.sort_method == 'area_asc':
                # Sort by pixel area, smallest first
                aois_with_indices.sort(key=lambda x: x[1].get('area', 0))

            elif self.sort_method == 'area_desc':
                # Sort by pixel area, largest first
                aois_with_indices.sort(key=lambda x: x[1].get('area', 0), reverse=True)

            elif self.sort_method == 'confidence_asc':
                # Sort by confidence, lowest first
                # Put AOIs without confidence at the end
                aois_with_indices.sort(key=lambda x: x[1].get('confidence', -1))

            elif self.sort_method == 'confidence_desc':
                # Sort by confidence, highest first
                # Put AOIs without confidence at the end
                aois_with_indices.sort(key=lambda x: x[1].get('confidence', -1), reverse=True)

            elif self.sort_method == 'color':
                # Sort by hue distance from target color
                if self.sort_color_hue is not None:
                    def color_sort_key(item):
                        idx, aoi = item
                        hue = self.get_aoi_hue(aoi)
                        if hue is None:
                            return 999999  # Put items without hue at the end
                        return self.calculate_hue_distance(hue, self.sort_color_hue)

                    aois_with_indices.sort(key=color_sort_key)

            elif self.sort_method == 'x':
                # Sort by X coordinate, smallest first
                aois_with_indices.sort(key=lambda x: x[1]['center'][0])

            elif self.sort_method == 'y':
                # Sort by Y coordinate, smallest first
                aois_with_indices.sort(key=lambda x: x[1]['center'][1])

            elif self.sort_method == 'temperature_asc':
                # Sort by temperature, lowest first (Celsius)
                def temp_sort_key_asc(item):
                    temp = item[1].get('temperature')
                    # Sort None/unavailable temperatures to the end
                    if temp is None:
                        return float('inf')
                    return temp
                aois_with_indices.sort(key=temp_sort_key_asc)

            elif self.sort_method == 'temperature_desc':
                # Sort by temperature, highest first (Celsius)
                def temp_sort_key_desc(item):
                    temp = item[1].get('temperature')
                    # Sort None/unavailable temperatures to the end
                    if temp is None:
                        return float('-inf')
                    return temp
                aois_with_indices.sort(key=temp_sort_key_desc, reverse=True)

        except Exception as e:
            self.logger.error(f"Error sorting AOIs: {e}")

        return aois_with_indices

    def filter_aois_with_indices(self, aois_with_indices, img_idx):
        """Filter AOIs based on current filter settings.

        Args:
            aois_with_indices: List of tuples (original_index, aoi)
            img_idx: Current image index for flag filtering

        Returns:
            list: Filtered list of tuples (original_index, aoi)
        """
        filtered = []
        flagged_set = self.flagged_aois.get(img_idx, set())

        for original_idx, aoi in aois_with_indices:
            # Apply flag filter
            if self.filter_flagged_only and original_idx not in flagged_set:
                continue

            # Apply color filter
            if self.filter_color_hue is not None and self.filter_color_range is not None:
                hue = self.get_aoi_hue(aoi)
                if hue is not None:
                    distance = self.calculate_hue_distance(hue, self.filter_color_hue)
                    if distance > self.filter_color_range:
                        continue
                else:
                    # Skip AOIs without hue information when color filter is active
                    continue

            # Apply pixel area filter
            area = aoi.get('area', 0)
            if self.filter_area_min is not None and area < self.filter_area_min:
                continue
            if self.filter_area_max is not None and area > self.filter_area_max:
                continue

            # Apply comment filter
            if self.filter_comment_pattern is not None:
                import fnmatch
                comment = aoi.get('user_comment', '').strip()
                if not comment:
                    continue
                if not fnmatch.fnmatch(comment.lower(), self.filter_comment_pattern.lower()):
                    continue

            # Apply temperature filter (in Celsius)
            if self.filter_temperature_min is not None or self.filter_temperature_max is not None:
                temp = aoi.get('temperature')
                if temp is None:
                    continue
                if self.filter_temperature_min is not None and temp < self.filter_temperature_min:
                    continue
                if self.filter_temperature_max is not None and temp > self.filter_temperature_max:
                    continue

            # AOI passed all filters
            filtered.append((original_idx, aoi))

        return filtered

    def set_sort_method(self, method, color_hue=None):
        """Set the sort method for AOIs.

        Args:
            method: Sort method ('area_asc', 'area_desc', 'color', 'x', 'y', or None)
            color_hue: Hue value (0-360) for color-based sorting (optional)
        """
        self.sort_method = method
        self.sort_color_hue = color_hue

        # Update combo box selection
        self._update_combo_selection()

        # Refresh AOI display
        self.refresh_aoi_display()

        # Always sync to gallery (it's kept alive)
        if hasattr(self.parent, 'gallery_controller'):
            self.parent.gallery_controller.set_sort_method(method, color_hue)

    def set_filters(self, filters):
        """Set filter settings for AOIs.

        Args:
            filters: Dict with filter settings {
                'flagged_only': bool,
                'color_hue': int or None,
                'color_range': int or None,
                'area_min': float or None,
                'area_max': float or None,
                'comment_filter': str or None,
                'temperature_min': float or None,
                'temperature_max': float or None
            }
        """
        self.filter_flagged_only = filters.get('flagged_only', False)
        self.filter_color_hue = filters.get('color_hue')
        self.filter_color_range = filters.get('color_range')
        self.filter_area_min = filters.get('area_min')
        self.filter_area_max = filters.get('area_max')
        self.filter_comment_pattern = filters.get('comment_filter')
        self.filter_temperature_min = filters.get('temperature_min')
        self.filter_temperature_max = filters.get('temperature_max')

        # Update button appearance if available
        has_filters = any([
            self.filter_flagged_only,
            self.filter_color_hue is not None,
            self.filter_area_min is not None,
            self.filter_area_max is not None,
            self.filter_comment_pattern is not None,
            self.filter_temperature_min is not None,
            self.filter_temperature_max is not None
        ])

        # Refresh AOI display
        self.refresh_aoi_display()

        # Always sync to gallery (it's kept alive)
        if hasattr(self.parent, 'gallery_controller'):
            self.parent.gallery_controller.set_filters(filters)

    def refresh_aoi_display(self):
        """Refresh the AOI display with current sort/filter settings (delegated to UI component)."""
        if self.ui_component:
            self.ui_component.refresh_aoi_display()

    def _initialize_sort_combo(self):
        """Initialize the sort combo box with options."""
        if not hasattr(self.parent, 'aoiSortComboBox'):
            return
            
        combo = self.parent.aoiSortComboBox
        
        # Clear existing items
        combo.clear()
        
        # Define sort options with their display text, data, and icons
        sort_options = [
            ("Default", None, qta.icon('fa6s.sort', color='#888888')),
            ("Pixel Area (Smallest First)", 'area_asc', qta.icon('fa6s.arrow-up', color='#4CAF50')),
            ("Pixel Area (Largest First)", 'area_desc', qta.icon('fa6s.arrow-down', color='#4CAF50')),
            ("Confidence (Highest First)", 'confidence_desc', qta.icon('fa6s.star', color='#FFD700')),
            ("Confidence (Lowest First)", 'confidence_asc', qta.icon('fa6s.star-half-stroke', color='#FFD700')),
            ("Temperature (Lowest First)", 'temperature_asc', qta.icon('fa6s.temperature-low', color='#2196F3')),
            ("Temperature (Highest First)", 'temperature_desc', qta.icon('fa6s.temperature-high', color='#F44336')),
            ("Color (Closest to Target)", 'color', qta.icon('fa6s.palette', color='#CCCCCC')),
            ("Left to Right", 'x', qta.icon('fa6s.arrow-right', color='#2196F3')),
            ("Top to Bottom", 'y', qta.icon('fa6s.arrow-down', color='#2196F3'))
        ]

        # Check if dataset has thermal data and AOIs have temperature values
        is_thermal = hasattr(self.parent, 'is_thermal') and self.parent.is_thermal

        # Debug logging
        self.logger.debug(f"Sort combo initialization: is_thermal={is_thermal}")

        # Also check if any AOI actually has temperature data
        has_temperature_data = False
        temp_count = 0
        total_aois_checked = 0
        if is_thermal and hasattr(self.parent, 'images'):
            for image in self.parent.images:
                aois = image.get('areas_of_interest', [])
                for aoi in aois:
                    total_aois_checked += 1
                    if 'temperature' in aoi and aoi['temperature'] is not None:
                        has_temperature_data = True
                        temp_count += 1
                        # Debug first few
                        if temp_count <= 3:
                            self.logger.debug(f"  Found temperature in AOI: {aoi.get('temperature')}°C at {aoi.get('center')}")
                        # Found temperature, can break early after checking a few
                        if temp_count >= 5:
                            break
                if temp_count >= 5:
                    break

        self.logger.debug(f"Sort combo: has_temperature_data={has_temperature_data}, found {temp_count} AOIs with temperature (checked {total_aois_checked} total AOIs)")

        # Add items dynamically
        for idx, (text, data, icon) in enumerate(sort_options):
            combo.addItem(icon, text, data)

            # Disable temperature options if no temperature data available
            if data in ['temperature_asc', 'temperature_desc'] and not has_temperature_data:
                # Disable the item
                model = combo.model()
                item = model.item(idx)
                item.setEnabled(False)
                item.setToolTip("Temperature sorting unavailable (no thermal data)")
        
        # Set current selection based on current sort method
        if self.sort_method is None:
            combo.setCurrentIndex(0)  # "Default"
        else:
            for i in range(combo.count()):
                if combo.itemData(i) == self.sort_method:
                    combo.setCurrentIndex(i)
                    break

    def on_sort_combo_changed(self, text):
        """Handle sort combo box selection change."""
        if not hasattr(self.parent, 'aoiSortComboBox'):
            return

        combo = self.parent.aoiSortComboBox
        current_data = combo.currentData()

        if current_data is None:
            # "Default" selected - no sorting
            self.set_sort_method(None)
        elif current_data == 'color':
            # Color-based sorting - show color picker to let user choose target color
            target_hue = self._show_color_picker_for_sort()

            if target_hue is not None:
                # User selected a color
                self.set_sort_method(current_data, color_hue=target_hue)
            else:
                # User cancelled - revert to previous sort method
                self._update_combo_selection()
        else:
            # Other sort methods (area_asc, area_desc, x, y)
            self.set_sort_method(current_data)
    
    def _update_combo_selection(self):
        """Update combo box selection to match current sort method."""
        if not hasattr(self.parent, 'aoiSortComboBox'):
            return
            
        combo = self.parent.aoiSortComboBox
        if self.sort_method is None:
            combo.setCurrentIndex(0)  # "No Sort"
        else:
            for i in range(combo.count()):
                if combo.itemData(i) == self.sort_method:
                    combo.setCurrentIndex(i)
                    break

    def _get_reference_hue_from_settings(self):
        """Extract reference hue from parent settings.

        Returns:
            int: Hue value (0-360) or None if not available
        """
        try:
            # Get selected_color from settings
            if hasattr(self.parent, 'settings'):
                options = self.parent.settings.get('options', {})
                selected_color = options.get('selected_color')

                if selected_color:
                    # selected_color could be a list/tuple [r, g, b] or a QColor
                    if isinstance(selected_color, (list, tuple)) and len(selected_color) >= 3:
                        # RGB tuple/list
                        r, g, b = selected_color[0], selected_color[1], selected_color[2]
                        # Normalize to 0-1 range
                        r_norm = r / 255.0 if r > 1 else r
                        g_norm = g / 255.0 if g > 1 else g
                        b_norm = b / 255.0 if b > 1 else b
                        # Convert to HSV and extract hue
                        h, _, _ = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
                        return int(h * 360)
                    else:
                        # Try to treat as QColor
                        try:
                            if isinstance(selected_color, QColor):
                                h, _, _, _ = selected_color.getHsv()
                                return h
                        except Exception:
                            pass

            return None

        except Exception as e:
            self.logger.error(f"Error extracting reference hue from settings: {e}")
            return None

    def _show_color_picker_for_sort(self):
        """Show color picker dialog for user to select target color for sorting.

        Returns:
            int: Hue value (0-360) or None if user cancelled
        """
        try:
            # Try to get initial color from current sort_color_hue or settings
            initial_color = QColor(Qt.white)

            # Check if we have a current sort color hue
            if self.sort_color_hue is not None:
                # Convert hue to RGB for color dialog
                r, g, b = colorsys.hsv_to_rgb(self.sort_color_hue / 360.0, 1.0, 1.0)
                initial_color = QColor(int(r * 255), int(g * 255), int(b * 255))
            else:
                # Try to get from settings as fallback
                settings_hue = self._get_reference_hue_from_settings()
                if settings_hue is not None:
                    r, g, b = colorsys.hsv_to_rgb(settings_hue / 360.0, 1.0, 1.0)
                    initial_color = QColor(int(r * 255), int(g * 255), int(b * 255))

            # Open color dialog
            color = QColorDialog.getColor(
                initial_color,
                self.parent,
                "Select Target Color for Sorting",
                QColorDialog.DontUseNativeDialog  # Use Qt dialog for consistency
            )

            if color.isValid():
                # Convert to HSV and extract hue
                h, s, v = color.getHsv()[0], color.getHsv()[1], color.getHsv()[2]
                # Qt hue is 0-359 (-1 for achromatic), we want 0-360
                if h == -1:
                    h = 0

                self.logger.info(f"User selected color for sorting: Hue {h}°")
                return h
            else:
                # User cancelled
                self.logger.info("User cancelled color selection for sorting")
                return None

        except Exception as e:
            self.logger.error(f"Error showing color picker for sort: {e}")
            return None

    def open_filter_dialog(self):
        """Open the filter dialog."""
        from core.views.viewer.dialogs.AOIFilterDialog import AOIFilterDialog

        # Get current filter settings
        current_filters = {
            'flagged_only': self.filter_flagged_only,
            'color_hue': self.filter_color_hue,
            'color_range': self.filter_color_range if self.filter_color_range is not None else 30,
            'area_min': self.filter_area_min,
            'area_max': self.filter_area_max,
            'comment_filter': self.filter_comment_pattern,
            'temperature_min': self.filter_temperature_min,
            'temperature_max': self.filter_temperature_max
        }

        # Get temperature unit and thermal flag from parent viewer
        temperature_unit = getattr(self.parent, 'temperature_unit', 'C')
        is_thermal = getattr(self.parent, 'is_thermal', False)

        dialog = AOIFilterDialog(self.parent, current_filters, temperature_unit, is_thermal)
        if dialog.exec():
            # User clicked Apply
            filters = dialog.get_filters()
            self.set_filters(filters)

    def create_aoi_from_circle(self, center_x, center_y, radius):
        """Create a new AOI from a user-drawn circle.

        Args:
            center_x (int): X coordinate of circle center
            center_y (int): Y coordinate of circle center
            radius (int): Radius of the circle in pixels
        """
        import math
        import colorsys
        import xml.etree.ElementTree as ET

        try:
            # Get current image
            if not hasattr(self.parent, 'images') or not hasattr(self.parent, 'current_image'):
                return

            image = self.parent.images[self.parent.current_image]

            # Get pixel color at center point
            if hasattr(self.parent, 'current_image_array') and self.parent.current_image_array is not None:
                img_array = self.parent.current_image_array
            else:
                return

            # Validate coordinates
            height, width = img_array.shape[:2]
            if not (0 <= center_y < height and 0 <= center_x < width):
                self.logger.error(f"Center coordinates ({center_x}, {center_y}) out of bounds")
                return

            # Get RGB values at center
            r, g, b = img_array[center_y, center_x]

            # Convert to HSV to get hue
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)

            # Calculate area: 2/3 of the circle area
            circle_area = math.pi * radius * radius
            aoi_area = (2.0 / 3.0) * circle_area

            # Create AOI dictionary
            new_aoi = {
                'center': (center_x, center_y),
                'radius': radius,
                'area': aoi_area,
                'flagged': False,
                'user_comment': ''
            }

            # Add to current image's areas of interest
            if 'areas_of_interest' not in image:
                image['areas_of_interest'] = []

            image['areas_of_interest'].append(new_aoi)

            # Create XML element and add to image XML
            if 'xml' in image and image['xml'] is not None:
                image_xml = image['xml']

                # Create new area_of_interest XML element
                aoi_xml = ET.SubElement(image_xml, 'area_of_interest')
                aoi_xml.set('center', str((center_x, center_y)))
                aoi_xml.set('radius', str(radius))
                aoi_xml.set('area', str(aoi_area))
                aoi_xml.set('flagged', 'False')

                # Store reference to XML element
                new_aoi['xml'] = aoi_xml

                # Save XML file
                if hasattr(self.parent, 'xml_service') and self.parent.xml_service:
                    try:
                        self.parent.xml_service.save_xml_file(self.parent.xml_path)
                    except Exception as e:
                        self.logger.error(f"Failed to save XML: {e}")

            # Show success message with hue information
            hue_degrees = int(h * 360)
            if hasattr(self.parent, 'status_controller'):
                self.parent.status_controller.show_toast(
                    f"AOI created: Hue {hue_degrees}°, Area {aoi_area:.0f} px",
                    3000,
                    color="#00C853"
                )

            # Reload the image to display the new AOI
            self.parent._load_image()

        except Exception as e:
            self.logger.error(f"Error creating AOI from circle: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def enter_creation_mode(self):
        """Enter AOI creation mode - user can click and drag to draw a circle."""
        if not hasattr(self.parent, 'main_image') or self.parent.main_image is None:
            return

        self.parent.aoi_creation_mode = True
        self.parent.main_image.viewport().setCursor(Qt.CrossCursor)

        # Show instruction toast
        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast(
                "AOI Creation Mode: Click and drag to draw circle",
                3000,
                color="#FFA500"
            )

    def exit_creation_mode(self):
        """Exit AOI creation mode and clean up."""
        self.parent.aoi_creation_mode = False
        self.parent.aoi_creation_start = None
        self.parent.aoi_creation_current = None

        # Remove preview circle if it exists
        if self.parent.aoi_creation_preview_item is not None:
            if hasattr(self.parent, 'main_image') and self.parent.main_image is not None:
                self.parent.main_image.scene.removeItem(self.parent.aoi_creation_preview_item)
            self.parent.aoi_creation_preview_item = None

        # Restore normal cursor
        if hasattr(self.parent, 'main_image') and self.parent.main_image is not None:
            self.parent.main_image.viewport().setCursor(Qt.ArrowCursor)