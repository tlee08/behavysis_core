"""
Utility functions.
"""

from __future__ import annotations

from inspect import currentframe
from typing import Callable, Optional

import numpy as np

from behavysis_core.constants import DIAGNOSTICS_SUCCESS_MESSAGES


class DiagnosticsMixin:
    """__summary__"""

    @staticmethod
    def success_msg() -> str:
        """
        Return a random positive message :)
        """
        return np.random.choice(DIAGNOSTICS_SUCCESS_MESSAGES)

    @staticmethod
    def warning_msg(func: Optional[Callable] = None):
        """
        Return a warning message for the given function.
        """
        if not func:
            # Getting the name of the calling function
            func_name = currentframe().f_back.f_code.co_name
        else:
            func_name = func.__name__
        return (
            "WARNING: Output file already exists - not overwriting file.\n"
            + f"To overwrite, specify `{func_name}(..., overwrite=True)`.\n"
        )
