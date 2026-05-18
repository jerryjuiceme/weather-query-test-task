from fastapi import HTTPException


class ApplicationException(Exception):
    """
    Base class for application exceptions.
    """

    def __init__(self, detail: str, *args: object) -> None:
        super().__init__(*args)
        self.detail = detail


class ServiceHTTPException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class SortingFieldsNotProvided(ApplicationException):
    detail = "Fields not provided"


class WeatherApiError(ApplicationException):
    """Base exception for the weather service."""


class CityNotFoundError(WeatherApiError):
    """City does not exist in OpenWeatherMap."""


class InvalidApiKeyError(WeatherApiError):
    """API key is missing or invalid."""


class WeatherApiTimeoutError(WeatherApiError):
    """Request to OpenWeatherMap timed out."""


class ExternalServiceError(WeatherApiError):
    """OpenWeatherMap returned 5xx or network-level error."""


class RateLimitError(WeatherApiError):
    """Per-IP rate limit exceeded."""
