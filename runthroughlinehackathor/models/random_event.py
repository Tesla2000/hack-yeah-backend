from pydantic import BaseModel
from runthroughlinehackathor.models.reaction import Reaction


class RandomEvent(BaseModel):
    name: str
    description: str
    reactions: list[Reaction]
