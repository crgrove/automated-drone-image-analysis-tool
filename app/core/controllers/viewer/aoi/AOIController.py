"""
AOIController - Handles Areas of Interest (AOI) management for the image viewer.

This controller manages AOI selection, flagging, filtering, display, and
interaction functionality.
"""

import colorsys
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidgetItem, QPushButton, QMenu, QApplication, QAbstractItemView
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
from PySide6.QtGui import QCursor

from core.views.components.QtImageViewer import QtImageViewer
from core.services.LoggerService import LoggerService
import qimage2ndarray


class AOIController:
    """
    Controller for managing Areas of Interest (AOI) functionality.

    Handles AOI display, selection, flagging, filtering, and interaction
    including context menus and data copying.
    """

    def __init__(self, parent_viewer, logger=None):
        """
        Initialize the AOI controller.

        Args:
            parent_viewer: The main Viewer instance
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_viewer
        self.logger = logger or LoggerService()

        # AOI state
        self.selected_aoi_index = -1
        self.flagged_aois = {}
        self.filter_flagged_only = False
        self.aoi_containers = []
        self.highlights = []

        # Sort and filter state
        self.sort_method = None  # 'area_asc', 'area_desc', 'color', 'x', 'y'
        self.sort_color_hue = None  # Hue value (0-360) for color-based sorting
        self.filter_color_hue = None  # Hue value (0-360) for color filtering
        self.filter_color_range = None  # ± degrees for color filtering
        self.filter_area_min = None  # Minimum pixel area for filtering
        self.filter_area_max = None  # Maximum pixel area for filtering

        # UI elements (will be set by parent)
        self.aoiListWidget = None
        self.areaCountLabel = None
        self.sortButton = None
        self.filterButton = None

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

    def set_ui_elements(self, aoi_list_widget, area_count_label, sort_button=None, filter_button=None):
        """Set references to UI elements.

        Args:
            aoi_list_widget: The QListWidget for displaying AOIs
            area_count_label: The QLabel showing AOI count
            sort_button: The QPushButton for sorting (optional)
            filter_button: The QPushButton for filtering (optional)
        """
        self.aoiListWidget = aoi_list_widget
        self.areaCountLabel = area_count_label
        self.sortButton = sort_button
        self.filterButton = filter_button

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
                # Check if temperature data is available
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
                # Use the already-loaded image array instead of loading from disk
                if hasattr(self.parent, 'current_image_array') and self.parent.current_image_array is not None:
                    img_array = self.parent.current_image_array
                else:
                    # Fallback only if we don't have the cached image
                    image = self.parent.images[self.parent.current_image]
                    image_path = image.get('path', '')
                    mask_path = image.get('mask_path', '')
                    from core.services.ImageService import ImageService
                    image_service = ImageService(image_path, mask_path)
                    img_array = image_service.img_array

                center = area_of_interest['center']
                radius = area_of_interest.get('radius', 0)

                # Collect RGB values within the AOI
                colors = []
                cx, cy = center
                shape = img_array.shape

                # If we have detected pixels, use those
                if 'detected_pixels' in area_of_interest and area_of_interest['detected_pixels']:
                    for pixel in area_of_interest['detected_pixels']:
                        if isinstance(pixel, (list, tuple)) and len(pixel) >= 2:
                            px, py = int(pixel[0]), int(pixel[1])
                            if 0 <= py < shape[0] and 0 <= px < shape[1]:
                                colors.append(img_array[py, px])
                # Otherwise sample within the circle
                else:
                    for y in range(max(0, cy - radius), min(shape[0], cy + radius + 1)):
                        for x in range(max(0, cx - radius), min(shape[1], cx + radius + 1)):
                            # Check if pixel is within circle
                            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                                colors.append(img_array[y, x])

                if colors:
                    # Calculate average RGB
                    avg_rgb = np.mean(colors, axis=0).astype(int)

                    # Convert to HSV for display (full saturation and value)
                    # First normalize RGB to 0-1 range
                    r, g, b = avg_rgb[0] / 255.0, avg_rgb[1] / 255.0, avg_rgb[2] / 255.0

                    # Convert to HSV
                    h, _, _ = colorsys.rgb_to_hsv(r, g, b)

                    # Create full saturation and full value version
                    full_sat_rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
                    full_sat_rgb = tuple(int(c * 255) for c in full_sat_rgb)

                    # Format as hex color
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*full_sat_rgb)

                    # Return hue angle, hex color, and RGB tuple for the color square
                    hue_degrees = int(h * 360)
                    return f"Hue: {hue_degrees}° {hex_color}", full_sat_rgb

        except Exception as e:
            self.logger.error(f"Error calculating AOI average info: {e}")
            return None, None

        return None, None

    def load_areas_of_interest(self, augmented_image, areas_of_interest, image_index=None):
        """Load areas of interest thumbnails for a given image.

        Args:
            augmented_image: The image array to create thumbnails from
            areas_of_interest: List of AOI dictionaries
            image_index: Index of the current image (if None, uses parent.current_image)
        """
        if not self.aoiListWidget:
            return

        # Block signals during rebuild to avoid re-entrant updates while rapidly switching
        self.aoiListWidget.blockSignals(True)
        self.aoiListWidget.clear()
        self.highlights = []
        self.aoi_containers = []  # Reset container list
        self.selected_aoi_index = -1  # Reset selection

        # Get flagged AOIs for this image
        img_idx = image_index if image_index is not None else self.parent.current_image
        flagged_set = self.flagged_aois.get(img_idx, set())

        # Apply sorting and filtering
        aois_with_indices = self.sort_aois_with_indices(areas_of_interest)
        aois_with_indices = self.filter_aois_with_indices(aois_with_indices, img_idx)

        # Keep track of total count before and after filtering
        total_count = len(areas_of_interest)
        filtered_count = len(aois_with_indices)

        # Keep track of actual visible container index
        visible_container_index = 0

        # Load AOI thumbnails for filtered and sorted list
        for original_index, area_of_interest in aois_with_indices:

            # Create container widget for thumbnail and label
            container = QWidget()
            container.setProperty("aoi_index", original_index)  # Store original AOI index
            container.setProperty("visible_index", visible_container_index)  # Store visible index
            layout = QVBoxLayout(container)
            layout.setSpacing(2)
            layout.setContentsMargins(0, 0, 0, 0)

            # Set up click handling for selection (use original index for selection)
            def handle_click(event, idx=original_index, vis_idx=visible_container_index):
                self.select_aoi(idx, vis_idx)
                return QWidget.mousePressEvent(container, event)  # Call the original handler
            container.mousePressEvent = handle_click

            # Skip thumbnail creation if no image provided (deferred case)
            if augmented_image is None:
                continue

            center = area_of_interest['center']
            radius = area_of_interest['radius'] + 10
            crop_arr = self.parent.crop_image(augmented_image, center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)

            # Create the image viewer
            highlight = QtImageViewer(self.parent, container, center, True)
            highlight.setObjectName(f"highlight{original_index}")
            highlight.setMinimumSize(QSize(190, 190))  # Reduced height to make room for label
            highlight.aspectRatioMode = Qt.KeepAspectRatio
            # Safely set the image on the highlight viewer
            try:
                img = qimage2ndarray.array2qimage(crop_arr)
                if _qt_is_valid(highlight):
                    highlight.setImage(img)
                else:
                    continue
            except RuntimeError:
                # Highlight was deleted during rapid switching; skip
                continue
            highlight.canZoom = False
            highlight.canPan = False

            # Calculate average color/temperature for the AOI
            avg_color_info, color_rgb = self.calculate_aoi_average_info(
                area_of_interest,
                self.parent.is_thermal,
                self.parent.temperature_data,
                self.parent.temperature_unit
            )

            # Create coordinate label with pixel area
            pixel_area = area_of_interest.get('area', 0)
            coord_text = f"X: {center[0]}, Y: {center[1]} | Area: {pixel_area:.0f} px"

            # Create info widget container for both text and color square
            info_widget = QWidget()
            info_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 150);
                    border-radius: 2px;
                }
            """)
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(4, 2, 4, 2)
            info_layout.setSpacing(2)

            # Create coordinate label
            coord_label = QLabel(coord_text)
            coord_label.setAlignment(Qt.AlignCenter)
            coord_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 10px;
                }
            """)
            info_layout.addWidget(coord_label)

            # Add color/temperature information with color square if applicable
            if avg_color_info:
                # Create horizontal layout for color info
                color_container = QWidget()
                color_layout = QHBoxLayout(color_container)
                color_layout.setContentsMargins(0, 0, 0, 0)
                color_layout.setSpacing(4)

                # Add color square if we have RGB values (not for temperature)
                if color_rgb is not None:
                    color_square = QLabel()
                    color_square.setFixedSize(12, 12)
                    color_square.setStyleSheet(f"""
                        QLabel {{
                            background-color: rgb({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]});
                            border: 1px solid white;
                        }}
                    """)
                    color_layout.addWidget(color_square)

                # Add text label
                color_label = QLabel(avg_color_info)
                color_label.setAlignment(Qt.AlignCenter)
                color_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        font-size: 10px;
                    }
                """)
                color_layout.addWidget(color_label)

                # Add flag icon if this AOI is flagged
                if original_index in flagged_set:
                    flag_label = QLabel("🚩")
                    flag_label.setStyleSheet("QLabel { color: red; font-size: 14px; font-weight: bold; }")
                    flag_label.setToolTip("This AOI is flagged")
                    color_layout.addWidget(flag_label)

                # Add document/comment icon (always visible)
                user_comment = area_of_interest.get('user_comment', '')
                comment_icon = QLabel("📝")
                comment_icon.setCursor(Qt.PointingHandCursor)

                # Style based on whether comment exists
                if user_comment:
                    comment_icon.setStyleSheet("QLabel { color: #FFD700; font-size: 14px; font-weight: bold; }")
                    # Show preview of comment (first 50 chars)
                    preview = user_comment[:50] + "..." if len(user_comment) > 50 else user_comment
                    comment_icon.setToolTip(f"Comment: {preview}\n(Click to edit)")
                else:
                    comment_icon.setStyleSheet("QLabel { color: #808080; font-size: 14px; }")
                    comment_icon.setToolTip("Add comment (click)")

                # Make icon clickable - use lambda with default parameter to capture current AOI index
                def make_comment_click_handler(aoi_idx):
                    return lambda event: self.edit_aoi_comment(aoi_idx)

                comment_icon.mousePressEvent = make_comment_click_handler(original_index)
                color_layout.addWidget(comment_icon)

                # Center the layout
                color_layout.addStretch()
                color_layout.insertStretch(0)

                info_layout.addWidget(color_container)

            # Enable context menu for the info widget
            info_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            # Use default parameters to properly capture the current values
            info_widget.customContextMenuRequested.connect(
                lambda pos, c=center, a=pixel_area, info=avg_color_info, idx=original_index: self.show_aoi_context_menu(pos, info_widget, c, a, info, idx)
            )

            # Add widgets to layout
            layout.addWidget(highlight)
            layout.addWidget(info_widget)

            # Create list item
            listItem = QListWidgetItem()
            listItem.setSizeHint(QSize(190, 210))  # Increased height to accommodate label
            self.aoiListWidget.addItem(listItem)
            self.aoiListWidget.setItemWidget(listItem, container)
            self.aoiListWidget.setSpacing(5)
            self.highlights.append(highlight)
            # Safely connect if the source is still valid
            if _qt_is_valid(highlight):
                try:
                    highlight.leftMouseButtonPressed.connect(self.area_of_interest_click)
                except RuntimeError:
                    pass

            # Store container reference
            self.aoi_containers.append(container)

            # Apply selection style if this is the selected AOI
            if original_index == self.selected_aoi_index:
                self.update_aoi_selection_style(container, True)

            visible_container_index += 1

        # Update area count label with filter information
        if self.areaCountLabel:
            if filtered_count < total_count:
                # Show filtered count vs total
                self.areaCountLabel.setText(f"{filtered_count} of {total_count} {'Area' if total_count == 1 else 'Areas'}")
            else:
                # Show just the count
                self.areaCountLabel.setText(f"{filtered_count} {'Area' if filtered_count == 1 else 'Areas'} of Interest")

        # Re-enable signals after rebuild
        self.aoiListWidget.blockSignals(False)

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
        # Clear ALL container styles first using the proper update method
        for i, container in enumerate(self.aoi_containers):
            self.update_aoi_selection_style(container, False)

        # Set new selection
        self.selected_aoi_index = aoi_index

        # Apply selection style to the clicked container using the proper method
        if aoi_index >= 0 and visible_index >= 0 and visible_index < len(self.aoi_containers):
            container = self.aoi_containers[visible_index]
            self.update_aoi_selection_style(container, True)
            container.update()
            container.repaint()

            # Scroll the AOI list to bring the selected item into view
            if self.aoiListWidget and visible_index < self.aoiListWidget.count():
                item = self.aoiListWidget.item(visible_index)
                if item:
                    self.aoiListWidget.scrollToItem(item, QAbstractItemView.PositionAtCenter)

        # Update AOI on GPS map if available
        if hasattr(self.parent, 'gps_map_controller') and self.parent.gps_map_controller:
            self.parent.gps_map_controller.update_aoi_on_map()

    def update_aoi_selection_style(self, container, selected):
        """Update the visual style of an AOI container based on selection state.

        Args:
            container (QWidget): The AOI container widget
            selected (bool): Whether the container is selected
        """
        if selected:
            # Get the current settings color for the selection (typically magenta/pink)
            color = self.parent.settings.get('identifier_color', [255, 255, 0])
            # Just change the background color, no border
            container.setStyleSheet(f"""
                QWidget {{
                    background-color: rgba({color[0]}, {color[1]}, {color[2]}, 40);
                    border-radius: 5px;
                }}
            """)
        else:
            # Explicitly set background to transparent to clear previous selection
            container.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                }
            """)
            container.repaint()

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
        from core.controllers.viewer.components.AOICommentDialog import AOICommentDialog
        dialog = AOICommentDialog(self.parent, current_comment)

        if dialog.exec():
            # User clicked OK - save the comment
            new_comment = dialog.get_comment()
            self.save_aoi_comment_to_xml(self.parent.current_image, aoi_index, new_comment)

            # Refresh the AOI display to update the icon
            if hasattr(self.parent, 'current_image_array') and self.parent.current_image_array is not None:
                # Save scroll position and selection
                scroll_pos = self.aoiListWidget.verticalScrollBar().value()
                selected_idx = self.selected_aoi_index

                # Reload AOIs
                self.load_areas_of_interest(
                    self.parent.current_image_array,
                    image['areas_of_interest'],
                    self.parent.current_image
                )

                # Restore selection and scroll
                self.selected_aoi_index = selected_idx
                for container in self.aoi_containers:
                    if container.property("aoi_index") == selected_idx:
                        self.update_aoi_selection_style(container, True)
                        break
                self.aoiListWidget.verticalScrollBar().setValue(scroll_pos)

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

        # Get or create flagged set for current image
        if self.parent.current_image not in self.flagged_aois:
            self.flagged_aois[self.parent.current_image] = set()

        flagged_set = self.flagged_aois[self.parent.current_image]

        # Toggle flag status
        is_now_flagged = self.selected_aoi_index not in flagged_set
        if is_now_flagged:
            flagged_set.add(self.selected_aoi_index)
        else:
            flagged_set.remove(self.selected_aoi_index)

        # Save to XML
        self.save_flagged_aoi_to_xml(self.parent.current_image, self.selected_aoi_index, is_now_flagged)

        # If AOI was just flagged, open comment dialog
        if is_now_flagged:
            image = self.parent.images[self.parent.current_image]
            aoi = image['areas_of_interest'][self.selected_aoi_index]
            current_comment = aoi.get('user_comment', '')

            from core.controllers.viewer.components.AOICommentDialog import AOICommentDialog
            dialog = AOICommentDialog(self.parent, current_comment)

            if dialog.exec():
                # User clicked OK - save the comment
                new_comment = dialog.get_comment()
                self.save_aoi_comment_to_xml(self.parent.current_image, self.selected_aoi_index, new_comment)

        # Save scroll position
        scroll_pos = self.aoiListWidget.verticalScrollBar().value()

        # Remember selected AOI index
        selected_idx = self.selected_aoi_index

        # Refresh the AOI display to show/hide flag icon
        image = self.parent.images[self.parent.current_image]
        if hasattr(self.parent, 'current_image_array') and self.parent.current_image_array is not None:
            self.load_areas_of_interest(self.parent.current_image_array, image['areas_of_interest'], self.parent.current_image)

        # Restore selection and scroll position
        self.selected_aoi_index = selected_idx
        # Find the container with the matching AOI index
        for container in self.aoi_containers:
            if container.property("aoi_index") == selected_idx:
                self.update_aoi_selection_style(container, True)
                break
        self.aoiListWidget.verticalScrollBar().setValue(scroll_pos)

    def add_sort_filter_buttons_to_layout(self):
        """Add the sort and filter buttons to the layout after UI initialization."""
        try:
            # Get the parent widget of nextImageButton
            parent = self.parent.nextImageButton.parent()
            if parent:
                layout = parent.layout()
                if layout:
                    # Find the position of nextImageButton
                    next_button_index = -1
                    for i in range(layout.count()):
                        item = layout.itemAt(i)
                        widget = item.widget() if item else None
                        if widget == self.parent.nextImageButton:
                            next_button_index = i
                            break

                    # Insert buttons right after next button
                    if next_button_index >= 0:
                        if self.sortButton:
                            layout.insertWidget(next_button_index + 1, self.sortButton)
                            self.sortButton.show()
                        if self.filterButton:
                            layout.insertWidget(next_button_index + 2, self.filterButton)
                            self.filterButton.show()
        except Exception as e:
            self.logger.error(f"Error adding AOI control buttons: {e}")

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

            # Get image GPS coordinates
            from helpers.MetaDataHelper import MetaDataHelper
            from helpers.LocationInfo import LocationInfo
            exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)

            if not gps_coords:
                return "N/A"

            # Get image dimensions and service
            from core.services.ImageService import ImageService
            image_service = ImageService(image['path'], image.get('mask_path', ''))
            img_array = image_service.img_array
            height, width = img_array.shape[:2]

            # Check gimbal pitch angle - must be within 5 degrees of nadir
            _, gimbal_pitch = image_service.get_gimbal_orientation()
            if gimbal_pitch is not None:
                # Nadir is typically -90 degrees (camera pointing straight down)
                if not (-95 <= gimbal_pitch <= -85):
                    return "N/A (gimbal not nadir)"

            # Get bearing
            # Use get_drone_orientation() to match the Drone Orientation displayed in viewer
            # For nadir shots (required by gimbal pitch check above), drone orientation is correct
            bearing = image_service.get_drone_orientation()
            if bearing is None:
                bearing = 0  # Default to north if bearing not available

            # Get GSD (Ground Sampling Distance) with custom altitude if available
            custom_alt = self.parent.custom_agl_altitude_ft if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0 else None
            gsd_cm = image_service.get_average_gsd(custom_altitude_ft=custom_alt)
            if gsd_cm is None:
                return "N/A (no GSD)"

            # Use GPS map controller's calculation method if available
            if hasattr(self.parent, 'gps_map_controller'):
                aoi_gps = self.parent.gps_map_controller.calculate_aoi_gps_coordinates(
                    gps_coords,
                    aoi['center'],
                    (width/2, height/2),
                    gsd_cm,
                    bearing
                )

                if aoi_gps and 'latitude' in aoi_gps and 'longitude' in aoi_gps:
                    # Format based on parent's position format preference
                    lat = aoi_gps['latitude']
                    lon = aoi_gps['longitude']

                    if hasattr(self.parent, 'position_format'):
                        if self.parent.position_format == 'Decimal Degrees':
                            return f"{lat:.6f}, {lon:.6f}"
                        elif self.parent.position_format == 'Degrees Minutes Seconds':
                            # Convert to DMS format
                            lat_dms = self.decimal_to_dms(lat, is_latitude=True)
                            lon_dms = self.decimal_to_dms(lon, is_latitude=False)
                            return f"{lat_dms}, {lon_dms}"
                        elif self.parent.position_format == 'Degrees Decimal Minutes':
                            # Convert to DDM format
                            lat_ddm = self.decimal_to_ddm(lat, is_latitude=True)
                            lon_ddm = self.decimal_to_ddm(lon, is_latitude=False)
                            return f"{lat_ddm}, {lon_ddm}"

                    # Default to decimal degrees
                    return f"{lat:.6f}, {lon:.6f}"

            return "N/A"

        except Exception as e:
            self.logger.error(f"Error calculating AOI GPS: {e}")
            return "N/A"

    def decimal_to_dms(self, decimal, is_latitude):
        """Convert decimal degrees to DMS format.

        Args:
            decimal: Decimal degrees
            is_latitude: True for latitude, False for longitude

        Returns:
            String in DMS format
        """
        direction = 'N' if decimal >= 0 and is_latitude else 'S' if is_latitude else 'E' if decimal >= 0 else 'W'
        decimal = abs(decimal)
        degrees = int(decimal)
        minutes_decimal = (decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60

        return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"

    def decimal_to_ddm(self, decimal, is_latitude):
        """Convert decimal degrees to DDM format.

        Args:
            decimal: Decimal degrees
            is_latitude: True for latitude, False for longitude

        Returns:
            String in DDM format
        """
        direction = 'N' if decimal >= 0 and is_latitude else 'S' if is_latitude else 'E' if decimal >= 0 else 'W'
        decimal = abs(decimal)
        degrees = int(decimal)
        minutes = (decimal - degrees) * 60

        return f"{degrees}°{minutes:.4f}'{direction}"

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
            # Calculate average color/hue for the AOI
            avg_info, color_rgb = self.calculate_aoi_average_info(
                aoi,
                self.parent.is_thermal,
                self.parent.temperature_data,
                self.parent.temperature_unit
            )

            # Extract hue from avg_info string (format: "Hue: 123° #rrggbb")
            if avg_info and "Hue:" in avg_info:
                hue_str = avg_info.split("Hue:")[1].split("°")[0].strip()
                return int(hue_str)

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

        # Update button appearance if available
        if self.sortButton:
            if method is None:
                self.sortButton.setStyleSheet("""
                    QPushButton {
                        background-color: #404040;
                        color: white;
                        border: 1px solid #555;
                        border-radius: 3px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                    }
                """)
            else:
                self.sortButton.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(100, 150, 255, 100);
                        border: 2px solid #4488ff;
                        border-radius: 3px;
                        font-size: 12px;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(100, 150, 255, 150);
                    }
                """)

        # Refresh AOI display
        self.refresh_aoi_display()

    def set_filters(self, filters):
        """Set filter settings for AOIs.

        Args:
            filters: Dict with filter settings {
                'flagged_only': bool,
                'color_hue': int or None,
                'color_range': int or None,
                'area_min': float or None,
                'area_max': float or None
            }
        """
        self.filter_flagged_only = filters.get('flagged_only', False)
        self.filter_color_hue = filters.get('color_hue')
        self.filter_color_range = filters.get('color_range')
        self.filter_area_min = filters.get('area_min')
        self.filter_area_max = filters.get('area_max')

        # Update button appearance if available
        has_filters = any([
            self.filter_flagged_only,
            self.filter_color_hue is not None,
            self.filter_area_min is not None,
            self.filter_area_max is not None
        ])

        if self.filterButton:
            if has_filters:
                self.filterButton.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(100, 255, 150, 100);
                        border: 2px solid #44ff88;
                        border-radius: 3px;
                        font-size: 12px;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(100, 255, 150, 150);
                    }
                """)
            else:
                self.filterButton.setStyleSheet("""
                    QPushButton {
                        background-color: #404040;
                        color: white;
                        border: 1px solid #555;
                        border-radius: 3px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                    }
                """)

        # Refresh AOI display
        self.refresh_aoi_display()

    def refresh_aoi_display(self):
        """Refresh the AOI display with current sort/filter settings."""
        if not hasattr(self.parent, 'current_image') or not hasattr(self.parent, 'images'):
            return

        image = self.parent.images[self.parent.current_image]
        if hasattr(self.parent, 'current_image_array') and self.parent.current_image_array is not None:
            # Save scroll position and selection
            scroll_pos = self.aoiListWidget.verticalScrollBar().value() if self.aoiListWidget else 0
            selected_idx = self.selected_aoi_index

            # Reload AOIs
            self.load_areas_of_interest(
                self.parent.current_image_array,
                image.get('areas_of_interest', []),
                self.parent.current_image
            )

            # Restore selection and scroll
            self.selected_aoi_index = selected_idx
            if self.aoiListWidget:
                self.aoiListWidget.verticalScrollBar().setValue(scroll_pos)

    def open_sort_menu(self):
        """Open a menu to select sort method."""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QCursor

        menu = QMenu(self.parent)
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

        # Add sort options
        action_area_asc = menu.addAction("📐 Pixel Area (Smallest First)")
        action_area_desc = menu.addAction("📐 Pixel Area (Largest First)")
        action_color = menu.addAction("🎨 Color Similarity...")
        action_x = menu.addAction("↔️ Order X (Left to Right)")
        action_y = menu.addAction("↕️ Order Y (Top to Bottom)")
        menu.addSeparator()
        action_clear = menu.addAction("❌ Clear Sort")

        # Show menu at button position
        action = menu.exec(QCursor.pos())

        if action == action_area_asc:
            self.set_sort_method('area_asc')
        elif action == action_area_desc:
            self.set_sort_method('area_desc')
        elif action == action_color:
            # Open color picker for color sorting
            from PySide6.QtWidgets import QColorDialog
            from PySide6.QtCore import Qt
            color = QColorDialog.getColor(Qt.white, self.parent, "Select Target Color for Sorting")
            if color.isValid():
                h, s, v = color.getHsv()[0], color.getHsv()[1], color.getHsv()[2]
                if h == -1:
                    h = 0
                self.set_sort_method('color', color_hue=h)
        elif action == action_x:
            self.set_sort_method('x')
        elif action == action_y:
            self.set_sort_method('y')
        elif action == action_clear:
            self.set_sort_method(None)

    def open_filter_dialog(self):
        """Open the filter dialog."""
        from core.controllers.viewer.components.AOIFilterDialog import AOIFilterDialog

        # Get current filter settings
        current_filters = {
            'flagged_only': self.filter_flagged_only,
            'color_hue': self.filter_color_hue,
            'color_range': self.filter_color_range if self.filter_color_range is not None else 30,
            'area_min': self.filter_area_min,
            'area_max': self.filter_area_max
        }

        dialog = AOIFilterDialog(self.parent, current_filters)
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
