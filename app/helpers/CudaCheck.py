import os
import subprocess
import onnxruntime as ort
import re

class CudaCheck:

    @staticmethod
    def check_onnxruntime_gpu_env():
        """
        Check the runtime environment for ONNX GPU support:
        - CUDA Toolkit installation (version >= 12.0)
        - cuDNN installation
        - cuDNN path configuration
        - ONNX Runtime CUDAExecutionProvider availability

        Returns:
            dict: A dictionary summarizing each check and an overall result.
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

        # Check CUDA
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

        # Check cuDNN (just check if directory exists)
        cuda_path = os.environ.get('CUDA_PATH') or os.environ.get('CUDA_HOME')
        cudnn_installed = False

        if os.name == 'nt':
            default_cudnn_dir = r"C:\Program Files\NVIDIA\CUDNN"
            if os.path.isdir(default_cudnn_dir):
                cudnn_installed = True

        results["cudnn_installed"] = cudnn_installed

        # Check cuDNN in PATH
        env_var = 'PATH' if os.name == 'nt' else 'LD_LIBRARY_PATH'
        search_path = os.environ.get(env_var, '')
        cudnn_dir = ""
        if cuda_path:
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
                # Check ONNX Runtime GPU provider
        providers = ort.get_available_providers()
        results["ort_cuda_provider_available"] = 'CUDAExecutionProvider' in providers

        # Overall check includes version requirement
        results["overall"] = (
            results["cuda_installed"]
            and results["cuda_version_sufficient"]
            and results["cudnn_in_path"]
            and results["ort_cuda_provider_available"]
        )
        return results