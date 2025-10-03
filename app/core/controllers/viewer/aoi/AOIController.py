"""
AOIController - Handles Areas of Interest (AOI) management for the image viewer.

This controller manages AOI selection, flagging, filtering, display, and
interaction functionality.
"""

import colorsys
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidgetItem, QPushButton, QMenu, QApplication
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
        
        # UI elements (will be set by parent)
        self.aoiListWidget = None
        self.areaCountLabel = None
        self.flagFilterButton = None
    
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
    
    def set_ui_elements(self, aoi_list_widget, area_count_label, flag_filter_button):
        """Set references to UI elements.
        
        Args:
            aoi_list_widget: The QListWidget for displaying AOIs
            area_count_label: The QLabel showing AOI count
            flag_filter_button: The QPushButton for flag filtering
        """
        self.aoiListWidget = aoi_list_widget
        self.areaCountLabel = area_count_label
        self.flagFilterButton = flag_filter_button
    
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
        count = 0
        self.highlights = []
        self.aoi_containers = []  # Reset container list
        self.selected_aoi_index = -1  # Reset selection

        # Get flagged AOIs for this image
        img_idx = image_index if image_index is not None else self.parent.current_image
        flagged_set = self.flagged_aois.get(img_idx, set())

        # Keep track of actual visible container index
        visible_container_index = 0

        # Load AOI thumbnails normally for all datasets
        for area_of_interest in areas_of_interest:
            # Skip if we're filtering and this AOI is not flagged
            if self.filter_flagged_only and count not in flagged_set:
                count += 1
                continue

            # Create container widget for thumbnail and label
            container = QWidget()
            container.setProperty("aoi_index", count)  # Store AOI index
            container.setProperty("visible_index", visible_container_index)  # Store visible index
            layout = QVBoxLayout(container)
            layout.setSpacing(2)
            layout.setContentsMargins(0, 0, 0, 0)

            # Set up click handling for selection (use visible index for selection)
            def handle_click(event, idx=count, vis_idx=visible_container_index):
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
            highlight.setObjectName(f"highlight{count}")
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
                if count in flagged_set:
                    flag_label = QLabel("🚩")
                    flag_label.setStyleSheet("QLabel { color: red; font-size: 14px; font-weight: bold; }")
                    flag_label.setToolTip("This AOI is flagged")
                    color_layout.addWidget(flag_label)

                # Center the layout
                color_layout.addStretch()
                color_layout.insertStretch(0)

                info_layout.addWidget(color_container)

            # Enable context menu for the info widget
            info_widget.setContextMenuPolicy(Qt.CustomContextMenu)
            # Use default parameters to properly capture the current values
            info_widget.customContextMenuRequested.connect(
                lambda pos, c=center, a=pixel_area, info=avg_color_info: self.show_aoi_context_menu(pos, info_widget, c, a, info)
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
            if count == self.selected_aoi_index:
                self.update_aoi_selection_style(container, True)

            count += 1
            visible_container_index += 1

        if self.areaCountLabel:
            self.areaCountLabel.setText(f"{count} {'Area' if count == 1 else 'Areas'} of Interest")
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
                        except Exception as e:
                            pass
                    else:
                        pass
                else:
                    pass
    
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
    
    def add_flag_button_to_layout(self):
        """Add the flag filter button to the layout after UI initialization."""
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

                    # Insert flag button right after next button
                    if next_button_index >= 0:
                        layout.insertWidget(next_button_index + 1, self.flagFilterButton)
                        self.flagFilterButton.show()
        except Exception as e:
            self.logger.error(f"Error adding flag button: {e}")
    
    def toggle_flag_filter(self):
        """Toggle the flag filter on/off and refresh the AOI display."""
        self.filter_flagged_only = self.flagFilterButton.isChecked()

        # Update button appearance based on state
        if self.filter_flagged_only:
            self.flagFilterButton.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 0, 0, 100);
                    border: 2px solid red;
                    border-radius: 3px;
                    font-size: 16px;
                    color: red;
                }
                QPushButton:hover {
                    background-color: rgba(255, 0, 0, 150);
                }
            """)
        else:
            self.flagFilterButton.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #555;
                    border-radius: 3px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 20);
                }
            """)

        # Refresh AOI display with filter applied
        image = self.parent.images[self.parent.current_image]
        if hasattr(self.parent, 'current_image_array') and self.parent.current_image_array is not None:
            self.load_areas_of_interest(self.parent.current_image_array, image['areas_of_interest'], self.parent.current_image)
    
    def show_aoi_context_menu(self, pos, label_widget, center, pixel_area, avg_info=None):
        """Show context menu for AOI coordinate label with copy option.

        Args:
            pos: Position where the context menu was requested (relative to label_widget)
            label_widget: The QLabel widget that was right-clicked
            center: Tuple of (x, y) coordinates of the AOI center
            pixel_area: The area of the AOI in pixels
            avg_info: Average color/temperature information string
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
        copy_action.triggered.connect(lambda: self.copy_aoi_data(center, pixel_area, avg_info))

        # Get the current cursor position (global coordinates)
        global_pos = QCursor.pos()

        # Show menu at cursor position
        menu.exec(global_pos)
    
    def copy_aoi_data(self, center, pixel_area, avg_info=None):
        """Copy AOI data to clipboard including image name, coordinates, and GPS.

        Args:
            center: Tuple of (x, y) coordinates of the AOI center
            pixel_area: The area of the AOI in pixels
            avg_info: Average color/temperature information string
        """
        # Get current image information
        image = self.parent.images[self.parent.current_image]
        image_name = image.get('name', 'Unknown')

        # Get GPS coordinates if available
        gps_coords = self.parent.messages.get('GPS Coordinates', 'N/A')

        # Format the data for clipboard
        clipboard_text = (
            f"Image: {image_name}\n"
            f"AOI Coordinates: X={center[0]}, Y={center[1]}\n"
            f"AOI Area: {pixel_area:.0f} px\n"
        )

        # Add average info if available
        if avg_info:
            clipboard_text += f"Average: {avg_info}\n"

        clipboard_text += f"GPS Coordinates: {gps_coords}"

        # Copy to clipboard
        QApplication.clipboard().setText(clipboard_text)

        # Show confirmation toast
        if hasattr(self.parent, 'status_controller'):
            self.parent.status_controller.show_toast("AOI data copied", 2000, color="#00C853")
