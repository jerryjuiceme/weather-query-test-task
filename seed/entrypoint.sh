#!/usr/bin/env bash
# script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

echo "Starting Entrypoint"
chmod +x ./seed/seed_migrations.sh
chmod +x ./seed/seed_superuser.sh
seed/seed_migrations.sh
./seed/seed_superuser.sh

echo "Entrypoint finished"

exec "$@"