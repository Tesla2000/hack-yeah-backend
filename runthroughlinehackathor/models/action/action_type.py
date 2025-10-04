from enum import Enum


class ActionType(str, Enum):
    HEALTH = "health"
    CAREER = "career"
    RELATIONS = "relations"
    MONEY = "money"
