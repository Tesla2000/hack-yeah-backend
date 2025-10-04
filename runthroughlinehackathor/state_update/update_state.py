from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.state_update.apply_action import apply_action
from runthroughlinehackathor.state_update.state_update import StateUpdate


def update_state(state: State, state_update: StateUpdate) -> None:
    for action in state_update.chosen_actions:
        apply_action(state, action)
