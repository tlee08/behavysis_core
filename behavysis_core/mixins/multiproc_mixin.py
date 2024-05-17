"""
Utility functions.
"""

from __future__ import annotations

import re
import subprocess
from multiprocessing import current_process


class MultiprocMixin:
    """__summary__"""

    @staticmethod
    def get_cpid() -> int:
        """Get child process ID for multiprocessing."""
        return current_process()._identity[0] if current_process()._identity else 0

    @staticmethod
    def get_gpu_ids():
        """
        gets list of GPU IDs from nvidia-smi
        """
        try:
            smi_output = subprocess.check_output(
                ["nvidia-smi", "-L"], universal_newlines=True
            )
            gpu_ids = re.findall(r"GPU (\d+):", smi_output)
            return gpu_ids
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            return []
