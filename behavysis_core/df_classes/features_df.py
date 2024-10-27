"""
Utility functions.
"""

from __future__ import annotations

from enum import Enum

from behavysis_core.constants import FramesIN
from behavysis_core.df_classes.df_mixin import DFMixin

####################################################################################################
# DATAFRAME CONSTANTS
####################################################################################################


class FeaturesCN(Enum):
    """Enum for the columns in the extracted features dataframe."""

    FEATURES = "features"


####################################################################################################
# MIXIN CLASS
####################################################################################################


class FeaturesDfMixin(DFMixin):
    """
    Mixin for features DF
    (generated from SimBA feature extraction)
    functions.
    """

    NULLABLE = False
    IN = FramesIN
    CN = FeaturesCN
