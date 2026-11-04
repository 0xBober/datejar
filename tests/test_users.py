import pytest
from sqlalchemy.orm import Session

from datejar import models  # noqa: F401 user model is needed to run test
from datejar.db import Base, create_db_engine
from datejar.security import verify_password
from datejar.services.users import (
    MAX_DISPLAY_NAME_LEN,
    MAX_PASSWORD_LEN,
    MAX_USERNAME_LEN,
    MIN_PASSWORD_LEN,
    MIN_USERNAME_LEN,
    UsernameTakenError,
    create_user,
)

TEST_USERNAME = "MIKE"
TEST_DISPLAY_NAME = "Michał"
TEST_PASSWORD = "ReallyHardPassword123"


@pytest.fixture
def session():
    engine = create_db_engine("sqlite://")
    Base.metadata.create_all(engine)
    db_session = Session(engine)
    yield db_session
    db_session.close()
    engine.dispose()


def test_create_user_normalizes_username(session):
    user = create_user(session, " Mike", "Michał", TEST_PASSWORD)

    assert user.username == "mike"
    assert user.id is not None
    assert user.created_at is not None


def test_create_user_password_hashed(session):
    user = create_user(session, " Mike", "Michał", TEST_PASSWORD)

    assert user.password_hash != TEST_PASSWORD
    assert verify_password(user.password_hash, TEST_PASSWORD) is True


def test_create_user_duplicate_usernames(session):
    create_user(session, "mike", TEST_DISPLAY_NAME, TEST_PASSWORD)

    with pytest.raises(UsernameTakenError):
        create_user(session, "MIKE", TEST_DISPLAY_NAME, TEST_PASSWORD)


def test_create_user_username_illegal_char(session):
    with pytest.raises(ValueError):
        create_user(session, "michał", TEST_DISPLAY_NAME, TEST_PASSWORD)


def test_create_user_username_short_long(session):
    with pytest.raises(
        ValueError, match=f"between {MIN_USERNAME_LEN} and {MAX_USERNAME_LEN}"
    ):
        create_user(
            session,
            TEST_USERNAME[0 : MIN_USERNAME_LEN - 1],
            TEST_DISPLAY_NAME,
            TEST_PASSWORD,
        )
    with pytest.raises(
        ValueError, match=f"between {MIN_USERNAME_LEN} and {MAX_USERNAME_LEN}"
    ):
        create_user(session, "", TEST_DISPLAY_NAME, TEST_PASSWORD)

    with pytest.raises(
        ValueError, match=f"between {MIN_USERNAME_LEN} and {MAX_USERNAME_LEN}"
    ):
        create_user(
            session,
            TEST_USERNAME + "a" * (MAX_USERNAME_LEN + 1),
            TEST_DISPLAY_NAME,
            TEST_PASSWORD,
        )


def test_create_user_display_name_empty_long(session):
    with pytest.raises(ValueError):
        create_user(session, TEST_USERNAME, "   ", TEST_PASSWORD)
    with pytest.raises(ValueError):
        create_user(
            session,
            TEST_USERNAME,
            TEST_DISPLAY_NAME + "a" * MAX_DISPLAY_NAME_LEN,
            TEST_PASSWORD,
        )


def test_create_user_password_short_long(session):
    with pytest.raises(ValueError, match="Password"):
        create_user(session, "mike", "Michał", TEST_PASSWORD[0 : MIN_PASSWORD_LEN - 1])
    with pytest.raises(ValueError, match="Password"):
        create_user(session, "mike", "Michał", TEST_PASSWORD + "a" * MAX_PASSWORD_LEN)


def test_session_still_works_after_username_taken(session):
    create_user(session, "mike", TEST_DISPLAY_NAME, TEST_PASSWORD)
    with pytest.raises(UsernameTakenError):
        create_user(session, "mike", TEST_DISPLAY_NAME, TEST_PASSWORD)

    test_user = create_user(session, "bob", TEST_DISPLAY_NAME, TEST_PASSWORD)
    assert test_user.id is not None
