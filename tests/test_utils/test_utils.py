from src.utils import name_to_snake, get_http_status, get_http_status_group

import pytest


def test_name_to_snake() -> None:
    """
    Test the `name_to_snake` function.
    """
    assert name_to_snake("HelloWorld") == "hello_world"
    assert name_to_snake("helloWorld") == "hello_world"
    assert name_to_snake("hello-world") == "hello_world"
    assert name_to_snake("HelloWorld") == "hello_world"
    assert name_to_snake("helloWorld") == "hello_world"
    assert name_to_snake("hello-world") == "hello_world"


def test_get_http_status_known_codes() -> None:
    assert get_http_status(200) == "OK"
    assert get_http_status(201) == "CREATED"
    assert get_http_status(301) == "MOVED_PERMANENTLY"
    assert get_http_status(400) == "BAD_REQUEST"
    assert get_http_status(401) == "UNAUTHORIZED"
    assert get_http_status(403) == "FORBIDDEN"
    assert get_http_status(404) == "NOT_FOUND"
    assert get_http_status(422) == "UNPROCESSABLE_CONTENT"
    assert get_http_status(500) == "INTERNAL_SERVER_ERROR"
    assert get_http_status(503) == "SERVICE_UNAVAILABLE"


def test_get_http_status_unknown_code() -> None:
    assert get_http_status(999) == "UNKNOWN"
    assert get_http_status(0) == "UNKNOWN"
    assert get_http_status(600) == "UNKNOWN"


@pytest.mark.parametrize("code", [100, 101, 199])
def test_get_http_status_group_informational(code: int) -> None:
    assert get_http_status_group(code) == "INFORMATIONAL"


@pytest.mark.parametrize("code", [200, 201, 204, 299])
def test_get_http_status_group_success(code: int) -> None:
    assert get_http_status_group(code) == "SUCCESS"


@pytest.mark.parametrize("code", [301, 302, 304, 399])
def test_get_http_status_group_redirection(code: int) -> None:
    assert get_http_status_group(code) == "REDIRECTION"


@pytest.mark.parametrize("code", [400, 401, 403, 404, 422, 499])
def test_get_http_status_group_client_error(code: int) -> None:
    assert get_http_status_group(code) == "CLIENT_ERROR"


@pytest.mark.parametrize("code", [500, 502, 503, 599])
def test_get_http_status_group_server_error(code: int) -> None:
    assert get_http_status_group(code) == "SERVER_ERROR"


@pytest.mark.parametrize("code", [0, 99, 600, 999])
def test_get_http_status_group_unknown(code: int) -> None:
    assert get_http_status_group(code) == "UNKNOWN"
