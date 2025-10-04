from pydantic import Field
from pydantic import PositiveInt
from runthroughlinehackathor.models.action.action_base import ActionBase
from runthroughlinehackathor.models.action.action_type import ActionType


class Action(ActionBase):
    type: ActionType
    time_cost: PositiveInt = Field(le=5)
    is_unique: bool = False
