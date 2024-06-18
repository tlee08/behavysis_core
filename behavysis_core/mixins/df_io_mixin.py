"""
Utility functions.
"""

from __future__ import annotations

import functools
import os
from typing import Callable

from enum import Enum

import numpy as np
import pandas as pd

from behavysis_core.constants import DLC_HDF_KEY, KEYPOINTS_CN


class DFIOMixin:
    """__summary"""

    ###############################################################################################
    # DF Read/Write functions
    ###############################################################################################

    @staticmethod
    def read_decorator(
        func: Callable[[str], pd.DataFrame],
    ) -> Callable[[str], pd.DataFrame]:
        """A decorator to catch errors when reading in files."""

        @functools.wraps(func)
        def wrapper(fp: str, *args, **kwargs):
            # try:
            return func(fp, *args, **kwargs)
            # except Exception as e:
            #     raise ValueError(
            #         f'The file, "{fp}", does not exist or is in an invalid format.'
            #         + "Please check this file."
            #     ) from e

        return wrapper

    @staticmethod
    def write_decorator(
        func: Callable[[pd.DataFrame, str], None],
    ) -> Callable[[pd.DataFrame, str], None]:
        """A decorator to catch errors when reading in files."""

        @functools.wraps(func)
        def wrapper(df, fp: str, *args, **kwargs):
            # Making the directory if it doesn't exist
            os.makedirs(os.path.split(fp)[0], exist_ok=True)
            # Writing the file
            return func(df, fp, *args, **kwargs)

        return wrapper

    @staticmethod
    @read_decorator
    def read_dlc_csv(fp: str) -> pd.DataFrame:
        """
        Reading DLC csv file.
        """
        return pd.read_csv(
            fp, header=np.arange(len(KEYPOINTS_CN)).tolist(), index_col=0
        ).sort_index()

    @staticmethod
    @write_decorator
    def write_dlc_csv(df: pd.DataFrame, fp: str) -> None:
        """
        Writing DLC dataframe to csv file.
        """
        df.to_csv(fp)

    @staticmethod
    @read_decorator
    def read_h5(fp: str) -> pd.DataFrame:
        """
        Reading h5 file.
        """
        return pd.DataFrame(pd.read_hdf(fp, key=DLC_HDF_KEY, mode="r").sort_index())

    @staticmethod
    @write_decorator
    def write_h5(df: pd.DataFrame, fp: str) -> None:
        """
        Writing dataframe h5 file.
        """
        df.to_hdf(fp, key=DLC_HDF_KEY, mode="w")

    @staticmethod
    @read_decorator
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        return pd.read_feather(fp).sort_index()

    @staticmethod
    @write_decorator
    def write_feather(df: pd.Series | pd.DataFrame, fp: str) -> None:
        """
        Writing dataframe feather file.
        """
        df.to_feather(fp)

    ###############################################################################################
    # DF Init functions
    ###############################################################################################

    @staticmethod
    def init_df(frame_vect: pd.Series | pd.Index) -> pd.DataFrame:
        """__summary__"""
        return pd.DataFrame(index=frame_vect)

    ###############################################################################################
    # Check functions
    ###############################################################################################

    @staticmethod
    def check_df(df: pd.DataFrame) -> None:
        """__summary__"""
        assert isinstance(df, pd.DataFrame), "The dataframe is not a pandas DataFrame."

    @staticmethod
    def check_df_index_names(df: pd.DataFrame, levels: Enum | tuple[str] | str) -> None:
        """__summary__"""
        # Converting `levels` to a tuple
        if isinstance(levels, Enum):
            # If Enum
            levels = tuple(i.value for i in levels)
        elif isinstance(levels, str):
            # If str
            levels = (levels,)
        assert (
            df.index.names == levels
        ), f"The index level is incorrect. Expected {levels} but got {df.index.name}."

    @staticmethod
    def check_df_column_names(
        df: pd.DataFrame, levels: Enum | tuple[str] | str
    ) -> None:
        """__summary__"""
        # Converting `levels` to a tuple
        if isinstance(levels, Enum):
            # If Enum
            levels = tuple(i.value for i in levels)
        elif isinstance(levels, str):
            # If str
            levels = (levels,)
        assert (
            df.columns.names == levels
        ), f"The column level is incorrect. Expected {levels} but got {df.columns.name}."
