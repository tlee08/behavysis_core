"""
_summary_
"""

from enum import Enum

####################################################################################################
# PIPELINE FOLDERS
####################################################################################################


class Folders(Enum):
    """Enum for the pipeline folders."""

    CONFIGS = "0_configs"
    RAW_VID = "1_raw_vid"
    FORMATTED_VID = "2_formatted_vid"
    DLC = "3_dlc"
    PREPROCESSED = "4_preprocessed"
    FEATURES_EXTRACTED = "5_features_extracted"
    PREDICTED_BEHAVS = "6_predicted_behavs"
    SCORED_BEHAVS = "7_scored_behavs"
    # ANALYSIS = "8_analysis"
    ANALYSIS_COMBINED = "9_analysis_combined"
    # EVALUATE = "10_evaluate"


FILE_EXTS = {
    Folders.CONFIGS: ".json",
    Folders.RAW_VID: ".mp4",
    Folders.FORMATTED_VID: ".mp4",
    Folders.DLC: ".feather",
    Folders.PREPROCESSED: ".feather",
    Folders.FEATURES_EXTRACTED: ".feather",
    Folders.PREDICTED_BEHAVS: ".feather",
    Folders.SCORED_BEHAVS: ".feather",
    Folders.ANALYSIS_COMBINED: ".feather",
}

# TODO: is there a better way to do the subsubdirs?
DIAGNOSTICS_DIR = "0_diagnostics"
ANALYSE_DIR = "8_analysis"
EVALUATE_DIR = "10_evaluate"
TEMP_DIR = ".temp"


####################################################################################################
# DIAGNOSTICS CONSTANTS
####################################################################################################


STR_DIV = "".ljust(50, "-")


####################################################################################################
# PLOT CONSTANTS
####################################################################################################

PLOT_STYLE = "whitegrid"
PLOT_DPI = 75
