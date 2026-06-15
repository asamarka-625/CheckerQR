# Внешние зависимости
from typing import Annotated, Optional
import re
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Схема участника мероприятия
class Participant(BaseModel):
    full_name: Annotated[str, Field(strict=True, min_length=1, max_length=128)]
    extra_info: Optional[Annotated[str, Field(strict=True)]]
    phone: Annotated[str, Field(min_length=11, max_length=64)]

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        digits = "".join(ch for ch in v if ch.isdigit())

        if len(digits) == 11 and digits.startswith("8"):
            digits = "7" + digits[1:]

        if len(digits) != 11:
            raise ValueError("Phone must contain exactly 11 digits")

        if not digits.startswith("7"):
            raise ValueError("Phone must start with 7")

        return digits


# Схема запроса на добавление участника
class AddParticipantRequest(Participant):
    pass


# Схема запроса на обновление участника
class UpdateParticipantRequest(BaseModel):
    full_name: Optional[Annotated[str, Field(min_length=1, max_length=128)]] = None
    extra_info: Optional[Annotated[str, Field(strict=True)]] = None

    model_config = ConfigDict(
        str_strip_whitespace=True
    )
