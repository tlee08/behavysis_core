"""
Utility functions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import mode

from behavysis_core.constants import BEHAV_COLUMN_NAMES, BEHAV_INDEX_NAME, BehavColumns
from behavysis_core.data_models.bouts import Bouts
from behavysis_core.mixins.df_io_mixin import DFIOMixin


class BehaviourMixin:
    """_summary_"""

    @staticmethod
    def vect_2_bouts(vect: np.ndarray | pd.Series) -> pd.DataFrame:
        """
        Will return a dataframe with the start and stop indexes of each contiguous set of
        positive values (i.e. a bout).

        Parameters
        ----------
        vect : np.ndarray | pd.Series
            Expects a vector of booleans

        Returns
        -------
        pd.DataFrame
            _description_
        """
        offset = 0
        if isinstance(vect, pd.Series):
            if vect.shape[0] > 0:
                offset = vect.index[0]
        # Getting stop and start indexes of each bout
        z = np.concatenate(([0], vect, [0]))
        start = np.flatnonzero(~z[:-1] & z[1:])
        stop = np.flatnonzero(z[:-1] & ~z[1:]) - 1
        bouts_ls = np.column_stack((start, stop)) + offset
        # Making dataframe
        bouts_df = pd.DataFrame(bouts_ls, columns=["start", "stop"])
        bouts_df["dur"] = bouts_df["stop"] - bouts_df["start"] + 1
        return bouts_df

    @staticmethod
    def frames_2_bouts(frames_df: pd.DataFrame) -> Bouts:
        """
        Frames df to bouts model object.
        """
        bouts_ls = []
        # For each behaviour
        for behav in frames_df.columns.unique(BEHAV_COLUMN_NAMES[0]):
            # Getting start-stop of each bout
            start_stop_df = BehaviourMixin.vect_2_bouts(frames_df[(behav, "pred")])
            # For each bout (i.e. start-stop pair)
            for _, row in start_stop_df.iterrows():
                # Getting only the frames in the current bout
                bout_frames_df = frames_df.loc[row["start"] : row["stop"]]
                # Preparing to make Bout model object
                bout_dict = {
                    "start": row["start"],
                    "stop": row["stop"],
                    "behaviour": behav,
                    "actual": int(
                        mode(bout_frames_df[(behav, BehavColumns.ACTUAL.value)]).mode
                    ),
                    "user_defined": {},
                }
                # Getting the mode value for the bout (actual, and specific user_behavs)
                for outcome, values in bout_frames_df[behav].items():
                    if outcome not in [i.value for i in BehavColumns]:
                        bout_dict["user_defined"][str(outcome)] = int(mode(values).mode)
                # Making the Bout model object and appending to bouts_ls
                bouts_ls.append(bout_dict)
        # Making and return the Bouts model object
        return Bouts(
            start=frames_df.index[0], stop=frames_df.index[-1] + 1, bouts=bouts_ls
        )

    @staticmethod
    def frames_add_behaviour(
        frames_df: pd.DataFrame, user_behavs: list[str]
    ) -> pd.DataFrame:
        """
        Adding in behaviour-outcomes from the list of user_behavs given.
        Also adds in the `ACTUAL` behaviour and sets
        is predicted frames of `ACTUAL` to "undecided".

        Any behaviour-outcomes that are already in `frames_df` will be unchanged.
        """
        frames_df = frames_df.copy()
        # Adding in ACTUAL and user defined columns (if they don't already exist)
        for behav in frames_df.columns.unique(BEHAV_COLUMN_NAMES[0]):
            # Adding in ACTUAL, and setting all is predicted frames to
            # actual "undecided" (i.e. -1)
            if (behav, BehavColumns.ACTUAL.value) not in frames_df.columns:
                frames_df[(behav, BehavColumns.ACTUAL.value)] = 0
                frames_df.loc[
                    frames_df[(behav, BehavColumns.PRED.value)] == 1,
                    (behav, BehavColumns.ACTUAL.value),
                ] = -1
            # Adding in other user defined behaviours
            for outcome in user_behavs:
                if (behav, outcome) not in frames_df.columns:
                    frames_df[(behav, outcome)] = 0
        return frames_df

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
        ret_df = BehaviourMixin.init_df(np.arange(bouts.start, bouts.stop))
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
            index=pd.Index(frame_vect, name=BEHAV_INDEX_NAME),
            columns=pd.MultiIndex.from_tuples((), names=BEHAV_COLUMN_NAMES),
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
        assert (
            not df.isnull().values.any()
        ), "The dataframe contains null values. Be sure to run interpolate_points first."
        # Checking that the index levels are correct
        assert (
            df.index.name == BEHAV_INDEX_NAME
        ), f"The index level is incorrect. They should be {BEHAV_INDEX_NAME}"
        # Checking that the column levels are correct
        assert (
            df.columns.names == BEHAV_COLUMN_NAMES
        ), f"The column levels are incorrect. They should be {BEHAV_COLUMN_NAMES}."

    @staticmethod
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        # Reading
        df = DFIOMixin.read_feather(fp)
        # Checking
        BehaviourMixin.check_df(df)
        # Returning
        return df
