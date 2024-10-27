"""
Functions have the following format:

Parameters
----------
dlc_fp : str
    The DLC dataframe filepath of the experiment to analyse.
analysis_dir : str
    The analysis directory path.
configs_fp : str
    the experiment's JSON configs file.

Returns
-------
str
    The outcome of the process.
"""

from __future__ import annotations

from enum import Enum

from behavysis_core.constants import FramesIN
from behavysis_core.df_classes.df_mixin import DFMixin

####################################################################################################
# ANALYSIS DATAFRAME CONSTANTS
####################################################################################################


class AnalyseCombineCN(Enum):
    """Enum for the columns in the analysis dataframe."""

    ANALYSIS = "analysis"
    INDIVIDUALS = "individuals"
    MEASURES = "measures"


#####################################################################
#               ANALYSIS API FUNCS
#####################################################################


class AnalyseCombineDf(DFMixin):
    """__summary__"""

    NULLABLE = False
    IN = FramesIN
    CN = AnalyseCombineCN
