from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Self

from pydantic import HttpUrl
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

    initial_turn_description: str = """Wkroczyleś do symulacji - masz obecnie {age} lat i właśnie rozpoczynasz swoją przygodę z dorosłością.
Przed Tobą wiele decyzji – każda z nich wpłynie na Twoją przyszłość.

Gra podzielona jest na etapy życia – od młodości, przez dorosłość, aż po wiek dojrzały.
Każdy etap składa się z tur, a każda tura to 5 lat Twojego życia.

W każdej turze:

Podejmiesz kluczową decyzję, która wyznaczy kierunek Twojej historii.

Wybierzesz pomniejsze akcje, by rozwijać karierę, relacje, zdrowie lub finanse.

Zmierzysz się z losowym wydarzeniem, które może wszystko zmienić.

Twoje wybory zbudują Twoje życie.
Czy osiągniesz sukces, szczęście, czy może coś pomiędzy?"""
    initial_age: PositiveInt = 15
    years_per_turn: PositiveInt = 5

    actions_file: str = "Akcje hackathon - Arkusz1.csv"
    random_events_file: str = "Akcje hackathon - Arkusz2.csv"
    reactions_file: str = "Akcje hackathon - Arkusz3.csv"

    stage_two_step: PositiveInt = 2
    stage_three_step: PositiveInt = 7

    MAX_PARAMETER_VALUE: PositiveInt = 100
    healthy_threshold: PositiveInt = 20

    end_age: Mapping[Gender, PositiveInt] = {
        Gender.MALE: 65,
        Gender.FEMALE: 60,
    }

    has_spouse_action_name: str = "Małżeństwo"
    has_child_action_name: str = "Dziecko"
    is_happy_min_mean: PositiveInt = 50

    VERCEL_BLOB_URL: HttpUrl = "https://blob.vercel-storage.com"
    BLOB_READ_WRITE_TOKEN: SecretStr = "token"

    # LLM Prompts
    action_weight_prompt: str = """Assign weights to given actions. Given state history. Weights should determine the probability of occurrence of given decision for user.
Current user parameters are {parameters}
Current history of previous user actions is {history}
You must add weights to the following actions {actions}
Return only action that are more likely given history"""

    game_loss_prompt: str = """Wyjaśnij użytkownikowi dlaczego przegrał grę
Parametry w drugim stane {parameters}
decyzje użytkownika {history}. Zwróć odpowiedź w języku polskim zwracając się bezpośrednio do gracza nie wspominaj bezpośrednio o wartości statystyk. Postaraj się być jak najbardziej obrazowy. Znaczenie parametru kariera (zdolność do zarabiana pieniędy)"""

    stage_summary_prompt: str = """Podsumuj zmiany jakie zrobił gracz między stanem pierwszym i drugim
Parametry w pierwszym stane {previous_parameters}
Parametry w drugim stane {current_parameters}
decyzje użytkownika {history_diff} zwróć odpowiedź w języku polskim zwracając się bezpośrednio do gracza nie wspominaj bezpośrednio o wartości statystyk. Postaraj się być jak najbardziej obrazowy. Znaczenie parametru kariera (zdolność do zarabiana pieniędy)"""

    turn_description_prompt: str = """Podsumuj zmiany jakich dokonał użytkowinik w poprzedmi kroku zmiany to {chosen_actions}
Zwóć histerię biorąc pod uwagę, że zmiany zaszły na przestrzeni 5 lat
Historie z poprzednich pięcioletnich okresów to {turn_descriptions}
Zwróć odpowiedź w języku polskim zwracając się bezpośrednio do gracza nie wspominaj bezpośrednio o wartości statystyk. Postaraj się być jak najbardziej obrazowy. Znaczenie parametru kariera (zdolność do zarabiana pieniędy)"""

    @model_validator(mode="after")
    def verify_n_actions(self) -> Self:
        if self.n_big_actions == self.n_big_actions + self.n_small_actions:
            raise ValueError(
                "Sum of number of big and small actions must be equal"
            )
        return self


settings = Settings()
