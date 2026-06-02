# Внешние зависимости
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


# Схема пользователя
class UserScheme(BaseModel):
    id: Annotated[int, Field(ge=1)]
    full_name: Annotated[str, Field(max_length=128)]

    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True
    )