# Внешние зависимости
from typing import Annotated, List, Optional
from zoneinfo import ZoneInfo
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
# Внутренние модули
from web_app.src.schemas.participant import Participant


MSK = ZoneInfo("Europe/Moscow")


# Схема запроса на создание мероприятия
class CreateEventRequest(BaseModel):
    title: Annotated[str, Field(strict=True, min_length=1, max_length=128)]
    start_datetime: datetime
    end_datetime: datetime
    participants: List[Participant]
    access_users: List[int] = []

    @field_validator("participants")
    @classmethod
    def validate_participants(cls, v):

        if not v or len(v) < 1:
            raise ValueError("Должен быть хотя бы один участник")

        return v

    @field_validator("start_datetime", "end_datetime")
    @classmethod
    def set_msk_timezone(cls, v: datetime):
        if v.tzinfo is None:
            return v.replace(tzinfo=MSK)
        return v.astimezone(MSK)

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# Схема запроса на обновления информации мероприятия
class UpdateEventRequest(BaseModel):
    title: Optional[Annotated[str, Field(strict=True, max_length=128)]] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    access_users: Optional[List[int]] = None

    @field_validator("start_datetime", "end_datetime")
    @classmethod
    def set_msk_timezone(cls, v: Optional[datetime]):
        if v is not None:
            if v.tzinfo is None:
                return v.replace(tzinfo=MSK)
            return v.astimezone(MSK)

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# Схема запроса на добавление доступа пользователя к мероприятию
class AddAccessUserEventRequest(BaseModel):
    target_user_id: Annotated[int, Field(ge=1)]