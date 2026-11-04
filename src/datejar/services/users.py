from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from datejar.models import User
from datejar.security import hash_password

ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789_-"
MIN_USERNAME_LEN = 2
MAX_USERNAME_LEN = 32
MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 64
MAX_DISPLAY_NAME_LEN = 64


class UsernameTakenError(Exception):
    """
    Raised when attempting to add a new user and the name is already taken
    """


def normalize_username(username: str) -> str:
    username = username.strip().lower()

    if not MIN_USERNAME_LEN <= len(username) <= MAX_USERNAME_LEN:
        raise ValueError(
            f"Username must fit between {MIN_USERNAME_LEN} and {MAX_USERNAME_LEN} characters"
        )

    for char in username:
        if char not in ALLOWED_CHARS:
            raise ValueError(f"{char} is a disallowed char")

    return username


def create_user(
    session: Session, username: str, display_name: str, password: str
) -> User:
    username = normalize_username(username)

    display_name = display_name.strip()

    if len(display_name) == 0 or len(display_name) > MAX_DISPLAY_NAME_LEN:
        raise ValueError(
            f"Display name is empty or longer than {MAX_DISPLAY_NAME_LEN} characters long"
        )

    if not MIN_PASSWORD_LEN <= len(password) <= MAX_PASSWORD_LEN:
        raise ValueError(
            f"Password must fit between {MIN_PASSWORD_LEN} and {MAX_PASSWORD_LEN} characters"
        )

    user = User(
        username=username,
        display_name=display_name,
        password_hash=hash_password(password),
    )

    session.add(user)

    try:
        session.commit()
    except IntegrityError as err:
        session.rollback()
        raise UsernameTakenError(f"Username {username} already exists") from err

    return user
