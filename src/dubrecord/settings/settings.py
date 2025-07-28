from enum import Enum
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModeEnum(Enum):
    POLLING = "polling"
    WEBHOOK = "webhook"

class TelegramConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="tg_") 
    token: str
    api_id: str
    api_hash: str

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_") 
    mode: ModeEnum
    host: str | None = None
    port: int = 8000

    @model_validator(mode="after")
    def check_webhook_data(self) -> Self:
        if self.mode == ModeEnum.WEBHOOK and self.host is None:
            raise ValueError("Webhook requires host url for set telegram webhook (https only). Port is optional (default 8000)")
        return self

class Settings(BaseSettings):
    tg: TelegramConfig = Field(default_factory=TelegramConfig)
    app: AppConfig = Field(default_factory=AppConfig)