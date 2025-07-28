from functools import lru_cache

from pyrogram import Client

from dubrecord.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_pyrogram_client() -> Client:
    return Client(
        "BOT",
        bot_token=get_settings().tg.token,
        api_id=get_settings().tg.api_id, 
        api_hash=get_settings().tg.api_hash,
    )