from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic import PositiveFloat
from pydantic import PositiveInt
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from runthroughlinehackathor.models.gender import Gender


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_PATH", ".env"), extra="ignore"
    )
    openai_api_key: SecretStr = "sk-proj-"

    n_actions: PositiveInt = 8
    time_pre_turn: PositiveInt = 10
    health_per_time_spent: PositiveInt = 1
    career_to_money_coefficient: PositiveFloat = 0.1

    n_big_actions: PositiveInt = 3
    n_small_actions: PositiveInt = 5

    small_action_max_cost: PositiveInt = 3

    initial_health: PositiveInt = 100
    initial_other_parameters: PositiveInt = 20

    initial_turn_description: str = "Jesteś {age} {gender}. Twoim obecnym ce"
    initial_age: PositiveInt = 15
    years_per_turn: PositiveInt = 5

    actions_file: Path = "resources/Akcje hackathon - Arkusz1.csv"
    random_events_file: Path = "resources/Akcje hackathon - Arkusz2.csv"
    reactions_file: Path = "resources/Akcje hackathon - Arkusz3.csv"

    stage_two_step: PositiveInt = 2
    stage_three_step: PositiveInt = 7

    end_age: Mapping[Gender, PositiveInt] = {
        Gender.MALE: 65,
        Gender.FEMALE: 60,
    }

    @model_validator(mode="after")
    def verify_n_actions(self) -> Self:
        if self.n_big_actions == self.n_big_actions + self.n_small_actions:
            raise ValueError(
                "Sum of number of big and small actions must be equal"
            )
        return self


settings = Settings()
