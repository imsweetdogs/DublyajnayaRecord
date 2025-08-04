from aiogram import Bot, Dispatcher

from dubrecord.dp import routers
from dubrecord.settings import get_settings, logger


def polling() -> None:
    """
    Для запуска локально, если нет технической возвожности указать webhook. 
    Не позволяет использовать одну и туже логику на разных ботах.
    """
    async def start_polling() -> None:
        for router in routers:
            dp.include_router(router)
        await dp.start_polling(bot)

    bot = Bot(get_settings().tg.token)
    dp = Dispatcher()

    try:
        import uvloop
        logger.debug("Optimization uvloop imported. It's very Nice!")
        uvloop.run(start_polling())
    except ImportError:
        import asyncio
        logger.debug("Uvloop not found... Press F. Used base asyncio.")
        asyncio.run(start_polling())