from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    environment: Literal["dev", "prod"]
    database_url: str
    secret_key: SecretStr


settings = Settings()
