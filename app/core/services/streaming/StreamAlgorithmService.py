"""Base contract for streaming algorithm services."""

from typing import Any, Dict

import numpy as np
from PySide6.QtCore import QObject

from core.services.streaming.contracts import StreamProcessResult


class StreamAlgorithmService(QObject):
    """Common interface for streaming algorithm processing services."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def update_config(self, config: Dict[str, Any]) -> None:
        raise NotImplementedError

    def get_config(self) -> Dict[str, Any]:
        raise NotImplementedError

    def process_frame(self, frame: np.ndarray, timestamp: float) -> StreamProcessResult:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    def cleanup(self) -> None:
        raise NotImplementedError
