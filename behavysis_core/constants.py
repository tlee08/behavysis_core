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


FILE_EXTS = {
    Folders.CONFIGS: ".json",
    Folders.RAW_VID: ".mp4",
    Folders.FORMATTED_VID: ".mp4",
    Folders.DLC: ".feather",
    Folders.PREPROCESSED: ".feather",
    Folders.FEATURES_EXTRACTED: ".feather",
    Folders.PREDICTED_BEHAVS: ".feather",
    Folders.SCORED_BEHAVS: ".feather",
}

ANALYSIS_DIR = "8_analysis"
DIAGNOSTICS_DIR = "0_diagnostics"
EVALUATE_DIR = "9_evaluate"
TEMP_DIR = ".temp"

####################################################################################################
# DLC DATAFRAME CONSTANTS
####################################################################################################

DLC_COLUMN_NAMES = ("scorer", "individuals", "bodyparts", "coords")
DLC_INDEX_NAME = "frame"

ANALYSIS_COLUMN_NAMES = ("individuals", "measures")
ANALYSIS_INDEX_NAME = "frame"

AGG_ANALYSIS_COLUMN_NAMES = (*ANALYSIS_COLUMN_NAMES, "aggs")
AGG_ANALYSIS_INDEX_NAME = ANALYSIS_INDEX_NAME

DLC_HDF_KEY = "data"

BODYCENTRE = "Centre"

SINGLE_COL = "single"
PROCESS_COL = "processed"

####################################################################################################
# BEHAVIOUR DATAFRAME CONSTANTS
####################################################################################################


class BehavColumns(Enum):
    """Enum for the columns in the behaviour dataframe."""

    PROB = "prob"
    PRED = "pred"
    ACTUAL = "actual"


BEHAV_COLUMN_NAMES = ("behaviours", "outcomes")
BEHAV_INDEX_NAME = "frame"


####################################################################################################
# DIAGNOSTICS CONSTANTS
####################################################################################################

DIAGNOSTICS_SUCCESS_MESSAGES = (
    "Success! Success! Success!!",
    "Done and DONE!!",
    "Yay! Completed!",
    "This process was completed. Good on you :)",
    "Thumbs up!",
    "Woohoo!!!",
    "Phenomenal!",
    ":) :) :) :) :)",
    "Go you!",
    "You are doing awesome!",
    "You got this!",
    "You're doing great!",
    "Sending good vibes.",
    "I believe in you!",
    "You're a champion!",
    "No task too tall :) :)",
    "A job done well, and a well done job!",
    "Top job!",
)

STR_DIV = "".ljust(50, "-")


####################################################################################################
# PLOT CONSTANTS
####################################################################################################

PLOT_STYLE = "whitegrid"
PLOT_DPI = 75
