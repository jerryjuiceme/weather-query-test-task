from typing import Iterable
import io
import csv

from src.schemas.weather import WeatherOutputMessage


def parse_to_csv(items: list[WeatherOutputMessage]) -> Iterable[str]:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=items[0].model_dump().keys())
    writer.writeheader()
    writer.writerows([item.model_dump() for item in items])
    buffer.seek(0)
    return iter([buffer.getvalue()])
