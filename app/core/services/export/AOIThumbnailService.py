"""
AOIThumbnailService - Generates zoomed-in AOI images for export.

Creates a cropped, "zoomed in" view centered on an area of interest so it can be
attached to an export (for example, uploaded to a CalTopo marker) instead of, or
in addition to, the full overhead image.
"""

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw

from core.services.LoggerService import LoggerService


class AOIThumbnailService:
    """
    Service for generating zoomed AOI images (thumbnails) on disk.

    The generated files are written to a working directory (a temporary directory
    by default) so they can be uploaded by an export routine and then removed with
    :meth:`cleanup`.
    """

    # How much context to keep around the AOI, as a multiple of the AOI radius
    DEFAULT_CONTEXT_MULTIPLIER = 6.0
    # Never crop tighter than this many pixels around the AOI center
    MIN_CROP_RADIUS_PX = 60
    # Output images are scaled into this range (longest edge, in pixels)
    MIN_OUTPUT_SIZE = 800
    MAX_OUTPUT_SIZE = 1600
    # Composite (multi-zoom) images may be larger since they contain the full frame
    MAX_COMPOSITE_SIZE = 2048
    JPEG_QUALITY = 90
    # Default color of the circle drawn around the AOI
    DEFAULT_HIGHLIGHT_RGB = (255, 0, 0)

    def __init__(self, output_dir: Optional[str] = None, logger=None):
        """
        Initialize the service.

        Args:
            output_dir (str, optional): Directory to write generated images to. If
                omitted, a temporary directory is created on first use and removed
                by :meth:`cleanup`.
            logger: Optional LoggerService instance.
        """
        self.logger = logger or LoggerService()
        self._output_dir = Path(output_dir) if output_dir else None
        self._owns_output_dir = output_dir is None
        self._used_names = set()

    @property
    def output_dir(self) -> Path:
        """
        Return the directory generated images are written to, creating it if needed.

        Returns:
            Path: The output directory.
        """
        if self._output_dir is None:
            self._output_dir = Path(tempfile.mkdtemp(prefix="adiat_aoi_thumbnails_"))
        else:
            self._output_dir.mkdir(parents=True, exist_ok=True)
        return self._output_dir

    def generate_thumbnail(self, image_path: str, aoi: Dict[str, Any], output_name: Optional[str] = None,
                           context_multiplier: Optional[float] = None, draw_highlight: bool = True,
                           highlight_rgb: Optional[Tuple[int, int, int]] = None) -> Optional[str]:
        """
        Generate a zoomed image centered on an AOI.

        Args:
            image_path (str): Path to the source image.
            aoi (dict): AOI dictionary containing 'center' and (optionally) 'radius'.
            output_name (str, optional): Base name (without extension) for the generated
                file. Defaults to the source file name.
            context_multiplier (float, optional): How much context to keep around the
                AOI, as a multiple of the AOI radius.
            draw_highlight (bool): Whether to draw a circle around the AOI.
            highlight_rgb (tuple, optional): RGB color of the highlight circle.

        Returns:
            str: Path to the generated image, or None if it could not be created.
        """
        try:
            if not image_path or not os.path.exists(image_path):
                return None

            center = aoi.get('center')
            if not center or len(center) < 2:
                return None

            cx, cy = float(center[0]), float(center[1])
            radius = float(aoi.get('radius') or 0)
            multiplier = context_multiplier if context_multiplier is not None else self.DEFAULT_CONTEXT_MULTIPLIER
            crop_radius = max(radius * multiplier, self.MIN_CROP_RADIUS_PX)

            with Image.open(image_path) as img:
                width, height = img.size

                x1 = max(0, int(round(cx - crop_radius)))
                y1 = max(0, int(round(cy - crop_radius)))
                x2 = min(width, int(round(cx + crop_radius)))
                y2 = min(height, int(round(cy + crop_radius)))

                if x2 <= x1 or y2 <= y1:
                    return None

                cropped = img.crop((x1, y1, x2, y2))
                if cropped.mode != 'RGB':
                    cropped = cropped.convert('RGB')

            # Scale the crop into a range that is comfortable to view once uploaded
            crop_w, crop_h = cropped.size
            longest = max(crop_w, crop_h)
            scale = 1.0
            if longest < self.MIN_OUTPUT_SIZE:
                scale = self.MIN_OUTPUT_SIZE / longest
            elif longest > self.MAX_OUTPUT_SIZE:
                scale = self.MAX_OUTPUT_SIZE / longest

            if scale != 1.0:
                cropped = cropped.resize(
                    (max(1, int(round(crop_w * scale))), max(1, int(round(crop_h * scale)))),
                    Image.Resampling.LANCZOS
                )

            if draw_highlight and radius > 0:
                self._draw_highlight(cropped, (cx - x1) * scale, (cy - y1) * scale, radius * scale,
                                     highlight_rgb or self.DEFAULT_HIGHLIGHT_RGB)

            output_path = self._build_output_path(output_name or Path(image_path).stem)
            cropped.save(output_path, format="JPEG", quality=self.JPEG_QUALITY)
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error generating AOI thumbnail for {image_path}: {e}")
            return None

    def save_composite(self, composite_bgr: np.ndarray, output_name: str) -> Optional[str]:
        """
        Save a multi-zoom composite image (BGR array) into the output directory.

        Args:
            composite_bgr: Composite image as a numpy array in BGR order (OpenCV convention).
            output_name (str): Base name (without extension) for the generated file.

        Returns:
            str: Path to the saved image, or None if it could not be saved.
        """
        try:
            if composite_bgr is None or composite_bgr.size == 0:
                return None

            # BGR -> RGB for PIL
            image = Image.fromarray(np.ascontiguousarray(composite_bgr[:, :, ::-1]))

            # Cap the long edge so uploads stay a reasonable size
            longest = max(image.size)
            if longest > self.MAX_COMPOSITE_SIZE:
                scale = self.MAX_COMPOSITE_SIZE / longest
                image = image.resize(
                    (max(1, int(round(image.width * scale))), max(1, int(round(image.height * scale)))),
                    Image.Resampling.LANCZOS
                )

            output_path = self._build_output_path(output_name)
            image.save(output_path, format="JPEG", quality=self.JPEG_QUALITY)
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error saving AOI composite image {output_name}: {e}")
            return None

    def _draw_highlight(self, image: Image.Image, x: float, y: float, radius: float,
                        highlight_rgb: Tuple[int, int, int]):
        """
        Draw a circle around the AOI so it stands out in the cropped view.

        Args:
            image (PIL.Image.Image): Image to draw on (modified in place).
            x (float): AOI center x within the image.
            y (float): AOI center y within the image.
            radius (float): AOI radius within the image.
            highlight_rgb (tuple): RGB color of the circle.
        """
        try:
            draw = ImageDraw.Draw(image)
            # Leave a little breathing room so the circle doesn't cover the detection
            circle_radius = max(radius * 1.2, radius + 4)
            line_width = max(2, int(round(max(image.size) / 200)))
            draw.ellipse(
                (x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius),
                outline=tuple(int(c) for c in highlight_rgb),
                width=line_width
            )
        except Exception as e:
            self.logger.error(f"Error drawing AOI highlight: {e}")

    def _build_output_path(self, base_name: str) -> Path:
        """
        Build a unique, filesystem-safe output path for a generated image.

        Args:
            base_name (str): Desired base name (without extension).

        Returns:
            Path: Unique path inside the output directory.
        """
        safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', base_name) or "aoi"
        candidate = safe_name
        suffix = 1
        while candidate in self._used_names or (self.output_dir / f"{candidate}.jpg").exists():
            candidate = f"{safe_name}_{suffix}"
            suffix += 1
        self._used_names.add(candidate)
        return self.output_dir / f"{candidate}.jpg"

    def cleanup(self):
        """Remove the temporary directory created by this service, if it owns one."""
        if self._owns_output_dir and self._output_dir is not None:
            try:
                shutil.rmtree(self._output_dir, ignore_errors=True)
            except Exception as e:
                self.logger.error(f"Error cleaning up AOI thumbnail directory: {e}")
            finally:
                self._output_dir = None
                self._used_names = set()
