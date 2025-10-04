import uuid

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from runthroughlinehackathor.models.gender import Gender
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.phase import Phase
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings
from runthroughlinehackathor.state_update.state_increment import StateIncrement
from runthroughlinehackathor.state_update.update_state import update_state

app = FastAPI()


states: list[State] = []


class _CreateNewGameInput(BaseModel):
    gender: Gender
    goal: str


@app.post("/create-new-game")
async def create_new_game(create_new_game_input: _CreateNewGameInput):
    gender_text = {Gender.MALE: "mężczyzną", Gender: "kobietą"}[
        create_new_game_input.gender
    ]
    age_text = f"{settings.initial_age} letni" + (
        "m" if create_new_game_input.gender == Gender.MALE else "ą"
    )
    new_state = State(
        id=uuid.uuid4(),
        parameters=Parameters(
            health=settings.initial_health,
            career=settings.initial_other_parameters,
            relations=settings.initial_other_parameters,
            money=settings.initial_other_parameters,
        ),
        history=[],
        turn_descriptions=settings.initial_turn_description.format(
            gender=gender_text, age=age_text
        ),
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
async def get_next_state(state_update: StateIncrement):
    state = next((s for s in states if s.id == state_update.state_id), None)
    if state is None:
        return HTMLResponse(
            content=f"No state with id={state_update.state_id}",
            status_code=400,
        )
    update_state(state, state_update)
    return JSONResponse(content=state.model_dump(mode="json"), status_code=200)


if __name__ == "__main__":
    uvicorn.run(app)
