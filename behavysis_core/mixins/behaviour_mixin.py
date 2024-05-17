"""
Utility functions.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd
from scipy.stats import mode

from behavysis_core.constants import (
    BEHAV_ACTUAL_COL,
    BEHAV_COLUMN_NAMES,
    BEHAV_PRED_COL,
    BEHAV_PROB_COL,
)
from behavysis_core.data_models.bouts import Bouts


class BehaviourMixin:
    """_summary_"""

    @staticmethod
    def vect_2_bouts(vect: Union[np.ndarray, pd.Series]) -> pd.DataFrame:
        """
        Will return a dataframe with the start and stop indexes of each contiguous set of
        positive values (i.e. a bout).

        Parameters
        ----------
        vect : Union[np.ndarray, pd.Series]
            Expects a vector of booleans

        Returns
        -------
        pd.DataFrame
            _description_
        """
        offset = 0
        if isinstance(vect, pd.Series):
            offset = vect.index[0]
        # Getting stop and start indexes of each bout
        z = np.concatenate(([0], vect, [0]))
        start = np.flatnonzero(~z[:-1] & z[1:])
        stop = np.flatnonzero(z[:-1] & ~z[1:]) - 1
        bouts_ls = np.column_stack((start, stop)) + offset
        # Making dataframe
        bouts_df = pd.DataFrame(bouts_ls, columns=["start", "stop"])
        bouts_df["dur"] = bouts_df["stop"] - bouts_df["start"]
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
                    "actual": int(mode(bout_frames_df[(behav, BEHAV_ACTUAL_COL)]).mode),
                    "user_defined": {},
                }
                # Getting the mode value for the bout (actual, and specific user_behavs)
                for outcome, values in bout_frames_df[behav].items():
                    if outcome not in [
                        BEHAV_PROB_COL,
                        BEHAV_PRED_COL,
                        BEHAV_ACTUAL_COL,
                    ]:
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
        Also adds in the `BEHAV_ACTUAL_COL` behaviour and sets
        is predicted frames to `BEHAV_ACTUAL_COL` "undecided".

        Any behaviour-outcomes that are already in `frames_df` will be unchanged.
        """
        frames_df = frames_df.copy()
        # Adding in BEHAV_ACTUAL_COL and user defined columns (if they don't already exist)
        for behav in frames_df.columns.unique(BEHAV_COLUMN_NAMES[0]):
            # Adding in BEHAV_ACTUAL_COL, and setting all is predicted frames to
            # actual "undecided" (i.e. -1)
            if (behav, BEHAV_ACTUAL_COL) not in frames_df.columns:
                frames_df[(behav, BEHAV_ACTUAL_COL)] = 0
                frames_df.loc[
                    frames_df[(behav, BEHAV_PRED_COL)] == 1,
                    (behav, BEHAV_ACTUAL_COL),
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
        ret_df = pd.DataFrame(index=np.arange(bouts.start, bouts.stop))
        # Making columns
        all_behavs = {}  # behav: user_behav_ls pairs
        for bout in bouts.bouts:
            if bout.behaviour not in all_behavs:
                all_behavs[bout.behaviour] = {BEHAV_PRED_COL, BEHAV_ACTUAL_COL}
            all_behavs[bout.behaviour] |= set(bout.user_defined.keys())

        # all_behavs dict to MultiIndex
        columns = pd.MultiIndex.from_tuples(
            [
                (behav, outcome)
                for behav, outcomes in all_behavs.items()
                for outcome in outcomes
            ],
            names=BEHAV_COLUMN_NAMES,
        )
        ret_df[columns] = 0
        ret_df.columns = columns
        ret_df = ret_df.reindex(columns=sorted(ret_df.columns))
        # Filling in all user_behavs columns for each behaviour
        for bout in bouts.bouts:
            bout_ret_df = ret_df.loc[bout.start : bout.stop]
            # Filling in predicted behaviour column
            bout_ret_df.loc[:, (bout.behaviour, BEHAV_PRED_COL)] = 1
            # Filling in actual behaviour column
            bout_ret_df.loc[:, (bout.behaviour, BEHAV_ACTUAL_COL)] = bout.actual
            # Filling in user_behavs columns
            for k, v in bout.user_defined.items():
                bout_ret_df.loc[:, (bout.behaviour, k)] = v
        # Returning frames df
        return ret_df
