#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

echo "Starting Entrypoint"
echo "Waiting for postgres..."

until uv run python -c "
import asyncio, asyncpg, os, sys
async def check():
    try:
        conn = await asyncpg.connect(
            host=os.environ['APP_CONFIG__DB__HOST'],
            port=os.environ['APP_CONFIG__DB__PORT'],
            user=os.environ['APP_CONFIG__DB__USERNAME'],
            password=os.environ['APP_CONFIG__DB__PASSWORD'],
        )
        await conn.close()
    except Exception:
        sys.exit(1)
asyncio.run(check())
" 2>/dev/null; do
    sleep 1
done

echo "Postgres is ready"

echo "Running migrations..."
uv run alembic upgrade head



# ./seed/seed_migrations.sh
uv run ./seed_superuser.py

echo "Entrypoint finished"

exec "$@"