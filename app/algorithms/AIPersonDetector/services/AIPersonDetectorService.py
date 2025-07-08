import cv2
import numpy as np
import sys
import os
from os import path
import onnxruntime as ort

from core.services.LoggerService import LoggerService
from algorithms.Algorithm import AlgorithmService, AnalysisResult
from helpers.SlidingWindowSlicer import SlidingWindowSlicer

SLICE_SIZE = 1280
OVERLAP = 0.2
MODEL_IMG_SIZE = 640


class AIPersonDetectorService(AlgorithmService):
    """
    Service class for detecting people in images using an ONNX object detection model.
    Processes large images using a sliding window approach, aggregates detections, 
    and identifies areas of interest.

    Args:
        identifier (str): Unique identifier for the analysis run.
        min_area (int): Minimum area for detected objects of interest.
        max_area (int): Maximum area for detected objects of interest.
        aoi_radius (int): Radius for defining areas of interest.
        combine_aois (bool): Whether to combine overlapping AOIs.
        options (dict): Algorithm-specific options, must include 'person_detector_confidence'.
    """

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """
        Initialize the AIPersonDetectorService.

        Args:
            identifier (str): Unique identifier for the analysis run.
            min_area (int): Minimum area for detected objects of interest.
            max_area (int): Maximum area for detected objects of interest.
            aoi_radius (int): Radius for defining areas of interest.
            combine_aois (bool): Whether to combine overlapping AOIs.
            options (dict): Algorithm-specific options, must include 'person_detector_confidence'.
        """
        self.logger = LoggerService()
        super().__init__('AIPersonDetector', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.confidence = options['person_detector_confidence'] / 100

        if getattr(sys, 'frozen', False):
            # Frozen (PyInstaller)
            self.model_path = os.path.join(sys._MEIPASS, 'ai_models' / 'model_s.onnx')
        else:
            # Not frozen (dev)
            self.model_path = path.abspath(path.join(path.dirname(__file__), 'model_s.onnx'))

    def process_image(self, img, full_path, input_dir, output_dir):
        """
        Process a single image to detect people, aggregate results, and identify areas of interest.

        Args:
            img (np.ndarray): Input image (BGR format).
            full_path (str): Full path to the input image.
            input_dir (str): Base input directory.
            output_dir (str): Base output directory.

        Returns:
            AnalysisResult: Result object with details of the analysis.
        """
        session = self._create_onnx_session()
        input_name = session.get_inputs()[0].name
        
        try:
            img_pre_processed = self._preprocess_whole_image(img)
            h, w = img.shape[:2]
            all_boxes = []
            all_scores = []
            all_classes = []
            slices = SlidingWindowSlicer.get_slices(img_pre_processed.shape, SLICE_SIZE, OVERLAP)
            for s_idx, (x1, y1, x2, y2) in enumerate(slices):
                crop = img_pre_processed[y1:y2, x1:x2]
                crop_w = x2 - x1
                crop_h = y2 - y1
                input_tensor = self._preprocess_slice(crop, out_size=MODEL_IMG_SIZE)
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
                    cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), color=255, thickness=-1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            augmented_image, areas_of_interest, base_contour_count = self.circle_areas_of_interest(img, contours)

            output_path = full_path.replace(input_dir, output_dir)
            if augmented_image is not None:
                self.store_image(full_path, output_path, augmented_image)

            return AnalysisResult(full_path, output_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))

    def _preprocess_whole_image(self, img):
        """
        Convert BGR image to RGB and normalize to [0, 1] float32.

        Args:
            img (np.ndarray): Input image in BGR format.

        Returns:
            np.ndarray: Normalized RGB image as float32.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_norm = img_rgb.astype(np.float32) / 255.0
        return img_norm

    def _preprocess_slice(self, slice_img, out_size=640):
        """
        Resize and format image slice for ONNX model input.

        Args:
            slice_img (np.ndarray): Image slice (float32, RGB).
            out_size (int, optional): Size for model input. Defaults to 640.

        Returns:
            np.ndarray: Model-ready input tensor (1, 3, out_size, out_size).
        """
        img_resized = cv2.resize(slice_img, (out_size, out_size))
        img_transposed = np.transpose(img_resized, (2, 0, 1))
        img_input = np.expand_dims(img_transposed, axis=0)
        return img_input

    def _postprocess(self, outputs, slice_rect, crop_w, crop_h):
        """
        Convert model outputs to bounding boxes in full image coordinates.

        Args:
            outputs (list): Raw model outputs.
            slice_rect (tuple): Top-left (x, y) of the slice in original image.
            crop_w (int): Width of slice.
            crop_h (int): Height of slice.

        Returns:
            list[tuple]: Bounding boxes as (x1, y1, x2, y2, confidence, class).
        """
        preds = outputs[0][0]
        bboxes = []
        for pred in preds:
            if len(pred) < 6:
                continue
            x1, y1, x2, y2, conf, cls = pred[:6]
            if conf < self.confidence:
                continue
            x1 = int((x1 / MODEL_IMG_SIZE) * crop_w) + slice_rect[0]
            x2 = int((x2 / MODEL_IMG_SIZE) * crop_w) + slice_rect[0]
            y1 = int((y1 / MODEL_IMG_SIZE) * crop_h) + slice_rect[1]
            y2 = int((y2 / MODEL_IMG_SIZE) * crop_h) + slice_rect[1]
            bboxes.append((x1, y1, x2, y2, float(conf), int(cls)))
        return bboxes

    def _draw_boxes(self, img, bboxes):
        """
        Draw bounding boxes on an image for visualization.

        Args:
            img (np.ndarray): Original image (BGR or RGB).
            bboxes (list[tuple]): List of (x1, y1, x2, y2, confidence, class).

        Returns:
            np.ndarray: Image with boxes drawn.
        """
        for (x1, y1, x2, y2, conf, cls) in bboxes:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f'{conf:.2f}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return img

    def _create_onnx_session(self):
        """
        Create an ONNX Runtime inference session.
        Tries to use CUDAExecutionProvider; falls back to CPUExecutionProvider if CUDA fails.

        Returns:
            onnxruntime.InferenceSession: Loaded ONNX model session.

        Raises:
            Exception: If both CUDA and CPU session creation fails.
        """
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        try:
            # Try to create session with GPU (CUDA)
            return ort.InferenceSession(
                self.model_path,
                sess_options=so,
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
            )
        except Exception as e:
            self.logger.warning(f"Failed to load CUDAExecutionProvider: {e}\nFalling back to CPUExecutionProvider.")
            try:
                # Fallback to CPU only
                return ort.InferenceSession(
                    self.model_path,
                    sess_options=so,
                    providers=["CPUExecutionProvider"]
                )
            except Exception as cpu_e:
                self.logger.error(f"Failed to load CPUExecutionProvider as well: {cpu_e}")
                raise cpu_e  # Escalate since both failed
