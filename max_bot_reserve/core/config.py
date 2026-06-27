# Внешние зависимости
from typing import Optional
import logging
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Конфиг приложения
class Config(BaseSettings):
    MAX_BOT_TOKEN: str = Field(alias="MAX_BOT_TOKEN")
    USERNAME_MAX_BOT: str = Field(alias="USERNAME_MAX_BOT")
    
    PROXY: Optional[str] = Field(alias="PROXY")

    TABLE_WITH_UUID: str = Field(alias="TABLE_WITH_UUID")

    @field_validator("PROXY", mode="before")
    @classmethod
    def parse_none(cls, v):
        if isinstance(v, str) and v.lower() in ("none", "null", ""):
            return None
        return v

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def __str__(self) -> str:
        try:
            return f"Config(redis_url={self.redis_url})"
        except:
            return "Config(redis_url=unknown)"


    model_config = SettingsConfigDict(
        env_file=[".env.shared", ".env.max_bot_reserve"],
        env_file_encoding="utf-8",
        extra="ignore"
    )


cfg = Config()