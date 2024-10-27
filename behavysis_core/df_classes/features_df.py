"""
Utility functions.
"""

from __future__ import annotations

from enum import Enum

from behavysis_core.df_classes.df_mixin import DFMixin, FramesIN

####################################################################################################
# DF CLASS
####################################################################################################


class FeaturesDf(DFMixin):
    """
    Mixin for features DF
    (generated from SimBA feature extraction)
    functions.
    """

    NULLABLE = False
    IN = FramesIN
    CN = Enum(
        value="FeaturesCN",
        names={
            "FEATURES": "features",
        },
    )
