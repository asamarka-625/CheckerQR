from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from shared_services import generate_code, is_valid_code


class Participant(BaseModel):
    full_name: Annotated[str, Field(strict=True, min_length=1, max_length=128)]
    extra_info: Optional[str] = Field(default="")
    code: Optional[str] = Field(default=None, max_length=9)

    # ВАЖНО: прогоняем валидаторы и для значений по умолчанию,
    # иначе при отсутствии code в запросе он останется None
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_default=True
    )

    @field_validator("extra_info", mode="before")
    @classmethod
    def normalize_extra_info(cls, v):
        # None -> "", чтобы Redis не падал на NoneType
        return v or ""

    @field_validator("code", mode="before")
    @classmethod
    def ensure_code(cls, v):
        # валиден -> используем как есть; иначе генерируем
        if isinstance(v, str) and is_valid_code(v):
            return v.strip().upper()
        return generate_code()


class AddParticipantRequest(Participant):
    pass


class UpdateParticipantRequest(BaseModel):
    full_name: Optional[Annotated[str, Field(min_length=1, max_length=128)]] = None
    extra_info: Optional[Annotated[str, Field(strict=True)]] = None

    model_config = ConfigDict(str_strip_whitespace=True)