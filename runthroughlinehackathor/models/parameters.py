from pydantic import BaseModel
from pydantic.v1 import NonNegativeInt


class Parameters(BaseModel):
    career: NonNegativeInt
    relations: NonNegativeInt
    health: NonNegativeInt
    money: NonNegativeInt
