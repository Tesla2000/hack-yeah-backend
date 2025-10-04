import random

from runthroughlinehackathor.action_selection.random_events_list import (
    random_events,
)
from runthroughlinehackathor.models.random_event import RandomEvent
from runthroughlinehackathor.models.state import HistoryElement


async def select_random_event(history: list[HistoryElement]) -> RandomEvent:
    return random.choice(
        tuple(filter(lambda e: e not in history, random_events))
    )
