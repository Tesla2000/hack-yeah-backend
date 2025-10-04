from runthroughlinehackathor.models.action.action_base import ActionBase
from runthroughlinehackathor.models.state import State


def apply_action(state: State, action: ActionBase) -> None:
    state.history.append(action)
    state.parameters += action.parameter_change
