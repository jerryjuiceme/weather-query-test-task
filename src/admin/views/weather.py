from sqladmin import ModelView
from src.repositories.crud.models import WeatherHistory
from src.repositories.crud.models import User
from sqladmin.filters import ForeignKeyFilter


class WeatherAdmin(ModelView, model=WeatherHistory):
    column_list = [
        WeatherHistory.city_name,
        WeatherHistory.temperature,
        WeatherHistory.created_at,
        WeatherHistory.description,
        WeatherHistory.humidity,
        WeatherHistory.units,
        WeatherHistory.is_from_cache,
    ] + [WeatherHistory.user]
    form_columns = [
        WeatherHistory.city_name,
        WeatherHistory.temperature,
        WeatherHistory.description,
        WeatherHistory.humidity,
        WeatherHistory.units,
        WeatherHistory.is_from_cache,
    ] + [WeatherHistory.user]

    column_filters = [
        # AllUniqueStringValuesFilter(column=WeatherHistory.user_id),
        ForeignKeyFilter(
            foreign_key=WeatherHistory.user_id,
            foreign_model=User,
            foreign_display_field=User.name,
            title="User",
        )
    ]
    column_searchable_list = [WeatherHistory.city_name, WeatherHistory.units]
    column_details_list = [
        WeatherHistory.temperature,
        WeatherHistory.description,
        WeatherHistory.created_at,
        WeatherHistory.humidity,
        WeatherHistory.user,
    ]
    column_formatters = {
        "created_at": lambda obj, _: obj.created_at.strftime("%d-%m-%Y  %H:%M"),
    }
    column_formatters_details = column_formatters
    column_sortable_list = [WeatherHistory.created_at]
    column_default_sort = [
        (WeatherHistory.created_at, False),
    ]
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "WeatherHistory"
    name_plural = "WeatherHistories"
    identity = "weather_history"
    icon = "fa-solid fa-note-sticky"
