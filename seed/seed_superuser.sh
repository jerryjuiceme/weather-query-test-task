#!/usr/bin/env bash
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
# cd ..
echo "Creating first superuser"
python ./seed_superuser.py
