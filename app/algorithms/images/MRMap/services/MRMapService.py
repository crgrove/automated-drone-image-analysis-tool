import logging
import numpy as np
import cv2
import math
import traceback

from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from algorithms import DetectionExpansion
from core.services.LoggerService import LoggerService
from collections import deque

MAX_SHADES = 256
NUMBER_OF_QUANTIZED_HISTOGRAM_BINS = 26


def _percent_to_u8(value):
    """Clamp a 0-100 percentage to the OpenCV 0-255 uint8 range."""
    try:
        pct = float(value or 0)
    except (TypeError, ValueError):
        return 0
    pct = max(0.0, min(100.0, pct))
    return int(round(pct / 100.0 * 255.0))


class MRMapService(AlgorithmService):
    """Service that executes the MRMap algorithm for detecting anomalies in spectral images.

    Uses Multi-Resolution Map (MRMap) algorithm to detect rare color combinations
    based on histogram analysis and bin count thresholds.

    Attributes:
        segments: Number of image segments for processing.
        threshold: Bin count threshold for anomaly detection.
        window_size: Window size for processing.
    """

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """Initialize the MRMapService with specific parameters for anomaly detection.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options, including 'threshold', 'segments', 'window', and 'colorspace'.
        """
        self.logger = LoggerService()
        super().__init__('MRMap', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.segments = options['segments']
        self.threshold = options['threshold']
        self.window_size = options['window']
        self.colorspace = options.get('colorspace', 'LAB')  # Default to LAB to match UI default
        # Optional AOI expansion. All default to 0 (off) — preserves legacy behavior.
        self.threshold_expansion = int(options.get('threshold_expansion', 0) or 0)
        self.hue_expansion = int(options.get('hue_expansion', 0) or 0)
        # Floors are user-facing percentages (0-100); convert to OpenCV S/V (0-255).
        self.hue_expansion_sat_floor = _percent_to_u8(options.get('hue_expansion_sat_floor', 0))
        self.hue_expansion_val_floor = _percent_to_u8(options.get('hue_expansion_val_floor', 0))

    def process_image(self, img, full_path, input_dir, output_dir):
        """Process a single image using the MR Map algorithm.

        Analyzes image using histogram-based bin counting to identify rare
        color combinations. Adds confidence scores based on bin count rarity.

        Args:
            img: The image to be processed as numpy array.
            full_path: The path to the image being analyzed.
            input_dir: The base input folder.
            output_dir: The base output folder.

        Returns:
            AnalysisResult containing the processed image path, list of areas
            of interest, base contour count, and error message if any.
        """
        try:
            height, width = img.shape[:2]

            # Convert to selected colorspace
            if self.colorspace == 'HSV':
                img_converted = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            elif self.colorspace == 'LAB':
                img_converted = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            else:  # RGB (default)
                img_converted = img

            hist = Histogram(img_converted, self.colorspace)

            # Extract channels (order depends on colorspace)
            # For all colorspaces, channels are in order [0, 1, 2]
            ch0, ch1, ch2 = img_converted[:, :, 0], img_converted[:, :, 1], img_converted[:, :, 2]
            # Compute bin counts for each pixel
            bin_counts = hist.bin_count(ch0, ch1, ch2)
            bin_counts = bin_counts * ((8000 * 6000) / (width * height))
            # Adjust counts based on image size
            # adjusted_counts = bin_counts * (STANDARD_IMAGE_SIZE / (width * height))

            # Identify anomalous pixels
            pixel_anom = (0 < bin_counts) & (bin_counts < self.threshold)

            mask, clusters = self._getMRMapsContours(pixel_anom)

            areas_of_interest, base_contour_count = self._build_aois_from_clusters(clusters, img.shape)

            # Confidence scores run on the *original* detection so rarity reflects
            # the anomaly itself, not pixels added by expansion.
            if areas_of_interest:
                areas_of_interest = self._add_confidence_scores(areas_of_interest, bin_counts, mask)

            # Optional anomaly / hue expansion. Overwrites detected_pixels and area
            # on each AOI and rewrites `mask` to match the expanded pixel set.
            if areas_of_interest and (self.threshold_expansion > 0 or self.hue_expansion > 0):
                expanded_bin_mask = None
                if self.threshold_expansion > 0:
                    expanded_threshold = self.threshold + self.threshold_expansion
                    expanded_bin_mask = (0 < bin_counts) & (bin_counts < expanded_threshold)

                hsv_img = None
                if self.hue_expansion > 0:
                    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

                areas_of_interest, mask = self._apply_expansion(
                    areas_of_interest, img.shape, expanded_bin_mask, hsv_img
                )

            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                mask_path = self.store_mask(full_path, output_path, mask)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            # print(traceback.format_exc())
            return AnalysisResult(full_path, error_message=str(e))

    def _getADIATContours(self, pixel_anom):
        """Get contours from pixel anomaly mask using standard method.

        Args:
            pixel_anom: Boolean array indicating anomalous pixels.

        Returns:
            List of contours from cv2.findContours.
        """
        mask = pixel_anom.astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def _getMRMapsContours(self, pixel_anom):
        """Build detection mask and cluster list from a pixel anomaly mask.

        Uses BFS connected component analysis with window-based connectivity
        to group nearby anomalous pixels into clusters. Clusters whose
        bounding rectangles overlap are merged by concatenating their pixel
        lists. The returned mask contains only the actual flagged pixels of
        valid clusters — not filled bounding rectangles.

        Args:
            pixel_anom: Boolean array indicating anomalous pixels.

        Returns:
            Tuple of (mask, clusters) where mask is a uint8 mask (255 on
            actual flagged pixels of valid clusters) and clusters is a list
            of dicts: {'rect': [xmin, ymin, xmax, ymax], 'pixels': [(x, y), ...]}.
        """
        visited = np.zeros_like(pixel_anom, dtype=bool)
        clusters = []
        mask = np.zeros_like(pixel_anom, dtype=np.uint8)
        height, width = pixel_anom.shape

        for y, x in zip(*np.where(pixel_anom & ~visited)):
            count, rect, pixels = self._find_connected_pixels(pixel_anom, visited, x, y, width, height)
            if count >= self.min_area:
                merged = False
                for i, existing in enumerate(clusters):
                    if self._rectangles_overlap(existing['rect'], rect):
                        existing['rect'] = self._merge_rectangles(existing['rect'], rect)
                        existing['pixels'].extend(pixels)
                        merged = True
                        break

                if not merged:
                    clusters.append({'rect': rect, 'pixels': pixels})

        # Mark only the actual flagged pixels in the mask (not rectangles)
        for cluster in clusters:
            if cluster['pixels']:
                coords = np.asarray(cluster['pixels'])
                mask[coords[:, 1], coords[:, 0]] = 255

        return mask, clusters

    def _find_connected_pixels(self, pixel_anom, visited, start_x, start_y, width, height):
        """Find connected pixels using BFS with window-based connectivity.

        Args:
            pixel_anom: Boolean array indicating anomalous pixels.
            visited: Boolean array tracking visited pixels.
            start_x: Starting X coordinate.
            start_y: Starting Y coordinate.
            width: Image width.
            height: Image height.

        Returns:
            Tuple of (count, rect, pixels) where count is the number of
            connected pixels, rect is [min_x, min_y, max_x, max_y], and
            pixels is a list of (x, y) tuples for every flagged pixel in
            the cluster.
        """
        queue = deque([(start_x, start_y)])
        rect = [start_x, start_y, start_x, start_y]
        count = 0
        pixels = []

        while queue:
            x, y = queue.popleft()

            if visited[y, x] or not pixel_anom[y, x]:
                continue  # Skip if already visited or not an anomaly

            visited[y, x] = True
            count += 1
            pixels.append((x, y))
            rect[0] = min(rect[0], x)
            rect[1] = min(rect[1], y)
            rect[2] = max(rect[2], x)
            rect[3] = max(rect[3], y)

            # Vectorized neighbor selection
            x_range = np.clip([x - self.window_size, x + self.window_size + 1], 0, width)
            y_range = np.clip([y - self.window_size, y + self.window_size + 1], 0, height)

            neighbors = np.argwhere(
                pixel_anom[y_range[0]:y_range[1], x_range[0]:x_range[1]] &
                ~visited[y_range[0]:y_range[1], x_range[0]:x_range[1]]
            )

            for dy, dx in neighbors:
                queue.append((x_range[0] + dx, y_range[0] + dy))

        return count, rect, pixels

    def _merge_rectangles(self, rect1, rect2):
        """Merge two overlapping rectangles into one.

        Args:
            rect1: First rectangle as [min_x, min_y, max_x, max_y].
            rect2: Second rectangle as [min_x, min_y, max_x, max_y].

        Returns:
            Merged rectangle as [min_x, min_y, max_x, max_y].
        """
        return [
            min(rect1[0], rect2[0]),  # left
            min(rect1[1], rect2[1]),  # top
            max(rect1[2], rect2[2]),  # right
            max(rect1[3], rect2[3])   # bottom
        ]

    def _rectangles_overlap(self, rect1, rect2):
        """Check if two rectangles overlap.

        Args:
            rect1: First rectangle as [min_x, min_y, max_x, max_y].
            rect2: Second rectangle as [min_x, min_y, max_x, max_y].

        Returns:
            True if rectangles overlap, False otherwise.
        """
        return not (
            rect1[2] < rect2[0] or  # rect1 right < rect2 left
            rect1[0] > rect2[2] or  # rect1 left > rect2 right
            rect1[3] < rect2[1] or  # rect1 bottom < rect2 top
            rect1[1] > rect2[3]     # rect1 top > rect2 bottom
        )

    def _build_aois_from_clusters(self, clusters, img_shape):
        """Build AOI dictionaries directly from BFS clusters.

        Replaces the generic contour-based identify_areas_of_interest for
        MRMap so that AOI geometry and detected_pixels are driven by the
        actual flagged pixels rather than filled bounding rectangles. Each
        cluster becomes exactly one AOI (before optional circle-based
        combining).

        Args:
            clusters: List of cluster dicts from _getMRMapsContours.
                Each has 'rect' and 'pixels' keys.
            img_shape: Shape of the processing-resolution image (H, W[, C]).

        Returns:
            Tuple of (areas_of_interest, base_contour_count). Returns
            (None, None) when no clusters pass filtering, mirroring
            AlgorithmService.identify_areas_of_interest behavior.
        """
        if not clusters:
            return None, None

        height, width = int(img_shape[0]), int(img_shape[1])

        # Build a mask of all actual-flagged pixels — used later for
        # bitwise_and intersection when combine_aois merges AOIs.
        original_pixels_mask = np.zeros((height, width), dtype=np.uint8)

        base_aois = []
        temp_mask = np.zeros((height, width), dtype=np.uint8)

        for cluster in clusters:
            pixels = cluster['pixels']
            area = len(pixels)
            if area < self.min_area:
                continue
            if self.max_area > 0 and area > self.max_area:
                continue

            coords = np.asarray(pixels)  # shape (N, 2), columns are (x, y)
            original_pixels_mask[coords[:, 1], coords[:, 0]] = 255

            # minEnclosingCircle expects a contour-like (N, 1, 2) array
            contour_pts = coords.reshape(-1, 1, 2).astype(np.int32)
            (cx, cy), radius = cv2.minEnclosingCircle(contour_pts)
            center = (int(cx), int(cy))
            radius = int(radius) + self.aoi_radius

            xmin, ymin, xmax, ymax = cluster['rect']
            contour_rect = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]

            base_aois.append({
                'center': center,
                'radius': radius,
                'area': area,
                'contour': contour_rect,
                'detected_pixels': coords.tolist(),
            })

            # Stamp the expanded circle onto temp_mask for the optional
            # combine_aois pass below.
            cv2.circle(temp_mask, center, radius, 255, -1)

        if not base_aois:
            return None, None

        base_contour_count = len(base_aois)

        if not self.combine_aois:
            base_aois.sort(key=lambda item: (item['center'][1], item['center'][0]))
            return base_aois, base_contour_count

        # combine_aois: iteratively stamp circles onto temp_mask until the
        # number of external contours stabilizes, then build merged AOIs.
        combined_contours, _ = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        while True:
            for cnt in combined_contours:
                (mx, my), mradius = cv2.minEnclosingCircle(cnt)
                cv2.circle(temp_mask, (int(mx), int(my)), int(mradius), 255, -1)
            next_contours, _ = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(next_contours) == len(combined_contours):
                combined_contours = next_contours
                break
            combined_contours = next_contours

        combined_aois = []
        for cnt in combined_contours:
            region_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.drawContours(region_mask, [cnt], -1, 255, thickness=-1)

            # Intersect the combined region with the actual flagged pixels
            # so detected_pixels and area reflect true anomalies only.
            aoi_pixels_mask = cv2.bitwise_and(original_pixels_mask, region_mask)
            ys, xs = np.where(aoi_pixels_mask > 0)
            if len(xs) == 0:
                continue
            aoi_pixels = np.stack([xs, ys], axis=1)

            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            center = (int(cx), int(cy))
            radius = int(radius)

            xmin, ymin = int(xs.min()), int(ys.min())
            xmax, ymax = int(xs.max()), int(ys.max())
            contour_rect = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]

            combined_aois.append({
                'center': center,
                'radius': radius,
                'area': int(len(aoi_pixels)),
                'contour': contour_rect,
                'detected_pixels': aoi_pixels.tolist(),
            })

        combined_aois.sort(key=lambda item: (item['center'][1], item['center'][0]))
        return combined_aois, base_contour_count

    def _apply_expansion(self, areas_of_interest, img_shape, expanded_bin_mask, hsv_img):
        """Apply threshold and/or hue expansion to each AOI.

        Threshold expansion (MRMap-specific): per AOI, expand to all pixels
        inside the cluster rectangle that pass bin_counts < threshold+expansion,
        then flood to connected pixels meeting that criterion outside the rect.

        Hue expansion: circular mean hue of the original detected pixels is
        the reference. Any pixel within +/- hue_expansion of that mean
        (circular distance) reachable by 8-connected flood from the current
        selection is added. Safety-capped per AOI.

        Area is replaced with convex-hull area of the expanded pixel set.

        Args:
            areas_of_interest: List of AOIs (modified in place; also returned).
            img_shape: (H, W[, C]) of processing image.
            expanded_bin_mask: Global bool mask for threshold expansion, or None.
            hsv_img: HxWx3 HSV image for hue expansion, or None.

        Returns:
            (areas_of_interest, combined_mask). combined_mask is uint8 with
            255 on every expanded pixel across all AOIs.
        """
        h, w = int(img_shape[0]), int(img_shape[1])
        combined_mask = np.zeros((h, w), dtype=np.uint8)

        for aoi in areas_of_interest:
            original_pixels = aoi.get('detected_pixels') or []
            if not original_pixels:
                continue

            # Seed mask from original detected pixels.
            coords = np.asarray(original_pixels, dtype=np.int32)
            seed_mask = np.zeros((h, w), dtype=bool)
            seed_mask[coords[:, 1], coords[:, 0]] = True

            # Derive cluster rect from the stored contour corners. MRMap stores
            # the axis-aligned cluster rectangle as 4 corner points.
            contour = aoi.get('contour') or []
            if contour:
                xs = [int(p[0]) for p in contour]
                ys = [int(p[1]) for p in contour]
                cluster_rect = [min(xs), min(ys), max(xs), max(ys)]
            else:
                cluster_rect = [
                    int(coords[:, 0].min()), int(coords[:, 1].min()),
                    int(coords[:, 0].max()), int(coords[:, 1].max()),
                ]

            safety_cap = DetectionExpansion.compute_safety_cap(cluster_rect)

            # Stage 1: threshold expansion (MRMap only).
            selected = seed_mask
            if expanded_bin_mask is not None:
                threshold_selected = DetectionExpansion.expand_threshold_mrmap(
                    expanded_bin_mask, cluster_rect, (h, w)
                )
                selected = seed_mask | threshold_selected

            # Stage 2: hue expansion. Reference = circular mean of *original*
            # detected pixel hues.
            if hsv_img is not None and self.hue_expansion > 0:
                seed_hues = hsv_img[coords[:, 1], coords[:, 0], 0]
                mean_hue = DetectionExpansion.circular_mean_hue(seed_hues)
                if mean_hue is not None:
                    hue_ok = DetectionExpansion.hue_distance_mask(
                        hsv_img, mean_hue, self.hue_expansion,
                        sat_floor=self.hue_expansion_sat_floor,
                        val_floor=self.hue_expansion_val_floor,
                    )
                    flooded, cap_hit = DetectionExpansion.expand_hue_flood(selected, hue_ok, safety_cap)
                    if cap_hit:
                        self.logger.warning(
                            f"MRMap hue expansion cap hit for AOI at {aoi.get('center')}; keeping pre-hue selection."
                        )
                    else:
                        selected = flooded

            # Commit expanded selection back to AOI.
            ys2, xs2 = np.where(selected)
            if len(xs2) == 0:
                continue
            aoi['detected_pixels'] = np.stack([xs2, ys2], axis=1).tolist()
            aoi['area'] = int(round(DetectionExpansion.convex_hull_area_from_mask(selected)))

            combined_mask[selected] = 255

        return areas_of_interest, combined_mask

    def _add_confidence_scores(self, areas_of_interest, bin_counts, mask):
        """Add confidence scores to AOIs based on histogram bin counts (rarity scores).

        Lower bin count = rarer color = higher confidence. Normalizes scores
        to 0-100 range based on detected pixel bin counts.

        Args:
            areas_of_interest: List of AOI dictionaries.
            bin_counts: Histogram bin counts for each pixel as numpy array.
            mask: Binary detection mask as numpy array.

        Returns:
            List of AOIs with added confidence scores.
        """
        # Get all bin counts from detected pixels to find max for normalization
        detected_bin_counts = bin_counts[mask > 0]
        if len(detected_bin_counts) == 0:
            return areas_of_interest

        max_bin_count = np.max(detected_bin_counts)
        min_bin_count = np.min(detected_bin_counts)
        bin_range = max_bin_count - min_bin_count if max_bin_count > min_bin_count else 1.0

        # Add confidence to each AOI
        for aoi in areas_of_interest:
            detected_pixels = aoi.get('detected_pixels', [])
            if len(detected_pixels) > 0:
                # Extract bin counts for this AOI's pixels
                # NOTE: detected_pixels are in PROCESSING resolution (same as bin_counts)
                # No transformation needed - coordinates are already at processing resolution
                aoi_bin_counts = []
                for pixel in detected_pixels:
                    x, y = int(pixel[0]), int(pixel[1])

                    if 0 <= y < bin_counts.shape[0] and 0 <= x < bin_counts.shape[1]:
                        aoi_bin_counts.append(bin_counts[y, x])

                if len(aoi_bin_counts) > 0:
                    # Calculate mean bin count for this AOI
                    mean_bin_count = np.mean(aoi_bin_counts)

                    # Normalize to 0-100 scale (INVERTED: lower bin count = rarer = higher confidence)
                    normalized_score = ((max_bin_count - mean_bin_count) / bin_range) * 100.0

                    # Add confidence fields to AOI
                    aoi['confidence'] = round(normalized_score, 1)
                    aoi['score_type'] = 'rarity'
                    aoi['raw_score'] = round(float(mean_bin_count), 3)
                    aoi['score_method'] = 'mean'
                else:
                    # No valid pixels, set low confidence
                    aoi['confidence'] = 0.0
                    aoi['score_type'] = 'rarity'
                    aoi['raw_score'] = 0.0
                    aoi['score_method'] = 'mean'
            else:
                # No detected pixels, set low confidence
                aoi['confidence'] = 0.0
                aoi['score_type'] = 'rarity'
                aoi['raw_score'] = 0.0
                aoi['score_method'] = 'mean'

        return areas_of_interest


