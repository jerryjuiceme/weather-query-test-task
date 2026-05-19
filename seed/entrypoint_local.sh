#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

echo "Starting Entrypoint"
echo "Waiting for postgres..."

until PGPASSWORD=$APP_CONFIG__DB__PASSWORD pg_isready \
    -h $APP_CONFIG__DB__HOST \
    -p $APP_CONFIG__DB__PORT \
    -U $APP_CONFIG__DB__USERNAME
do
    sleep 1
done
echo "Postgres is ready"

echo "Running migrations..."
uv run alembic upgrade head



# ./seed/seed_migrations.sh
uv run ./seed_superuser.py

echo "Entrypoint finished"

exec "$@"