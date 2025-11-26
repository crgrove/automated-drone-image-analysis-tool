"""
Comprehensive tests for CPUService.

Tests CPU core detection and process count recommendations.
"""

import pytest
from unittest.mock import patch
from core.services.CPUService import CPUService


def test_get_cpu_count():
    """Test getting CPU count."""
    count = CPUService.get_cpu_count()

    assert count > 0
    assert isinstance(count, int)


def test_get_cpu_count_fallback():
    """Test CPU count with fallback mechanisms."""
    with patch('os.cpu_count', side_effect=AttributeError):
        with patch('multiprocessing.cpu_count', return_value=4):
            count = CPUService.get_cpu_count()
            assert count == 4


def test_get_cpu_count_default():
    """Test CPU count defaults to 1 if all methods fail."""
    with patch('os.cpu_count', side_effect=AttributeError):
        with patch('multiprocessing.cpu_count', side_effect=OSError):
            count = CPUService.get_cpu_count()
            assert count == 1


def test_get_recommended_process_count():
    """Test getting recommended process count."""
    recommended = CPUService.get_recommended_process_count()

    assert recommended > 0
    assert isinstance(recommended, int)


def test_get_recommended_process_count_single_core():
    """Test recommended process count with single core."""
    with patch.object(CPUService, 'get_cpu_count', return_value=1):
        recommended = CPUService.get_recommended_process_count()
        assert recommended == 1


def test_get_recommended_process_count_multi_core():
    """Test recommended process count with multiple cores."""
    with patch.object(CPUService, 'get_cpu_count', return_value=8):
        recommended = CPUService.get_recommended_process_count()
        assert recommended == 7  # CPU count - 1
