import uuid

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from runthroughlinehackathor.models._gender import Gender
from runthroughlinehackathor.models._phase import Phase
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings
from runthroughlinehackathor.state_update.state_update import StateUpdate
from runthroughlinehackathor.state_update.update_state import update_state

app = FastAPI()


states: list[State] = []


class _CreateNewGameInput(BaseModel):
    gender: Gender
    goal: str


@app.post("/create-new-game")
async def create_new_game(create_new_game_input: _CreateNewGameInput):
    new_state = State(
        id=uuid.uuid4(),
        parameters=Parameters(
            health=settings.initial_health,
            career=settings.initial_other_parameters,
            relations=settings.initial_other_parameters,
            money=settings.initial_other_parameters,
        ),
        history=[],
        turn_descriptions=settings.initial_turn_description,
        current_phase=Phase.FIRST,
        game_turn=0,
        gender=create_new_game_input.gender,
        goal=create_new_game_input.goal,
    )
    states.append(new_state)
    return JSONResponse(
        content=new_state.model_dump(mode="json"), status_code=201
    )


@app.post("/next-turn")
async def get_next_state(state_update: StateUpdate):
    state = next((s for s in states if s.id == state_update.state_id), None)
    if state is None:
        return HTMLResponse(
            content=f"No state with id={state_update.state_id}",
            status_code=400,
        )
    update_state(state, state_update)
    return JSONResponse(content=state.model_dump(mode="json"), status_code=200)
