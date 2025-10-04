from abc import ABC

from pydantic import BaseModel
from runthroughlinehackathor.models.parameters import Parameters


class ActionBase(BaseModel, ABC):
    name: str
    description: str
    parameter_change: Parameters
