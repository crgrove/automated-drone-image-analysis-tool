"""
AOIUIComponent - Handles UI manipulation for Areas of Interest (AOI) display.

This component is responsible for all UI operations related to AOI display,
including creating widgets, updating styles, and managing visual interactions.
It works in conjunction with AOIController which handles the business logic.
"""

import colorsys
import numpy as np
import qimage2ndarray
import qtawesome as qta

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidgetItem, QPushButton, QMenu, QApplication, QAbstractItemView, QFrame, QProgressBar
try:
    from shiboken6 import isValid as _qt_is_valid
except Exception:
    def _qt_is_valid(obj):
        try:
            _ = obj.metaObject()
            return True
        except Exception:
            return False
from PySide6.QtCore import Qt, QSize, QPoint, QTimer
from PySide6.QtGui import QCursor

from core.services.LoggerService import LoggerService
from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer



class AOIUIComponent:
    """
    UI component for managing Areas of Interest (AOI) display and interaction.
    
    This component handles all UI operations while AOIController manages business logic.
    """

    def __init__(self, aoi_controller):
        """
        Initialize the AOI UI component.

        Args:
            aoi_controller: Reference to the AOIController for business logic
        """
        self.aoi_controller = aoi_controller
        self.logger = LoggerService()  # Create our own logger

        # UI state
        self.aoi_containers = []
        self.highlights = []

        # Batch loading state
        self.batch_timer = QTimer()
        self.batch_timer.timeout.connect(self._process_next_batch)
        self.batch_loading_state = None  # Stores state during batch loading
        self.batch_progress_widget = None  # Progress indicator widget


    def load_areas_of_interest(self, augmented_image, areas_of_interest):
        """Load areas of interest thumbnails for a given image.

        Args:
            augmented_image: The image array to create thumbnails from
            areas_of_interest: List of AOI dictionaries
        """
        aoi_list_widget = self.aoi_controller.parent.aoiListWidget
        if not aoi_list_widget:
            return

        # Cancel any ongoing batch loading
        if self.batch_timer.isActive():
            self.batch_timer.stop()
            self._remove_progress_widget()

        # Ensure the list widget itself does not manage selection/focus styles
        # We control AOI selection visuals manually
        try:
            aoi_list_widget.setSelectionMode(QAbstractItemView.NoSelection)
            aoi_list_widget.setFocusPolicy(Qt.NoFocus)
            aoi_list_widget.setUniformItemSizes(True)
            # Lock the width to prevent layout jitter (matches UI minimum)
            aoi_list_widget.setFixedWidth(max(250, aoi_list_widget.minimumWidth()))
        except Exception:
            pass

        # Block signals during rebuild to avoid re-entrant updates while rapidly switching
        aoi_list_widget.blockSignals(True)
        aoi_list_widget.clear()
        self.highlights = []
        self.aoi_containers = []  # Reset container list

        # Get flagged AOIs for this image
        img_idx = self.aoi_controller.parent.current_image
        flagged_set = self.aoi_controller.flagged_aois.get(img_idx, set())

        # Apply sorting and filtering (business logic handled by controller)
        aois_with_indices = self.aoi_controller.sort_aois_with_indices(areas_of_interest)
        aois_with_indices = self.aoi_controller.filter_aois_with_indices(aois_with_indices, img_idx)

        # Keep track of total count before and after filtering
        total_count = len(areas_of_interest)
        filtered_count = len(aois_with_indices)

        # Update area count label with filter information
        self._update_count_label(filtered_count, total_count)

        # Re-enable signals after rebuild
        aoi_list_widget.blockSignals(False)

        # If we have many AOIs, use batch loading to keep UI responsive
        if filtered_count > 100:
            self._start_batch_loading(aois_with_indices, augmented_image, flagged_set)
        else:
            # For small counts, load synchronously (fast enough)
            visible_container_index = 0
            for original_index, area_of_interest in aois_with_indices:
                container = self._create_aoi_container(original_index, visible_container_index, area_of_interest, augmented_image, flagged_set)
                if container:
                    self.aoi_containers.append(container)
                    visible_container_index += 1

    def _create_aoi_container(self, original_index, visible_container_index, area_of_interest, augmented_image, flagged_set):
        """Create a single AOI container widget.

        Args:
            original_index: Original AOI index in the full list
            visible_container_index: Index in the visible containers list
            area_of_interest: AOI dictionary
            augmented_image: Image array for thumbnails
            flagged_set: Set of flagged AOI indices

        Returns:
            QWidget: The created container widget or None if creation failed
        """
        try:
            # Get UI elements from parent
            aoi_list_widget = self.aoi_controller.parent.aoiListWidget
            if not aoi_list_widget:
                return None
            # Create container widget for thumbnail and label
            container = QWidget()
            container.setObjectName("AOIItemContainer")
            container.setProperty("aoi_index", original_index)  # Store original AOI index
            container.setProperty("visible_index", visible_container_index)  # Store visible index
            layout = QVBoxLayout(container)
            layout.setSpacing(4)
            layout.setContentsMargins(6, 6, 6, 6)
            # Base border around each list item container
            container.setStyleSheet(
                "#AOIItemContainer { border: 1px solid #666; border-radius: 4px; background-color: transparent; }"
            )

            # Set up click handling for selection (use original index for selection)
            def handle_click(event, idx=original_index, vis_idx=visible_container_index):
                self.aoi_controller.select_aoi(idx, vis_idx)
                return QWidget.mousePressEvent(container, event)  # Call the original handler
            container.mousePressEvent = handle_click

            # Skip thumbnail creation if no image provided (deferred case)
            if augmented_image is None:
                return container

            center = area_of_interest['center']
            radius = area_of_interest['radius'] + 10
            crop_arr = self.aoi_controller.parent.crop_image(augmented_image, center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)

            # Create the image viewer

            highlight = QtImageViewer(self.aoi_controller.parent, container, center, True)
            highlight.setObjectName(f"highlight{original_index}")
            highlight.setMinimumSize(QSize(180, 180))  # Reduced height to make room for label
            highlight.aspectRatioMode = Qt.KeepAspectRatio
            # Remove default QFrame border around QGraphicsView
            try:
                highlight.setFrameShape(QFrame.NoFrame)
            except Exception:
                pass
            # Safely set the image on the highlight viewer
            try:
                img = qimage2ndarray.array2qimage(crop_arr)
                if _qt_is_valid(highlight):
                    highlight.setImage(img)
                else:
                    return container
            except RuntimeError:
                # Highlight was deleted during rapid switching; skip
                return container
            highlight.canZoom = False
            highlight.canPan = False

            # Calculate average color/temperature for the AOI (business logic)
            # Get temperature data from thermal controller if available
            temperature_data = None
            if hasattr(self.aoi_controller.parent, 'thermal_controller'):
                temperature_data = self.aoi_controller.parent.thermal_controller.temperature_data
            
            avg_color_info, color_rgb = self.aoi_controller.calculate_aoi_average_info(
                area_of_interest,
                self.aoi_controller.parent.is_thermal,
                temperature_data,
                self.aoi_controller.parent.temperature_unit
            )

            # Create coordinate label with pixel area
            pixel_area = area_of_interest.get('area', 0)
            coord_text = f"X: {center[0]}, Y: {center[1]} | Area: {pixel_area:.0f} px"

            # Create separate top and bottom info bars
            top_info_widget = self._create_top_info_widget(coord_text, original_index, area_of_interest)
            bottom_info_widget = self._create_bottom_info_widget(avg_color_info, color_rgb, original_index, flagged_set, area_of_interest)

            # Add widgets directly to the container layout: top bar, image, bottom bar
            layout.addWidget(top_info_widget)
            layout.addWidget(highlight)
            layout.addWidget(bottom_info_widget)

            # Create list item
            listItem = QListWidgetItem()
            listItem.setSizeHint(QSize(190, 250))  # Slightly increased height for two info bars
            aoi_list_widget.addItem(listItem)
            aoi_list_widget.setItemWidget(listItem, container)
            aoi_list_widget.setSpacing(5)
            self.highlights.append(highlight)
            # Safely connect if the source is still valid
            if _qt_is_valid(highlight):
                try:
                    highlight.leftMouseButtonPressed.connect(self.aoi_controller.area_of_interest_click)
                except RuntimeError:
                    pass

            return container

        except Exception as e:
            self.logger.error(f"Error creating AOI container: {e}")
            return None

    def _create_top_info_widget(self, coord_text, original_index, area_of_interest):
        """Create the top info bar showing coordinates and area."""
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 150);
                border-radius: 2px;
            }
        """)

        # Build tooltip with confidence info if available
        tooltip_text = "AOI Information\nRight-click to copy data to clipboard"
        if 'confidence' in area_of_interest and 'score_type' in area_of_interest:
            score_type = area_of_interest.get('score_type', '')
            raw_score = area_of_interest.get('raw_score', 0)
            score_method = area_of_interest.get('score_method', 'mean')
            tooltip_text += f"\n\nScore Type: {score_type}\nRaw Score: {raw_score} ({score_method})"

        info_widget.setToolTip(tooltip_text)
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(4, 2, 4, 2)
        info_layout.setSpacing(2)

        coord_label = QLabel(coord_text)
        coord_label.setAlignment(Qt.AlignCenter)
        coord_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 10px;
            }
        """)
        info_layout.addWidget(coord_label)

        # Add confidence display if available
        if 'confidence' in area_of_interest:
            confidence = area_of_interest['confidence']

            # Add a separator
            separator = QLabel("|")
            separator.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
            info_layout.addWidget(separator)

            # Confidence icon with color based on value
            if confidence >= 75:
                conf_color = '#4CAF50'  # Green for high confidence
                conf_icon = '⭐'
            elif confidence >= 50:
                conf_color = '#FFD700'  # Gold for medium-high confidence
                conf_icon = '⭐'
            elif confidence >= 25:
                conf_color = '#FFA500'  # Orange for medium-low confidence
                conf_icon = '⭐'
            else:
                conf_color = '#FF6B6B'  # Red for low confidence
                conf_icon = '⭐'

            # Confidence label
            conf_label = QLabel(f"{conf_icon} {confidence:.1f}%")
            conf_label.setStyleSheet(f"""
                QLabel {{
                    color: {conf_color};
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)
            conf_label.setToolTip(f"Confidence Score: {confidence:.1f}%")
            info_layout.addWidget(conf_label)

        # Enable context menu for the info widget
        info_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        info_widget.customContextMenuRequested.connect(
            lambda pos, c=area_of_interest['center'], a=area_of_interest.get('area', 0), info=None, idx=original_index: self.aoi_controller.show_aoi_context_menu(pos, info_widget, c, a, info, idx)
        )

        return info_widget

    def _create_bottom_info_widget(self, avg_color_info, color_rgb, original_index, flagged_set, area_of_interest):
        """Create the bottom info bar showing color/temperature info and actions."""
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 150);
                border-radius: 2px;
            }
        """)
        info_widget.setToolTip("AOI Information\nRight-click to copy data to clipboard")
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(4, 2, 4, 2)
        info_layout.setSpacing(4)

        # Optional color square
        if color_rgb is not None:
            color_square = QLabel()
            color_square.setFixedSize(12, 12)
            color_square.setStyleSheet(f"""
                QLabel {{
                    background-color: rgb({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]});
                    border: 1px solid white;
                }}
            """)
            info_layout.addWidget(color_square)

        # Optional info text
        if avg_color_info:
            color_label = QLabel(avg_color_info)
            color_label.setAlignment(Qt.AlignCenter)
            color_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 10px;
                }
            """)
            info_layout.addWidget(color_label)

        # Stretch between info and action icons
        info_layout.addStretch()

        # Flag icon (always visible)
        is_flagged = original_index in flagged_set
        flag_color = '#FF7043' if is_flagged else '#808080'
        flag_icon = qta.icon('fa6s.flag', color=flag_color)
        flag_label = QLabel()
        flag_label.setCursor(Qt.PointingHandCursor)
        flag_label.setToolTip("Unflag AOI" if is_flagged else "Flag AOI")
        flag_label.setPixmap(flag_icon.pixmap(16, 16))

        def make_flag_click_handler(aoi_idx):
            return lambda event: self.aoi_controller.toggle_aoi_flag_by_index(aoi_idx)

        flag_label.mousePressEvent = make_flag_click_handler(original_index)
        info_layout.addWidget(flag_label)

        # Comment icon (always visible)
        user_comment = area_of_interest.get('user_comment', '')
        comment_icon = QLabel("📝")
        comment_icon.setCursor(Qt.PointingHandCursor)
        if user_comment:
            comment_icon.setStyleSheet("QLabel { color: #FFD700; font-size: 14px; font-weight: bold; }")
            comment_icon.setToolTip(f"Comment:\n{user_comment}\n\nClick to edit comment")
        else:
            comment_icon.setStyleSheet("QLabel { color: #808080; font-size: 14px; }")
            comment_icon.setToolTip("No comment yet.\nClick to add a comment for this AOI.\n\nUse comments to note important details, observations,\nor actions needed for this detection.")

        def make_comment_click_handler(aoi_idx):
            return lambda event: self.aoi_controller.edit_aoi_comment(aoi_idx)

        comment_icon.mousePressEvent = make_comment_click_handler(original_index)
        info_layout.addWidget(comment_icon)

        # Enable context menu for the info widget
        info_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        info_widget.customContextMenuRequested.connect(
            lambda pos, c=area_of_interest['center'], a=area_of_interest.get('area', 0), info=avg_color_info, idx=original_index: self.aoi_controller.show_aoi_context_menu(pos, info_widget, c, a, info, idx)
        )

        return info_widget

    def _update_count_label(self, filtered_count, total_count):
        """Update the area count label.

        Args:
            filtered_count: Number of AOIs after filtering
            total_count: Total number of AOIs before filtering
        """
        area_count_label = self.aoi_controller.parent.areaCountLabel
        if area_count_label:
            if filtered_count < total_count:
                # Show filtered count vs total
                area_count_label.setText(f"{filtered_count} of {total_count} {'Area' if total_count == 1 else 'Areas'}")
            else:
                # Show just the count
                area_count_label.setText(f"{filtered_count} {'Area' if filtered_count == 1 else 'Areas'} of Interest")

    def update_aoi_selection_style(self, container, selected):
        """Update the visual style of an AOI container based on selection state.

        Args:
            container (QWidget): The AOI container widget
            selected (bool): Whether the container is selected
        """
        if selected:
            # Get the current settings color for the selection (typically magenta/pink)
            color = self.aoi_controller.parent.settings.get('identifier_color', [255, 255, 0])
            container.setStyleSheet(
                f"#AOIItemContainer {{ border: 1px solid #666; border-radius: 5px; background-color: rgba({color[0]}, {color[1]}, {color[2]}, 40); }}"
            )
        else:
            # Transparent background but keep the border
            container.setStyleSheet(
                "#AOIItemContainer { border: 1px solid #666; border-radius: 5px; background-color: transparent; }"
            )
            container.repaint()

    def scroll_to_aoi(self, visible_index):
        """Scroll the AOI list to bring the selected item into view.

        Args:
            visible_index: Index of the AOI in the visible containers list
        """
        aoi_list_widget = self.aoi_controller.parent.aoiListWidget
        if aoi_list_widget and visible_index < aoi_list_widget.count():
            item = aoi_list_widget.item(visible_index)
            if item:
                aoi_list_widget.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    def get_scroll_position(self):
        """Get the current scroll position of the AOI list.

        Returns:
            int: Current scroll position
        """
        aoi_list_widget = self.aoi_controller.parent.aoiListWidget
        return aoi_list_widget.verticalScrollBar().value() if aoi_list_widget else 0

    def set_scroll_position(self, position):
        """Set the scroll position of the AOI list.

        Args:
            position: Scroll position to set
        """
        aoi_list_widget = self.aoi_controller.parent.aoiListWidget
        if aoi_list_widget:
            aoi_list_widget.verticalScrollBar().setValue(position)

    def clear_aoi_display(self):
        """Clear all AOI display elements."""
        aoi_list_widget = self.aoi_controller.parent.aoiListWidget
        if aoi_list_widget:
            aoi_list_widget.clear()
        self.aoi_containers = []
        self.highlights = []

    def _start_batch_loading(self, aois_with_indices, augmented_image, flagged_set):
        """
        Start batch loading of AOI containers.

        Args:
            aois_with_indices: List of (original_index, aoi_data) tuples
            augmented_image: Image array for thumbnails
            flagged_set: Set of flagged AOI indices
        """
        # Initialize batch loading state
        self.batch_loading_state = {
            'aois_with_indices': aois_with_indices,
            'augmented_image': augmented_image,
            'flagged_set': flagged_set,
            'current_index': 0,
            'visible_container_index': 0,
            'total_count': len(aois_with_indices),
            'batch_size': 50  # Process 50 items per batch
        }

        # Show progress widget
        self._show_progress_widget()

        # Start batch timer (10ms intervals for responsive UI)
        self.batch_timer.start(10)

        self.logger.info(f"Starting batch loading of {len(aois_with_indices)} AOIs...")

    def _process_next_batch(self):
        """Process the next batch of AOI containers."""
        if not self.batch_loading_state:
            return

        state = self.batch_loading_state
        start_idx = state['current_index']
        end_idx = min(start_idx + state['batch_size'], state['total_count'])

        # Process batch
        for i in range(start_idx, end_idx):
            original_index, area_of_interest = state['aois_with_indices'][i]
            container = self._create_aoi_container(
                original_index,
                state['visible_container_index'],
                area_of_interest,
                state['augmented_image'],
                state['flagged_set']
            )
            if container:
                self.aoi_containers.append(container)
                state['visible_container_index'] += 1

        # Update progress
        state['current_index'] = end_idx
        progress_percent = int((end_idx / state['total_count']) * 100)
        self._update_progress_widget(progress_percent, end_idx, state['total_count'])

        # Check if done
        if end_idx >= state['total_count']:
            self._finish_batch_loading()

    def _finish_batch_loading(self):
        """Finish batch loading and cleanup."""
        self.batch_timer.stop()
        self._remove_progress_widget()
        self.batch_loading_state = None
        self.logger.info("Batch loading complete")

    def _show_progress_widget(self):
        """Show a progress indicator at the top of the AOI list."""
        aoi_list_widget = self.aoi_controller.parent.aoiListWidget
        if not aoi_list_widget:
            return

        # Create progress widget
        progress_container = QWidget()
        layout = QVBoxLayout(progress_container)
        layout.setContentsMargins(10, 10, 10, 10)

        label = QLabel("Loading AOIs...")
        label.setStyleSheet("color: white; font-size: 11pt;")

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #666;
                border-radius: 3px;
                background-color: #2d2d2d;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)

        layout.addWidget(label)
        layout.addWidget(progress_bar)

        # Add to list as first item
        item = QListWidgetItem(aoi_list_widget)
        item.setSizeHint(progress_container.sizeHint())
        aoi_list_widget.setItemWidget(item, progress_container)

        # Store reference
        self.batch_progress_widget = {
            'item': item,
            'container': progress_container,
            'label': label,
            'progress_bar': progress_bar
        }

    def _update_progress_widget(self, percent, current, total):
        """Update the progress widget."""
        if not self.batch_progress_widget:
            return

        self.batch_progress_widget['label'].setText(f"Loading AOIs... ({current}/{total})")
        self.batch_progress_widget['progress_bar'].setValue(percent)

    def _remove_progress_widget(self):
        """Remove the progress widget."""
        if not self.batch_progress_widget:
            return

        aoi_list_widget = self.aoi_controller.parent.aoiListWidget
        if aoi_list_widget:
            row = aoi_list_widget.row(self.batch_progress_widget['item'])
            if row >= 0:
                aoi_list_widget.takeItem(row)

        self.batch_progress_widget = None

    def refresh_aoi_display(self):
        """Refresh the AOI display with current sort/filter settings."""
        if not hasattr(self.aoi_controller.parent, 'current_image') or not hasattr(self.aoi_controller.parent, 'images'):
            return

        image = self.aoi_controller.parent.images[self.aoi_controller.parent.current_image]
        if hasattr(self.aoi_controller.parent, 'current_image_array') and self.aoi_controller.parent.current_image_array is not None:
            # Save scroll position and selection
            scroll_pos = self.get_scroll_position()
            selected_idx = self.aoi_controller.selected_aoi_index

            # Reload AOIs
            self.load_areas_of_interest(
                self.aoi_controller.parent.current_image_array,
                image.get('areas_of_interest', [])
            )

            # Restore selection and scroll
            self.aoi_controller.selected_aoi_index = selected_idx
            self.set_scroll_position(scroll_pos)

    def get_aoi_containers(self):
        """Get the list of AOI container widgets.

        Returns:
            list: List of AOI container widgets
        """
        return self.aoi_containers

    def get_highlights(self):
        """Get the list of highlight widgets.

        Returns:
            list: List of highlight widgets
        """
        return self.highlights
