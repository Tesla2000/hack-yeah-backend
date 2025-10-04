from runthroughlinehackathor.models.random_event import RandomEvent
from runthroughlinehackathor.models.state import HistoryElement


async def select_random_event(_: list[HistoryElement]) -> RandomEvent:
    return RandomEvent(
        name="",
        description="",
        reactions=[],
    )
