import uuid

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from runthroughlinehackathor.models._gender import Gender
from runthroughlinehackathor.models._phase import Phase
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings

app = FastAPI()


states = []


class _CreateStateInput(BaseModel):
    gender: Gender
    goal: str


@app.post("/create-state")
async def create_state(create_state_input: _CreateStateInput):
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
        gender=create_state_input.gender,
        goal=create_state_input.goal,
    )
    states.append(new_state)
    return JSONResponse(
        content=new_state.model_dump(mode="json"), status_code=201
    )


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
