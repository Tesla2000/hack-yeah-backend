from pydantic import BaseModel
from runthroughlinehackathor.models.action.action_base import ActionBase


class StateUpdate(BaseModel):
    chosen_actions: list[ActionBase]
