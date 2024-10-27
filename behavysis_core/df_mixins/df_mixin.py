"""
Utility functions.
"""

from __future__ import annotations

import functools
import os
from enum import EnumType
from typing import Callable

import pandas as pd


class DFMixin:
    """__summary"""

    ###############################################################################################
    # DF Read/Write functions
    ###############################################################################################

    @classmethod
    def __read_decorator(
        cls, func: Callable[[str], pd.DataFrame]
    ) -> Callable[[str], pd.DataFrame]:
        """A decorator to catch errors when reading in a file."""

        @functools.wraps(func)
        def wrapper(cls, fp: str):
            # Reading the file and sorting by index
            df = func(fp).sort_index()
            # Checking
            cls.check_df(df)
            # Returning
            return df

        return wrapper

    @classmethod
    def __write_decorator(
        cls, func: Callable[[pd.DataFrame, str], None]
    ) -> Callable[[pd.DataFrame, str], None]:
        """A decorator to catch errors when writing to a file."""

        @functools.wraps(func)
        def wrapper(df, fp: str):
            # Making the directory if it doesn't exist
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            # Writing the file
            return func(df, fp)

        return wrapper

    @classmethod
    @__read_decorator
    def read_dlc_csv(cls, fp: str) -> pd.DataFrame:
        """
        Reading DLC csv file.
        """
        return pd.read_csv(fp, index_col=0)

    @classmethod
    @__write_decorator
    def write_dlc_csv(cls, df: pd.DataFrame, fp: str) -> None:
        """
        Writing DLC dataframe to csv file.
        """
        df.to_csv(fp)

    @classmethod
    @__read_decorator
    def read_h5(cls, fp: str) -> pd.DataFrame:
        """
        Reading h5 file.
        """
        return pd.DataFrame(pd.read_hdf(fp, mode="r"))

    @classmethod
    @__write_decorator
    def write_h5(cls, df: pd.DataFrame, fp: str) -> None:
        """
        Writing dataframe h5 file.
        """
        # df.to_hdf(fp, key=DLC_HDF_KEY, mode="w")
        df.to_hdf(fp, mode="w")

    @classmethod
    @__read_decorator
    def read_feather(cls, fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        return pd.read_feather(fp)

    @classmethod
    @__write_decorator
    def write_feather(cls, df: pd.Series | pd.DataFrame, fp: str) -> None:
        """
        Writing dataframe feather file.
        """
        df.to_feather(fp)

    ###############################################################################################
    # DF init functions
    ###############################################################################################

    @classmethod
    def init_df(cls, frame_vect: pd.Series | pd.Index) -> pd.DataFrame:
        """__summary__"""
        return pd.DataFrame(index=frame_vect)

    ###############################################################################################
    # DF Check functions
    ###############################################################################################

    @staticmethod
    def check_df(df: pd.DataFrame) -> None:
        """__summary__"""
        assert isinstance(df, pd.DataFrame), "The dataframe is not a pandas DataFrame."

    @staticmethod
    def check_df_index_names(
        df: pd.DataFrame, levels: EnumType | tuple[str] | str
    ) -> None:
        """__summary__"""
        # Converting `levels` to a tuple
        if isinstance(levels, EnumType):  # If Enum
            levels = DFMixin.enum2tuple(levels)
        elif isinstance(levels, str):  # If str
            levels = (levels,)
        assert (
            df.index.names == levels
        ), f"The index level is incorrect. Expected {levels} but got {df.index.names}."

    @staticmethod
    def check_df_column_names(
        df: pd.DataFrame, levels: EnumType | tuple[str] | str
    ) -> None:
        """__summary__"""
        # Converting `levels` to a tuple
        if isinstance(levels, EnumType):  # If Enum
            levels = DFMixin.enum2tuple(levels)
        elif isinstance(levels, str):  # If str
            levels = (levels,)
        assert (
            df.columns.names == levels
        ), f"The column level is incorrect. Expected {levels} but got {df.columns.names}."

    @staticmethod
    def enum2tuple(my_enum):
        """
        Useful helper function to convert an Enum to a list of its values.
        Used in `check_df` and `init_df` functions.
        """
        return tuple(i.value for i in my_enum)
