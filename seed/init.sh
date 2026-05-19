#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

echo "Initializing project"

# uv
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed."
    echo "Install: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# check .env.sample
if [ ! -f ".env.sample" ]; then
    echo "ERROR: .env.sample not found"
    exit 1
fi

# Copy .env from .env.sample
if [ ! -f ".env" ]; then
    cp .env.sample .env
    echo "Info: .env created from .env.sample"
else
    echo "Info: .env already exists"
fi

# request for API KEY
read -rp "Enter WEATHER API KEY: " WEATHER_API_KEY

# Secrets
RESET_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
VERIFICATION_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
APP_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

# update .env
sed -i.bak "s|^APP_CONFIG__WEATHER__API_KEY=.*|APP_CONFIG__WEATHER__API_KEY=${WEATHER_API_KEY}|" .env
sed -i.bak "s|^APP_CONFIG__ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET=.*|APP_CONFIG__ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET=${RESET_SECRET}|" .env
sed -i.bak "s|^APP_CONFIG__ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET=.*|APP_CONFIG__ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET=${VERIFICATION_SECRET}|" .env
sed -i.bak "s|^APP_CONFIG__SECRET_KEY=.*|APP_CONFIG__SECRET_KEY=${APP_SECRET}|" .env

rm -f .env.bak

echo "INFO: .env updated"

# Python 3.13 environment
echo "🐍 Creating Python 3.13 environment..."
uv venv --python 3.13

# Sync dependencies
echo "Info: Syncing dependencies..."
uv sync

echo ""
echo "SUCCESS: Project initialized successfully"
echo ""
echo "Activate venv:"
echo "source .venv/bin/activate"