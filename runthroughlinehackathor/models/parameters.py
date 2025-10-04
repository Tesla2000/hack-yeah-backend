from typing import Self

from pydantic import BaseModel
from pydantic import NonNegativeInt


class Parameters(BaseModel):
    career: NonNegativeInt
    relations: NonNegativeInt
    health: NonNegativeInt
    money: NonNegativeInt

    def __add__(self, other: Self) -> Self:
        return Parameters(
            career=self.career + other.career,
            relations=self.relations + other.relations,
            health=self.health + other.health,
            money=self.money + other.money,
        )
