from fastapi_users.password import PasswordHelper
from sqladmin import ModelView
from starlette.requests import Request
from src.repositories.crud.models.user import User
from sqladmin.filters import (
    BooleanFilter,
)

password_helper = PasswordHelper()


class UserAdmin(ModelView, model=User):
    column_list = [  # type: ignore
        User.name,
        User.email,
        User.family_name,
        User.hashed_password,
        User.given_name,
        User.preferred_username,
        User.is_active,
        User.is_superuser,
        User.is_verified,
        User.updated_at,
        User.created_at,
    ]
    form_columns = [c.name for c in User.__table__.c] + [User.weather_history]

    form_create_rules = [
        "name",
        "email",
        "hashed_password",
        "preferred_username",
        "given_name",
        "family_name",
        "is_active",
        "is_superuser",
        "is_verified",
    ]
    form_edit_rules = [
        "name",
        "email",
        "hashed_password",
        "preferred_username",
        "given_name",
        "family_name",
        "is_active",
        "is_superuser",
        "is_verified",
        # "notes",
    ]
    column_labels = {
        User.hashed_password: "Password",
    }

    column_filters = [
        BooleanFilter(column=User.is_active),  # type: ignore
        BooleanFilter(column=User.is_superuser),  # type: ignore
        BooleanFilter(column=User.is_verified),  # type: ignore
    ]

    column_formatters = {
        "hashed_password": lambda obj, _: "***",
        "updated_at": lambda obj, _: obj.updated_at.strftime("%d-%m-%Y  %H:%M"),
        "created_at": lambda obj, _: obj.created_at.strftime("%d-%m-%Y  %H:%M"),
    }
    column_formatters_details = {
        "hashed_password": lambda obj, _: "***" if obj.hashed_password else "***",
        "updated_at": lambda obj, _: obj.updated_at.strftime("%d-%m-%Y  %H:%M"),
        "created_at": lambda obj, _: obj.created_at.strftime("%d-%m-%Y  %H:%M"),
    }
    column_details_list = [  # type: ignore
        User.name,
        User.email,
        User.family_name,
        # User.hashed_password,
        User.given_name,
        User.preferred_username,
        User.is_active,
        User.is_superuser,
        User.is_verified,
        User.updated_at,
        User.created_at,
    ]
    column_sortable_list = [User.created_at, User.updated_at]
    column_searchable_list = [User.name, User.email]
    column_default_sort = [(User.created_at, False)]
    use_pretty_export = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    async def on_model_change(
        self,
        data: dict,
        model: User,
        is_created: bool,
        request: Request,
    ) -> None:
        """
        :param data:
        :param model:
        :param is_created:
        :param request:
        :return:
        """
        # data may contain not hashed password
        raw_password = data.get("hashed_password") or password_helper.generate()
        if is_created or model.hashed_password != raw_password:
            data.update(hashed_password=password_helper.hash(raw_password))
