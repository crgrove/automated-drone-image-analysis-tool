"""Unit tests for streaming AI person detector service."""

import numpy as np
from unittest.mock import Mock, patch

from algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService import (
    AIPersonStreamingService,
    AIPersonStreamingConfig,
)


class TestAIPersonStreamingService:
    """Test suite for AIPersonStreamingService."""

    def test_default_config_uses_source_fps_mode(self):
        """Default service config should not impose an algorithm FPS cap."""
        cfg = AIPersonStreamingConfig()

        assert cfg.confidence_threshold == 0.50
        assert cfg.render_text is True
        assert cfg.max_detections_to_render == 25
        assert cfg.target_fps is None
        assert cfg.enable_temporal_voting is False
        assert cfg.enable_aspect_ratio_filter is False
        assert cfg.max_aspect_ratio == 5.0
        # SAR default: tile + letterbox on (no whole-frame stretch-to-square).
        assert cfg.enable_tiled_inference is True
        assert cfg.use_letterbox_preprocessing is True

    def test_process_frame_converts_raw_boxes_to_detections(self):
        """Service should convert model boxes into streaming detection objects."""
        service = AIPersonStreamingService()
        service.update_config(
            AIPersonStreamingConfig(
                confidence_threshold=0.5,
                max_detections_to_render=10,
                render_text=False,
                enable_temporal_voting=False,
            )
        )

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with patch(
            "algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService.ONNXRUNTIME_AVAILABLE",
            True,
        ), patch.object(
            service,
            "_infer",
            return_value=[(10, 20, 110, 220, 0.9), (0, 0, 2, 2, 0.4)],
        ):
            annotated, detections, timings = service.process_frame(frame, 12.34)

        assert annotated.shape == frame.shape
        assert len(detections) == 1
        assert detections[0].bbox == (10, 20, 100, 200)
        assert detections[0].detection_type == "person"
        assert detections[0].confidence == 0.9
        assert timings.total_ms >= 0.0

    def test_apply_nms_removes_overlapping_boxes(self):
        """Overlapping tiled/full-frame detections should merge via NMS."""
        service = AIPersonStreamingService()

        filtered = service._apply_nms(
            [
                (10, 10, 110, 210, 0.95),
                (12, 12, 108, 208, 0.90),
                (200, 50, 260, 180, 0.80),
            ],
            0.45,
        )

        assert len(filtered) == 2
        assert filtered[0][:4] == (10, 10, 110, 210)

    def test_apply_mask_filter_rejects_outside_mask(self):
        """Mask filtering should keep only detections inside the allowed region."""
        service = AIPersonStreamingService()
        detections = [
            service._to_detection_objects([(10, 10, 40, 60, 0.9)], 1.0, 1.0, 1.0, 0.5, 0)[0],
            service._to_detection_objects([(70, 70, 90, 95, 0.9)], 1.0, 1.0, 1.0, 0.5, 0)[0],
        ]
        cfg = AIPersonStreamingConfig(
            mask_enabled=True,
            frame_mask_enabled=True,
            frame_buffer_pixels=20,
            enable_temporal_voting=False,
        )

        filtered = service._apply_mask_filter(detections, (100, 100, 3), cfg)

        assert len(filtered) == 1
        assert filtered[0].centroid == detections[0].centroid

    def test_temporal_voting_requires_confirmation(self):
        """Detections should only emit once they persist across the configured window."""
        service = AIPersonStreamingService()
        cfg = AIPersonStreamingConfig(
            enable_temporal_voting=True,
            temporal_window_frames=5,
            temporal_threshold_frames=3,
        )
        detection = service._to_detection_objects([(10, 10, 50, 110, 0.9)], 1.0, 1.0, 1.0, 0.5, 0)[0]

        assert service._apply_temporal_voting([detection], cfg) == []
        assert service._apply_temporal_voting([detection], cfg) == []

        stabilized = service._apply_temporal_voting([detection], cfg)

        assert len(stabilized) == 1
        assert stabilized[0].bbox == detection.bbox

    def test_prepare_model_input_restores_letterboxed_coordinates(self):
        """Letterbox preprocessing should preserve geometry when mapping back."""
        service = AIPersonStreamingService()
        cfg = AIPersonStreamingConfig(high_resolution_model=False, use_letterbox_preprocessing=True)
        frame = np.zeros((200, 400, 3), dtype=np.uint8)

        input_tensor, scale_x, scale_y, pad_x, pad_y = service._prepare_model_input(frame, 640, cfg)

        assert input_tensor.shape == (1, 3, 640, 640)
        assert scale_x == 1.6
        assert scale_y == 1.6
        assert pad_x == 0.0
        assert pad_y == 160.0

    def test_prepare_model_input_uses_axis_specific_scaling_without_letterbox(self):
        """Stretch-to-square preprocessing must restore X/Y with separate scales."""
        service = AIPersonStreamingService()
        cfg = AIPersonStreamingConfig(high_resolution_model=False, use_letterbox_preprocessing=False)
        frame = np.zeros((200, 400, 3), dtype=np.uint8)

        input_tensor, scale_x, scale_y, pad_x, pad_y = service._prepare_model_input(frame, 640, cfg)

        assert input_tensor.shape == (1, 3, 640, 640)
        assert scale_x == 1.6
        assert scale_y == 3.2
        assert pad_x == 0.0
        assert pad_y == 0.0

    def test_process_frame_tiles_on_source_skipping_pre_resize(self):
        """Oversized frames should bypass pre-resize so tiles preserve source resolution."""
        service = AIPersonStreamingService()
        service.update_config(
            AIPersonStreamingConfig(
                confidence_threshold=0.5,
                max_detections_to_render=10,
                render_text=False,
                enable_temporal_voting=False,
                enable_tiled_inference=True,
                processing_width=1280,
                processing_height=720,
            )
        )

        frame = np.zeros((1500, 2000, 3), dtype=np.uint8)
        captured = {}

        def fake_infer(received_frame, cfg):
            captured["shape"] = received_frame.shape
            return [(10, 20, 110, 220, 0.9)]

        with patch(
            "algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService.ONNXRUNTIME_AVAILABLE",
            True,
        ), patch.object(service, "_infer", side_effect=fake_infer):
            _, detections, _ = service.process_frame(frame, 0.0)

        assert captured["shape"] == (1500, 2000, 3)
        assert detections[0].bbox == (10, 20, 100, 200)

    def test_process_frame_pre_resizes_when_not_tiling(self):
        """Without tiling, the frame should still be downscaled to processing resolution."""
        service = AIPersonStreamingService()
        service.update_config(
            AIPersonStreamingConfig(
                confidence_threshold=0.5,
                max_detections_to_render=10,
                render_text=False,
                enable_temporal_voting=False,
                enable_tiled_inference=False,
                processing_width=640,
                processing_height=480,
            )
        )

        frame = np.zeros((1500, 2000, 3), dtype=np.uint8)
        captured = {}

        def fake_infer(received_frame, cfg):
            captured["shape"] = received_frame.shape
            return []

        with patch(
            "algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService.ONNXRUNTIME_AVAILABLE",
            True,
        ), patch.object(service, "_infer", side_effect=fake_infer):
            service.process_frame(frame, 0.0)

        assert captured["shape"] == (480, 640, 3)

    def test_process_frame_tiling_with_letterbox_preserves_frame_coordinates(self):
        """Tiling + letterbox (the new defaults) must map detections back to correct frame
        coordinates. process_frame uses scale 1.0 on the un-resized source while each tile's
        letterbox scale/offset is inverted inside _infer_single_frame, then offset to frame
        space. Regression for the flipped defaults: verifies the two transforms COMPOSE,
        not double-apply."""
        service = AIPersonStreamingService()
        service.update_config(
            AIPersonStreamingConfig(
                confidence_threshold=0.5,
                render_text=False,
                enable_temporal_voting=False,
                enable_tiled_inference=True,
                use_letterbox_preprocessing=True,
                high_resolution_model=False,  # 640 model -> tile_size 960
            )
        )
        # 960x1600 frame -> tiles at x={0,640}, y={0}; each 960x960 square tile letterboxes
        # to 640 at scale 640/960 with zero pad.
        frame = np.zeros((960, 1600, 3), dtype=np.uint8)

        input_meta = Mock()
        input_meta.name = "images"
        mock_session = Mock()
        mock_session.get_inputs.return_value = [input_meta]
        # model-space box (96,96,192,192) -> tile coords (144,144,288,288) at 1.5x inverse scale
        preds = np.array([[[96.0, 96.0, 192.0, 192.0, 0.9, 0.0]]], dtype=np.float32)
        mock_session.run.return_value = [preds]

        with patch(
            "algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService.ONNXRUNTIME_AVAILABLE",
            True,
        ), patch.object(service, "_get_session", return_value=mock_session):
            _, detections, _ = service.process_frame(frame, 0.0)

        # tile0 offset (0,0) -> (144,144,144,144); tile1 offset (640,0) -> (784,144,144,144)
        boxes = sorted(d.bbox for d in detections)
        assert boxes == [(144, 144, 144, 144), (784, 144, 144, 144)]

    def test_tiled_inference_fallback_disables_tiles_after_slow_window(self):
        """Sustained slow tiled inference should auto-disable tiles until reset."""
        service = AIPersonStreamingService()
        service._last_inference_used_tiles = True

        for _ in range(30):
            service._update_tiled_inference_fallback(200.0)

        assert service._tiled_inference_fallback_active is True
        service.reset()
        assert service._tiled_inference_fallback_active is False

    def test_process_frame_returns_empty_when_runtime_unavailable(self):
        """Service should fail gracefully when ONNX runtime is unavailable."""
        service = AIPersonStreamingService()
        frame = np.zeros((120, 160, 3), dtype=np.uint8)

        with patch(
            "algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService.ONNXRUNTIME_AVAILABLE",
            False,
        ):
            annotated, detections, timings = service.process_frame(frame, 1.0)

        assert annotated.shape == frame.shape
        assert detections == []
        assert timings.total_ms >= 0.0

    def test_get_session_uses_cpu_fallback(self):
        """Session creation should fall back to CPU provider after provider failure."""
        service = AIPersonStreamingService()
        cfg = AIPersonStreamingConfig(cpu_only=False)

        mock_ort = Mock()
        mock_ort.ExecutionMode.ORT_SEQUENTIAL = object()
        mock_ort.GraphOptimizationLevel.ORT_ENABLE_ALL = object()
        mock_ort.SessionOptions.return_value = Mock()
        cpu_session = Mock()
        mock_ort.InferenceSession.side_effect = [RuntimeError("DML unavailable"), cpu_session]

        with patch(
            "algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService.ONNXRUNTIME_AVAILABLE",
            True,
        ), patch(
            "algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService.ort",
            mock_ort,
        ), patch.object(
            service,
            "_resolve_model_path",
            return_value="/tmp/model.onnx",
        ):
            session = service._get_session(cfg)

        assert session is cpu_session
        assert mock_ort.InferenceSession.call_count == 2
