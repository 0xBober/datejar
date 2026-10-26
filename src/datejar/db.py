from sqlalchemy import create_engine, event
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

from datejar.config import settings


def _set_sqlite_pragma(dbapi_connection, connection_record):
    previous_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

    # restore previous autocommit setting
    dbapi_connection.autocommit = previous_autocommit


def create_db_engine(database_url: str):
    engine = create_engine(
        database_url, echo=settings.environment == "dev"
    )  # Logging SQL queries in dev mode
    event.listen(
        engine, "connect", _set_sqlite_pragma
    )  # Enable foreign key support for SQLite
    return engine


engine = create_db_engine(settings.database_url)
SessionLocal = sessionmaker(engine)  # Create a session factory


class Base(DeclarativeBase):
    pass
