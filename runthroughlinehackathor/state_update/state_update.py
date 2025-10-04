from typing import Union
from uuid import UUID

from pydantic import BaseModel
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.reaction import Reaction


class StateUpdate(BaseModel):
    state_id: UUID
    chosen_actions: list[Union[Action, Reaction]]
