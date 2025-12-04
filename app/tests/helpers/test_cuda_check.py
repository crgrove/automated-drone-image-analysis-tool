"""
Comprehensive tests for CudaCheck.

Tests CUDA and GPU support detection utilities.
"""

import pytest
from unittest.mock import patch, MagicMock
from helpers.CudaCheck import CudaCheck


def test_check_onnxruntime_gpu_env_no_cuda():
    """Test when CUDA is not installed."""
    with patch('subprocess.check_output', side_effect=Exception("nvcc not found")):
        result = CudaCheck.check_onnxruntime_gpu_env()

        assert result['cuda_installed'] is False
        assert result['cuda_version_sufficient'] is False
        assert result['overall'] is False


def test_check_onnxruntime_gpu_env_cuda_old_version():
    """Test when CUDA is installed but version is too old."""
    mock_output = "Cuda compilation tools, release 11.5, V11.5.0"

    with patch('subprocess.check_output', return_value=mock_output), \
            patch('os.path.isdir', return_value=False), \
            patch('os.environ.get', return_value=''), \
            patch('onnxruntime.get_available_providers', return_value=[]):
        result = CudaCheck.check_onnxruntime_gpu_env()

        assert result['cuda_installed'] is True
        assert result['cuda_version_sufficient'] is False
        assert result['overall'] is False


def test_check_onnxruntime_gpu_env_cuda_sufficient():
    """Test when CUDA version is sufficient."""
    mock_output = "Cuda compilation tools, release 12.0, V12.0.0"

    def mock_isdir(path):
        # Return True for the default cudnn dir and bin path
        if path == r"C:\Program Files\NVIDIA\CUDNN":
            return True
        if path == r"C:\Program Files\NVIDIA\CUDNN\v9\bin":
            return True
        return False

    def mock_listdir(path):
        if path == r"C:\Program Files\NVIDIA\CUDNN":
            return ['v9']
        if path == r"C:\Program Files\NVIDIA\CUDNN\v9\bin":
            return ['12']
        return []

    def mock_environ_get(key, default=''):
        if key == 'PATH':
            return r'C:\Program Files\NVIDIA\CUDNN\v9\bin\12;other;paths'
        if key == 'CUDA_PATH' or key == 'CUDA_HOME':
            return r'C:\Program Files\NVIDIA\CUDA\v12.0'
        return default

    with patch('subprocess.check_output', return_value=mock_output), \
            patch('os.path.isdir', side_effect=mock_isdir), \
            patch('os.listdir', side_effect=mock_listdir), \
            patch('os.path.join', side_effect=lambda *args: '\\'.join(args)), \
            patch('os.environ.get', side_effect=mock_environ_get), \
            patch('onnxruntime.get_available_providers', return_value=['CUDAExecutionProvider']):
        result = CudaCheck.check_onnxruntime_gpu_env()

        assert result['cuda_installed'] is True
        assert result['cuda_version_sufficient'] is True
        assert result['cudnn_in_path'] is True
        assert result['ort_cuda_provider_available'] is True


def test_check_onnxruntime_gpu_env_no_cudnn():
    """Test when CUDA is installed but cuDNN is not."""
    mock_output = "Cuda compilation tools, release 12.0, V12.0.0"

    with patch('subprocess.check_output', return_value=mock_output), \
            patch('os.path.isdir', return_value=False), \
            patch('os.environ.get', return_value=''), \
            patch('onnxruntime.get_available_providers', return_value=['CUDAExecutionProvider']):
        result = CudaCheck.check_onnxruntime_gpu_env()

        assert result['cuda_installed'] is True
        assert result['cuda_version_sufficient'] is True
        assert result['cudnn_installed'] is False
        assert result['overall'] is False


def test_check_onnxruntime_gpu_env_no_ort_provider():
    """Test when CUDA is installed but ONNX Runtime provider is not available."""
    mock_output = "Cuda compilation tools, release 12.0, V12.0.0"

    with patch('subprocess.check_output', return_value=mock_output), \
            patch('os.path.isdir', return_value=True), \
            patch('os.listdir', return_value=['v9']), \
            patch('os.path.join', side_effect=lambda *args: '/'.join(args)), \
            patch('os.environ.get', return_value='C:\\Program Files\\NVIDIA\\CUDNN\\v9\\bin\\12'), \
            patch('onnxruntime.get_available_providers', return_value=[]):  # No CUDA provider
        result = CudaCheck.check_onnxruntime_gpu_env()

        assert result['cuda_installed'] is True
        assert result['cuda_version_sufficient'] is True
        assert result['ort_cuda_provider_available'] is False
        assert result['overall'] is False
