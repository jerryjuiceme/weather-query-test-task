#!/usr/bin/env bash
# script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
# cd ..
cd "$(dirname "$0")/.."
echo "Creating first superuser"
uv run ./seed_superuser.py
