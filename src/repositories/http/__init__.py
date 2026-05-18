__all__ = ["HttpRepository", "get_weather_repo", "WeatherRepoDep"]
from typing import Annotated

from fastapi import Depends, Request

from .weather import HttpRepository


# --- Dependency for weather repository ---
def get_weather_repo(request: Request) -> HttpRepository:
    return request.app.state.weather_repo


WeatherRepoDep = Annotated[HttpRepository, Depends(get_weather_repo)]
