from __future__ import annotations

import os

from pydantic import PositiveInt
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_PATH", ".env"), extra="ignore"
    )
    n_actions: PositiveInt = 8
    time_pre_turn: PositiveInt = 10
    health_per_time_spent: PositiveInt = 1


settings = Settings()
