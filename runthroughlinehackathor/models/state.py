from typing import Union
from uuid import UUID

from pydantic import BaseModel
from pydantic import NonNegativeInt
from runthroughlinehackathor.models._gender import Gender
from runthroughlinehackathor.models._phase import Phase
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.reaction import Reaction
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.random_event import RandomEvent


class State(BaseModel):
    id: UUID
    parameters: Parameters
    history: list[Union[Action, RandomEvent, Reaction]]
    turn_descriptions: list[str]
    current_phase: Phase
    game_turn: NonNegativeInt
    gender: Gender
