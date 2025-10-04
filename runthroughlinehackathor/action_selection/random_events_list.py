import csv

from runthroughlinehackathor.models.action.reaction import Reaction
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.random_event import RandomEvent
from runthroughlinehackathor.settings import settings

_reactions: dict[int, Reaction] = dict(
    (
        int(id_),
        Reaction(
            description=description,
            image_url="https://i.imgflip.com/61gawy.jpg",
            parameter_change=Parameters(
                career=career or 0,
                relations=relations or 0,
                health=health or 0,
                money=money or 0,
            ),
            result=result,
        ),
    )
    for id_, description, career, health, money, relations, result in (
        csv.reader(settings.reactions_file.read_text().splitlines()[1:])
    )
)

random_events: tuple[RandomEvent, ...] = tuple(
    RandomEvent(
        name=name,
        description=description,
        reactions=[
            _reactions[int(reaction_1_id)],
            _reactions[int(reaction_2_id)],
        ],
    )
    for name, description, reaction_1_id, reaction_2_id in csv.reader(
        settings.random_events_file.read_text().splitlines()[1:]
    )
)
