"""
Utility functions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from behavysis_core.constants import BehavCN, BehavColumns, BehavIN
from behavysis_core.data_models.bouts import Bouts
from behavysis_core.mixins.df_io_mixin import DFIOMixin

# TODO: should we combine with BoutsDfMixin?

####################################################################################################
# DATAFRAME CONSTANTS
####################################################################################################


####################################################################################################
# MIXIN CLASS
####################################################################################################


class BehavDfMixin:
    """
    Mixin for behaviour DF
    (generated from maDLC keypoint detection)
    functions.
    """

    @staticmethod
    def include_outcome_behavs(
        df: pd.DataFrame, behav_outcomes: dict[str, tuple[str]]
    ) -> pd.DataFrame:
        """
        Adding the user_behavs columns to the df for each behaviour.

        Expects `behav_outcomes` to be a dictionary
        with the behaviour str as the key
        and a tuple of specific behaviour strs as the value.

        Also adds the `actual` and `pred` columns for each behaviour (but doesn't include `prob`).
        """
        # TODO: maybe keep `prob` so as to contain in export.py instead?
        # Keeping the `actual`, `pred`, and all user_behavs columns
        out_df = BehavDfMixin.init_df(df.index)
        a = BehavColumns.ACTUAL.value
        p = BehavColumns.PRED.value
        # For each behaviour, adding `actual`, `pred`, and all user_defined columns
        for behav, user_behavs in behav_outcomes.items():
            # Adding pred column
            out_df[(behav, p)] = df[(behav, p)].values
            # NOTE: unsure why we had the "quick flip" before
            # # Adding actual column and setting to "undecided" (-1)
            # # TODO: quick flip but make more explicit
            # out_df[(behav, a)] = df[(behav, p)].values * np.array(-1)
            out_df[(behav, a)] = df[(behav, a)].values
            # Adding user_behav columns
            for i in user_behavs:
                out_df[(behav, i)] = 0
        # Ordering by "behaviours" level
        out_df = out_df.sort_index(axis=1, level=BehavCN.BEHAVIOURS.value)
        # Returning the new df
        return out_df

    @staticmethod
    def bouts_2_frames(bouts: Bouts) -> pd.DataFrame:
        """
        Bouts model object to frames df.
        """
        # Making columns
        all_behavs = {}  # behav: user_behav_ls pairs
        for bout in bouts.bouts:
            if bout.behaviour not in all_behavs:
                all_behavs[bout.behaviour] = {
                    BehavColumns.PRED.value,
                    BehavColumns.ACTUAL.value,
                }
            all_behavs[bout.behaviour] |= set(bout.user_defined.keys())

        # construct ret_df with index from given start and stop, and all_behavs dict
        ret_df = BehavDfMixin.init_df(np.arange(bouts.start, bouts.stop))
        for behav, outcomes in all_behavs.items():
            for outcome in outcomes:
                ret_df[(behav, outcome)] = 0
        ret_df = ret_df.sort_index(axis=1)
        # Filling in all user_behavs columns for each behaviour
        for bout in bouts.bouts:
            bout_ret_df = ret_df.loc[bout.start : bout.stop]
            # Filling in predicted behaviour column
            bout_ret_df.loc[:, (bout.behaviour, BehavColumns.PRED.value)] = 1
            # Filling in actual behaviour column
            bout_ret_df.loc[:, (bout.behaviour, BehavColumns.ACTUAL.value)] = (
                bout.actual
            )
            # Filling in user_behavs columns
            for k, v in bout.user_defined.items():
                bout_ret_df.loc[:, (bout.behaviour, k)] = v
        # Returning frames df
        return ret_df

    @staticmethod
    def init_df(frame_vect: pd.Series | pd.Index | np.ndarray) -> pd.DataFrame:
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
            index=pd.Index(frame_vect, name=DFIOMixin.enum2tuple(BehavIN)[0]),
            columns=pd.MultiIndex.from_tuples((), names=DFIOMixin.enum2tuple(BehavCN)),
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
        DFIOMixin.check_df_index_names(df, BehavIN)
        # Checking that the column levels are correct
        DFIOMixin.check_df_column_names(df, BehavCN)

    @staticmethod
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        # Reading
        df = DFIOMixin.read_feather(fp)
        # Checking
        BehavDfMixin.check_df(df)
        # Returning
        return df

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
