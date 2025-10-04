from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings
from runthroughlinehackathor.state_update.apply_action import apply_action
from runthroughlinehackathor.state_update.state_increment import StateIncrement


def update_state(state: State, state_update: StateIncrement) -> None:
    for action in state_update.chosen_actions:
        apply_action(state, action)
    spent_time = sum(a.time_cost for a in state_update.chosen_actions)
    remaining_time = settings.time_pre_turn - spent_time
    assert remaining_time >= 0
    state.parameters.health += settings.health_per_time_spent * remaining_time
