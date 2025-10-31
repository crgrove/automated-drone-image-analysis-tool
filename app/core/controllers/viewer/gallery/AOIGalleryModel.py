"""
AOIGalleryModel - Qt Model for efficient virtual scrolling of AOI thumbnails.

This model provides a flattened view of all AOIs from all images, supporting
lazy loading and efficient rendering of large datasets.
"""

from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QSize, QThread, Signal, Slot
from PySide6.QtGui import QPixmap, QIcon, QImage, QColor
import numpy as np
import qimage2ndarray
from pathlib import Path
from typing import Dict, Tuple, Optional
from core.services.LoggerService import LoggerService
from core.services.AOIService import AOIService
from core.services.ColorCacheService import ColorCacheService
from .ThumbnailLoader import ThumbnailLoader


class AOIGalleryModel(QAbstractListModel):
    """
    Model for displaying AOIs from all images in a gallery view.

    Supports virtual scrolling, lazy thumbnail loading, and efficient rendering
    of large datasets (1000+ AOIs).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Data storage: list of (image_index, aoi_index, aoi_data) tuples
        self.aoi_items = []

        # Reference to parent viewer for accessing images
        self.viewer = None

        # Fast in-memory cache: {(image_idx, aoi_idx): QIcon}
        self.thumbnail_cache: Dict[Tuple[int, int], QIcon] = {}

        # Thumbnail size
        self.thumbnail_size = QSize(180, 180)

        # Placeholder icon (gray square)
        self.placeholder_icon = self._create_placeholder_icon()

        # Background thumbnail loader
        self.thumbnail_loader = ThumbnailLoader(self)
        self.thumbnail_loader.thumbnail_ready.connect(self._on_thumbnail_ready)
        self.thumbnail_loader.batch_complete.connect(self._on_batch_complete)

        # Index mapping for fast lookups
        self.row_to_aoi: Dict[int, Tuple[int, int]] = {}  # row -> (image_idx, aoi_idx)
        self.aoi_to_row: Dict[Tuple[int, int], int] = {}  # (image_idx, aoi_idx) -> row

        # Cache for AOIService instances per image
        self._aoi_service_cache: Dict[int, AOIService] = {}

        # Pre-computed color info cache: {(image_idx, aoi_idx): color_info_dict}
        self._color_info_cache: Dict[Tuple[int, int], Optional[dict]] = {}

        # Color cache service for per-dataset cached colors
        self.color_cache_service: Optional[ColorCacheService] = None
        self.dataset_dir: Optional[Path] = None

    def set_viewer(self, viewer):
        """Set reference to the parent viewer."""
        self.viewer = viewer

    def set_dataset_directory(self, xml_path: str):
        """
        Set the dataset directory for accessing per-dataset caches.

        Args:
            xml_path: Path to the XML file (used to determine dataset directory)
        """
        try:
            self.dataset_dir = Path(xml_path).parent
            color_cache_dir = self.dataset_dir / '.color_cache'
            thumbnail_cache_dir = self.dataset_dir / '.thumbnails'

            # Initialize color cache service if cache directory exists
            if color_cache_dir.exists():
                self.color_cache_service = ColorCacheService(cache_dir=str(color_cache_dir))
                self.logger.info(f"Using per-dataset color cache from {color_cache_dir}")
            else:
                self.logger.debug(f"No color cache found at {color_cache_dir}, will calculate on-demand")
                self.color_cache_service = None

            # Update thumbnail loader with dataset cache directory
            if thumbnail_cache_dir.exists():
                self.thumbnail_loader.set_dataset_cache_dir(str(thumbnail_cache_dir))
                self.logger.info(f"Using per-dataset thumbnail cache from {thumbnail_cache_dir}")
            else:
                self.logger.debug(f"No thumbnail cache found at {thumbnail_cache_dir}, will use global cache")

        except Exception as e:
            self.logger.error(f"Error setting dataset directory: {e}")
            self.color_cache_service = None

    def _create_placeholder_icon(self):
        """Create a placeholder icon for thumbnails that haven't loaded yet."""
        pixmap = QPixmap(self.thumbnail_size)
        pixmap.fill(QColor(60, 60, 60))
        return QIcon(pixmap)

    @Slot(int, int, QIcon)
    def _on_thumbnail_ready(self, image_idx: int, aoi_idx: int, icon: QIcon):
        """Handle thumbnail ready signal from background loader."""
        # Add to cache
        cache_key = (image_idx, aoi_idx)
        self.thumbnail_cache[cache_key] = icon

        # Find row and emit dataChanged
        if cache_key in self.aoi_to_row:
            row = self.aoi_to_row[cache_key]
            index = self.index(row, 0)
            self.dataChanged.emit(index, index, [Qt.DecorationRole])

    @Slot(int)
    def _on_batch_complete(self, count: int):
        """Handle batch complete signal."""
        self.logger.debug(f"Loaded {count} thumbnails")

    def set_aoi_items(self, items):
        """
        Set the AOI items to display.

        Args:
            items: List of (image_index, aoi_index, aoi_data) tuples
        """
        self.beginResetModel()

        # Clear old data
        self.aoi_items = items
        self.thumbnail_cache.clear()
        self.thumbnail_loader.clear_queue()
        self._color_info_cache.clear()

        # Rebuild index mappings for O(1) lookups
        self.row_to_aoi.clear()
        self.aoi_to_row.clear()

        for row, (img_idx, aoi_idx, aoi_data) in enumerate(items):
            key = (img_idx, aoi_idx)
            self.row_to_aoi[row] = key
            self.aoi_to_row[key] = row

        self.endResetModel()

        # Pre-calculate color information for all AOIs in background
        self._precalculate_color_info()

        # Start loading visible thumbnails
        self._queue_visible_thumbnails()

    def rowCount(self, parent=QModelIndex()):
        """Return the number of AOIs."""
        if parent.isValid():
            return 0
        return len(self.aoi_items)

    def data(self, index, role=Qt.DisplayRole):
        """
        Return data for the given index and role.

        Args:
            index: QModelIndex of the item
            role: Qt.ItemDataRole

        Returns:
            Data for the requested role
        """
        if not index.isValid() or index.row() >= len(self.aoi_items):
            return None

        image_idx, aoi_idx, aoi_data = self.aoi_items[index.row()]

        if role == Qt.DecorationRole:
            # Return thumbnail icon
            return self._get_thumbnail_icon(image_idx, aoi_idx, aoi_data)

        elif role == Qt.DisplayRole:
            # Return display text (shown below thumbnail)
            return self._get_display_text(image_idx, aoi_idx, aoi_data)

        elif role == Qt.ToolTipRole:
            # Return tooltip with detailed info
            return self._get_tooltip_text(image_idx, aoi_idx, aoi_data)

        elif role == Qt.UserRole:
            # Return raw data for custom rendering with color info
            color_info = self._get_color_info(image_idx, aoi_idx)
            return {
                'image_idx': image_idx,
                'aoi_idx': aoi_idx,
                'aoi_data': aoi_data,
                'color_info': color_info
            }

        return None

    def _get_thumbnail_icon(self, image_idx, aoi_idx, aoi_data):
        """
        Get thumbnail icon for an AOI using multi-level caching.

        Args:
            image_idx: Index of the parent image
            aoi_idx: Index of the AOI within the image
            aoi_data: AOI dictionary

        Returns:
            QIcon - cached thumbnail or placeholder
        """
        cache_key = (image_idx, aoi_idx)

        # Check in-memory cache first (fastest)
        if cache_key in self.thumbnail_cache:
            return self.thumbnail_cache[cache_key]

        # Queue for background loading if needed
        if self.viewer and image_idx < len(self.viewer.images):
            image = self.viewer.images[image_idx]
            # Use path for loading the actual image
            image_path = image.get('path', '')
            # Use xml_path for legacy cache lookups (original path before relocation)
            xml_path = image.get('xml_path', '')

            if image_path:
                # Queue for background loading (non-blocking)
                self.thumbnail_loader.queue_thumbnail(
                    image_idx, aoi_idx, image_path, aoi_data,
                    xml_path=xml_path,
                    high_priority=False  # Will be set to high priority if visible
                )

        # Return placeholder while loading
        return self.placeholder_icon

    def _queue_visible_thumbnails(self):
        """Queue visible thumbnails for priority loading."""
        # This will be called by the UI component
        pass

    def queue_thumbnails_for_range(self, start_row: int, end_row: int, high_priority: bool = False):
        """
        Queue thumbnails for a range of rows.

        Args:
            start_row: Start row index
            end_row: End row index (inclusive)
            high_priority: Whether these are high priority (visible)
        """
        if not self.viewer:
            return

        for row in range(start_row, min(end_row + 1, len(self.aoi_items))):
            if row < 0 or row >= len(self.aoi_items):
                continue

            image_idx, aoi_idx, aoi_data = self.aoi_items[row]
            cache_key = (image_idx, aoi_idx)

            # Skip if already cached
            if cache_key in self.thumbnail_cache:
                continue

            # Get image path
            if image_idx < len(self.viewer.images):
                image = self.viewer.images[image_idx]
                # Use path for loading the actual image
                image_path = image.get('path', '')
                # Use xml_path for legacy cache lookups (original path before relocation)
                xml_path = image.get('xml_path', '')

                if image_path:
                    self.thumbnail_loader.queue_thumbnail(
                        image_idx, aoi_idx, image_path, aoi_data,
                        xml_path=xml_path,
                        high_priority=high_priority
                    )

    def _generate_thumbnail_fast(self, image_idx, aoi_idx, aoi_data, image_array):
        """
        Generate thumbnail quickly from an already-loaded image array.

        Args:
            image_idx: Index of the parent image
            aoi_idx: Index of the AOI within the image
            aoi_data: AOI dictionary
            image_array: Pre-loaded numpy array

        Returns:
            QIcon or None
        """
        cache_key = (image_idx, aoi_idx)

        try:
            # Crop AOI region
            thumbnail_array = self._crop_aoi_region(image_array, aoi_data)
            if thumbnail_array is None:
                return None

            # Convert to QPixmap
            qimage = qimage2ndarray.array2qimage(thumbnail_array, normalize=False)
            pixmap = QPixmap.fromImage(qimage)

            # Scale to thumbnail size (fast)
            if pixmap.width() > self.thumbnail_size.width() or pixmap.height() > self.thumbnail_size.height():
                pixmap = pixmap.scaled(
                    self.thumbnail_size,
                    Qt.KeepAspectRatio,
                    Qt.FastTransformation  # Use fast scaling
                )

            icon = QIcon(pixmap)

            # Cache the icon (with size limit)
            if len(self.thumbnail_cache) >= self.max_cache_size:
                # Remove oldest entries (simple FIFO)
                keys_to_remove = list(self.thumbnail_cache.keys())[:200]
                for key in keys_to_remove:
                    del self.thumbnail_cache[key]

            self.thumbnail_cache[cache_key] = icon
            return icon

        except Exception as e:
            self.logger.error(f"Error generating thumbnail for image {image_idx}, AOI {aoi_idx}: {e}")
            return None


    def _crop_aoi_region(self, image_array, aoi_data):
        """
        Crop the AOI region from the image array.

        Args:
            image_array: Full image array (H, W, C)
            aoi_data: AOI dictionary with 'center' and 'radius'

        Returns:
            Cropped array or None
        """
        try:
            center = aoi_data.get('center')
            radius = aoi_data.get('radius', 50)

            if not center:
                return None

            cx, cy = center
            crop_radius = radius + 10  # Add padding

            # Calculate crop bounds
            h, w = image_array.shape[:2]
            sx = max(0, int(cx - crop_radius))
            sy = max(0, int(cy - crop_radius))
            ex = min(w, int(cx + crop_radius))
            ey = min(h, int(cy + crop_radius))

            # Crop the region
            cropped = image_array[sy:ey, sx:ex]

            return cropped

        except Exception as e:
            self.logger.error(f"Error cropping AOI region: {e}")
            return None

    def _get_display_text(self, image_idx, aoi_idx, aoi_data):
        """Get display text for an AOI item."""
        try:
            if not self.viewer or image_idx >= len(self.viewer.images):
                return f"AOI {aoi_idx}"

            image = self.viewer.images[image_idx]
            image_name = image.get('name', f'Image {image_idx}')

            # Get confidence if available
            confidence = aoi_data.get('confidence')
            if confidence is not None:
                return f"{image_name}\nAOI {aoi_idx} - {confidence:.1%}"
            else:
                return f"{image_name}\nAOI {aoi_idx}"

        except Exception:
            return f"AOI {aoi_idx}"

    def _get_tooltip_text(self, image_idx, aoi_idx, aoi_data):
        """Get tooltip text with detailed AOI information."""
        try:
            if not self.viewer or image_idx >= len(self.viewer.images):
                return ""

            image = self.viewer.images[image_idx]
            image_name = image.get('name', f'Image {image_idx}')

            lines = [f"Image: {image_name}", f"AOI Index: {aoi_idx}"]

            # Add AOI details
            center = aoi_data.get('center')
            if center:
                lines.append(f"Center: ({center[0]:.0f}, {center[1]:.0f})")

            area = aoi_data.get('area')
            if area:
                lines.append(f"Area: {area:.0f} px²")

            confidence = aoi_data.get('confidence')
            if confidence is not None:
                lines.append(f"Confidence: {confidence:.1%}")

            flagged = aoi_data.get('flagged', False)
            if flagged:
                lines.append("🚩 Flagged")

            comment = aoi_data.get('user_comment', '').strip()
            if comment:
                lines.append(f"Comment: {comment}")

            return '\n'.join(lines)

        except Exception:
            return ""

    def clear_cache(self):
        """Clear the thumbnail cache to free memory."""
        self.thumbnail_cache.clear()
        self.thumbnail_loader.clear_queue()
        self._aoi_service_cache.clear()
        self._color_info_cache.clear()

    def cleanup(self):
        """Cleanup resources when model is destroyed."""
        if hasattr(self, 'thumbnail_loader'):
            self.thumbnail_loader.shutdown()

    def get_aoi_info(self, index):
        """
        Get AOI information for the given model index.

        Args:
            index: QModelIndex

        Returns:
            Tuple of (image_idx, aoi_idx, aoi_data) or None
        """
        if not index.isValid() or index.row() >= len(self.aoi_items):
            return None
        return self.aoi_items[index.row()]

    def prefetch_current_image_thumbnails(self):
        """
        Prioritize loading thumbnails for the current image.
        This is called after an image loads to quickly populate its thumbnails.
        """
        if not self.viewer:
            return

        try:
            current_idx = self.viewer.current_image

            # Find all AOIs from current image and queue them
            rows_to_queue = []
            for row in range(len(self.aoi_items)):
                image_idx, aoi_idx, aoi_data = self.aoi_items[row]

                # Only queue for current image
                if image_idx == current_idx:
                    rows_to_queue.append(row)

            # Queue with high priority
            if rows_to_queue:
                start_row = min(rows_to_queue)
                end_row = max(rows_to_queue)
                self.queue_thumbnails_for_range(start_row, end_row, high_priority=True)

        except Exception as e:
            self.logger.error(f"Error prefetching thumbnails: {e}")

    def _precalculate_color_info(self):
        """
        Pre-calculate color information for all AOIs to avoid expensive calculations during scrolling.

        Checks per-dataset cache first, only calculates if not cached.
        """
        if not self.viewer or not self.aoi_items:
            return

        self.logger.info(f"Loading color info for {len(self.aoi_items)} AOIs...")

        try:
            cached_count = 0
            calculated_count = 0

            for img_idx, aoi_idx, aoi_data in self.aoi_items:
                cache_key = (img_idx, aoi_idx)

                # First, try to get from per-dataset cache
                if self.color_cache_service and img_idx < len(self.viewer.images):
                    image = self.viewer.images[img_idx]
                    # Use path for loading the actual image
                    image_path = image.get('path', '')
                    # Use xml_path for legacy cache lookups (original path before relocation)
                    xml_path = image.get('xml_path', '')

                    # Store xml_path temporarily in aoi_data for cache lookups
                    aoi_data_with_xml = aoi_data.copy()
                    if xml_path:
                        aoi_data_with_xml['_xml_path'] = xml_path

                    cached_color = self.color_cache_service.get_color_info(image_path, aoi_data_with_xml)

                    if cached_color:
                        self._color_info_cache[cache_key] = cached_color
                        cached_count += 1
                        continue

                # Not in cache, calculate it
                if img_idx not in self._aoi_service_cache:
                    if img_idx < len(self.viewer.images):
                        image = self.viewer.images[img_idx]
                        self._aoi_service_cache[img_idx] = AOIService(image)

                aoi_service = self._aoi_service_cache.get(img_idx)
                if aoi_service:
                    # Calculate color info
                    color_result = aoi_service.get_aoi_representative_color(aoi_data)
                    if color_result:
                        self._color_info_cache[cache_key] = {
                            'rgb': color_result['rgb'],
                            'hex': color_result['hex'],
                            'hue_degrees': color_result['hue_degrees']
                        }
                        calculated_count += 1
                    else:
                        self._color_info_cache[cache_key] = None
                else:
                    self._color_info_cache[cache_key] = None

            if cached_count > 0:
                self.logger.info(f"Loaded {cached_count} colors from cache, calculated {calculated_count}")
            else:
                self.logger.info(f"Calculated {calculated_count} colors (no cache available)")

        except Exception as e:
            self.logger.error(f"Error loading color info: {e}")

    def _get_color_info(self, image_idx, aoi_idx):
        """
        Get color information for an AOI from cache.

        Args:
            image_idx: Index of the image containing the AOI
            aoi_idx: Index of the AOI within the image

        Returns:
            dict with 'rgb', 'hex', and 'hue_degrees' keys, or None
        """
        # Return cached color info (already pre-calculated)
        cache_key = (image_idx, aoi_idx)
        return self._color_info_cache.get(cache_key)
