"""
Functions have the following format:

Parameters
----------
dlc_fp : str
    The DLC dataframe filepath of the experiment to analyse.
ANALYSE_DIR : str
    The analysis directory path.
configs_fp : str
    the experiment's JSON configs file.

Returns
-------
str
    The outcome of the process.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Callable

import numpy as np
import pandas as pd
import seaborn as sns

from behavysis_core.df_classes.analyse_df import AnalyseDf
from behavysis_core.df_classes.bouts_df import BoutsDf
from behavysis_core.df_classes.df_mixin import DFMixin, FramesIN

FBF = "fbf"
SUMMARY = "summary"
BINNED = "binned"
CUSTOM = "custom"

####################################################################################################
# DF CLASS
####################################################################################################


class AnalyseAggDf(DFMixin):
    """__summary__"""

    NULLABLE = False
    IN = FramesIN
    CN = Enum(
        value="AnalyseAggCN",
        names={
            "INDIVIDUALS": "individuals",
            "MEASURES": "measures",
            "AGGS": "aggs",
        },
    )

    @classmethod
    def agg_quantitative(cls, analysis_df: pd.DataFrame, fps: float) -> pd.DataFrame:
        """
        Generates the summarised data across the entire period, including mean,
        std, min, Q1, median, Q3, and max.
        Used for quantitative numeric data.

        Params:
            analysis_df: pd.DataFrame
                _description_

        Returns:
        str
            The outcome string.
        """
        # Getting summary stats for each individual
        summary_df_ls = np.zeros(analysis_df.shape[1], dtype="object")
        for i, col in enumerate(analysis_df.columns):
            # Getting column vector of individual-measure
            vect = analysis_df[col]
            # Handling edge case where columns are empty
            vect = np.array([0]) if vect.shape[0] == 0 else vect
            # Setting columns to type float
            vect = vect.astype(np.float64)
            # Aggregating stats
            summary_df_ls[i] = (
                pd.Series(
                    {
                        "mean": np.nanmean(vect),
                        "std": np.nanstd(vect),
                        "min": np.nanmin(vect),
                        "Q1": np.nanquantile(vect, q=0.25),
                        "median": np.nanmedian(vect),
                        "Q3": np.nanquantile(vect, q=0.75),
                        "max": np.nanmax(vect),
                    },
                    name=col,
                )
                .to_frame()
                .T
            )
        # Concatenating summary_df_ls
        summary_df = pd.concat(summary_df_ls, axis=0)
        # Setting the index and columns
        summary_df.index = analysis_df.columns
        summary_df.columns.name = cls.CN.AGGS.value
        # Returning summary_df
        return summary_df

    @classmethod
    def agg_behavs(cls, analysis_df: pd.DataFrame, fps: float) -> pd.DataFrame:
        """
        Generates the summarised data across the entire period, including number of bouts,
        and mean, std, min, Q1, median, Q3, and max duration of bouts.
        Used for boolean behavs classification data.

        Parameters
        ----------
        analysis_df : pd.DataFrame
            _description_
        Returns
        -------
        str
            The outcome string.
        """
        # Getting summary stats for each individual
        summary_df_ls = np.zeros(analysis_df.shape[1], dtype="object")
        for i, col in enumerate(analysis_df.columns):
            # Getting column vector of individual-measure
            vect = analysis_df[col]
            # Getting duration of each behav bout
            bouts = BoutsDf.vect2bouts(vect == 1)["dur"]
            # Converting bouts duration from frames to seconds
            bouts = bouts / fps
            # Getting bout frequency (before it is overwritten if empty)
            bout_freq = bouts.shape[0]
            # Handling edge case where bouts is empty
            bouts = np.array([0]) if bouts.shape[0] == 0 else bouts
            # Setting bouts to type float
            bouts = bouts.astype(np.float64)
            # Aggregating stats
            summary_df_ls[i] = (
                pd.Series(
                    {
                        "bout_freq": bout_freq,
                        "bout_dur_total": np.nansum(bouts),
                        "bout_dur_mean": np.nanmean(bouts),
                        "bout_dur_std": np.nanstd(bouts),
                        "bout_dur_min": np.nanmin(bouts),
                        "bout_dur_Q1": np.nanquantile(bouts, q=0.25),
                        "bout_dur_median": np.nanmedian(bouts),
                        "bout_dur_Q3": np.nanquantile(bouts, q=0.75),
                        "bout_dur_max": np.nanmax(bouts),
                    },
                    name=col,
                )
                .to_frame()
                .T
            )
        # Concatenating summary_df_ls
        summary_df = pd.concat(summary_df_ls, axis=0)
        # Setting the index and columns
        summary_df.index = analysis_df.columns
        summary_df.columns.name = cls.CN.AGGS.value
        # Returning summary_df
        return summary_df

    @classmethod
    def make_binned(
        cls,
        analysis_df: pd.DataFrame,
        fps: float,
        bins_: list,
        summary_func: Callable[[pd.DataFrame, float], pd.DataFrame],
    ) -> pd.DataFrame:
        """
        Generates the binned data and line graph for the given analysis_df, and given bin_sec.
        The aggregated statistics are very similar to the summary data.
        """
        # For each column, displays the mean of each binned group.
        timestamps = analysis_df.index.get_level_values("frame") / fps
        # Ensuring all bins are included (start frame and end frame)
        bins = np.asarray(bins_)
        bins = np.append(0, bins) if np.min(bins) > 0 else bins
        t_max = np.max(timestamps)
        bins = np.append(bins, t_max) if np.max(bins) < t_max else bins
        # Making binned data
        bin_sec = pd.cut(timestamps, bins=bins, labels=bins[1:], include_lowest=True)  # type: ignore
        grouped_df = analysis_df.groupby(bin_sec)
        binned_df = grouped_df.apply(
            lambda x: summary_func(x, fps)
            .unstack(DFMixin.enum2tuple(AnalyseDf.CN))
            .reorder_levels(list(DFMixin.enum2tuple(cls.CN)))
            .sort_index(level=DFMixin.enum2tuple(AnalyseDf.CN))
        )
        binned_df.index.name = "bin_sec"
        # returning binned_df
        return binned_df

    @staticmethod
    def make_binned_plot(
        binned_df: pd.DataFrame,
        out_fp: str,
        agg_column: str,
    ):
        """
        _summary_
        """
        # Making binned_df long
        binned_stacked_df = (
            binned_df.stack(DFMixin.enum2tuple(AnalyseDf.CN))[agg_column]
            .rename("value")
            .reset_index()
        )
        # Plotting line graph
        g = sns.relplot(
            data=binned_stacked_df,
            x="bin_sec",
            y="value",
            hue="measures",
            col="individuals",
            kind="line",
            height=4,
            aspect=1.5,
            alpha=0.5,
            marker="X",
            markersize=10,
            legend=True,
        )
        # Setting fig titles and labels
        g.set_titles(col_template="{col_name}")
        g.figure.subplots_adjust(top=0.85)
        g.figure.suptitle("Binned data", fontsize=12)
        # Saving fig
        os.makedirs(os.path.split(out_fp)[0], exist_ok=True)
        g.savefig(out_fp)
        g.figure.clf()

    @classmethod
    def summary_binned_quantitative(
        cls,
        analysis_df: pd.DataFrame,
        out_dir: str,
        name: str,
        fps: float,
        bins_ls: list,
        cbins_ls: list,
    ) -> str:
        """
        _summary_
        """
        return cls.summary_binned(
            analysis_df=analysis_df,
            out_dir=out_dir,
            name=name,
            fps=fps,
            summary_func=cls.agg_quantitative,
            agg_column="mean",
            bins_ls=bins_ls,
            cbins_ls=cbins_ls,
        )

    @classmethod
    def summary_binned_behavs(
        cls,
        analysis_df: pd.DataFrame,
        out_dir: str,
        name: str,
        fps: float,
        bins_ls: list,
        cbins_ls: list,
    ) -> str:
        """
        _summary_
        """
        return cls.summary_binned(
            analysis_df=analysis_df,
            out_dir=out_dir,
            name=name,
            fps=fps,
            summary_func=cls.agg_behavs,
            agg_column="bout_dur_total",
            bins_ls=bins_ls,
            cbins_ls=cbins_ls,
        )

    @classmethod
    def summary_binned(
        cls,
        analysis_df: pd.DataFrame,
        out_dir: str,
        name: str,
        fps: float,
        summary_func: Callable[[pd.DataFrame, float], pd.DataFrame],
        agg_column: str,
        bins_ls: list,
        cbins_ls: list,
    ) -> str:
        """
        _summary_
        """
        outcome = ""
        # Offsetting the frames index to start from 0 (i.e. when the experiment
        # started, rather than when the recording started)
        analysis_df.index = analysis_df.index - analysis_df.index[0]
        # Summarising analysis_df
        summary_fp = os.path.join(out_dir, "summary", f"{name}.feather")
        summary_df = summary_func(analysis_df, fps)
        DFMixin.write_feather(summary_df, summary_fp)
        # Getting timestamps index
        timestamps = analysis_df.index.get_level_values("frame") / fps
        # Binning analysis_df
        for bin_sec in bins_ls:
            # Making filepaths
            binned_fp = os.path.join(out_dir, f"binned_{bin_sec}", f"{name}.feather")
            binned_plot_fp = os.path.join(
                out_dir, f"binned_{bin_sec}_plot", f"{name}.png"
            )
            # Making binned df
            bins = np.arange(0, np.max(timestamps) + bin_sec, bin_sec)
            binned_df = cls.make_binned(analysis_df, fps, bins, summary_func)
            DFMixin.write_feather(binned_df, binned_fp)
            # Making binned plots
            cls.make_binned_plot(binned_df, binned_plot_fp, agg_column)
        # Custom binning analysis_df
        if cbins_ls:
            # Making filepaths
            binned_fp = os.path.join(out_dir, "binned_custom", f"{name}.feather")
            binned_plot_fp = os.path.join(out_dir, "binned_custom_plot", f"{name}.png")
            # Making binned df
            binned_df = cls.make_binned(analysis_df, fps, cbins_ls, summary_func)
            DFMixin.write_feather(binned_df, binned_fp)
            # Making binned plots
            cls.make_binned_plot(binned_df, binned_plot_fp, agg_column)
        # Returning outcome
        return outcome
