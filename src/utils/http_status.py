"""
Module for parsing HTTP status codes for logging
"""

from http import HTTPStatus


def get_http_status(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).name
    except ValueError:
        return "UNKNOWN"


def get_http_status_group(status_code: int) -> str:
    if 100 <= status_code < 200:
        return "INFORMATIONAL"

    if 200 <= status_code < 300:
        return "SUCCESS"

    if 300 <= status_code < 400:
        return "REDIRECTION"

    if 400 <= status_code < 500:
        return "CLIENT_ERROR"

    if 500 <= status_code < 600:
        return "SERVER_ERROR"

    return "UNKNOWN"
