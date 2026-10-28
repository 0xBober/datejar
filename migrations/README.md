# Database migrations

Schema changes are managed with [Alembic](https://alembic.sqlalchemy.org/).
The database URL comes from `DATABASE_URL` in `.env` (see `env.py`), never from `alembic.ini`.

## Everyday commands

```bash
# Apply all pending migrations (run after every pull / deploy)
uv run alembic upgrade head

# Create a new migration after changing models
uv run alembic revision --autogenerate -m "add users table"

# Undo the last migration
uv run alembic downgrade -1

# Show the current revision and the history
uv run alembic current
uv run alembic history
```

## Workflow for a schema change

1. Change or add a model.
2. Generate a migration with `--autogenerate`.
3. **Review the generated file.** Autogenerate is a draft, not the truth: it can miss renames
   (seen as drop + add) and some constraint changes.
4. Run `upgrade head`, then `downgrade -1`, then `upgrade head` again,
   to prove both directions work.
5. Commit the migration together with the model change.

## SQLite notes

- SQLite supports only a small subset of `ALTER TABLE`, so `env.py` enables
  `render_as_batch=True`: Alembic rebuilds the table, copies the data and swaps it in.
- Never edit a migration that has already been applied on the server.
  Write a new one instead.