"""
Utility functions.
"""

from __future__ import annotations

from enum import Enum

import numpy as np
import pandas as pd

from behavysis_core.constants import FramesIN
from behavysis_core.df_classes.df_mixin import DFMixin

# TODO: should we combine with BoutsDfMixin?

####################################################################################################
# DATAFRAME CONSTANTS
####################################################################################################


class BehavCN(Enum):
    """Enum for the columns in the behaviour dataframe."""

    BEHAVIOURS = "behaviours"
    OUTCOMES = "outcomes"


class BehavColumns(Enum):
    """Enum for the columns in the behaviour dataframe."""

    PROB = "prob"
    PRED = "pred"
    ACTUAL = "actual"


####################################################################################################
# MIXIN CLASS
####################################################################################################


class BehavDf(DFMixin):
    """
    Mixin for behaviour DF
    (generated from maDLC keypoint detection)
    functions.
    """

    NULLABLE = False
    IN = FramesIN
    CN = BehavCN

    @staticmethod
    def include_user_behavs(
        df: pd.DataFrame, user_behavs: dict[str, tuple[str]]
    ) -> pd.DataFrame:
        """
        Adding the user_behavs columns to the df for each behaviour.

        Expects `behav_outcomes` to be a dictionary
        with the auto-classifier behaviour str as the key
        and a tuple of user behaviour strs as the value.

        Also adds the `actual` and `pred` columns for each behaviour (but doesn't include `prob`).
        """
        # TODO: maybe keep `prob` so as to contain in export.py instead?
        # Keeping the `actual`, `pred`, and all user_behavs columns
        out_df = BehavDfMixin.init_df(df.index)
        a = BehavColumns.ACTUAL.value
        p = BehavColumns.PRED.value
        # For each behaviour, adding `actual`, `pred`, and all user_defined columns
        for behav_i, user_behavs_i in user_behavs.items():
            # Adding pred column
            out_df[(behav_i, p)] = df[(behav_i, p)].values
            # NOTE: unsure why we had the "quick flip" before
            # # Adding actual column and setting to "undecided" (-1)
            # # TODO: quick flip but make more explicit
            # out_df[(behav, a)] = df[(behav, p)].values * np.array(-1)
            out_df[(behav_i, a)] = df[(behav_i, a)].values
            # Adding user_behav columns
            for k in user_behavs_i:
                out_df[(behav_i, k)] = 0
        # Ordering by "behaviours" level
        out_df = out_df.sort_index(axis=1, level=BehavCN.BEHAVIOURS.value)
        # Returning the new df
        return out_df

    @staticmethod
    def update_behav(df: pd.DataFrame, behav_src: str, behav_dst: str) -> pd.DataFrame:
        """
        Update the behaviour column with the given outcome and value.
        """
        # Getting columns
        columns = df.columns.to_frame(index=False)
        # Updating the behaviour column
        columns[BehavCN.BEHAVIOURS.value] = columns[BehavCN.OUTCOMES.value].map(
            lambda x: behav_dst if x == behav_src else x
        )
        # Setting the new columns
        df.columns = pd.MultiIndex.from_frame(columns)
        # Returning
        return df

    @staticmethod
    def import_boris_tsv(
        fp: str, behavs_ls: list[str], start_frame: int, stop_frame: int
    ) -> pd.DataFrame:
        """
        Importing Boris TSV file.
        """
        # Making df structure
        df = BehavDfMixin.init_df(np.arange(start_frame, stop_frame))
        # Reading in corresponding BORIS tsv file
        df_boris = pd.read_csv(fp, sep="\t")
        # Initialising new classification columns based on
        # BORIS behavs and given `behavs_ls`
        # TODO: how to reconcile this with the behavs_ls?
        for behav in df_boris["Behavior"].unique():
            df[(behav, BehavColumns.ACTUAL.value)] = 0
            df[(behav, BehavColumns.PRED.value)] = 0
        for behav in behavs_ls:
            df[(behav, BehavColumns.ACTUAL.value)] = 0
            df[(behav, BehavColumns.PRED.value)] = 0
        # Setting the classification values from the BORIS file
        for ind, row in df_boris.iterrows():
            # Getting corresponding frame of this event point
            behav = row["Behavior"]
            frame = row["Image index"]
            status = row["Behavior type"]
            # Updating the classification in the scored df
            df.loc[frame:, (behav, BehavColumns.ACTUAL.value)] = status == "START"
            df.loc[frame:, (behav, BehavColumns.PRED.value)] = status == "START"
        # Setting dtype to int8
        df = df.astype(np.int8)
        return df