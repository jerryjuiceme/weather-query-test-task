from fastapi_users.authentication import BearerTransport

from src.config import settings

bearer_transport = BearerTransport(
    # tokenUrl="api/v1/auth/login",
    tokenUrl=settings.api.bearer_token_url,
)
