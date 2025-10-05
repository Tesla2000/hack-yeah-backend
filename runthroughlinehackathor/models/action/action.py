from typing import Self

from pydantic import Field
from pydantic import PositiveInt
from runthroughlinehackathor.models.action.action_base import ActionBase
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.stage import Stage


class Action(ActionBase):
    name: str
    type: ActionType
    time_cost: PositiveInt = Field(le=5)
    is_unique: bool = False
    allowed_stages: list[Stage]
    prerequisite_names: list[str]

    @property
    def prerequisites(self) -> list[Self]:
        from runthroughlinehackathor.action_selection.action_list import (
            name_to_action,
        )

        return list(map(name_to_action.__getitem__, self.prerequisite_names))
