"""
Utility functions.
"""

from __future__ import annotations

import os
from multiprocessing import current_process
from subprocess import PIPE, Popen

from ba_core.utils.constants import TEMP_DIR


class SubprocessMixin:
    """__summary__"""

    @staticmethod
    def get_cpid() -> int:
        """Get child process ID for multiprocessing."""
        return current_process()._identity[0] if current_process()._identity else 0

    @staticmethod
    def run_subprocess_fstream(cmd: list[str], fp: str = None) -> None:
        """Run a subprocess and stream the output to a file."""
        if not fp:
            cpid = SubprocessMixin.get_cpid()
            fp = os.path.join(TEMP_DIR, f"subprocess_output_{cpid}.txt")
        # Making a file to store the output
        os.makedirs(os.path.split(fp)[0], exist_ok=True)
        with open(fp, "w", encoding="utf-8") as f:
            # Starting the subprocess
            with Popen(cmd, stdout=f, stderr=f) as p:
                # Wait for the subprocess to finish
                p.wait()
                # Error handling
                if p.returncode:
                    f.seek(0)
                    raise ValueError(f.read().decode())

    @staticmethod
    def run_subprocess_str(cmd: list[str]) -> str:
        """Run a subprocess and return the output as a string."""
        # Running the subprocess
        with Popen(cmd, stdout=PIPE, stderr=PIPE) as p:
            # Wait for the subprocess to finish
            out, err = p.communicate()
            # Error handling
            if p.returncode:
                raise ValueError(err.decode("utf-8"))
            return out.decode("utf-8")

    @staticmethod
    def run_subprocess_console(cmd: list[str]) -> None:
        """Run a subprocess and stream the output to a file."""
        # Starting the subprocess
        with Popen(cmd) as p:
            # Wait for the subprocess to finish
            p.wait()
            # Error handling
            if p.returncode:
                raise ValueError("ERROR: Subprocess failed to run.")
