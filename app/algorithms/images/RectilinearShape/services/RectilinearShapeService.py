"""
RectilinearShapeService.py - detects man-made rectangles of a known physical size.

Flags suitcases, coolers, boxes and small tents by geometry rather than
colour: straight edges of the right physical length meeting at right angles
or running parallel at the right separation, scored on size, edge support,
ring contrast and orientation coherence ("boxiness"). Per-image GSD turns the
physical size range into pixels, which is what makes edge-based detection
tractable - without it line detectors return thousands of segments a frame.

The geometry lives in algorithms.Shared.services.RectilinearGeometry; this
service only orchestrates it.
"""

import math
import os
from pathlib import Path

import cv2
import numpy as np

from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from algorithms.Shared.services import RectilinearGeometry as geometry
from algorithms.images.RectilinearShape.services.RectilinearPresets import normalize_options
from core.services.LoggerService import LoggerService


# Gaussian sigma for the pre-blur. Suppresses JPEG 8x8 block edges, which
# are axis-aligned and balanced and would otherwise inflate boxiness.
_PRE_BLUR_SIGMA = 0.8

# Rotated-rectangle IoU above which the weaker of two hypotheses is dropped.
_NMS_IOU = 0.3

# Ring width around a hypothesis for the contrast test, as a fraction of its short side.
_RING_FRACTION = 0.3

# Delta E at which the contrast score reaches 0.9 (saturating curve).
_CONTRAST_DELTA_E_AT_0_9 = 15.0

# Boxiness window side as a multiple of the longest expected side.
_BOXINESS_WINDOW_FACTOR = 1.25

# Boxiness grid: the decimated map keeps at least this many cells across the
# shortest expected side.
_BOXINESS_CELLS_PER_SHORT_SIDE = 8

# Boxiness energy floor: a fraction of the frame's median gradient, with an
# absolute minimum (see _boxiness_energy_floor).
_ENERGY_FLOOR_MEDIAN_FRACTION = 0.05
_ENERGY_FLOOR_MIN = 0.05

# Fused-confidence exponents (initial values; to be tuned with field data).
_EXP_SIZE = 0.35
_EXP_EDGE = 0.35
_EXP_CONTRAST = 0.15
_EXP_BOXINESS = 0.15

# Floor on the boxiness term so a hypothesis with clean edges but a cluttered
# window is damped rather than vetoed.
_BOXINESS_TERM_FLOOR = 0.05

# Edge-support samples per perimeter.
_EDGE_SAMPLES = 64

# Camera tilt from nadir above which GSD varies enough across the frame that
# the size tolerance is widened by the top/bottom GSD ratio.
_OBLIQUE_TILT_DEG = 10.0

# Cap on line hypotheses scored per image. Rock fields and talus can produce
# right-angle pairs by the thousand; the cheap size score runs first, so the
# cap only bites on pathological frames, and is logged when it does.
_MAX_HYPOTHESES = 20000


