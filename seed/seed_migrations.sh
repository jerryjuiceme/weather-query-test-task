#!/usr/bin/env bash

echo "Starting migrations"
uv run alembic upgrade head
echo "Applied migrations successfully!"

