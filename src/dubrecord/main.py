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
    try:
        from contextlib import asynccontextmanager
        from functools import lru_cache

        import uvicorn
        from aiogram import types
        from fastapi import APIRouter, FastAPI, Response
    except ImportError:
        raise ImportError("Webhook requires fastapi and uvicorn server") from None

    @asynccontextmanager
    async def lifespan(app: FastAPI): # noqa ANN202
        bot = Bot(get_settings().tg.token)
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(url=f"{get_settings().app.host}bot/{get_settings().tg.token}")
        yield

    @lru_cache
    def get_dp() -> Dispatcher:
        dp = Dispatcher()
        for router in routers:
            dp.include_router(router)
        return dp

    def get_router() -> APIRouter:
        router = APIRouter()

        @router.post("/bot/{token}")
        async def updates(token: str, update: dict) -> Response:
            update = types.Update(**update)
            bot = Bot(token)
            await get_dp().feed_update(bot, update)
        return router

    app = FastAPI(lifespan=lifespan)
    app.include_router(get_router())
    uvicorn.run(app, host="0.0.0.0", port=get_settings().app.port)

def start() -> None:
    if get_settings().app.mode == ModeEnum.WEBHOOK:
        webhook()
    else:
        polling()

if __name__ == "__main__":
    start()