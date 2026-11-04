import argparse
import sys
from getpass import getpass

from datejar.db import SessionLocal
from datejar.services.users import (
    MAX_USERNAME_LEN,
    MIN_USERNAME_LEN,
    UsernameTakenError,
    create_user,
    normalize_username,
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

    args = parser.parse_args(argv)

    if args.command == "create-user":
        return _create_user_command(args.username)

    return 1
