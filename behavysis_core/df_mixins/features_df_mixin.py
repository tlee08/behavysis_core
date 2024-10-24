"""
Utility functions.
"""

from __future__ import annotations

from enum import Enum

import pandas as pd

from behavysis_core.constants import FramesIN
from behavysis_core.mixins.df_io_mixin import DFIOMixin

####################################################################################################
# DATAFRAME CONSTANTS
####################################################################################################


class FeaturesCN(Enum):
    """Enum for the columns in the extracted features dataframe."""

    FEATURES = "features"


####################################################################################################
# MIXIN CLASS
####################################################################################################


class FeaturesDfMixin:
    """
    Mixin for features DF
    (generated from SimBA feature extraction)
    functions.
    """

    @staticmethod
    def init_df(frame_vect: pd.Series | pd.Index) -> pd.DataFrame:
        """
        Returning a frame-by-frame analysis_df with the frame number (according to original video)
        as the MultiIndex index, relative to the first element of frame_vect.
        Note that that the frame number can thus begin on a non-zero number.

        Parameters
        ----------
        frame_vect : pd.Series | pd.Index
            _description_

        Returns
        -------
        pd.DataFrame
            _description_
        """
        return pd.DataFrame(
            index=pd.Index(frame_vect, name=DFIOMixin.enum2tuple(FramesIN)[0]),
            columns=pd.MultiIndex.from_tuples(
                (), names=DFIOMixin.enum2tuple(FeaturesCN)
            ),
        )

    @staticmethod
    def check_df(df: pd.DataFrame) -> None:
        """
        Checks whether the dataframe is in the correct format for the keypoints functions.

        Checks that:

        - There are no null values.
        - The column levels are correct.
        - The index levels are correct.
        """
        # Checking for null values
        assert not df.isnull().values.any(), "The dataframe contains null values. Be sure to run interpolate_points first."
        # Checking that the index levels are correct
        DFIOMixin.check_df_index_names(df, FramesIN)
        # Checking that the column levels are correct
        DFIOMixin.check_df_column_names(df, FeaturesCN)

    @staticmethod
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        # Reading
        df = DFIOMixin.read_feather(fp)
        # Checking
        FeaturesDfMixin.check_df(df)
        # Returning
        return df
