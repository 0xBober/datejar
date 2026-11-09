import pytest
from sqlalchemy.orm import Session

from datejar import models  # noqa: F401 user model is needed to run test
from datejar.db import Base, create_db_engine


@pytest.fixture
def engine():
    """In-memory SQLite engine with all tables created."""
    engine = create_db_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    """Database session bound to the in-memory engine, closed after the test."""
    db_session = Session(engine)
    yield db_session
    db_session.close()
