from pydantic import Field
from pydantic.v1 import PositiveInt
from runthroughlinehackathor.models.action._action_type import ActionType
from runthroughlinehackathor.models.action.action_base import ActionBase


class Action(ActionBase):
    type: ActionType
    time_cost: PositiveInt = Field(le=5)
