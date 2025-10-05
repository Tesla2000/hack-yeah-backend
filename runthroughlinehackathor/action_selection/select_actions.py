import random
from collections.abc import Iterable
from itertools import chain
from itertools import cycle
from itertools import islice

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from pydantic import Field
from pydantic import PositiveInt
from runthroughlinehackathor.action_selection.action_list import action_list
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.models.state import HistoryElement
from runthroughlinehackathor.settings import settings


async def select_actions(
    history: list[HistoryElement], current_stage: Stage, parameters: Parameters
) -> list[Action]:
    valid_actions = tuple(
        action
        for action in action_list
        if (not action.is_unique or action not in history)
        and current_stage in action.allowed_stages
        and all(
            prerequisite in history for prerequisite in action.prerequisites
        )
    )
    action_stream = await _shuffle_actions_with_weight(
        parameters, history, valid_actions
    )
    chosen_actions = []
    for action in islice(action_stream, 1000):
        if _can_add_action(action, chosen_actions):
            chosen_actions.append(action)
        if len(chosen_actions) == settings.n_actions:
            return chosen_actions
    raise ValueError("Not enough actions to satisfy conditions")


def _can_add_action(action: Action, chosen_actions: list[Action]) -> bool:
    if action in chosen_actions:
        return False
    chosen_actions = chosen_actions + [action]
    n_remaining_actions_to_gather = settings.n_actions - len(chosen_actions)
    present_types = frozenset(a.type for a in chosen_actions)
    n_remaining_types = len(ActionType) - len(present_types)
    if n_remaining_types > n_remaining_actions_to_gather:
        return False
    n_small_actions = sum(
        a.time_cost <= settings.small_action_max_cost for a in chosen_actions
    )
    if n_small_actions > settings.n_small_actions:
        return False
    n_big_actions = sum(
        a.time_cost > settings.small_action_max_cost for a in chosen_actions
    )
    if n_big_actions > settings.n_big_actions:
        return False
    return True


async def _shuffle_actions_with_weight(
    parameters: Parameters,
    history: list[HistoryElement],
    valid_actions: Iterable[Action],
) -> Iterable[Action]:
    class ActionsWithWeights(BaseModel):
        actions_with_weights: list[_ActionWeight] = Field(
            description="Return up to 10 actions", max_length=10
        )

    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, api_key=settings.openai_api_key
    ).with_structured_output(ActionsWithWeights)
    action_weights: list[_ActionWeight] = (
        await model.ainvoke(
            [
                HumanMessage(
                    "Assign weights to given actions. "
                    "Given state history. "
                    "Weights should determine the probability of occurrence of given decision for user."
                    f"Current user parameters are {parameters.model_dump_json(indent=2)}\n"
                    f"Current history of previous user actions is {'\n'.join(elem.model_dump_json(indent=2) for elem in history)}\n"
                    f"You must add weights to the following actions {'\n'.join(action.model_dump_json(indent=2) for action in valid_actions)}"
                    "Return only action that are more likely given history"
                )
            ]
        )
    ).actions_with_weights
    name_to_weight = {a.action_name: a.action_weight for a in action_weights}
    action_weight_pairs = tuple(
        (a, name_to_weight.get(a.name, 1)) for a in valid_actions
    )
    actions_with_weights = list(
        chain.from_iterable(w * (a,) for a, w in action_weight_pairs)
    )
    random.shuffle(actions_with_weights)
    return cycle(actions_with_weights)


class _ActionWeight(BaseModel):
    action_name: str
    action_weight: PositiveInt = Field(descriprion="1 to 10", le=10)
