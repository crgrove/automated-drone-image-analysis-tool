"""
MaskManager - Service for creating and caching processing masks.

Handles mask generation, caching, and resizing for frame and image mask modes.
Used by streaming detection algorithms to define processing regions.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Dict, Any
from threading import Lock


class MaskManager:
    """
    Manages processing masks for streaming detection algorithms.

    Handles:
    - Frame mode: Creates rectangular mask with pixel buffer from edges
    - Image mask mode: Loads and scales image masks
    - Caching: Maintains cached masks at both original and processing resolutions

    Thread-safe for use in worker threads.
    """

    def __init__(self):
        self._lock = Lock()
        self._cache: Dict[str, Any] = {
            'mask_original': None,
            'mask_processing': None,
            'original_resolution': None,
            'processing_resolution': None,
            'config_hash': None,
        }

    def get_mask(self, config: Dict[str, Any],
                 original_resolution: Tuple[int, int],
                 processing_resolution: Optional[Tuple[int, int]] = None) -> Optional[np.ndarray]:
        """
        Get processing mask at the specified resolution.

        The mask is created at original resolution and resized once to processing
        resolution. Subsequent calls with the same config return the cached mask.

        Args:
            config: Mask configuration dict with keys:
                - mask_enabled: bool
                - mask_mode: 'frame' or 'image'
                - frame_buffer_pixels: int (for frame mode)
                - mask_image_path: str (for image mode)
            original_resolution: (width, height) of original video frame
            processing_resolution: (width, height) for processing, or None for original

        Returns:
            Binary mask (255=process, 0=exclude) at processing resolution,
            or None if mask is disabled
        """
        if not config.get('mask_enabled', False):
            return None

        target_resolution = processing_resolution or original_resolution

        with self._lock:
            # Check if we can use cached mask
            config_hash = self._compute_config_hash(config, original_resolution)

            if (self._cache['config_hash'] == config_hash and
                self._cache['processing_resolution'] == target_resolution and
                    self._cache['mask_processing'] is not None):
                return self._cache['mask_processing']

            # Need to regenerate mask
            mask_original = self._create_mask(config, original_resolution)

            if mask_original is None:
                return None

            # Resize to processing resolution if needed
            if target_resolution != original_resolution:
                mask_processing = cv2.resize(
                    mask_original,
                    target_resolution,
                    interpolation=cv2.INTER_NEAREST  # Preserve binary values
                )
            else:
                mask_processing = mask_original.copy()

            # Update cache
            self._cache['mask_original'] = mask_original
            self._cache['mask_processing'] = mask_processing
            self._cache['original_resolution'] = original_resolution
            self._cache['processing_resolution'] = target_resolution
            self._cache['config_hash'] = config_hash

            return mask_processing

    def get_mask_for_rendering(self, config: Dict[str, Any],
                               render_resolution: Tuple[int, int],
                               original_resolution: Tuple[int, int]) -> Optional[np.ndarray]:
        """
        Get mask scaled for rendering overlay.

        Args:
            config: Mask configuration
            render_resolution: Resolution of the render frame (width, height)
            original_resolution: Original video resolution (width, height)

        Returns:
            Mask at render resolution for overlay visualization,
            or None if mask/overlay disabled
        """
        if not config.get('mask_enabled', False) or not config.get('show_mask_overlay', True):
            return None

        with self._lock:
            # Get original mask first (may already be cached)
            config_hash = self._compute_config_hash(config, original_resolution)

            if self._cache['mask_original'] is None or \
               self._cache['config_hash'] != config_hash:
                mask_original = self._create_mask(config, original_resolution)
                if mask_original is None:
                    return None
                self._cache['mask_original'] = mask_original
                self._cache['original_resolution'] = original_resolution
                self._cache['config_hash'] = config_hash
            else:
                mask_original = self._cache['mask_original']

            if mask_original is None:
                return None

            # Resize to render resolution
            if render_resolution != original_resolution:
                return cv2.resize(
                    mask_original,
                    render_resolution,
                    interpolation=cv2.INTER_NEAREST
                )
            return mask_original.copy()

    def get_frame_bounds(self, config: Dict[str, Any],
                         resolution: Tuple[int, int],
                         scale_factor: float = 1.0) -> Optional[Tuple[int, int, int, int]]:
        """
        Get frame buffer bounds for rectangle rendering.

        Args:
            config: Mask configuration
            resolution: Resolution to get bounds for (width, height)
            scale_factor: Scale factor to apply to buffer pixels

        Returns:
            Tuple of (x1, y1, x2, y2) for inner rectangle bounds,
            or None if frame buffer not enabled or mask disabled
        """
        if not config.get('mask_enabled', False):
            return None

        if not config.get('frame_mask_enabled', False):
            return None

        width, height = resolution
        buffer_px = config.get('frame_buffer_pixels', 50)

        # Apply scale factor for rendering at different resolutions
        scaled_buffer = int(buffer_px * scale_factor)

        # Calculate bounds
        x1 = min(scaled_buffer, width // 2)
        y1 = min(scaled_buffer, height // 2)
        x2 = max(width - scaled_buffer, width // 2)
        y2 = max(height - scaled_buffer, height // 2)

        return (x1, y1, x2, y2)

    def _create_mask(self, config: Dict[str, Any],
                     resolution: Tuple[int, int]) -> Optional[np.ndarray]:
        """Create mask at specified resolution, combining modes if both enabled."""
        width, height = resolution

        frame_enabled = config.get('frame_mask_enabled', False)
        image_enabled = config.get('image_mask_enabled', False)

        frame_mask = None
        image_mask = None

        if frame_enabled:
            frame_mask = self._create_frame_mask(config, width, height)

        if image_enabled:
            image_mask = self._create_image_mask(config, width, height)

        # Combine masks with AND logic
        if frame_mask is not None and image_mask is not None:
            return cv2.bitwise_and(frame_mask, image_mask)
        elif frame_mask is not None:
            return frame_mask
        elif image_mask is not None:
            return image_mask

        return None

    def _create_frame_mask(self, config: Dict[str, Any],
                           width: int, height: int) -> np.ndarray:
        """
        Create rectangular frame mask with pixel buffer from edges.

        White (255) = process area (inside rectangle)
        Black (0) = excluded area (buffer zone at edges)
        """
        buffer_px = config.get('frame_buffer_pixels', 50)

        # Create black mask (all excluded)
        mask = np.zeros((height, width), dtype=np.uint8)

        # Calculate inner rectangle bounds
        x1 = min(buffer_px, width // 2)
        y1 = min(buffer_px, height // 2)
        x2 = max(width - buffer_px, width // 2)
        y2 = max(height - buffer_px, height // 2)

        # Fill inner rectangle with white (process area)
        mask[y1:y2, x1:x2] = 255

        return mask

    def _create_image_mask(self, config: Dict[str, Any],
                           width: int, height: int) -> Optional[np.ndarray]:
        """
        Load and scale image mask to target resolution.

        White (255) = process area
        Black (0) = excluded area
        """
        mask_path = config.get('mask_image_path')

        if not mask_path:
            return None

        # Load mask image as grayscale
        mask_img = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask_img is None:
            return None

        # Scale to target resolution
        mask_scaled = cv2.resize(mask_img, (width, height),
                                 interpolation=cv2.INTER_LINEAR)

        # Threshold to ensure binary (handle any anti-aliasing from scaling)
        _, mask_binary = cv2.threshold(mask_scaled, 127, 255, cv2.THRESH_BINARY)

        return mask_binary

    def _compute_config_hash(self, config: Dict[str, Any],
                             resolution: Tuple[int, int]) -> str:
        """Compute hash of config for cache invalidation."""
        return f"{
            config.get('frame_mask_enabled')}_{
            config.get('image_mask_enabled')}_{
            config.get('frame_buffer_pixels')}_{
                config.get('mask_image_path')}_{resolution}"

    def invalidate_cache(self):
        """Force cache invalidation."""
        with self._lock:
            self._cache = {
                'mask_original': None,
                'mask_processing': None,
                'original_resolution': None,
                'processing_resolution': None,
                'config_hash': None,
            }

    @staticmethod
    def validate_mask_image(file_path: str,
                            video_aspect_ratio: Optional[float] = None,
                            tolerance: float = 0.05) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]]]:
        """
        Validate a mask image file.

        Args:
            file_path: Path to the mask image
            video_aspect_ratio: Expected aspect ratio (width/height), or None to skip check
            tolerance: Aspect ratio tolerance (default 5%)

        Returns:
            Tuple of (is_valid, error_message, image_dimensions)
        """
        # Try to load the image
        mask_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if mask_img is None:
            return (False, "Could not load image file", None)

        mask_h, mask_w = mask_img.shape[:2]
        dimensions = (mask_w, mask_h)

        # Check aspect ratio if provided
        if video_aspect_ratio is not None and mask_h > 0:
            mask_aspect = mask_w / mask_h
            aspect_diff = abs(mask_aspect - video_aspect_ratio) / video_aspect_ratio

            if aspect_diff > tolerance:
                return (True,
                        f"Aspect ratio mismatch: mask is {mask_aspect:.2f}, video is {video_aspect_ratio:.2f}",
                        dimensions)

        return (True, None, dimensions)
