from pydantic import BaseModel
from runthroughlinehackathor.models.parameters import Parameters


class Action(BaseModel):
    name: str
    description: str
    parameter_change: Parameters
