import cv2
import numpy as np
import sys
import os
from os import path

# Optional import for onnxruntime - handle DLL load failures gracefully
try:
    import onnxruntime as ort
    ONNXRUNTIME_AVAILABLE = True
except (ImportError, OSError, Exception) as e:
    ONNXRUNTIME_AVAILABLE = False
    ort = None
    _onnxruntime_error = str(e)

from core.services.LoggerService import LoggerService
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from helpers.SlidingWindowSlicer import SlidingWindowSlicer

OVERLAP = 0.2


class AIPersonDetectorService(AlgorithmService):
    """Service class for detecting people in images using an ONNX object detection model.

    Processes large images using a sliding window approach, aggregates detections,
    and identifies areas of interest. Supports both CPU and GPU inference.

    Attributes:
        confidence: Confidence threshold for detections (0.0 to 1.0).
        cpu_only: Whether to use CPU-only mode.
        slice_size: Size of image slices for processing.
        model_img_size: Input size for the ONNX model.
        model_path: Path to the ONNX model file.
    """

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """Initialize the AIPersonDetectorService.

        Args:
            identifier: Unique identifier for the analysis run.
            min_area: Minimum area for detected objects of interest.
            max_area: Maximum area for detected objects of interest.
            aoi_radius: Radius for defining areas of interest.
            combine_aois: Whether to combine overlapping AOIs.
            options: Algorithm-specific options, must include
                'person_detector_confidence' and 'cpu_only'.
        
        Raises:
            RuntimeError: If onnxruntime is not available or cannot be loaded.
        """
        self.logger = LoggerService()
        
        # Check if onnxruntime is available before proceeding
        if not ONNXRUNTIME_AVAILABLE or ort is None:
            error_msg = (
                "ONNX Runtime is not available. The AI Person Detector requires onnxruntime to function. "
                "Please ensure onnxruntime-directml is properly installed. "
                "If you continue to see this error, the DLL may have failed to load. "
                "Try reinstalling the application or installing the required Visual C++ Redistributables."
            )
            if '_onnxruntime_error' in globals():
                error_msg += f"\nOriginal error: {_onnxruntime_error}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        super().__init__('AIPersonDetector', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.confidence = options['person_detector_confidence'] / 100
        self.cpu_only = options['cpu_only']
        if self.cpu_only:
            self.slice_size = 1280
            self.model_img_size = 640
            if getattr(sys, 'frozen', False):
                # Frozen (PyInstaller)
                self.model_path = os.path.join(sys._MEIPASS, 'ai_models', 'ai_person_model_V2_640.onnx')
            else:
                # Not frozen (dev)
                self.model_path = path.abspath(path.join(path.dirname(__file__), 'ai_person_model_V2_640.onnx'))
        else:
            self.slice_size = 2048
            self.model_img_size = 1024
            if getattr(sys, 'frozen', False):
                # Frozen (PyInstaller)
                self.model_path = os.path.join(sys._MEIPASS, 'ai_models', 'ai_person_model_V2_1024.onnx')
            else:
                # Not frozen (dev)
                self.model_path = path.abspath(path.join(path.dirname(__file__), 'ai_person_model_V2_1024.onnx'))

    def process_image(self, img, full_path, input_dir, output_dir):
        """Process a single image to detect people, aggregate results, and identify areas of interest.

        Uses sliding window approach to process large images, runs ONNX model
        inference on each slice, aggregates detections, and applies NMS to
        remove duplicates.

        Args:
            img: Input image (BGR format) as numpy array.
            full_path: Full path to the input image.
            input_dir: Base input directory.
            output_dir: Base output directory.

        Returns:
            AnalysisResult object with details of the analysis including
            detected people as areas of interest.
        """
        session = self._create_onnx_session()
        input_name = session.get_inputs()[0].name

        try:
            img_pre_processed = self._preprocess_whole_image(img)
            all_boxes = []
            all_scores = []
            all_classes = []
            slices = SlidingWindowSlicer.get_slices(img_pre_processed.shape, self.slice_size, OVERLAP)
            for s_idx, (x1, y1, x2, y2) in enumerate(slices):
                crop = img_pre_processed[y1:y2, x1:x2]
                crop_w = x2 - x1
                crop_h = y2 - y1
                input_tensor = self._preprocess_slice(crop, out_size=self.model_img_size)
                outputs = session.run(None, {input_name: input_tensor})
                bboxes = self._postprocess(outputs, (x1, y1), crop_w, crop_h)
                for bx in bboxes:
                    bx1, by1, bx2, by2, conf, cls = bx
                    all_boxes.append([bx1, by1, bx2, by2])
                    all_scores.append(conf)
                    all_classes.append(cls)
            merged_bboxes = SlidingWindowSlicer.merge_slice_detections(
                all_boxes, all_scores, all_classes, iou_threshold=0.5
            )

            # --- MASK LOGIC ---
            mask = np.zeros(img.shape[:2], dtype=np.uint8)

            for bbox in merged_bboxes:
                x_min, y_min, x_max, y_max, conf, cls = bbox
                if conf >= self.confidence:
                    # Fill the bounding box area with white (255)
                    mask[y_min:y_max, x_min:x_max] = 255

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)
            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                mask_path = self.store_mask(full_path, output_path, mask)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))

    def _preprocess_whole_image(self, img):
        """Convert BGR image to RGB and normalize to [0, 1] float32.

        Args:
            img: Input image in BGR format as numpy array.

        Returns:
            Normalized RGB image as float32 numpy array.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_norm = img_rgb.astype(np.float32) / 255.0
        return img_norm

    def _preprocess_slice(self, slice_img, out_size=640):
        """Resize and format image slice for ONNX model input.

        Args:
            slice_img: Image slice (float32, RGB) as numpy array.
            out_size: Size for model input. Defaults to 640.

        Returns:
            Model-ready input tensor (1, 3, out_size, out_size) as numpy array.
        """
        img_resized = cv2.resize(slice_img, (out_size, out_size))
        img_transposed = np.transpose(img_resized, (2, 0, 1))
        img_input = np.expand_dims(img_transposed, axis=0)
        return img_input

    def _postprocess(self, outputs, slice_rect, crop_w, crop_h):
        """Convert model outputs to bounding boxes in full image coordinates.

        Args:
            outputs: Raw model outputs from ONNX inference.
            slice_rect: Top-left (x, y) of the slice in original image.
            crop_w: Width of slice.
            crop_h: Height of slice.

        Returns:
            List of bounding boxes as (x1, y1, x2, y2, confidence, class) tuples.
        """
        preds = outputs[0][0]
        bboxes = []
        for pred in preds:
            if len(pred) < 6:
                continue
            x1, y1, x2, y2, conf, cls = pred[:6]
            if conf < self.confidence:
                continue
            x1 = int((x1 / self.model_img_size) * crop_w) + slice_rect[0]
            x2 = int((x2 / self.model_img_size) * crop_w) + slice_rect[0]
            y1 = int((y1 / self.model_img_size) * crop_h) + slice_rect[1]
            y2 = int((y2 / self.model_img_size) * crop_h) + slice_rect[1]
            bboxes.append((x1, y1, x2, y2, float(conf), int(cls)))
        return bboxes

    def _create_onnx_session(self):
        """Create an ONNX Runtime inference session.

        Tries to use DmlExecutionProvider (DirectML) first; falls back to
        CPUExecutionProvider if DirectML fails or if cpu_only is True.

        Returns:
            Loaded ONNX model session (onnxruntime.InferenceSession).
        """
        so = ort.SessionOptions()
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        so.enable_mem_pattern = False
        so.enable_mem_reuse = True
        so.enable_profiling = False
        so.intra_op_num_threads = 1

        providers_cuda_first = ["DmlExecutionProvider", "CPUExecutionProvider"]

        providers_cpu_only = ["CPUExecutionProvider"]
        if self.cpu_only:
            return ort.InferenceSession(
                self.model_path,
                sess_options=so,
                providers=providers_cpu_only
            )
        try:
            return ort.InferenceSession(
                self.model_path,
                sess_options=so,
                providers=providers_cuda_first
            )
        except Exception as e:
            self.logger.warning(f"DmlExecutionProvider failed: {e}")
            try:
                return ort.InferenceSession(
                    self.model_path,
                    sess_options=so,
                    providers=providers_cpu_only
                )
            except Exception as cpu_e:
                self.logger.error(f"Failed to load model even with CPUExecutionProvider: {cpu_e}")
                raise RuntimeError("ONNX model could not be loaded with any provider.")
