"""
Utility functions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ba_core.utils.constants import PROCESS_COL, SINGLE_COL


class KeypointsMixin:
    """__summary__"""

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
        Returns a tuple of the individuals (animals, not "single"), and tuple of the multi-animal
        bodyparts.

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
        for i in [PROCESS_COL, SINGLE_COL]:
            if i in columns.unique("individuals"):
                columns = columns.drop(i, level="individuals")
        # Getting individuals list
        indivs = columns.unique("individuals").to_list()
        # Getting bodyparts list
        bpts = columns.unique("bodyparts").to_list()
        return indivs, bpts

    @staticmethod
    def clean_headings(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drops the "scorer" level (and any other unnecessary levels) in the column
        header of the dataframe. This makes analysis easier.

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
        # Removing the scorer column because all values are identical
        df.columns = df.columns.droplevel("scorer")
        # Grouping the columns by the individuals level for cleaner presentation
        # TODO: is there a better way to group/sort the columns?
        df = df.reindex(columns=df.columns.unique("individuals"), level="individuals")
        return df