class Histogram:
    """Histogram class for quantized color analysis.

    Creates a quantized 3D histogram of color values for efficient
    bin counting and rarity analysis. Supports RGB, HSV, and LAB color spaces
    with color-space-aware quantization.

    Attributes:
        image_array: Original image array.
        colorspace: Color space of the image ('RGB', 'HSV', or 'LAB').
        mapping: Quantization mapping from 256 shades to bins (per channel).
        q_histogram: Quantized 3D histogram array.
    """

    def __init__(self, image, colorspace='RGB'):
        """Initialize histogram with image data.

        Args:
            image: Image array to analyze.
            colorspace: Color space of the image ('RGB', 'HSV', or 'LAB').
        """
        self.image_array = image
        self.colorspace = colorspace

        # Create color-space-aware quantization mappings
        self.mapping_ch0, self.mapping_ch1, self.mapping_ch2 = self._create_mappings()

        self.q_histogram = None
        self.create_histogram()

    def _create_mappings(self):
        """Create color-space-aware quantization mappings for each channel.

        Returns:
            Tuple of (mapping_ch0, mapping_ch1, mapping_ch2) where each mapping
            is a numpy array that maps 0-255 values to bin indices 0-25.
        """
        if self.colorspace == 'HSV':
            # HSV: H (0-179), S (0-255), V (0-255)
            # H channel: Map 0-179 to 26 bins more effectively
            # Use full range of H values (0-179) instead of wasting bins on 180-255
            h_max = 180  # OpenCV HSV H channel max value
            h_bin_size = h_max / NUMBER_OF_QUANTIZED_HISTOGRAM_BINS
            mapping_h = np.clip((np.arange(MAX_SHADES) / h_bin_size).astype(np.uint8),
                                0, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS - 1)

            # S and V channels: Standard mapping (0-255)
            bin_size = math.ceil(MAX_SHADES / NUMBER_OF_QUANTIZED_HISTOGRAM_BINS)
            mapping_sv = (np.arange(MAX_SHADES) / bin_size).astype(np.uint8)
            mapping_sv = np.clip(mapping_sv, 0, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS - 1)

            return mapping_h, mapping_sv, mapping_sv

        elif self.colorspace == 'LAB':
            # LAB: L (0-255), A (0-255, centered ~128), B (0-255, centered ~128)
            # L channel: Standard mapping (0-255) - lightness uses full range
            bin_size = math.ceil(MAX_SHADES / NUMBER_OF_QUANTIZED_HISTOGRAM_BINS)
            mapping_l = (np.arange(MAX_SHADES) / bin_size).astype(np.uint8)
            mapping_l = np.clip(mapping_l, 0, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS - 1)

            # A and B channels: Use non-uniform quantization to better capture
            # the typical distribution centered around 128 (neutral gray)
            # This provides finer resolution in the common range (64-192) while
            # still covering the full range (0-255)
            # Strategy: Use more bins in the center range, fewer at extremes
            mapping_ab = np.zeros(MAX_SHADES, dtype=np.uint8)

            # Create a non-uniform binning that emphasizes the center
            # Split into 3 regions: low (0-64), center (65-192), high (193-255)
            # Center gets more bins since that's where most values cluster
            center_bins = NUMBER_OF_QUANTIZED_HISTOGRAM_BINS // 2  # 13 bins for center
            low_bins = (NUMBER_OF_QUANTIZED_HISTOGRAM_BINS - center_bins) // 2  # 6 bins for low
            high_bins = NUMBER_OF_QUANTIZED_HISTOGRAM_BINS - center_bins - low_bins  # 7 bins for high

            # Low range: 0-64 (inclusive, 65 values) -> bins 0 to low_bins-1
            low_range = np.arange(0, 65)
            mapping_ab[low_range] = np.clip(
                (low_range * low_bins / 65).astype(np.uint8),
                0, low_bins - 1
            )

            # Center range: 65-192 (inclusive, 128 values) -> bins low_bins to low_bins+center_bins-1
            center_range = np.arange(65, 193)
            mapping_ab[center_range] = np.clip(
                (low_bins + ((center_range - 65) * center_bins / 128).astype(np.uint8)),
                low_bins, low_bins + center_bins - 1
            )

            # High range: 193-255 (inclusive, 63 values) -> bins low_bins+center_bins to NUMBER_OF_QUANTIZED_HISTOGRAM_BINS-1
            high_range = np.arange(193, 256)
            mapping_ab[high_range] = np.clip(
                (low_bins + center_bins + ((high_range - 193) * high_bins / 63).astype(np.uint8)),
                low_bins + center_bins, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS - 1
            )

            return mapping_l, mapping_ab, mapping_ab

        else:  # RGB/BGR
            # RGB: All channels use standard mapping (0-255)
            bin_size = math.ceil(MAX_SHADES / NUMBER_OF_QUANTIZED_HISTOGRAM_BINS)
            mapping = (np.arange(MAX_SHADES) / bin_size).astype(np.uint8)
            mapping = np.clip(mapping, 0, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS - 1)
            return mapping, mapping, mapping

    def create_histogram(self):
        """Create quantized 3D histogram from image.

        Maps pixel values to quantized bins using color-space-aware mappings
        and computes histogram for efficient bin count lookups.
        """
        # Use channel-specific mappings for better quantization
        ch0_mapped = self.mapping_ch0[self.image_array[:, :, 0]]
        ch1_mapped = self.mapping_ch1[self.image_array[:, :, 1]]
        ch2_mapped = self.mapping_ch2[self.image_array[:, :, 2]]

        # Compute histogram directly without storing a large intermediate array
        self.q_histogram, _ = np.histogramdd(
            (ch0_mapped.ravel(), ch1_mapped.ravel(), ch2_mapped.ravel()),  # Direct ravel to avoid memory overhead
            bins=(NUMBER_OF_QUANTIZED_HISTOGRAM_BINS,) * 3,
            range=((0, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS),) * 3
        )

    def bin_count(self, ch0, ch1, ch2):
        """
        Get the histogram bin count for each pixel.

        Args:
            ch0, ch1, ch2: Channel values for each pixel (can be RGB, HSV, LAB, etc.)

        Returns:
            numpy.ndarray: Bin counts for each pixel
        """
        # Use channel-specific mappings
        q0 = self.mapping_ch0[ch0]
        q1 = self.mapping_ch1[ch1]
        q2 = self.mapping_ch2[ch2]

        return self.q_histogram[q0, q1, q2]
