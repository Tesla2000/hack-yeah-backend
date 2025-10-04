from typing import Union
from uuid import UUID

from pydantic import BaseModel
from pydantic import computed_field
from pydantic import NonNegativeInt
from pydantic import PositiveInt
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.reaction import Reaction
from runthroughlinehackathor.models.gender import Gender
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.phase import Phase
from runthroughlinehackathor.models.random_event import RandomEvent
from runthroughlinehackathor.settings import settings

HistoryElement = Union[Action, RandomEvent, Reaction]


class State(BaseModel):
    id: UUID
    parameters: Parameters
    history: list[HistoryElement]
    turn_descriptions: list[str]
    current_phase: Phase
    game_turn: NonNegativeInt
    gender: Gender
    goal: str

    @computed_field
    def age(self) -> PositiveInt:
        return self.game_turn * settings.years_per_turn + settings.initial_age
