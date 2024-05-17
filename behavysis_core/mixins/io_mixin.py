"""
Utility functions.
"""

from __future__ import annotations

import os
import re
import shutil


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
