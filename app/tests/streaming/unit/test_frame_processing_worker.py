"""Unit tests for FrameProcessingWorker."""

import numpy as np

from core.controllers.streaming.components.FrameProcessingWorker import FrameProcessingWorker


def test_paused_frame_emits_skipped_result():
    """Paused frames should still emit a callback to release in-flight state."""
    frame = np.zeros((32, 32, 3), dtype=np.uint8)
    worker = FrameProcessingWorker(lambda _f, _t: [], pause_check=lambda: True)

    received = []
    worker.frameProcessed.connect(
        lambda frm, dets, ts, ms, skipped, pos: received.append((frm, dets, ts, ms, skipped, pos))
    )

    worker._process_frame_internal(frame, 1.23, 7)

    assert len(received) == 1
    out_frame, detections, timestamp, processing_ms, skipped, frame_pos = received[0]
    assert out_frame.shape == frame.shape
    assert detections == []
    assert timestamp == 1.23
    assert processing_ms == 0.0
    assert skipped is True
    assert frame_pos == 7
