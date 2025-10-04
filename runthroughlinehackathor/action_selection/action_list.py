import csv

from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.settings import settings

bool_mapper = {"TRUE": True, "FALSE": False, "": False}
type_mapper = {
    "Kariera": ActionType.CAREER,
    "Pieniądze": ActionType.MONEY,
    "Zdrowie": ActionType.HEALTH,
    "Relacje": ActionType.RELATIONS,
}
action_list: tuple[Action, ...] = tuple(
    Action(
        name=action_name,
        description="",
        image_url="https://i.imgflip.com/61gawy.jpg",
        parameter_change=Parameters(
            career=career or 0,
            relations=relations or 0,
            health=health or 0,
            money=money or 0,
        ),
        allowed_stages=bool_mapper[valid_at_stage_1] * [Stage.FIRST]
        + bool_mapper[valid_at_stage_2] * [Stage.SECOND]
        + bool_mapper[valid_at_stage_3] * [Stage.THIRD],
        type=type_mapper[type_.strip()],
        time_cost=time_cost,
        is_unique=bool_mapper[unique],
    )
    for action_name, unique, valid_at_stage_1, valid_at_stage_2, valid_at_stage_3, time_cost, career, health, money, relations, type_ in csv.reader(
        settings.actions_file.read_text().splitlines()[1:]
    )
)
