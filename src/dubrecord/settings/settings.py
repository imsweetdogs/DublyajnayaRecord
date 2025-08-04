from enum import Enum
from functools import lru_cache
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pyrogram import Client


class ModeEnum(Enum):
    POLLING = "polling"
    WEBHOOK = "webhook"

class TelegramConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="tg_") 
    token: str
    api_id: int
    api_hash: str

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_") 
    mode: ModeEnum
    host: str | None = None
    port: int = 8000

    @model_validator(mode="after")
    def check_webhook_data(self) -> Self:
        if self.mode != ModeEnum.WEBHOOK: 
            return self
        if not self.host: 
            raise ValueError("Webhook requires host url for set telegram webhook (https only). Port is optional (default 8000)")
        if not self.host.startswith("https://"): 
            raise ValueError("Webhook host must start with 'https://'")
        return self

class Settings(BaseSettings):
    tg: TelegramConfig = Field(default_factory=TelegramConfig)
    app: AppConfig = Field(default_factory=AppConfig)

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache(maxsize=5)
def get_pyrogram_client(token: str, app_id: int, api_hash: str) -> Client:
    return Client(
        "BOT",
        bot_token=token,
        api_id=app_id, 
        api_hash=api_hash,
    )