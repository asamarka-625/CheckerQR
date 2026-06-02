# Внешние зависимости
from typing import Annotated, Optional
import re
from pydantic import BaseModel, Field, ConfigDict


# Схема участника мероприятия
class Participant(BaseModel):
    full_name: Annotated[str, Field(strict=True, min_length=1, max_length=128)]
    extra_info: Optional[Annotated[str, Field(strict=True)]]

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


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
