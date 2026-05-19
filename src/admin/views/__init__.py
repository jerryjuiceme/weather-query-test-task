from sqladmin import Admin

from src.admin.views.user import UserAdmin
from src.admin.views.weather import WeatherAdmin


def register_admin_views(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(WeatherAdmin)
