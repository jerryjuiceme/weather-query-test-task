from fastapi import HTTPException, status


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


class UserAlreadyExistsException(ServiceHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Email already exists"


class UseCaseBaseError(ApplicationException):
    """Base class for use case errors"""

    ...


class SortingFieldsNotProvided(ApplicationException):
    detail = "Fields not provided"
