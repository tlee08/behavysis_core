"""
Utility functions.
"""

from __future__ import annotations

from enum import Enum

import numpy as np
import pandas as pd

from behavysis_core.constants import FramesIN
from behavysis_core.mixins.df_io_mixin import DFIOMixin

####################################################################################################
# DATAFRAME CONSTANTS
####################################################################################################


class KeypointsCN(Enum):
    """Enum for the columns in the keypoints dataframe."""

    SCORER = "scorer"
    INDIVIDUALS = "individuals"
    BODYPARTS = "bodyparts"
    COORDS = "coords"


class Coords(Enum):
    """Enum for the coordinates in the keypoints dataframe."""

    X = "x"
    Y = "y"
    LIKELIHOOD = "likelihood"


class IndivColumns(Enum):
    """Enum for the `individuals` level's values in the columns of the keypoints dataframe."""

    SINGLE = "single"
    PROCESS = "processed"  # TODO: remove this


DLC_HDF_KEY = "data"

####################################################################################################
# MIXIN CLASS
####################################################################################################


class KeypointsMixin:
    """
    Mixin for behaviour DF
    (generated from maDLC keypoint detection)
    functions.
    """

    @staticmethod
    def check_bpts_exist(df: pd.DataFrame, bodyparts: list) -> None:
        """
        _summary_

        Parameters
        ----------
        df : pd.DataFrame
            _description_
        bodyparts : list
            _description_

        Raises
        ------
        ValueError
            _description_
        """
        # Checking that the bodyparts are all valid:
        bodyparts_exist = np.isin(bodyparts, df.columns.unique("bodyparts"))
        if not bodyparts_exist.all():
            msg = (
                "Some bodyparts in the config file are missing from the csv file.\n"
                + "They are:\n"
            )
            for bp in np.array(bodyparts)[~bodyparts_exist]:
                msg += f"    - {bp}\n"
            raise ValueError(msg)

    @staticmethod
    def get_headings(df: pd.DataFrame) -> tuple[list[str], list[str]]:
        """
        Returns a tuple of the individuals (only animals, not "single"), and tuple of
        the multi-animal bodyparts.

        Parameters
        ----------
        df : pd.DataFrame
            Keypoints pd.DataFrame.

        Returns
        -------
        tuple[list[str], list[str]]
            `(indivs_ls, bpts_ls)` tuples. It is recommended to unpack these vals.
        """
        # Getting column MultiIndex
        columns = df.columns
        # Filtering out any single and processing columns
        # Not incl. the `single` or `process`columns
        columns_filt = np.isin(
            df.columns.get_level_values(KeypointsCN.INDIVIDUALS.value),
            [IndivColumns.PROCESS.value, IndivColumns.SINGLE.value],
            invert=True,
        )
        columns = df.columns[columns_filt]
        # Getting individuals list
        indivs = columns.unique("individuals").to_list()
        # Getting bodyparts list
        bpts = columns.unique("bodyparts").to_list()
        return indivs, bpts

    @staticmethod
    def clean_headings(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drops the "scorer" level in the column
        header of the dataframe. This makes subsequent processing easier.

        Parameters
        ----------
        df : pd.DataFrame
            Keypoints pd.DataFrame.

        Returns
        -------
        pd.DataFrame
            Keypoints pd.DataFrame.
        """
        df = df.copy()
        # Keeping only the "individuals", "bodyparts", and "coords" levels
        # (i.e. dropping "scorer" level)
        columns = df.columns.to_frame(index=False)
        columns = columns[
            [
                KeypointsCN.INDIVIDUALS.value,
                KeypointsCN.BODYPARTS.value,
                KeypointsCN.COORDS.value,
            ]
        ]
        df.columns = pd.MultiIndex.from_frame(columns)
        # Grouping the columns by the individuals level for cleaner presentation
        df = df.sort_index(axis=1)
        return df

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
                (), names=DFIOMixin.enum2tuple(KeypointsCN)
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
        DFIOMixin.check_df_column_names(df, KeypointsCN)

    @staticmethod
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        # Reading
        df = DFIOMixin.read_feather(fp)
        # Checking
        KeypointsMixin.check_df(df)
        # Returning
        return df
