# DateJar

A self-hosted date idea jar for couples: add ideas, tag them by mood, weather and budget, and draw your next date at random.

> **Status: early development.** The foundation is in place (configuration, database, accounts, CLI, CI, deployment), but the jar itself is not built yet. Expect breaking changes.

## Features

**Available now**

- User accounts managed from the command line (`datejar create-user`, `datejar set-password`)
- Passwords hashed with argon2id
- SQLite database with migrations (Alembic)
- Health check endpoint for monitoring (`/healthz`)
- Production mode with API docs disabled

**Planned**

- Web login
- Add, edit and archive date ideas, each tagged by energy, weather, budget, time and place
- Draw a random idea using tag filters
- Done ideas return to the jar after a 30-day cooldown
- Date history with ratings and notes
- Installable on a phone as a PWA

## Tech stack

- Python 3.13, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 and [Alembic](https://alembic.sqlalchemy.org/) on SQLite (WAL mode)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration
- [uv](https://docs.astral.sh/uv/) for dependencies, [ruff](https://docs.astral.sh/ruff/) for linting and formatting, [pytest](https://docs.pytest.org/) for tests

## Running locally

### Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs the right Python version for you if needed.
- Git

### Setup

```bash
git clone https://github.com/0xBober/datejar.git
cd datejar
uv sync
```

Create your `.env` from the template:

```bash
cp .env.example .env
```

Then edit `.env`:

- `ENVIRONMENT=dev`
- `SECRET_KEY`: generate one with
  ```bash
  uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  The app refuses to start with a key shorter than 32 characters.
- `DATABASE_URL` can stay as it is (`sqlite:///./datejar.db`).

Create the database and your first account:

```bash
uv run alembic upgrade head
uv run datejar create-user <username>
```

Start the app:

```bash
uv run uvicorn datejar.main:app --reload
```

Open <http://127.0.0.1:8000/healthz> or the API docs at <http://127.0.0.1:8000/docs> (dev mode only).

## Configuration

All settings are read from environment variables or a `.env` file in the working directory. See [`.env.example`](.env.example).

| Variable | Required | Description |
| --- | --- | --- |
| `ENVIRONMENT` | yes | `dev` or `prod`. In `prod`, `/docs`, `/redoc` and `/openapi.json` are disabled. |
| `SECRET_KEY` | yes | At least 32 characters. Use a different key per environment and never commit it. |
| `DATABASE_URL` | no | SQLite URL. Use four slashes for an absolute path: `sqlite:////var/lib/datejar/datejar.db`. |

## Managing users

There is no public sign-up. Accounts are created by whoever runs the server:

```bash
uv run datejar create-user <username>
uv run datejar set-password <username>
```

Usernames are lowercased and may contain `a-z`, `0-9`, `_` and `-` (2–32 characters). Passwords must be 8–64 characters and are entered without echo.

## Development

Run the same checks as CI:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Tests use an in-memory SQLite database and never touch your local `datejar.db`.

Database schema changes are done with Alembic migrations. See [`migrations/README.md`](migrations/README.md) for the workflow.

### Contributing

- Work on a branch and open a pull request. `main` is protected and CI must pass.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `ci:`).

## Deployment

DateJar is designed to run on a single Linux server behind a reverse proxy.

- [`deploy/datejar.service`](deploy/datejar.service): systemd unit running Uvicorn as an unprivileged user with sandboxing
- [`deploy/Caddyfile.example`](deploy/Caddyfile.example): Caddy reverse proxy template
- [`deploy/caddy-override.conf`](deploy/caddy-override.conf): systemd drop-in so Caddy waits for the network interface it binds to
- [`scripts/deploy.sh`](scripts/deploy.sh): pulls the latest code, syncs dependencies, backs up the database, runs migrations, restarts the service and checks `/healthz`

On the server, install dependencies with `uv sync --locked --no-dev` and set `ENVIRONMENT=prod`.

## License

[AGPL-3.0-or-later](LICENSE). You can use, modify and self-host DateJar freely. If you run a modified version as a service for others, you must publish your changes under the same license.
