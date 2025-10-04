from typing import Optional
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
from runthroughlinehackathor.models.random_event import RandomEvent
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.settings import settings

HistoryElement = Union[Action, RandomEvent, Reaction]


class State(BaseModel):
    id: UUID
    parameters: Parameters
    history: list[HistoryElement]
    turn_description: str
    current_stage: Stage
    game_turn: NonNegativeInt
    gender: Gender
    name: str
    goal: str
    big_actions: list[Action]
    small_actions: list[Action]
    random_event: RandomEvent
    stage_summary: Optional[str] = None
    is_game_finished: bool = False

    @computed_field
    def age(self) -> PositiveInt:
        return self.game_turn * settings.years_per_turn + settings.initial_age
