import asyncio

from runthroughlinehackathor.action_selection.select_actions import (
    select_actions,
)
from runthroughlinehackathor.action_selection.select_random_event import (
    select_random_event,
)
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings
from runthroughlinehackathor.state_update.apply_action import apply_action
from runthroughlinehackathor.state_update.state_increment import StateIncrement


async def update_state(state: State, state_update: StateIncrement) -> None:
    for action in state_update.chosen_actions:
        apply_action(state, action)
    spent_time = sum(a.time_cost for a in state_update.chosen_actions)
    remaining_time = settings.time_pre_turn - spent_time
    assert remaining_time >= 0
    state.parameters.health += settings.health_per_time_spent * remaining_time
    actions, random_event = await asyncio.gather(
        select_actions(
            history=state.history,
            current_stage=state.current_stage,
            parameters=state.parameters,
        ),
        select_random_event(state.history),
    )
    state.random_event = random_event
    state.big_actions = list(
        a for a in actions if a.time_cost > settings.small_action_max_cost
    )
    state.small_actions = list(
        a for a in actions if a.time_cost <= settings.small_action_max_cost
    )
