# Внешние зависимости
from typing import Type
from sqladmin import ModelView
from sqladmin.forms import Form
from wtforms import StringField
from wtforms.validators import ValidationError, DataRequired, Optional
# Внутренние модули
from models import User
from web_app.src.utils import get_password_hash


# Админка для User
class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
    ]

    column_labels = {
        User.id: "Идентификатор",
        User.full_name: "ФИО",
        User.username: "Имя пользователя",
        User.created_at: "Создан",
        User.updated_at: "Последние обновление",
        "password": "Пароль"
    }

    async def scaffold_form(self, form_type: str = None) -> Type[Form]:
        form_class = await super().scaffold_form(form_type)

        if "password" in form_type:
            if "optional_password" in form_type:
                validators = [Optional()]
            else:
                validators = [DataRequired()]

            form_class.password = StringField(
                label="Password",
                validators=validators
            )

        return form_class

    async def on_model_change(self, data, model, is_created, request):
        if "password" in data:
            password = data.pop("password", None)
            if is_created or password:
                if not password:
                    raise ValidationError("Пароль не записан")

                try:
                    data["password_hash"] = get_password_hash(password)

                except Exception as e:
                    raise ValidationError(f"Ошибка: {e}")

    column_searchable_list = [
        User.id,
        User.username,
    ] # список столбцов, которые можно искать
    column_sortable_list = [
        User.id
    ]  # список столбцов, которые можно сортировать

    column_default_sort = [(User.id, True)]

    form_create_rules = [
        "full_name",
        "username",
        "password"
    ]

    column_details_list = [
        User.id,
        User.full_name,
        User.username,
        User.created_at,
        User.updated_at
    ]

    form_edit_rules = [
        "full_name",
        "username",
        "password",
        "optional_token"
    ]

    can_create = True # право создавать
    can_edit = True # право редактировать
    can_delete = True # право удалять
    can_view_details = True # право смотреть всю информацию
    can_export = False # право экспортировать

    name = "Пользователь" # название
    name_plural = "Пользователи " # множественное название
    icon = "fa-solid fa-layer-group" # иконка
    category = "Пользователи" # категория
    category_icon = "fa-solid fa-list" # иконка категории

    page_size = 10
    page_size_options = [10, 25, 50, 100]