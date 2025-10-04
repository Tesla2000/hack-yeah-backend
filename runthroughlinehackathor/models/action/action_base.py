from abc import ABC

from pydantic import BaseModel
from pydantic import HttpUrl
from runthroughlinehackathor.models.parameters import Parameters


class ActionBase(BaseModel, ABC):
    name: str
    description: str
    image_url: HttpUrl
    parameter_change: Parameters
