import pytest
from pydantic import ValidationError

from datejar.config import MIN_SECRET_KEY_LENGTH, Settings


def test_secret_key_with_min_length_is_accepted():
    key = "a" * MIN_SECRET_KEY_LENGTH

    settings = Settings(
        _env_file=None,
        environment="dev",
        database_url="sqlite://",
        secret_key=key,
    )

    assert settings.secret_key.get_secret_value() == key


def test_placeholder_secret_key_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="dev",
            database_url="sqlite://",
            secret_key="change_me",
        )


def test_secret_key_too_short_is_rejected():
    key = "a" * (MIN_SECRET_KEY_LENGTH - 1)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="dev",
            database_url="sqlite://",
            secret_key=key,
        )
