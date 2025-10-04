from typing import Self

from pydantic import BaseModel


class Parameters(BaseModel):
    career: int
    relations: int
    health: int
    money: int

    def __add__(self, other: Self) -> Self:
        return Parameters(
            career=self.career + other.career,
            relations=self.relations + other.relations,
            health=self.health + other.health,
            money=self.money + other.money,
        )
