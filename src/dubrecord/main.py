import asyncio

from aiogram import Bot, Dispatcher

from dubrecord.dp import routers
from dubrecord.settings import ModeEnum, get_settings


def polling() -> None: 
    """
    Для запуска локально, если нет технической возвожности указать webhook. 
    Не позволяет использовать одну и туже логику на разных ботах.
    """
    async def start_polling() -> None:
        for router in routers:
            dp.include_router(router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    bot = Bot(get_settings().tg.token)
    dp = Dispatcher()

    asyncio.run(start_polling())

def webhook() -> None:
    """
    Для запуска когда имеется возможность указать webhook (рекомендуется).
    Позволяет использовать один и тот же функционал на разных ботах.
    """

def start() -> None:
    if get_settings().app.mode == ModeEnum.WEBHOOK:
        webhook()
    else:
        polling()

if __name__ == "__main__":
    start()