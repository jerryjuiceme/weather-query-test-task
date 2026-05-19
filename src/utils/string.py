"""
String utils module
"""

import re


def name_to_snake(file_name: str) -> str:
    """Convert a PascalCase, camelCase, or kebab-case string to snake_case."""
    snake = re.sub(
        r"([A-Z]+)([A-Z][a-z])", lambda m: f"{m.group(1)}_{m.group(2)}", file_name
    )
    snake = re.sub(r"([a-z])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    snake = re.sub(r"([0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    snake = re.sub(r"([a-z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    snake = snake.replace("-", "_")
    snake = snake.replace(" ", "_")

    return snake.lower()
