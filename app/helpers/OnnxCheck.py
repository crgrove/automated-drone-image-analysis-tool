import os
import subprocess
import re

# Optional import for onnxruntime - handle DLL load failures gracefully
try:
    import onnxruntime as ort
    ONNXRUNTIME_AVAILABLE = True
except (ImportError, OSError, Exception) as e:
    ONNXRUNTIME_AVAILABLE = False
    ort = None
    _onnxruntime_error = str(e)


class OnnxCheck:
    """Helper class for checking ONNX Runtime availability and execution providers.

    Note: This class is used with onnxruntime-directml, which uses DirectML
    (DirectX) for GPU acceleration, not CUDA. DirectML works on Windows with
    DirectX 12 compatible GPUs and does not require CUDA/cuDNN.
    """

    @staticmethod
    def is_onnxruntime_available():
        """Check if onnxruntime is available and can be imported.

        Returns:
            bool: True if onnxruntime is available, False otherwise.
        """
        return ONNXRUNTIME_AVAILABLE

    @staticmethod
    def check_directml_availability():
        """Check if DirectML execution provider is available.

        Since we're using onnxruntime-directml, this checks for the
        DmlExecutionProvider which provides GPU acceleration via DirectX.

        Returns:
            Dictionary with DirectML availability information:
            {
                "onnxruntime_available": bool,
                "dml_provider_available": bool,
                "available_providers": list,
                "overall": bool
            }
        """
        results = {
            "onnxruntime_available": ONNXRUNTIME_AVAILABLE,
            "dml_provider_available": False,
            "available_providers": [],
            "overall": False,
        }

        if ONNXRUNTIME_AVAILABLE and ort is not None:
            try:
                providers = ort.get_available_providers()
                results["available_providers"] = providers
                results["dml_provider_available"] = 'DmlExecutionProvider' in providers
            except Exception:
                results["dml_provider_available"] = False
                results["available_providers"] = []

        results["overall"] = results["onnxruntime_available"] and results["dml_provider_available"]
        return results

    @staticmethod
    def check_onnxruntime_gpu_env():
        """Check the runtime environment for ONNX GPU support.

        DEPRECATED: This method checks for CUDA, but we use DirectML.
        Use check_directml_availability() instead.

        Kept for backward compatibility with existing tests.

        Returns:
            Dictionary summarizing each check and an overall result:
            {
                "cuda_installed": bool,
                "cuda_version_sufficient": bool,
                "cudnn_installed": bool,
                "cudnn_in_path": bool,
                "ort_cuda_provider_available": bool,
                "overall": bool
            }
        """
        results = {
            "cuda_installed": False,
            "cuda_version_sufficient": False,
            "cudnn_installed": False,
            "cudnn_in_path": False,
            "ort_cuda_provider_available": False,
        }

        # Check CUDA (not needed for DirectML, but kept for compatibility)
        try:
            output = subprocess.check_output(['nvcc', '--version'], encoding='utf-8')
            results["cuda_installed"] = True

            # Parse version from output
            match = re.search(r"release (\d+)\.(\d+)", output)
            if match:
                major, _ = int(match.group(1)), int(match.group(2))
                results["cuda_version_sufficient"] = major >= 12
        except Exception:
            results["cuda_installed"] = False
            results["cuda_version_sufficient"] = False

        # Check cuDNN (not needed for DirectML, but kept for compatibility)
        cuda_path = os.environ.get('CUDA_PATH') or os.environ.get('CUDA_HOME')
        cudnn_installed = False
        default_cudnn_dir = None

        if os.name == 'nt':
            default_cudnn_dir = r"C:\Program Files\NVIDIA\CUDNN"
            if os.path.isdir(default_cudnn_dir):
                cudnn_installed = True

        results["cudnn_installed"] = cudnn_installed

        # Check cuDNN in PATH (not needed for DirectML)
        env_var = 'PATH' if os.name == 'nt' else 'LD_LIBRARY_PATH'
        search_path = os.environ.get(env_var, '')
        cudnn_dir = ""
        if cuda_path and default_cudnn_dir and os.path.isdir(default_cudnn_dir):
            try:
                # Find first matching v9+ folder
                for v_folder in os.listdir(default_cudnn_dir):
                    if re.match(r"v(\d+)", v_folder, re.IGNORECASE):
                        major_version = int(re.match(r"v(\d+)", v_folder, re.IGNORECASE).group(1))
                        if major_version >= 9:
                            v_path = os.path.join(default_cudnn_dir, v_folder)
                            sub_dir = 'bin' if os.name == 'nt' else 'lib64'

                            # Find CUDA version subfolder >= 12
                            bin_path = os.path.join(v_path, sub_dir)
                            if os.path.isdir(bin_path):
                                for cuda_ver in os.listdir(bin_path):
                                    if re.match(r"^(\d+)", cuda_ver):
                                        if int(re.match(r"^(\d+)", cuda_ver).group(1)) >= 12:
                                            cudnn_dir = os.path.join(bin_path, cuda_ver)
                                            raise StopIteration
            except StopIteration:
                pass

        results["cudnn_in_path"] = cudnn_dir in search_path if cudnn_dir else False

        # Check ONNX Runtime providers (only if onnxruntime is available)
        if ONNXRUNTIME_AVAILABLE and ort is not None:
            try:
                providers = ort.get_available_providers()
                results["ort_cuda_provider_available"] = 'CUDAExecutionProvider' in providers
            except Exception:
                results["ort_cuda_provider_available"] = False
        else:
            results["ort_cuda_provider_available"] = False

        # Overall check (not meaningful for DirectML, but kept for compatibility)
        results["overall"] = (
            results["cuda_installed"]
            and results["cuda_version_sufficient"]
            and results["cudnn_in_path"]
            and results["ort_cuda_provider_available"]
        )
        return results
