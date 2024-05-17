"""
_summary_
"""

from typing import Dict, List

from pydantic import BaseModel

from behavysis_core.data_models.pydantic_base_model import PydanticBaseModel


class Bout(BaseModel):
    """__summary__"""

    start: int
    stop: int
    behaviour: str
    actual: int
    user_defined: Dict[str, int]


class Bouts(PydanticBaseModel, BaseModel):
    """__summary__"""

    start: int
    stop: int
    bouts: List[Bout]


if __name__ == "__main__":
    fp = (
        "/Users/timothylee/Desktop/Work/dev/ba_viewer/tests/resources/updated_abcd.json"
    )

    with open(fp, "r", encoding="utf-8") as f:
        model = Bouts.model_validate_json(f.read())
        print(model)
