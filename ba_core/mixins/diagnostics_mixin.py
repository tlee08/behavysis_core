"""
Utility functions.
"""

from __future__ import annotations

from inspect import currentframe
from typing import Callable, Optional

import numpy as np

from ba_core.utils.constants import DIAGNOSTICS_SUCCESS_MESSAGES


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
            func = currentframe().f_back.f_code.co_name
        return (
            "WARNING: Output file already exists - not overwriting file.\n"
            + f"To overwrite, specify `{func.__name__}(..., overwrite=True)`.\n"
        )
