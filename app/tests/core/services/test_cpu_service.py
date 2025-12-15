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

    # Should return at least 1
    assert count >= 1
    assert isinstance(count, int)


def test_get_cpu_count_with_mock():
    """Test getting CPU count with mocked os.cpu_count."""
    with patch('os.cpu_count', return_value=8):
        count = CPUService.get_cpu_count()
        assert count == 8


def test_get_cpu_count_fallback():
    """Test fallback to multiprocessing when os.cpu_count fails."""
    with patch('os.cpu_count', side_effect=AttributeError), \
            patch('multiprocessing.cpu_count', return_value=4):
        count = CPUService.get_cpu_count()
        assert count == 4


def test_get_cpu_count_default():
    """Test default to 1 when all methods fail."""
    with patch('os.cpu_count', return_value=None), \
            patch('multiprocessing.cpu_count', side_effect=OSError):
        count = CPUService.get_cpu_count()
        assert count == 1


def test_get_recommended_process_count():
    """Test getting recommended process count."""
    with patch('core.services.CPUService.CPUService.get_cpu_count', return_value=8):
        recommended = CPUService.get_recommended_process_count()
        # Should be CPU count - 1, but at least 1
        assert recommended == 7
        assert recommended >= 1


def test_get_recommended_process_count_single_core():
    """Test recommended process count with single core."""
    with patch('core.services.CPUService.CPUService.get_cpu_count', return_value=1):
        recommended = CPUService.get_recommended_process_count()
        # Should still be at least 1
        assert recommended == 1