class RectilinearShapeService(AlgorithmService):
    """Image algorithm that detects rectangles of a known physical size.

    Attributes:
        settings (dict): Normalised options (every key in DEFAULT_OPTIONS).
        batch_min_area (int): Global minimum AOI area from the batch, kept
            only to report when it disagrees with the size gate.
        batch_max_area (int): Global maximum AOI area from the batch, likewise.
    """

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """Initialize the service.

        Args:
            identifier: RGB values for the color to highlight areas of interest.
            min_area: Batch minimum AOI area in pixels (diagnostic only, see below).
            max_area: Batch maximum AOI area in pixels (diagnostic only, see below).
            aoi_radius: Radius added to the minimum enclosing circle around an AOI.
            combine_aois: If True, overlapping AOIs are combined.
            options: Algorithm options; missing keys take their defaults.
        """
        self.logger = LoggerService()
        super().__init__('RectilinearShape', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.settings = normalize_options(options)
        # The physical-size gate is this algorithm's size filter. The batch
        # limits come from the guide's Target Size page, which cannot express
        # a preset (it squares a square-feet value as if it were linear feet)
        # and would silently drop e.g. a tent; they are kept for diagnostics
        # and identify_areas_of_interest is run unbounded.
        self.batch_min_area = min_area
        self.batch_max_area = max_area
        self.min_area = 0
        self.max_area = 0

    def process_image(self, img, full_path, input_dir, output_dir):
        """Detect rectilinear targets in one image.

        Args:
            img (np.ndarray): BGR image at processing resolution.
            full_path (str): Path to the image being analysed.
            input_dir (str): Base input folder.
            output_dir (str): Base output folder.

        Returns:
            AnalysisResult: AOIs carry ``confidence`` (0-100) and
            ``score_type = 'shape'``; ``error_message`` is set when the image
            has no usable GSD or processing failed.
        """
        try:
            bgr = self._to_bgr8(img)
            gsd_cm, gsd_service = self._resolve_gsd_cm(bgr, full_path)
            if gsd_cm is None or gsd_cm <= 0:
                message = (
                    f"RectilinearShape: no ground sample distance for {full_path} "
                    "(missing altitude or camera metadata) and no fallback GSD is set"
                )
                self.logger.warning(message)
                return AnalysisResult(full_path, error_message=message)

            settings = self.settings
            tolerance = self._effective_tolerance(settings['size_tolerance'], gsd_service, full_path)
            long_min_px = settings['long_side_cm_min'] / gsd_cm
            long_max_px = settings['long_side_cm_max'] / gsd_cm
            short_min_px = settings['short_side_cm_min'] / gsd_cm
            short_max_px = settings['short_side_cm_max'] / gsd_cm
            self.logger.debug(
                f"RectilinearShape: {full_path} effective GSD {gsd_cm:.2f} cm/px, "
                f"short side {short_min_px:.1f}-{short_max_px:.1f} px, long side {long_min_px:.1f}-{long_max_px:.1f} px"
            )
            if short_min_px < settings['min_short_side_px']:
                self.logger.warning(
                    f"RectilinearShape: skipped {full_path} - the smallest target side is "
                    f"{short_min_px:.1f} px at {gsd_cm:.2f} cm/px (processing scale {self.scale_factor:.2f}), "
                    f"below the {settings['min_short_side_px']} px floor. Raise the processing resolution."
                )
                return self._empty_result(full_path, output_dir)

            hypotheses, scores, debug_layers = self._detect(
                bgr, gsd_cm, tolerance, (long_min_px, long_max_px, short_min_px, short_max_px)
            )

            contours = [self._contour_in_frame(r, bgr.shape) for r in hypotheses]
            areas_of_interest, base_contour_count = self.identify_areas_of_interest(bgr.shape, contours)
            if areas_of_interest:
                self._attach_scores(areas_of_interest, hypotheses, scores)
                self._report_batch_area_disagreement(areas_of_interest, full_path)

            if settings['debug_output']:
                self._write_debug_overlay(bgr, full_path, output_dir, debug_layers, hypotheses, scores)

            mask_path = None
            if areas_of_interest:
                mask = np.zeros(bgr.shape[:2], dtype=np.uint8)
                for contour in contours:
                    cv2.fillPoly(mask, [contour], 255)
                output_path = self._construct_output_path(full_path, input_dir, output_dir)
                mask_path = self.store_mask(full_path, output_path, mask)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            # LoggerService.error appends the traceback itself inside an except block.
            self.logger.error(f"RectilinearShape failed for {full_path}: {e}")
            return AnalysisResult(full_path, error_message=f"RectilinearShape failed for {full_path}: {e}")

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    @staticmethod
    def _to_bgr8(img):
        """Normalise the decoded frame to 3-channel uint8 BGR.

        AnalyzeService decodes with IMREAD_UNCHANGED, so the frame may carry
        alpha, be 16-bit, or be single-channel.
        """
        frame = img
        if frame.dtype != np.uint8:
            peak = float(frame.max()) if frame.size else 0.0
            scale = 255.0 / peak if peak > 0 else 1.0
            frame = np.clip(frame.astype(np.float32) * scale, 0, 255).astype(np.uint8)
        if frame.ndim == 2:
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        if frame.shape[2] == 4:
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame

    def _resolve_gsd_cm(self, img, full_path):
        """Ground sample distance at processing resolution, in cm/px.

        Terrain-aware from cached DEM tiles only - a pool worker must never
        block on a download - falling back to the takeoff-relative altitude
        inside ImageService, then to the operator's ``fallback_gsd_cm``.

        Returns:
            tuple: (gsd_cm or None, GSDService or None). The GSD service is
            returned so the oblique-tolerance check can reuse it.
        """
        native_gsd = None
        exif_width = None
        gsd_service = None
        try:
            # Imported here: ImageService pulls in pandas and the metadata
            # stack, which pool workers should not pay for at import time.
            from core.services.image.ImageService import ImageService
            scale = self.scale_factor if self.scale_factor > 0 else 1.0
            frame_size = (int(round(img.shape[1] / scale)), int(round(img.shape[0] / scale)))
            image_service = ImageService(full_path, defer_load=True)
            gsd_service = image_service.get_gsd_service(use_terrain=True, offline_only=True, frame_size=frame_size)
            if gsd_service is not None:
                native_gsd = gsd_service.compute_average_gsd()
                exif_width = gsd_service.image[0]
        except Exception as e:
            self.logger.debug(f"RectilinearShape: GSD lookup failed for {full_path}: {e}")
            gsd_service = None
            native_gsd = None

        if native_gsd is not None and native_gsd > 0 and exif_width:
            # GSD is per EXIF pixel; rescale to the pixels actually being processed.
            return native_gsd * float(exif_width) / float(img.shape[1]), gsd_service

        fallback = self.settings['fallback_gsd_cm']
        if fallback:
            scale = self.scale_factor if self.scale_factor > 0 else 1.0
            self.logger.info(f"RectilinearShape: using fallback GSD {fallback} cm/px for {full_path}")
            return fallback / scale, None
        return None, None

    def _effective_tolerance(self, tolerance, gsd_service, full_path):
        """Widen the size tolerance for oblique frames.

        v1 uses one GSD per image; on an oblique frame the near and far edges
        differ, so the tolerance grows by the bottom/top GSD ratio.
        """
        if gsd_service is None:
            return tolerance
        try:
            tilt = float(getattr(gsd_service, 'title_angle', 0.0) or 0.0)
            if tilt <= _OBLIQUE_TILT_DEG:
                return tolerance
            width, height = gsd_service.image
            centre_col = width / 2.0
            top = gsd_service.compute_gsd(0, centre_col)
            bottom = gsd_service.compute_gsd(height - 1, centre_col)
            if not top or not bottom or top <= 0 or bottom <= 0:
                return tolerance
            ratio = max(top, bottom) / min(top, bottom)
            widened = (1.0 + tolerance) * ratio - 1.0
            self.logger.debug(
                f"RectilinearShape: {full_path} tilt {tilt:.0f} deg, size tolerance widened to {widened:.2f}"
            )
            return widened
        except Exception as e:
            self.logger.debug(f"RectilinearShape: oblique GSD check failed for {full_path}: {e}")
            return tolerance

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def _detect(self, bgr, gsd_cm, tolerance, px_ranges):
        """Run segments -> hypotheses -> scoring -> suppression.

        Returns:
            tuple: (rects, confidences, debug_layers) for the kept hypotheses,
            highest confidence first.
        """
        settings = self.settings
        long_min_px, long_max_px, short_min_px, short_max_px = px_ranges
        angle_tol = settings['angle_tolerance_deg']

        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        working = cv2.GaussianBlur(lab[:, :, 0], (0, 0), _PRE_BLUR_SIGMA)
        mag, ang = geometry.compute_gradients(working)

        # Boxiness on a decimated grid (see RectilinearGeometry.boxiness_map).
        decimation = max(1, int(short_min_px // _BOXINESS_CELLS_PER_SHORT_SIDE))
        window_px = _BOXINESS_WINDOW_FACTOR * long_max_px
        boxiness = theta = None
        if settings['use_boxiness']:
            weights = geometry.boxiness_weights(mag)
            energy_floor = self._boxiness_energy_floor(mag)
            boxiness, _, _, theta, energy = geometry.boxiness_map(weights, ang, window_px, energy_floor, decimation)
            # JPEG blocking: axis-aligned and low-energy windows are halved.
            # A real axis-aligned target carries far more edge energy than
            # block artifacts, so it is unaffected.
            axis_offset = np.minimum(theta, 90.0 - theta)
            blocky = (axis_offset < 2.0) & (energy < 3.0 * energy_floor)
            boxiness[blocky] *= 0.5

        max_len = (1.0 + tolerance) * long_max_px
        segments = geometry.detect_segments(
            working, 0.5 * short_min_px, max_len, settings['min_edge_contrast']
        )
        rects = []
        if len(segments):
            segment_hash = geometry.build_segment_hash(segments, max_len)
            join_px = max(3.0, 0.15 * short_min_px)
            rects.extend(geometry.corner_hypotheses(segments, segment_hash, angle_tol, join_px, max_len))
            separation = ((1.0 - tolerance) * short_min_px, (1.0 + tolerance) * long_max_px)
            rects.extend(geometry.parallel_hypotheses(segments, segment_hash, angle_tol, separation, max_len))
        if boxiness is not None:
            rects.extend(geometry.boxiness_hypotheses(
                boxiness, theta, mag, ang, settings['min_boxiness'], short_min_px,
                window_px, decimation, angle_tol, existing=rects,
            ))

        ranges_cm = (
            settings['long_side_cm_min'], settings['long_side_cm_max'],
            settings['short_side_cm_min'], settings['short_side_cm_max'],
        )
        # Cheapest score first: most pairs are the wrong size.
        sized = []
        for rect in rects:
            s_size = geometry.size_score(rect.length * gsd_cm, rect.width * gsd_cm, ranges_cm, tolerance)
            if s_size >= 0.05:
                sized.append((s_size, rect))
        if len(sized) > _MAX_HYPOTHESES:
            self.logger.info(
                f"RectilinearShape: {len(sized)} size-plausible hypotheses, scoring the best {_MAX_HYPOTHESES}"
            )
            sized.sort(key=lambda item: -item[0])
            sized = sized[:_MAX_HYPOTHESES]

        # Edge support counts pixels at half the segment contrast: the
        # Sobel peak of a blurred step is lower than the step itself.
        contrast_floor = 0.5 * settings['min_edge_contrast']
        scored_rects = []
        scored = []
        for s_size, rect in sized:
            s_edge = geometry.edge_support(rect, mag, ang, angle_tol, contrast_floor, _EDGE_SAMPLES)
            if s_edge < settings['min_edge_support']:
                continue
            delta_e = geometry.ring_contrast_lab(lab, rect, _RING_FRACTION)
            s_ctr = self._contrast_score(delta_e)
            s_box = 1.0
            if boxiness is not None:
                row = min(boxiness.shape[0] - 1, max(0, int(rect.cy // decimation)))
                col = min(boxiness.shape[1] - 1, max(0, int(rect.cx // decimation)))
                s_box = float(boxiness[row, col])
            confidence = 100.0 * (
                s_size ** _EXP_SIZE
                * s_edge ** _EXP_EDGE
                * s_ctr ** _EXP_CONTRAST
                * max(s_box, _BOXINESS_TERM_FLOOR) ** _EXP_BOXINESS
            )
            # Suppression only ever removes a hypothesis in favour of a
            # stronger one, so thresholding first gives the same survivors
            # and keeps the O(n^2) NMS small.
            if confidence < settings['min_confidence']:
                continue
            scored_rects.append(rect)
            scored.append(confidence)

        kept = geometry.rotated_nms(scored_rects, scored, _NMS_IOU)
        kept = kept[:max(0, settings['max_detections_per_image'])]
        debug_layers = {'segments': segments, 'boxiness': boxiness, 'decimation': decimation}
        return [scored_rects[k] for k in kept], [scored[k] for k in kept], debug_layers

    @staticmethod
    def _boxiness_energy_floor(mag):
        """Mean boxiness weight below which a window counts as flat.

        The weights already have the frame's noise floor subtracted (see
        RectilinearGeometry.boxiness_weights), so a window of pure texture
        averages close to zero and one holding a target's perimeter does not.
        The floor stops a near-flat window whose few surviving gradients
        happen to line up from scoring high by chance. Relative to the
        frame's median gradient, with an absolute minimum for frames so
        smooth the median is zero.
        """
        return max(_ENERGY_FLOOR_MIN, _ENERGY_FLOOR_MEDIAN_FRACTION * float(np.median(mag)))

    @staticmethod
    def _contrast_score(delta_e):
        """Saturating map of Delta E to [0, 1]: 0 -> 0, ~15 -> 0.9."""
        k = _CONTRAST_DELTA_E_AT_0_9 / math.log(10.0)
        return 1.0 - math.exp(-max(0.0, delta_e) / k)

    # ------------------------------------------------------------------
    # Emission
    # ------------------------------------------------------------------

    @staticmethod
    def _contour_in_frame(rect, shape):
        """Integer contour of ``rect``, clipped to the frame.

        A target cut by the frame edge yields a rectangle whose fitted corners
        lie outside the image; AOI pixel lists must stay inside it.
        """
        corners = np.rint(geometry.rect_corners(rect)).astype(np.int32)
        corners[:, 0] = np.clip(corners[:, 0], 0, shape[1] - 1)
        corners[:, 1] = np.clip(corners[:, 1], 0, shape[0] - 1)
        return corners.reshape(-1, 1, 2)

    @staticmethod
    def _attach_scores(areas_of_interest, rects, scores):
        """Give each AOI the confidence of the hypothesis whose centre is nearest.

        identify_areas_of_interest re-sorts AOIs by position, so they are
        matched back to hypotheses geometrically.
        """
        centres = np.array([(r.cx, r.cy) for r in rects], dtype=np.float32)
        for aoi in areas_of_interest:
            cx, cy = aoi['center']
            nearest = int(np.argmin(np.hypot(centres[:, 0] - cx, centres[:, 1] - cy)))
            aoi['confidence'] = round(float(scores[nearest]), 1)
            aoi['score_type'] = 'shape'

    def _report_batch_area_disagreement(self, areas_of_interest, full_path):
        """Log AOIs the batch min/max area would have dropped.

        The service gates on physical size instead (see __init__); this keeps
        the disagreement visible when someone compares against the guide's
        target size.
        """
        outside = 0
        for aoi in areas_of_interest:
            area = aoi.get('area', 0)
            too_small = bool(self.batch_min_area) and area < self.batch_min_area
            too_large = bool(self.batch_max_area) and area > self.batch_max_area
            if too_small or too_large:
                outside += 1
        if outside:
            self.logger.info(
                f"RectilinearShape: {outside} detection(s) in {full_path} fall outside the batch "
                f"area limits ({self.batch_min_area}-{self.batch_max_area} px) and were kept; "
                "the target size preset governs this algorithm"
            )

    def _empty_result(self, full_path, output_dir):
        """A successful result with no detections."""
        return AnalysisResult(full_path, None, output_dir, None, None)

    def _write_debug_overlay(self, bgr, full_path, output_dir, layers, rects, scores):
        """Write the tuning overlay: boxiness heatmap, kept segments, hypotheses.

        Saved as <output_dir>/rectilinear_debug/<image>_debug.jpg. A failure
        here must never fail the analysis, so it is logged and swallowed.
        """
        try:
            overlay = bgr.copy()
            boxiness = layers.get('boxiness')
            if boxiness is not None:
                heat = cv2.resize(
                    np.clip(boxiness * 255.0, 0, 255).astype(np.uint8),
                    (bgr.shape[1], bgr.shape[0]),
                    interpolation=cv2.INTER_LINEAR,
                )
                overlay = cv2.addWeighted(overlay, 0.6, cv2.applyColorMap(heat, cv2.COLORMAP_JET), 0.4, 0)
            for x1, y1, x2, y2 in layers.get('segments', []):
                cv2.line(overlay, (int(x1), int(y1)), (int(x2), int(y2)), (160, 160, 160), 1)
            for rect, score in zip(rects, scores):
                # Red at the emission threshold up to green at 100.
                fraction = min(1.0, max(0.0, score / 100.0))
                colour = (0, int(255 * fraction), int(255 * (1.0 - fraction)))
                corners = np.rint(geometry.rect_corners(rect)).astype(np.int32)
                cv2.polylines(overlay, [corners], True, colour, 2)
                cv2.putText(
                    overlay, f"{score:.0f}", (int(rect.cx), int(rect.cy)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1, cv2.LINE_AA,
                )
            debug_dir = Path(output_dir) / 'rectilinear_debug'
            debug_dir.mkdir(parents=True, exist_ok=True)
            target = debug_dir / f"{Path(full_path).stem}_debug.jpg"
            ok, encoded = cv2.imencode('.jpg', overlay)
            if ok:
                encoded.tofile(os.fspath(target))
        except Exception as e:
            self.logger.warning(f"RectilinearShape: debug overlay failed for {full_path}: {e}")
