from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    environment: Literal["dev", "prod"]
    database_url: str = "sqlite:///./datejar.db"
    secret_key: SecretStr

    @field_validator("secret_key")
    @classmethod
    def check_secret_key(cls, value: SecretStr) -> SecretStr:

        if len(value.get_secret_value()) < MIN_SECRET_KEY_LENGTH:
            raise ValueError(
                f"""SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters long. 
                Generate a new key with 'uv run python -c \"import secrets; print(secrets.token_urlsafe(32))\"' and set it in the .env file."""
            )

        return value


settings = Settings()
