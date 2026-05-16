from fastapi_users.authentication import AuthenticationBackend
from src.authentication.transport import bearer_transport
from .strategy import app_strategy


strategy = app_strategy.make_a_strategy()

authentication_backend = AuthenticationBackend(
    name=app_strategy.name,
    transport=bearer_transport,
    get_strategy=strategy,
)
