import asyncio
import os
import uuid

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from runthroughlinehackathor.action_selection.select_actions import (
    select_actions,
)
from runthroughlinehackathor.action_selection.select_random_event import (
    select_random_event,
)
from runthroughlinehackathor.models.gender import Gender
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings
from runthroughlinehackathor.state_update.state_increment import StateIncrement
from runthroughlinehackathor.state_update.update_state import update_state
from starlette.responses import RedirectResponse

app = FastAPI()


states: list[State] = []


class _CreateNewGameInput(BaseModel):
    gender: Gender
    goal: str
    name: str


@app.get("/ping")
async def ping():
    return Response("pong")


X_API_KEY = APIKeyHeader(name="X_API_KEY")


def api_key_auth(x_api_key: str = Depends(X_API_KEY)):
    if x_api_key != os.environ["X_API_KEY"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid api key",
        )


@app.post("/create-new-game", dependencies=[Depends(api_key_auth)])
async def create_new_game(create_new_game_input: _CreateNewGameInput):
    gender_text = {Gender.MALE: "mężczyzną", Gender.FEMALE: "kobietą"}[
        create_new_game_input.gender
    ]
    age_text = f"{settings.initial_age} letni" + (
        "m" if create_new_game_input.gender == Gender.MALE else "ą"
    )
    history = []
    current_stage = Stage.FIRST
    parameters = Parameters(
        health=settings.initial_health,
        career=settings.initial_other_parameters,
        relations=settings.initial_other_parameters,
        money=settings.initial_other_parameters,
    )
    actions, random_event = await asyncio.gather(
        select_actions(
            history=history, current_stage=current_stage, parameters=parameters
        ),
        select_random_event(history),
    )
    new_state = State(
        id=uuid.uuid4(),
        parameters=parameters,
        history=history,
        turn_description=settings.initial_turn_description.format(
            gender=gender_text, age=age_text
        ),
        current_stage=current_stage,
        game_turn=0,
        gender=create_new_game_input.gender,
        goal=create_new_game_input.goal,
        name=create_new_game_input.name,
        big_actions=list(
            a for a in actions if a.time_cost > settings.small_action_max_cost
        ),
        small_actions=list(
            a for a in actions if a.time_cost <= settings.small_action_max_cost
        ),
        random_event=random_event,
    )
    states.append(new_state)
    return JSONResponse(
        content=new_state.model_dump(mode="json"), status_code=201
    )


@app.post("/next-turn", dependencies=[Depends(api_key_auth)])
async def get_next_state(state_update: StateIncrement):
    state = next((s for s in states if s.id == state_update.state_id), None)
    if state is None:
        return HTTPException(
            detail=f"No state with id={state_update.state_id}",
            status_code=404,
        )
    await update_state(state, state_update)
    return JSONResponse(content=state.model_dump(mode="json"), status_code=200)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")
