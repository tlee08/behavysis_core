"""
_summary_
"""

from typing import Optional, Union

from behavysis_core.data_models.pydantic_base_model import PydanticBaseModel
from pydantic import ConfigDict


class VidMetadata(PydanticBaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    fps: Optional[Union[int, float]] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    total_frames: Optional[int] = None
