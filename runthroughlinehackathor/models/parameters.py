from typing import Self

from pydantic import BaseModel
from runthroughlinehackathor.settings import settings


class Parameters(BaseModel):
    career: int
    relations: int
    health: int
    money: int

    def __add__(self, other: Self) -> Self:
        return Parameters(
            career=min(
                settings.MAX_PARAMETER_VALUE, self.career + other.career
            ),
            relations=min(
                settings.MAX_PARAMETER_VALUE, self.relations + other.relations
            ),
            health=min(
                settings.MAX_PARAMETER_VALUE, self.health + other.health
            ),
            money=min(settings.MAX_PARAMETER_VALUE, self.money + other.money),
        )
