import os
import multiprocessing


class CPUService:
    """Platform-agnostic service for detecting CPU core count."""
    
    @staticmethod
    def get_cpu_count():
        """
        Get the number of CPU cores available on the system.
        
        Uses os.cpu_count() which is available on all platforms (Python 3.4+).
        Falls back to multiprocessing.cpu_count() if needed.
        
        Returns:
            int: Number of CPU cores, or 1 if detection fails.
        """
        try:
            # os.cpu_count() is the most reliable and platform-agnostic method
            count = os.cpu_count()
            if count is not None and count > 0:
                return count
        except (AttributeError, OSError):
            pass
        
        # Fallback to multiprocessing.cpu_count()
        try:
            count = multiprocessing.cpu_count()
            if count is not None and count > 0:
                return count
        except (OSError, NotImplementedError):
            pass
        
        # Default to 1 if all detection methods fail
        return 1
    
    @staticmethod
    def get_recommended_process_count():
        """
        Get the recommended number of processes to run simultaneously.
        
        Typically, this is CPU count - 1 to leave one core for the OS and UI.
        
        Returns:
            int: Recommended number of processes (at least 1).
        """
        cpu_count = CPUService.get_cpu_count()
        recommended = max(1, cpu_count - 1)
        return recommended

