"""
Functions have the following format:

Parameters
----------
dlc_fp : str
    The DLC dataframe filepath of the experiment to analyse.
analysis_dir : str
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

import pandas as pd
import seaborn as sns

from behavysis_core.constants import FramesIN
from behavysis_core.df_classes.df_mixin import DFMixin
from behavysis_core.df_classes.keypoints_df import Coords
from behavysis_core.mixins.io_mixin import IOMixin
from behavysis_core.pydantic_models.experiment_configs import ExperimentConfigs

####################################################################################################
# ANALYSIS DATAFRAME CONSTANTS
####################################################################################################


class AnalyseCN(Enum):
    """Enum for the columns in the analysis dataframe."""

    INDIVIDUALS = "individuals"
    MEASURES = "measures"


FBF = "fbf"
SUMMARY = "summary"
BINNED = "binned"
CUSTOM = "custom"

#####################################################################
#               ANALYSIS API FUNCS
#####################################################################


class AnalyseDf(DFMixin):
    """__summary__"""

    NULLABLE = False
    IN = FramesIN
    CN = AnalyseCN

    @staticmethod
    @IOMixin.overwrite_check()
    def get_configs(
        configs: ExperimentConfigs,
    ) -> tuple[
        float,
        float,
        float,
        float,
        list,
        list,
    ]:
        """
        _summary_

        Parameters
        ----------
        configs : Configs
            _description_

        Returns
        -------
        tuple[ float, float, float, float, list, list, ]
            _description_
        """
        assert configs.auto.formatted_vid.fps
        assert configs.auto.formatted_vid.width_px
        assert configs.auto.formatted_vid.height_px
        assert configs.auto.px_per_mm
        return (
            float(configs.auto.formatted_vid.fps),
            float(configs.auto.formatted_vid.width_px),
            float(configs.auto.formatted_vid.height_px),
            float(configs.auto.px_per_mm),
            list(configs.get_ref(configs.user.analyse.bins_sec)),
            list(configs.get_ref(configs.user.analyse.custom_bins_sec)),
        )

    @staticmethod
    def make_location_scatterplot(
        analysis_df: pd.DataFrame, roi_c_df: pd.DataFrame, out_fp, measure: str
    ):
        """
        Expects analysis_df index levels to be (frame,),
        and column levels to be (individual, measure).
        """
        analysis_stacked_df = analysis_df.stack(level="individuals").reset_index(
            "individuals"
        )
        g = sns.relplot(
            data=analysis_stacked_df,
            x=Coords.X.value,
            y=Coords.Y.value,
            hue=measure,
            col="individuals",
            kind="scatter",
            col_wrap=2,
            height=8,
            aspect=0.5 * analysis_stacked_df["individuals"].nunique(),
            alpha=0.8,
            linewidth=0,
            marker=".",
            s=10,
            legend=True,
        )
        # Invert the y axis
        g.axes[0].invert_yaxis()
        # Adding region definition (from roi_df) to the plot
        roi_c_df = pd.concat(
            [roi_c_df, roi_c_df.groupby("group").first().reset_index()],
            ignore_index=True,
        )
        for ax in g.axes:
            sns.lineplot(
                data=roi_c_df,
                x=Coords.X.value,
                y=Coords.Y.value,
                hue="group",
                # color=(1, 0, 0),
                linewidth=1,
                marker="+",
                markeredgecolor=(1, 0, 0),
                markeredgewidth=2,
                markersize=5,
                estimator=None,
                sort=False,
                legend=False,
                ax=ax,
            )
            ax.set_aspect("equal")
        # Setting fig titles and labels
        g.set_titles(col_template="{col_name}")
        g.figure.subplots_adjust(top=0.85)
        g.figure.suptitle("Spatial position", fontsize=12)
        # Saving fig
        os.makedirs(os.path.split(out_fp)[0], exist_ok=True)
        g.savefig(out_fp)
        g.figure.clf()

    @staticmethod
    def pt_in_roi(pt: pd.Series, roi_df: pd.DataFrame) -> bool:
        """__summary__"""
        # Counting crossings over edge in region when point is translated to the right
        crossings = 0
        # To loop back to the first point at the end
        first_roi_pt = pd.DataFrame(roi_df.iloc[0]).T
        roi_df = pd.concat((roi_df, first_roi_pt), axis=0, ignore_index=True)
        # Making x and y aliases
        x = Coords.X.value
        y = Coords.Y.value
        # For each edge
        for i in range(roi_df.shape[0] - 1):
            # Getting corner points of edge
            c1 = roi_df.iloc[i]
            c2 = roi_df.iloc[i + 1]
            # Getting whether point-y is between corners-y
            y_between = (c1[y] > pt[y]) != (c2[y] > pt[y])
            # Getting whether point-x is to the left (less than) the intersection of corners-x
            x_left_of = (
                pt[x] < (c2[x] - c1[x]) * (pt[y] - c1[y]) / (c2[y] - c1[y]) + c1[x]
            )
            if y_between and x_left_of:
                crossings += 1
        # Odd number of crossings means point is in region
        return crossings % 2 == 1
