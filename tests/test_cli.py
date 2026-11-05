import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from datejar import (
    cli,
    models,  # noqa: F401  (import registers tables on Base.metadata)
)
from datejar.db import Base, create_db_engine
from datejar.models import User
from datejar.security import verify_password

TEST_PASSWORD = "ReallyHardPassword123"
NEW_TEST_PASSWORD = "NotAsHardPassword321"


@pytest.fixture
def session_factory(monkeypatch):
    engine = create_db_engine("sqlite://")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    monkeypatch.setattr("datejar.cli.SessionLocal", factory)
    yield factory
    engine.dispose()


def fake_prompts(monkeypatch, display_name, passwords):
    monkeypatch.setattr("builtins.input", lambda: display_name)
    answers = iter(passwords)
    monkeypatch.setattr("datejar.cli.getpass", lambda prompt: next(answers))


def test_create_user_command_creates_user(session_factory, monkeypatch, capsys):
    fake_prompts(monkeypatch, "Michał", [TEST_PASSWORD, TEST_PASSWORD])

    exit_code = cli.main(["create-user", "mike"])

    assert exit_code == 0
    with session_factory() as session:
        user = session.scalar(select(User).where(User.username == "mike"))
    assert user is not None
    assert "mike" in capsys.readouterr().out


def must_not_be_called(prompt):
    raise AssertionError("getpass should not be called")


def test_create_user_command_rejects_invalid_username(
    session_factory, monkeypatch, capsys
):
    monkeypatch.setattr("datejar.cli.getpass", must_not_be_called)

    exit_code = cli.main(["create-user", "michał"])

    assert exit_code == 1
    assert "ł" in capsys.readouterr().err


def test_create_user_command_different_passwords(session_factory, monkeypatch, capsys):
    fake_prompts(monkeypatch, "Michał", [TEST_PASSWORD, NEW_TEST_PASSWORD])

    exit_code = cli.main(["create-user", "mike"])

    assert exit_code == 1
    assert "don't match" in capsys.readouterr().err


def test_set_password_command_change_users_password(
    session_factory, monkeypatch, capsys
):
    fake_prompts(monkeypatch, "Michał", [TEST_PASSWORD, TEST_PASSWORD])

    exit_code = cli.main(["create-user", "mike"])

    assert exit_code == 0

    with session_factory() as session:
        user = session.scalar(select(User).where(User.username == "mike"))
    assert verify_password(password_hash=user.password_hash, password=TEST_PASSWORD)
