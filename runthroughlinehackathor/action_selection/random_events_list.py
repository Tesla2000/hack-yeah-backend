import csv

from runthroughlinehackathor.action_selection._download_from_vercel_blob import (
    download_from_vercel_blob,
)
from runthroughlinehackathor.models.action.reaction import Reaction
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.random_event import RandomEvent
from runthroughlinehackathor.settings import settings

reactions: dict[int, Reaction] = dict(
    (
        int(id_),
        Reaction(
            id=id_,
            description=description,
            image_url=image_url,
            parameter_change=Parameters(
                career=career or 0,
                relations=relations or 0,
                health=health or 0,
                money=money or 0,
            ),
            result=result,
        ),
    )
    for id_, description, career, health, money, relations, result, image_url in csv.reader(
        download_from_vercel_blob(settings.reactions_file).splitlines()[1:]
    )
)

random_events: tuple[RandomEvent, ...] = tuple(
    RandomEvent(
        name=name,
        description=description,
        reactions=[
            reactions[int(reaction_1_id)],
            reactions[int(reaction_2_id)],
        ],
    )
    for name, description, reaction_1_id, reaction_2_id in csv.reader(
        download_from_vercel_blob(settings.random_events_file).splitlines()[1:]
    )
)


if __name__ == "__main__":
    pass
