"""
_summary_
"""

from typing import Optional, Union

from pydantic import ConfigDict

from ba_core.data_models.pydantic_base_model import PydanticBaseModel


class VidMetadata(PydanticBaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    fps: Optional[Union[int, float]] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    total_frames: Optional[int] = None