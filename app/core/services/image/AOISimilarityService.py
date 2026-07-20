"""
AOISimilarityService - Ranks AOIs across a dataset by visual similarity to a reference AOI.

Similarity is color-first: an HSV hue/saturation histogram computed over a circular
mask of the cached 180x180 AOI thumbnail is the dominant signal, blended with a
brightness (V) histogram, a pixel-area log-ratio, and mean saturation/value stats.
Descriptors are cached in memory for the lifetime of the service (one Viewer session).

Thread-safety: descriptors are computed and cached only from a single worker thread,
and the owning controller enforces one search at a time, so no locking is used here.
Only ndarray/PIL/cv2 code paths of ThumbnailCacheService are used (never QPixmap/QIcon),
which keeps this service safe to run off the GUI thread.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import cv2
import numpy as np

from core.services.LoggerService import LoggerService
from core.services.cache.ThumbnailCacheService import ThumbnailCacheService

THUMB_SIZE = 180
CROP_PADDING = 10
HS_BINS = (16, 8)
V_BINS = 16
CHROMA_S_MIN = 40
CHROMA_V_MIN = 40
CHROMA_MIN_PIXELS = 25
CHROMA_MIN_FRACTION = 0.10
MAX_RESULTS_DEFAULT = 40
AREA_RATIO_SATURATION = 16.0
PROGRESS_EVERY = 100

# Fixed blend weights per regime. The mixed regime carries a flat penalty because a
# chromatic AOI is categorically unlike an achromatic one, but candidates can still
# rank among themselves via brightness/area.
WEIGHT_CHROMATIC_HS = 0.55
WEIGHT_CHROMATIC_V = 0.20
WEIGHT_CHROMATIC_AREA = 0.15
WEIGHT_CHROMATIC_STATS = 0.10
WEIGHT_ACHROMATIC_V = 0.55
WEIGHT_ACHROMATIC_AREA = 0.25
WEIGHT_ACHROMATIC_STATS = 0.20
MIXED_PENALTY = 0.30
WEIGHT_MIXED_V = 0.35
WEIGHT_MIXED_AREA = 0.20
WEIGHT_MIXED_STATS = 0.15


@dataclass
class AOIDescriptor:
    """Compact per-AOI appearance descriptor (~600 bytes)."""
    hs_hist: Optional[np.ndarray]  # L1-normalized 16x8 hue/sat histogram; None when achromatic
    v_hist: np.ndarray             # L1-normalized 16-bin brightness histogram
    chromatic_fraction: float      # Fraction of masked pixels passing the chroma gate
    mean_s: float                  # Mean saturation over the circular mask (0-255)
    mean_v: float                  # Mean value over the circular mask (0-255)
    area: float                    # Detected pixel count (fallback: circle area)

    @property
    def is_chromatic(self) -> bool:
        return self.hs_hist is not None


class AOISimilarityService:
    """Computes appearance descriptors for AOIs and ranks candidates by similarity."""

    def __init__(self, dataset_thumbnail_dir: Optional[str] = None):
        """
        Args:
            dataset_thumbnail_dir: The dataset's .thumbnails directory, when it exists.
                Cached 180x180 crops are read from (and self-healed back to) this dir.
        """
        self.logger = LoggerService()
        self.thumbnail_cache = ThumbnailCacheService(dataset_cache_dir=dataset_thumbnail_dir)
        # Keyed by the thumbnail cache key (content-derived from filename:center:radius),
        # so entries survive AOI index shifts and auto-invalidate on center/radius edits.
        # Failed computations are cached as None to avoid re-decoding broken images.
        self._descriptor_cache: Dict[str, Optional[AOIDescriptor]] = {}

    def clear_cache(self):
        """Drop all cached descriptors."""
        self._descriptor_cache.clear()

    def get_crop(self, image_path: str, aoi_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Get the 180x180 RGB crop for an AOI without loading the full source image.

        Checks the disk thumbnail cache (portable then legacy key), then falls back to a
        lazy PIL region extract; a successful fallback is written back to the cache so
        legacy datasets self-heal.
        """
        cache = self.thumbnail_cache
        cache_key = cache.get_cache_key(image_path, aoi_data)
        crop = cache.load_thumbnail_from_disk(cache_key)

        if crop is None:
            legacy_key = cache.get_legacy_cache_key(image_path, aoi_data, aoi_data.get('_xml_path'))
            if legacy_key != cache_key:
                crop = cache.load_thumbnail_from_disk(legacy_key)

        if crop is None:
            crop = cache.extract_aoi_region_fast(image_path, aoi_data, (THUMB_SIZE, THUMB_SIZE))
            if crop is not None and cache.dataset_cache_dir:
                try:
                    cache.save_thumbnail_to_disk(cache_key, crop, cache.dataset_cache_dir)
                except Exception:
                    pass  # Best-effort self-heal; read-only datasets must not fail the search

        return crop

    def build_circle_mask(self, radius: float) -> np.ndarray:
        """
        Build the circular mask isolating the AOI within its 180x180 thumbnail.

        The thumbnail is a (radius + padding) square crop resized to 180px, so the AOI
        circle maps to 90 * radius / (radius + padding) pixels, clamped to keep at least
        a few samples and to stay inside the tile.
        """
        radius = max(1.0, float(radius))
        mask_radius = int(round((THUMB_SIZE / 2) * radius / (radius + CROP_PADDING)))
        mask_radius = max(4, min(88, mask_radius))
        mask = np.zeros((THUMB_SIZE, THUMB_SIZE), dtype=np.uint8)
        cv2.circle(mask, (THUMB_SIZE // 2, THUMB_SIZE // 2), mask_radius, 255, -1)
        return mask

    def compute_descriptor(self, crop_rgb: Optional[np.ndarray], aoi_data: Dict[str, Any]) -> Optional[AOIDescriptor]:
        """
        Compute the appearance descriptor for one AOI crop. Deterministic.

        Gray/near-gray pixels are excluded from the hue/sat histogram (chroma gate); when
        too few chromatic pixels remain the crop is flagged achromatic (hs_hist=None) and
        similarity falls back to brightness/area/stats.
        """
        if crop_rgb is None:
            return None
        try:
            crop = self._normalize_crop(crop_rgb)
            radius = aoi_data.get('radius', 50)
            mask = self.build_circle_mask(radius)
            mask_bool = mask > 0
            mask_count = int(np.count_nonzero(mask_bool))
            if mask_count == 0:
                return None

            hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
            saturation = hsv[:, :, 1]
            value = hsv[:, :, 2]

            chroma_bool = mask_bool & (saturation >= CHROMA_S_MIN) & (value >= CHROMA_V_MIN)
            chroma_count = int(np.count_nonzero(chroma_bool))
            chromatic_fraction = chroma_count / mask_count

            hs_hist = None
            if chroma_count >= CHROMA_MIN_PIXELS and chromatic_fraction >= CHROMA_MIN_FRACTION:
                chroma_mask = chroma_bool.astype(np.uint8) * 255
                hs_hist = cv2.calcHist([hsv], [0, 1], chroma_mask, list(HS_BINS), [0, 180, 0, 256])
                total = float(hs_hist.sum())
                hs_hist = (hs_hist / total).astype(np.float32) if total > 0 else None

            v_hist = cv2.calcHist([hsv], [2], mask, [V_BINS], [0, 256])
            v_total = float(v_hist.sum())
            if v_total > 0:
                v_hist = (v_hist / v_total).astype(np.float32)
            else:
                v_hist = v_hist.astype(np.float32)

            area = aoi_data.get('area') or round(math.pi * max(1.0, float(radius)) ** 2)
            return AOIDescriptor(
                hs_hist=hs_hist,
                v_hist=v_hist,
                chromatic_fraction=chromatic_fraction,
                mean_s=float(saturation[mask_bool].mean()),
                mean_v=float(value[mask_bool].mean()),
                area=float(area),
            )
        except Exception as e:
            self.logger.error(f"Error computing AOI similarity descriptor: {e}")
            return None

    def get_descriptor(self, image_path: str, aoi_data: Dict[str, Any]) -> Optional[AOIDescriptor]:
        """Cached wrapper around get_crop + compute_descriptor."""
        cache_key = self.thumbnail_cache.get_cache_key(image_path, aoi_data)
        if cache_key in self._descriptor_cache:
            return self._descriptor_cache[cache_key]
        descriptor = self.compute_descriptor(self.get_crop(image_path, aoi_data), aoi_data)
        self._descriptor_cache[cache_key] = descriptor
        return descriptor

    def compare(self, desc_a: AOIDescriptor, desc_b: AOIDescriptor) -> float:
        """
        Blended distance between two descriptors, in [0, 1] (0 = identical).

        Histogram distances use Bhattacharyya: symmetric, bounded, and more tolerant of
        bin-edge/JPEG jitter on single-dominant-bin (solid color) crops than intersection.
        """
        d_v = self._bhattacharyya(desc_a.v_hist, desc_b.v_hist)
        d_area = min(1.0, abs(math.log((desc_a.area + 1.0) / (desc_b.area + 1.0))) / math.log(AREA_RATIO_SATURATION))
        d_stats = (abs(desc_a.mean_s - desc_b.mean_s) + abs(desc_a.mean_v - desc_b.mean_v)) / (2.0 * 255.0)

        if desc_a.is_chromatic and desc_b.is_chromatic:
            d_hs = self._bhattacharyya(desc_a.hs_hist, desc_b.hs_hist)
            distance = (WEIGHT_CHROMATIC_HS * d_hs + WEIGHT_CHROMATIC_V * d_v +
                        WEIGHT_CHROMATIC_AREA * d_area + WEIGHT_CHROMATIC_STATS * d_stats)
        elif not desc_a.is_chromatic and not desc_b.is_chromatic:
            distance = (WEIGHT_ACHROMATIC_V * d_v + WEIGHT_ACHROMATIC_AREA * d_area +
                        WEIGHT_ACHROMATIC_STATS * d_stats)
        else:
            distance = min(1.0, MIXED_PENALTY + WEIGHT_MIXED_V * d_v +
                           WEIGHT_MIXED_AREA * d_area + WEIGHT_MIXED_STATS * d_stats)

        return min(max(distance, 0.0), 1.0)

    def find_similar(self, images: List[Dict[str, Any]], ref_image_idx: int, ref_aoi_idx: int,
                     progress_callback: Optional[Callable[[int, int], None]] = None,
                     cancel_check: Optional[Callable[[], bool]] = None,
                     max_results: int = MAX_RESULTS_DEFAULT) -> List[Dict[str, Any]]:
        """
        Rank every other AOI in the dataset by similarity to the reference AOI.

        Args:
            images: Viewer image dicts (each with 'path' and 'areas_of_interest').
            ref_image_idx / ref_aoi_idx: Location of the reference AOI.
            progress_callback: Optional callable(done, total), invoked every 100 AOIs.
            cancel_check: Optional callable returning True to abort; returns [] on cancel.
            max_results: Cap on returned matches.

        Returns:
            Top-N result dicts sorted by similarity desc (ties: image/AOI index asc).

        Raises:
            ValueError: If the reference AOI is missing or cannot be analyzed.
        """
        try:
            ref_image = images[ref_image_idx]
            ref_aoi = ref_image['areas_of_interest'][ref_aoi_idx]
        except (IndexError, KeyError, TypeError):
            raise ValueError(f"Reference AOI not found (image {ref_image_idx}, AOI {ref_aoi_idx})")

        ref_descriptor = self.get_descriptor(ref_image.get('path'), ref_aoi)
        if ref_descriptor is None:
            raise ValueError(
                f"Could not analyze the selected AOI (image '{ref_image.get('path')}', AOI {ref_aoi_idx})"
            )

        candidates = []
        for image_idx, image in enumerate(images):
            for aoi_idx, aoi in enumerate(image.get('areas_of_interest') or []):
                if image_idx == ref_image_idx and aoi_idx == ref_aoi_idx:
                    continue
                candidates.append((image_idx, aoi_idx, aoi, image))

        total = len(candidates)
        scored = []
        skipped = 0
        for done, (image_idx, aoi_idx, aoi, image) in enumerate(candidates, start=1):
            if cancel_check and cancel_check():
                return []
            try:
                descriptor = self.get_descriptor(image.get('path'), aoi)
            except Exception as e:
                self.logger.error(
                    f"Similarity search: descriptor failed for image '{image.get('path')}' AOI {aoi_idx}: {e}"
                )
                descriptor = None
            if descriptor is None:
                skipped += 1
            else:
                distance = self.compare(ref_descriptor, descriptor)
                similarity = int(max(0, min(100, round(100.0 * (1.0 - distance)))))
                scored.append((similarity, image_idx, aoi_idx, aoi, image))
            if progress_callback and (done % PROGRESS_EVERY == 0 or done == total):
                progress_callback(done, total)

        if skipped:
            self.logger.warning(f"Similarity search skipped {skipped} AOI(s) with no readable thumbnail")

        scored.sort(key=lambda entry: (-entry[0], entry[1], entry[2]))
        return [self._build_result(image, image_idx, aoi_idx, aoi, similarity)
                for similarity, image_idx, aoi_idx, aoi, image in scored[:max_results]]

    def build_reference_entry(self, images: List[Dict[str, Any]], ref_image_idx: int,
                              ref_aoi_idx: int) -> Dict[str, Any]:
        """Build the display entry for the reference AOI itself (similarity 100)."""
        image = images[ref_image_idx]
        aoi = image['areas_of_interest'][ref_aoi_idx]
        entry = self._build_result(image, ref_image_idx, ref_aoi_idx, aoi, 100)
        entry['is_reference'] = True
        return entry

    def _build_result(self, image: Dict[str, Any], image_idx: int, aoi_idx: int,
                      aoi: Dict[str, Any], similarity: int) -> Dict[str, Any]:
        image_path = image.get('path')
        return {
            'image_idx': image_idx,
            'aoi_idx': aoi_idx,
            'image_name': Path(image_path).name if image_path else '',
            'image_path': image_path,
            'aoi_number': aoi.get('number'),
            'center': aoi.get('center'),
            'area': aoi.get('area'),
            'similarity': similarity,
            'thumbnail': self.get_crop(image_path, aoi),
            'aoi_data': aoi,
            'is_reference': False,
        }

    @staticmethod
    def _bhattacharyya(hist_a: np.ndarray, hist_b: np.ndarray) -> float:
        distance = float(cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_BHATTACHARYYA))
        return min(max(distance, 0.0), 1.0)

    @staticmethod
    def _normalize_crop(crop: np.ndarray) -> np.ndarray:
        """Coerce a cached/loaded crop to 180x180 RGB uint8."""
        if crop.ndim == 2:
            crop = np.stack([crop] * 3, axis=-1)
        elif crop.shape[2] == 4:
            crop = crop[:, :, :3]
        if crop.dtype != np.uint8:
            crop = np.clip(crop, 0, 255).astype(np.uint8)
        if crop.shape[0] != THUMB_SIZE or crop.shape[1] != THUMB_SIZE:
            crop = cv2.resize(crop, (THUMB_SIZE, THUMB_SIZE), interpolation=cv2.INTER_AREA)
        return np.ascontiguousarray(crop)
