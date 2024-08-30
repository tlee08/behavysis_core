"""
_summary_
"""

from pydantic import ConfigDict

from behavysis_core.data_models.pydantic_base_model import PydanticBaseModel


class VidMetadata(PydanticBaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    fps: None | float = None
    width_px: None | int = None
    height_px: None | int = None
    total_frames: None | int = None
