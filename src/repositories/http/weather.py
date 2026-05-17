from typing import Any, Literal, Self

import httpx

from src.config import settings
import structlog

from src.exceptions import (
    CityNotFoundError,
    ExternalServiceError,
    InvalidApiKeyError,
    WeatherApiTimeoutError,
)
from src.schemas.weather import WeatherData

logger = structlog.get_logger()


class HttpRepository:
    _timeout = httpx.Timeout(connect=3.0, read=5.0, write=3.0, pool=2.0)

    def __init__(self) -> None:
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        if self.client is None:
            self.client = self.make_client()
        logger.info("OpenWeatherMap client created, httpx client started")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any | None,
    ) -> None:
        if self.client:
            await self.client.aclose()
        self.client = None
        logger.info("OpenWeatherMap client stopped, httpx client closed")
        return None

    def make_client(self) -> httpx.AsyncClient:
        transport = httpx.AsyncHTTPTransport(
            retries=settings.weather.retries,
            verify=settings.weather.verify,
        )
        return httpx.AsyncClient(
            base_url=settings.weather.host,
            transport=transport,
            timeout=self._timeout,
            headers={"Accept": "application/json"},
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=30.0,
            ),
        )

    ####################
    ### API requests ###
    ####################

    async def ping(self) -> bool:
        """
        Healthcheck for the API
        """
        try:
            assert self.client
            response = await self.client.get(
                "/weather",
                params={"q": "London", "appid": settings.weather.api_key},
                timeout=httpx.Timeout(connect=2.0, read=2.0, write=1.0, pool=1.0),
            )

            return response.status_code != 500
        except (httpx.TimeoutException, httpx.NetworkError):
            return False

    async def get_weather_by_city(
        self, city: str, units: Literal["metric", "imperial"] = "metric"
    ):
        assert self.client

        params = {"q": city, "appid": settings.weather.api_key, "units": units}
        try:
            response = await self.client.get("/weather", params=params)
            logger.info(
                "Get weather",
                status_code=response.status_code,
                city=city,
                units=units,
                url=response.url,
            )
        except httpx.TimeoutException as e:
            logger.warning("OpenWeatherMap timeout", city=city, exc_info=e)
            raise WeatherApiTimeoutError("Request timeout for '%s'", city) from e

        except httpx.NetworkError as e:
            logger.error("Network error for city", city=city, exc_info=e)
            raise ExternalServiceError(f"Network error: {e}") from e

        return self._parse_response(response, city, units)

    def _parse_response(
        self,
        response: httpx.Response,
        city: str,
        units: Literal["metric", "imperial"],
    ) -> WeatherData:

        if response.status_code == 200:
            return self._map_to_weather_data(response.json(), units)

        if response.status_code == 404:
            raise CityNotFoundError(f"City '{city}' not found")

        if response.status_code == 401:
            raise InvalidApiKeyError("Invalid OpenWeatherMap API key")

        if response.status_code == 429:
            raise ExternalServiceError("OpenWeatherMap rate limit exceeded")

        if response.status_code >= 500:
            raise ExternalServiceError(
                f"OpenWeatherMap service error: {response.status_code}"
            )

        logger.error(
            "Unexpected status from OpenWeatherMap",
            status_code=response.status_code,
            response_body=response.text[:200],
        )
        raise ExternalServiceError(f"Unexpected status: {response.status_code}")

    @staticmethod
    def _map_to_weather_data(
        resp_data: dict,
        units: Literal["metric", "imperial"],
    ) -> WeatherData:
        return WeatherData(
            city_name=resp_data["name"],
            temperature=resp_data["main"]["temp"],
            humidity=resp_data["main"]["humidity"],
            description=resp_data["weather"][0]["description"],
            units=units,
        )


# weather_repository = HttpRepository()
