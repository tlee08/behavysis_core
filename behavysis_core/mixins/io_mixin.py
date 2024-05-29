"""
Utility functions.
"""

from __future__ import annotations

import functools
import os
import re
import shutil
from typing import Any, Callable

from behavysis_core.mixins.diagnostics_mixin import DiagnosticsMixin


class IOMixin:
    """__summary__"""

    @staticmethod
    def clear_dir_junk(my_dir: str) -> None:
        """
        Removes all hidden junk files in given directory.
        Hidden files begin with ".".
        """
        for i in os.listdir(dir):
            path = os.path.join(my_dir, i)
            # If the file has a "." at the start, remove it
            if re.search(r"^\.", i):
                IOMixin.silent_rm(path)

    @staticmethod
    def silent_rm(fp: str) -> None:
        """
        Removes the given file or dir if it exists.
        Does nothing if not.
        Does not throw any errors,
        """
        try:
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)
        except (OSError, FileNotFoundError):
            pass

    @staticmethod
    def get_name(fp: str) -> str:
        """
        Given the filepath, returns the name of the file.
        The name is:
        ```
        <path_to_file>/<name>.<ext>
        ```
        """
        return os.path.splitext(os.path.basename(fp))[0]

    @staticmethod
    def overwrite_check(
        out_fp_var: str = "out_fp", overwrite_var: str = "overwrite"
    ) -> Callable[[Any], str]:
        """
        Decorator to check if we should skip processing (i.e. not overwrite the file).
        Returns the function early if we should skip.
        """

        def decorator(func: Callable[[Any], str]) -> Callable[[Any], str]:
            """__summary__"""

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> str:
                """__summary__"""
                out_fp = kwargs.get(out_fp_var, False)
                overwrite = kwargs.get(overwrite_var, False)
                # If overwrite is False, checking if we should skip processing
                if not overwrite and os.path.exists(out_fp):
                    return DiagnosticsMixin.warning_msg()
                # Running the function and returning
                return func(*args, **kwargs)

            return wrapper

        return decorator
