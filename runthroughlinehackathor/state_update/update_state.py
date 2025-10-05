import asyncio
import logging
from itertools import filterfalse
from math import floor

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from runthroughlinehackathor.action_selection.select_actions import (
    select_actions,
)
from runthroughlinehackathor.action_selection.select_random_event import (
    select_random_event,
)
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings
from runthroughlinehackathor.state_update.apply_action import apply_action
from runthroughlinehackathor.state_update.state_increment import StateIncrement

previous_states = []

_logger = logging.getLogger(__name__)


async def update_state(state: State, state_update: StateIncrement) -> None:
    previous_states.append(state.model_copy(deep=True))
    for action in filterfalse(
        Action.__instancecheck__, state_update.chosen_actions
    ):
        apply_action(state, action)
    spent_time = 0
    for action in filter(
        Action.__instancecheck__, state_update.chosen_actions
    ):
        if spent_time + action.time_cost <= settings.time_pre_turn:
            apply_action(state, action)
        else:
            break
    if any(
        parameter_value < 0
        for parameter_value in state.parameters.model_dump().values()
    ):
        state.is_game_finished = True
        state.did_user_win = False
        state.stage_summary = (
            await ChatOpenAI(
                name="gpt-4o-mini", api_key=settings.openai_api_key
            ).ainvoke(
                [
                    HumanMessage(
                        "Wyjaśnij użytkownikowi dlaczego przegrał grę\n"
                        f"Parametry w drugim stane {state.parameters}\n"
                        f"decyzje użytkownika {state.history}. Zwróć odpowiedź w języku polskim zwracając się bezpośrednio do gracza nie wspominaj bezpośrednio o wartości statystyk. Postaraj się być jak najbardziej obrazowy. Znaczenie parametru kariera (zdolność do zarabiana pieniędy)"
                    )
                ]
            )
        ).content
        return
    remaining_time = settings.time_pre_turn - spent_time
    state.parameters.health += settings.health_per_time_spent * remaining_time
    state.parameters.money += floor(
        settings.career_to_money_coefficient * state.parameters.career
    )
    actions, random_event, turn_description = await asyncio.gather(
        select_actions(
            history=state.history,
            current_stage=state.current_stage,
            parameters=state.parameters,
        ),
        select_random_event(state.history),
        _generate_turn_description(state, state_update),
    )
    state.turn_descriptions.append(turn_description)
    state.random_event = random_event
    state.history.append(random_event)
    state.big_actions = list(
        a for a in actions if a.time_cost > settings.small_action_max_cost
    )
    state.small_actions = list(
        a for a in actions if a.time_cost <= settings.small_action_max_cost
    )
    state.game_turn += 1
    if state.age >= settings.end_age[state.gender]:
        state.stage_summary = await _generate_summary(Stage.THIRD, state)
        state.is_game_finished = True
    elif state.game_turn >= settings.stage_three_step:
        if state.current_stage == Stage.SECOND:
            state.stage_summary = await _generate_summary(Stage.SECOND, state)
        state.current_stage = Stage.THIRD
    elif state.game_turn >= settings.stage_two_step:
        if state.current_stage == Stage.FIRST:
            state.stage_summary = await _generate_summary(Stage.FIRST, state)
        state.current_stage = Stage.SECOND


async def _generate_summary(previous_stage: Stage, state: State) -> str:
    previous_state: State = max(
        filter(
            lambda s: s.current_stage == previous_stage and s.id == state.id,
            previous_states,
        ),
        key=lambda s: s.game_turn,
    )
    return (
        await ChatOpenAI(
            name="gpt-4o-mini", api_key=settings.openai_api_key
        ).ainvoke(
            [
                HumanMessage(
                    "Podsumuj zmiany jakie zrobił gracz między stanem pierwszym i drugim\n"
                    f"Parametry w pierwszym stane {previous_state.parameters}\n"
                    f"Parametry w drugim stane {state.parameters}\n"
                    f"decyzje użytkownika {state.history[len(previous_state.history):]} zwróć odpowiedź w języku polskim zwracając się bezpośrednio do gracza nie wspominaj bezpośrednio o wartości statystyk. Postaraj się być jak najbardziej obrazowy. Znaczenie parametru kariera (zdolność do zarabiana pieniędy)"
                )
            ]
        )
    ).content


async def _generate_turn_description(
    state: State, state_increment: StateIncrement
) -> str:
    return (
        await ChatOpenAI(
            name="gpt-4o-mini", api_key=settings.openai_api_key
        ).ainvoke(
            [
                HumanMessage(
                    f"Podsumuj zmiany jakich dokonał użytkowinik w poprzedmi kroku zmiany to {state_increment.chosen_action_references}\n"
                    "Zwóć histerię biorąc pod uwagę, że zmiany zaszły na przestrzeni 5 lat\n"
                    f"Historie z poprzednich pięcioletnich okresów to {state.turn_descriptions}"
                    "Zwróć odpowiedź w języku polskim zwracając się bezpośrednio do gracza nie wspominaj bezpośrednio o wartości statystyk. Postaraj się być jak najbardziej obrazowy. Znaczenie parametru kariera (zdolność do zarabiana pieniędy)"
                )
            ]
        )
    ).content
