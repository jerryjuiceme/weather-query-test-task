"""
String utils module
"""

import base64
import re
import string
from random import choice


def name_to_snake(file_name: str) -> str:
    """Convert a PascalCase, camelCase, or kebab-case string to snake_case.

    Args:
        camel: The string to convert.

    Returns:
        The converted string in snake_case.
    """
    # Handle the sequence of uppercase letters followed by a lowercase letter
    snake = re.sub(
        r"([A-Z]+)([A-Z][a-z])", lambda m: f"{m.group(1)}_{m.group(2)}", file_name
    )
    # Insert an underscore between a lowercase letter and an uppercase letter
    snake = re.sub(r"([a-z])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a digit and an uppercase letter
    snake = re.sub(r"([0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a lowercase letter and a digit
    snake = re.sub(r"([a-z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Replace hyphens with underscores to handle kebab-case
    snake = snake.replace("-", "_")
    snake = snake.replace(" ", "_")

    return snake.lower()


def make_random_string(size: int) -> str:
    """
    Create a random string.
    """
    return "".join(choice(string.ascii_letters + string.digits) for _ in range(size))


def encode_base64(raw_value: str) -> str:
    """
    Encode a string to base64.
    """
    return base64.b64encode(raw_value.encode()).decode()


def decode_base64(value: str) -> str:
    """
    Decode a base64 string.
    """
    return base64.b64decode(value).decode()


def str_to_bool(value: str) -> bool:
    """
    Convert a string to a boolean value.
    """
    true_set = {"yes", "true", "t", "y", "1"}
    false_set = {"no", "false", "f", "n", "0"}

    value = value.lower()
    if value in true_set:
        return True
    if value in false_set:
        return False
    raise ValueError('Expected "%s"' % '", "'.join(true_set | false_set))
