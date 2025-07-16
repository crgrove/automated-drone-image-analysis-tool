import numpy as np


class SlidingWindowSlicer:
    """
    Utility class for performing sliding window operations on images, including
    slicing an image into overlapping windows and merging detection results.
    """

    @staticmethod
    def get_slices(img_shape, slice_size, overlap):
        """
        Compute a list of sliding window slices over an image.

        Args:
            img_shape (tuple): Shape of the input image as (height, width, ...).
            slice_size (int): Size (pixels) of each window (assumes square windows).
            overlap (float): Fractional overlap between consecutive windows (0 to <1).

        Returns:
            list of tuple: List of window coordinates as (x1, y1, x2, y2), where
            (x1, y1) is the top-left and (x2, y2) is the bottom-right corner of the slice.
        """
        h, w = img_shape[:2]
        step = int(slice_size * (1 - overlap))
        xs = list(range(0, max(w - slice_size + 1, 1), step))
        ys = list(range(0, max(h - slice_size + 1, 1), step))
        if xs[-1] != w - slice_size:
            xs.append(w - slice_size)
        if ys[-1] != h - slice_size:
            ys.append(h - slice_size)
        slices = []
        for y in ys:
            for x in xs:
                x2 = min(x+slice_size, w)
                y2 = min(y+slice_size, h)
                slices.append((x, y, x2, y2))
        return slices

    @staticmethod
    def merge_slice_detections(all_boxes, all_scores, all_classes, iou_threshold=0.5):
        """
        Merge overlapping bounding boxes from multiple sliding windows using non-maximum suppression (NMS).

        Args:
            all_boxes (list of list or ndarray): Bounding boxes, each as [x1, y1, x2, y2].
            all_scores (list or ndarray): Confidence scores for each bounding box.
            all_classes (list or ndarray): Class labels for each bounding box.
            iou_threshold (float, optional): IoU threshold for NMS. Detections with IoU > threshold are suppressed.
                Defaults to 0.5.

        Returns:
            list of tuple: Merged bounding boxes, each as (x1, y1, x2, y2, score, class).
        """
        if len(all_boxes) == 0:
            return []
        boxes = np.array(all_boxes)
        scores = np.array(all_scores)
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            iou = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(iou <= iou_threshold)[0]
            order = order[inds + 1]
        merged = [(*all_boxes[i], all_scores[i], all_classes[i]) for i in keep]
        return merged
