from sqlalchemy import text

from datejar.db import create_db_engine


def test_sqlite_pragma_settings(tmp_path):
    temp_engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")

    with temp_engine.connect() as connection:
        foreign_keys = connection.execute(text("PRAGMA foreign_keys")).scalar()
        journal_mode = connection.execute(text("PRAGMA journal_mode")).scalar()
        assert foreign_keys == 1  # Foreign keys should be enabled
        assert journal_mode == "wal"  # Journal mode should be WAL

    temp_engine.dispose()
