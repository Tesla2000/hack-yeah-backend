from typing import Union
from uuid import UUID

from pydantic import BaseModel
from runthroughlinehackathor.action_selection.action_list import name_to_action
from runthroughlinehackathor.action_selection.random_events_list import (
    reactions,
)
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.reaction import Reaction


class StateIncrement(BaseModel):
    state_id: UUID
    chosen_action_references: list[Union[str, int]]

    @property
    def chosen_actions(self) -> tuple[Union[Action, Reaction], ...]:
        return tuple(
            map(
                {**name_to_action, **reactions}.__getitem__,
                sorted(
                    self.chosen_action_references,
                    key=lambda reference: isinstance(reference, str),
                ),
            )
        )
