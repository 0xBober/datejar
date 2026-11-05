import argparse
import sys
from getpass import getpass

from datejar.db import SessionLocal
from datejar.services.users import (
    MAX_USERNAME_LEN,
    MIN_USERNAME_LEN,
    UsernameDoesNotExistError,
    UsernameTakenError,
    create_user,
    normalize_username,
    set_password,
    validate_password,
)


def _create_user_command(username: str) -> int:
    try:
        normalize_username(username)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 1
    print("Display name: ", end="", file=sys.stderr)
    display_name = input()
    password1 = getpass("Password: ")
    try:
        validate_password(password=password1)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 1
    password2 = getpass("Repeat password: ")
    if password1 != password2:
        print("Passwords don't match", file=sys.stderr)
        return 1

    with SessionLocal() as session:
        try:
            user = create_user(
                session=session,
                username=username,
                display_name=display_name,
                password=password1,
            )
        except (ValueError, UsernameTakenError) as err:
            print(err, file=sys.stderr)
            return 1
        else:
            print(f"User with ID:{user.id} USERNAME:{user.username} was created")
            return 0


def set_password_command(username: str) -> int:
    try:
        username = normalize_username(username)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 1
    print(f"Please provide a new password for {username}")
    new_password1 = getpass("Password: ")
    try:
        validate_password(password=new_password1)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 1
    new_password2 = getpass("Repeat password: ")
    if new_password1 != new_password2:
        print("Passwords don't match", file=sys.stderr)
        return 1

    with SessionLocal() as session:
        try:
            set_password(session=session, username=username, new_password=new_password1)
        except (ValueError, UsernameDoesNotExistError) as err:
            print(err, file=sys.stderr)
            return 1
        else:
            print(f"User {username} has had their password successfully changed")
            return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="datejar", description="DateJar admin commands"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_user_parser = subparsers.add_parser("create-user", help="Create a new user")
    create_user_parser.add_argument(
        "username",
        help=f"Login name ({MIN_USERNAME_LEN}-{MAX_USERNAME_LEN} chars: a-z, 0-9, _ and -)",
    )

    create_set_password_parser = subparsers.add_parser(
        "set-password",
        help="Set new password to existing user. After providing a VALID username, type in a new password",
    )
    create_set_password_parser.add_argument(
        "username", help="Login name of an existing user"
    )

    args = parser.parse_args(argv)

    match args.command:
        case "create-user":
            return _create_user_command(args.username)
        case "set-password":
            return set_password_command(args.username)

    return 1
