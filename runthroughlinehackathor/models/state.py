from typing import Union
from uuid import UUID

from pydantic import BaseModel
from runthroughlinehackathor.models.action import Action
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.random_event import RandomEvent
from runthroughlinehackathor.models.reaction import Reaction


class State(BaseModel):
    id: UUID
    parameters: Parameters
    history: list[Union[Action, RandomEvent, Reaction]]
