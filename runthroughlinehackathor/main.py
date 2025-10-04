import os
import uuid

import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
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
        turn_description=settings.initial_turn_description.format(
            gender=gender_text, age=age_text
        ),
        current_stage=Stage.FIRST,
        game_turn=0,
        gender=create_new_game_input.gender,
        goal=create_new_game_input.goal,
        name=create_new_game_input.name,
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
    update_state(state, state_update)
    return JSONResponse(content=state.model_dump(mode="json"), status_code=200)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
