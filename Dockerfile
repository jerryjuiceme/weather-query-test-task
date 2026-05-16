FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.28 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Use a builder to install test dependencies
FROM builder AS test-builder

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen  --group dev

# Use a slim Python image for the tests
FROM python:3.13-slim AS test

WORKDIR /app

COPY --from=test-builder /app /app
COPY --from=test-builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    TEST_ENV_REAL=REAL \
    APP_CONFIG__ENV=TEST

CMD ["pytest", "-v"]

# Use a slim Python image for the final application
FROM python:3.13-slim AS prod

WORKDIR /app


COPY --from=builder /app /app
COPY --from=builder /app/.venv /app/.venv

RUN chmod +x ./seed/entrypoint.sh
ENTRYPOINT [ "./seed/entrypoint.sh" ]

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 

EXPOSE 8000

CMD ["python", "-m", "gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]