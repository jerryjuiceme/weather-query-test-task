#!/usr/bin/env bash

echo "Starting migrations"
alembic upgrade head
echo "Applied migrations successfully!"

