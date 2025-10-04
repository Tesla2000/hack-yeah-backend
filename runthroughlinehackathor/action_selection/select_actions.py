import random
from collections.abc import Container
from collections.abc import Iterable

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from pydantic import Field
from pydantic import PositiveInt
from runthroughlinehackathor.action_selection.action_list import action_list
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings


async def select_actions(
    state: State, n_actions: PositiveInt = settings.n_actions
) -> list[Action]:
    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0
    ).with_structured_output(list[_ActionWeight])
    action_weights: list[_ActionWeight] = await model.ainvoke(
        [
            HumanMessage(
                "Assign weights to given actions. "
                "Given state history. "
                "Weights should determine the probability of occurrence of given decision for user."
                f"Current user parameters are {state.parameters.model_dump_json(indent=2)}\n"
                f"Current history of previous user actions is {'\n'.join(elem.model_dump_json(indent=2) for elem in state.history)}"
            )
        ]
    )
    name_to_weight = {a.action_name: a.action_weight for a in action_weights}
    action_weight_pairs = tuple(
        (a, name_to_weight.get(a.name, 1)) for a in action_list
    )
    cards_of_each_type = _get_cards_of_each_type(action_weight_pairs)
    remaining_cards = _remove_card_from_weighs(
        action_weight_pairs, cards_of_each_type
    )
    rest_of_cards = _get_rest_of_cards(
        remaining_cards, n_actions - len(cards_of_each_type)
    )
    return cards_of_each_type + rest_of_cards


def _remove_card_from_weighs(
    action_weight_pairs: Iterable[tuple[Action, int]],
    removed_action: Container[Action],
) -> list[tuple[Action, int]]:
    return list(
        (a, w) for a, w in action_weight_pairs if a not in removed_action
    )


def _get_cards_of_each_type(
    action_weight_pairs: Iterable[tuple[Action, int]],
) -> list[Action]:
    return [
        random.choices(
            tuple(a for a, _ in action_weight_pairs if a.type == action_type),
            weights=tuple(
                w for a, w in action_weight_pairs if a.type == action_type
            ),
        )[0]
        for action_type in ActionType
    ]


def _get_rest_of_cards(
    action_weight_pairs: list[tuple[Action, int]], n_remaining_actions: int
) -> list[Action]:
    assert n_remaining_actions >= 0
    remaining_actions = []
    for _ in range(n_remaining_actions):
        next_action = random.choices(
            tuple(a for a, _ in action_weight_pairs),
            weights=tuple(w for a, w in action_weight_pairs),
        )[0]
        action_weight_pairs = _remove_card_from_weighs(
            action_weight_pairs, next_action
        )
        remaining_actions.append(next_action)
    return remaining_actions


class _ActionWeight(BaseModel):
    action_name: str
    action_weight: PositiveInt = Field(descriprion="1 to 10", le=10)
