from uuid import UUID

from pydantic import BaseModel
from runthroughlinehackathor.models.state import HistoryElement


class StateIncrement(BaseModel):
    state_id: UUID
    chosen_actions: list[HistoryElement]
