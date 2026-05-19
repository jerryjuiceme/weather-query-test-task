# Weather Query — Test Task
[![Python 3.13](https://img.shields.io/badge/Python-3.12--3.13-000000?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Last Commit](https://img.shields.io/github/last-commit/jerryjuiceme/kafka-prefect-connector?style=for-the-badge&color=000000)](https://github.com/jerryjuiceme/weather-query-test-task/commits)

A simple web application that allows users to enter a city name, fetch current weather data from a public API (OpenWeatherMap), and store and display the query history using PostgreSQL. Built as a test assignment.

* * *

## Important / Disclaimer

**On authentication:** The assignment states **"The application must use PostgreSQL to store user queries**." Since storing and serving user-specific data without any access control is a security concern, I added JWT-based authentication and authorization layer using FastAPI Users. This way each user receives only their own data, and admins have full access.

**On AI assistance:** All core application code was written without AI assistance. Some help was used for seed/bash scripts, helping with this Readme.MD and minor refactoring moments. The overall architectural style is based on a personal boilerplate, custom implementations and snippets, and select open-source solutions, No AI agentic coding was used.

* * *

## Stack

| Area | Technology |
| --- | --- |
| Language | Python 3.13 |
| Dependency manager | UV  |
| Framework | FastAPI |
| Cache | Redis (Valkey) / redis.asyncio |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy + Asyncpg |
| Migrations | Alembic |
| HTTP client | HTTPX |
| Validation / DTOs / schemas | Pydantic |
| Logging | Structlog |
| Retry | Stamina |
| Rate limiting | Waygate |
| Containerization | Docker / Docker Compose |

* * *

## Quick Start

### Prerequisites

- [UV](https://docs.astral.sh/uv/) with Python 3.13
- Docker (Engine or Desktop)
- POSIX-compatible system (Linux / macOS)

All commands are managed via `Makefile`.

### Initialize the project

```sh
git clone https://github.com/jerryjuiceme/weather-query-test-task
cd weather-query-test-task

make init
```

The script will ask for your OpenWeatherMap API key. After that it initializes the project, creates a virtual environment, and generates a `.env` file.

### Run locally

```sh
make run
```

Runs the entrypoint script, applies database migrations, and creates a superuser (admin).

### Run in Docker (Preferred method!)

```sh
make run-in-docker
```

Starts the full application stack in an isolated Docker Compose network.

* * *

## API

Base URL: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

Admin panel: `http://localhost:8000/admin`

### Business logic URIs

| Method | URI | Description |
| --- | --- | --- |
| GET | `/api/v1/weather` | Returns weather data for a requested city and unit system |
| GET | `/api/v1/history` | Returns paginated query history for the authenticated user |
| GET | `/api/v1/history/export` | Streams a CSV file of the user's query history (with optional filters applied) |

Several endpoints for authentication and login are also available.

![API overview](static/api_overview.png)

### Authentication

JWT-based authentication using Bearer transport, implemented via FastAPI Users. Only `access_token` is used — no refresh tokens.

Every business logic endpoint requires authorization. To authenticate:

1.  Use the Swagger UI authorize button, or
2.  Send a `POST /api/v1/auth/login` request, receive the token, and attach it to subsequent requests:

```sh
-H 'Authorization: Bearer <token>'
```

To easy log-in please default superuser credentials (created automatically via entrypoint):

```
EMAIL=superadmin@gmail.com
PASSWORD=superadmin
```

![Swagger auth](static/swagger_auth.png)

### Health checks

2 probes are implemented for replica health monitoring `liveness` and`readiness` .

`GET /api/healthcheck/liveness` — confirms the application is responding:

```json
{
  "status": "healthy"
}
```

`GET /api/healthcheck/readiness` — checks all integrations. If any service is unavailable, the overall status returns `unhealthy`:

```json
{
  "status": "healthy",
  "service": [
    { "service": "db", "status": "healthy" },
    { "service": "redis", "status": "healthy" },
    { "service": "openweathermap", "status": "healthy" }
  ]
}
```

* * *

## Architecture

### Modularity

The application uses a layered architecture with the Repository pattern for data access abstraction and a service layer where the core business logic lives.

### Database

PostgreSQL 16 with SQLAlchemy as the ORM and Asyncpg as the driver. Migrations are managed by Alembic. Primary keys use UUID7. No additional transaction control beyond the standard SQLAlchemy session is required for this scope.

### Cache

Redis integration is implemented using `redis.asyncio` with a custom **abstract cache class** — making it easy to swap in alternative storage backends without affecting services. Cache is applied only in `src/services/http/weather.py` (the external weather API call), with a TTL of 5 minutes.

If Redis is unavailable at runtime, the request still succeeds by falling through to the external API. For tests, an `InMemoryCache` implementation is provided as an alternative.

Example response when data is served from cache:

```json
{
  "cityName": "Minsk",
  "temperature": 16.01,
  "description": "few clouds",
  "humidity": 83,
  "units": "metric",
  "isFromCache": true,
  "requested_at": "2026-05-19 17:04:15"
}
```

### Rate Limiting

The `GET /api/v1/weather` endpoint is rate-limited using [Waygate](https://attakay78.github.io/waygate/tutorial/rate-limiting/) with a Redis backend (to synchronize state across replicas). Strategy: per IP, 30 requests per minute. On limit breach the service responds with `429`:

```json
{
  "code": "string",
  "message": "string",
  "limit": 0,
  "retry_after_seconds": 0,
  "reset_at": "2026-05-19T17:04:15.463Z",
  "path": "string"
}
```

If Redis is unavailable at startup, the rate limiter falls back to an in-memory engine automatically.

### Logging

Structured centralized logging via Structlog, using a machine-readable `key=value` format. Context variables (request ID, method, path, route, client IP, user agent) are bound per-request via middleware and propagated through the entire call chain. Uvicorn and Gunicorn error logs are also wired into Structlog. External API response latency is logged separately in `src/services/http/weather.py`.

```python
async def per_request_middleware(request: Request, call_next):
    structlog.contextvars.clear_contextvars()

    request_id = str(uuid.uuid4())
    route = request.scope.get("route")
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        route=route.path if route else request.url.path,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
```

### External API

The OpenWeatherMap integration is implemented as a repository using HTTPX with a **persistent connection**, managed as a context manager in the application lifespan. The main `fetch_weather` method uses retry logic via Stamina (a batteries-included wrapper around Tenacity).

### Error Handling

In accordance with the layered architecture, an error hierarchy is implemented where exceptions are raised at the appropriate application layers. All raised errors and exceptions are caught by error handlers and processed at the service layer.

* * *

## Containerization

Dockerfile uses a **multi-stage build** producing two images: one for tests and one for production. The production image is approximately 380 MB after build.

* * *

## Testing

### Stack

Pytest, Polyfactory, TestContainers, `unittest.MagicMock`, Dirtyequals

### Test design

The project contains **102 tests** in total.

Repository tests and end-to-end API tests spin up real TestContainers for PostgreSQL and Redis. TestContainer fixtures are defined in `fixtures_testcontainer.py`. Service and business logic tests mock all repositories.

Run tests locally:

```sh
make test
```

Run tests inside an isolated Docker environment using a dedicated test image:

```sh
make test-in-docker
```

The test environment is controlled by the `TEST_ENV` variable (`CONTAINER` or `REAL`). If the databases are unreachable, tests that require a real connection are gracefully **skipped** (approximately 59 tests) rather than failing — useful at different CI pipeline stages.

* * *

## Extra: Admin Panel

[SQLAdmin](https://github.com/smithyhq/sqladmin) is connected for quick and convenient access to collected data and user records.

Login with the default superuser credentials:

```
EMAIL=superadmin@gmail.com
PASSWORD=superadmin
```

![Admin panel list](static/admin_panel_list.png)

![Admin panel detail](static/admin_panel_detail.png)

* * *

## Make Commands

| Command | Description |
| --- | --- |
| `make init` | Initialize the project: runs `seed/init.sh`, sets up environment and `.env` file |
| `make run` | Start Postgres and Redis in Docker, run entrypoint script locally, start the app |
| `make run-in-docker` | Start the full stack (including app) in Docker Compose |
| `make test` | Run the test suite locally with pytest and TestContainers |
| `make test-in-docker` | Run tests in an isolated Docker environment using the test image |
| `make up-docker` | Start only Postgres and Redis containers |
| `make migrate` | Apply Alembic migrations (`alembic upgrade head`) |
| `make seed-admin-user` | Apply migrations and seed the superuser |