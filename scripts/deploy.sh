#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/datejar
APP_USER=datejar
SERVICE=datejar
DATABASE_PATH=/var/lib/datejar/datejar.db
BACKUP_DIR=/var/lib/datejar/backups

echo "==> Pulling Latest Code"
sudo -H -u "$APP_USER" git -C "$APP_DIR" pull --ff-only

echo "==> Running UV Sync"
sudo -H -u "$APP_USER" uv --directory "$APP_DIR" sync --locked --no-dev

echo "==> Backing up database"
sudo -u "$APP_USER" mkdir -p "$BACKUP_DIR"
sudo -u "$APP_USER" sqlite3 "$DATABASE_PATH" ".backup '$BACKUP_DIR/$(date +%Y%m%d-%H%M%S)-datejar.db'"

echo "==> Migrating Database"
sudo -H -u "$APP_USER" sh -c "cd '$APP_DIR' && .venv/bin/alembic upgrade head"

echo "==> Restarting '$SERVICE' Service"
sudo systemctl restart "$SERVICE"

echo "==> Testing healthz endpoint"
curl http://127.0.0.1:8000/healthz --fail --silent --retry 5 --retry-delay 2 --retry-connrefused --output /dev/null

echo "Deploy Successful"
