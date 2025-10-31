"""
BackfillCacheService - Regenerates thumbnail and color caches for existing datasets.

This service is used to create caches for datasets that were processed before
the caching feature was implemented, or to regenerate caches that were lost.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal

from core.services.LoggerService import LoggerService
from core.services.ThumbnailCacheService import ThumbnailCacheService
from core.services.ColorCacheService import ColorCacheService
from core.services.AOIService import AOIService
from core.services.XmlService import XmlService


class BackfillCacheService(QObject):
    """
    Service for regenerating thumbnail and color caches for existing datasets.

    This reads an existing ADIAT_Data.xml file and generates thumbnails
    and color info for all AOIs in the dataset.
    """

    # Signals for progress updates
    progress_message = Signal(str)  # Progress message
    progress_percent = Signal(int)  # Percentage complete (0-100)
    complete = Signal(int, int)  # (total_images, total_aois)
    error = Signal(str)  # Error message

    def __init__(self):
        """Initialize the backfill cache service."""
        super().__init__()
        self.logger = LoggerService()
        self.cancelled = False

    def regenerate_cache(self, xml_path: str) -> bool:
        """
        Regenerate thumbnail and color caches for a dataset.

        Args:
            xml_path: Path to the ADIAT_Data.xml file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate XML path
            xml_file = Path(xml_path)
            if not xml_file.exists():
                self.error.emit(f"XML file not found: {xml_path}")
                return False

            # Load XML data
            self.progress_message.emit("Loading dataset XML...")
            xml_service = XmlService(xml_path)
            images = xml_service.get_images()

            if not images:
                self.error.emit("No images found in dataset")
                return False

            # Set up cache directories
            dataset_dir = xml_file.parent
            thumbnail_cache_dir = dataset_dir / '.thumbnails'
            color_cache_dir = dataset_dir / '.color_cache'

            # Create cache directories
            thumbnail_cache_dir.mkdir(parents=True, exist_ok=True)
            color_cache_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Creating caches in {dataset_dir}")
            self.progress_message.emit(f"Creating caches for {len(images)} images...")

            # Initialize cache services
            thumbnail_service = ThumbnailCacheService(dataset_cache_dir=str(thumbnail_cache_dir))
            color_service = ColorCacheService(cache_dir=str(color_cache_dir))

            # Load existing cache if present
            color_service.load_cache_file()

            # Process each image
            total_images = len(images)
            total_aois = 0
            processed_images = 0

            for img_idx, image in enumerate(images):
                if self.cancelled:
                    self.progress_message.emit("Cache generation cancelled")
                    return False

                # Get original image path (not mask)
                image_path = image.get('original_path') or image.get('path')
                if not image_path:
                    continue

                # Check if file exists
                if not Path(image_path).exists():
                    self.logger.warning(f"Image not found: {image_path}")
                    continue

                areas_of_interest = image.get('areas_of_interest', [])
                if not areas_of_interest:
                    continue

                # Update progress
                percent = int((processed_images / total_images) * 100)
                self.progress_percent.emit(percent)
                self.progress_message.emit(
                    f"Processing {Path(image_path).name} ({len(areas_of_interest)} AOIs)..."
                )

                # Load image
                try:
                    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                    if img is None:
                        self.logger.error(f"Could not load image: {image_path}")
                        continue

                    # Generate cache for each AOI
                    aoi_count = self._generate_aoi_cache(
                        img=img,
                        image_path=image_path,
                        image_data=image,
                        areas_of_interest=areas_of_interest,
                        thumbnail_service=thumbnail_service,
                        color_service=color_service
                    )

                    total_aois += aoi_count
                    processed_images += 1

                except Exception as e:
                    self.logger.error(f"Error processing {image_path}: {e}")
                    continue

            # Save color cache to disk
            self.progress_message.emit("Saving color cache...")
            color_service.save_cache_file()

            # Complete
            self.progress_percent.emit(100)
            self.progress_message.emit(
                f"Cache generation complete: {processed_images} images, {total_aois} AOIs"
            )
            self.complete.emit(processed_images, total_aois)

            self.logger.info(f"Cache regeneration complete: {processed_images} images, {total_aois} AOIs")
            return True

        except Exception as e:
            error_msg = f"Error regenerating cache: {e}"
            self.logger.error(error_msg)
            self.error.emit(error_msg)
            return False

    def _generate_aoi_cache(self, img: np.ndarray, image_path: str, image_data: dict,
                           areas_of_interest: list, thumbnail_service: ThumbnailCacheService,
                           color_service: ColorCacheService) -> int:
        """
        Generate thumbnails and color info for all AOIs in an image.

        Args:
            img: Loaded image array (BGR format from cv2.imread)
            image_path: Path to the source image
            image_data: Image dictionary from XML
            areas_of_interest: List of AOI dictionaries
            thumbnail_service: Thumbnail cache service
            color_service: Color cache service

        Returns:
            Number of AOIs processed
        """
        try:
            # Convert BGR to RGB for AOIService (avoids reloading image)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Create AOIService for color calculation with pre-loaded image
            aoi_service = AOIService(image_data, img_array=img_rgb)

            cached_count = 0

            for aoi in areas_of_interest:
                if self.cancelled:
                    break

                center = aoi.get('center')
                radius = aoi.get('radius', 50)

                if not center:
                    continue

                cx, cy = center

                # Calculate crop bounds with padding
                crop_radius = radius + 10
                x1 = int(max(0, cx - crop_radius))
                y1 = int(max(0, cy - crop_radius))
                x2 = int(min(img.shape[1], cx + crop_radius))
                y2 = int(min(img.shape[0], cy + crop_radius))

                # Extract thumbnail region
                try:
                    thumbnail_region = img[y1:y2, x1:x2]

                    if thumbnail_region.size == 0:
                        continue

                    # Resize to 180x180
                    thumbnail_resized = cv2.resize(
                        thumbnail_region,
                        (180, 180),
                        interpolation=cv2.INTER_LANCZOS4
                    )

                    # Convert BGR to RGB
                    if len(thumbnail_resized.shape) == 3 and thumbnail_resized.shape[2] == 3:
                        thumbnail_rgb = cv2.cvtColor(thumbnail_resized, cv2.COLOR_BGR2RGB)
                    else:
                        thumbnail_rgb = thumbnail_resized

                    # Save thumbnail to cache
                    thumbnail_service.save_thumbnail_from_array(
                        image_path,
                        aoi,
                        thumbnail_rgb,
                        cache_dir=Path(thumbnail_service.dataset_cache_dir) if thumbnail_service.dataset_cache_dir else None
                    )

                    # Calculate and save color info
                    color_result = aoi_service.get_aoi_representative_color(aoi)
                    if color_result:
                        color_service.save_color_info(image_path, aoi, {
                            'rgb': color_result['rgb'],
                            'hex': color_result['hex'],
                            'hue_degrees': color_result['hue_degrees']
                        })

                    cached_count += 1

                except Exception as e:
                    self.logger.error(f"Error generating cache for AOI: {e}")
                    continue

            return cached_count

        except Exception as e:
            self.logger.error(f"Error in _generate_aoi_cache: {e}")
            return 0

    def cancel(self):
        """Cancel the current cache regeneration."""
        self.cancelled = True
        self.logger.info("Cache regeneration cancelled")
