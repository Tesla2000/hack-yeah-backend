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


settings = Settings()
