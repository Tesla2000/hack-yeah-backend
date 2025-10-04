from typing import Union

from pydantic import BaseModel
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.reaction import Reaction


class StateUpdate(BaseModel):
    chosen_actions: list[Union[Action, Reaction]]
