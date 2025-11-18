"""Pytest fixtures for streaming algorithm tests."""

import sys
import os
import pytest
import numpy as np
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock, MagicMock

# Add the app directory to the Python path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


@pytest.fixture(scope='session')
def qapp():
    """Create QApplication for Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def sample_frame():
    """Create a sample test frame (640x480 BGR)."""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_detections():
    """Create sample detection dictionaries."""
    return [
        {
            'bbox': (100, 100, 50, 50),
            'confidence': 0.85,
            'class_name': 'person',
            'id': 1
        },
        {
            'bbox': (200, 200, 80, 80),
            'confidence': 0.92,
            'class_name': 'vehicle',
            'id': 2
        }
    ]


@pytest.fixture
def algorithm_config():
    """Default algorithm configuration."""
    return {
        'name': 'TestAlgorithm',
        'version': '1.0.0',
        'description': 'Test algorithm',
        'category': 'streaming'
    }


@pytest.fixture
def mock_logger():
    """Mock logger service."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def mock_stream_manager():
    """Mock stream manager."""
    manager = Mock()
    manager.connect = Mock(return_value=True)
    manager.disconnect = Mock(return_value=True)
    manager.is_connected = False
    manager.get_stream_info = Mock(return_value={'fps': 30, 'width': 640, 'height': 480})
    return manager


@pytest.fixture
def mock_recording_manager():
    """Mock recording manager."""
    manager = Mock()
    manager.start_recording = Mock(return_value=True)
    manager.stop_recording = Mock(return_value=True)
    manager.is_recording = False
    return manager
