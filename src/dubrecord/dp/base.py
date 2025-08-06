import asyncio
import re

from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import Client, types

from dubrecord.settings import get_pyrogram_client, get_settings, logger

router = Router()

def push_kb(title: str, url: str) -> None:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title,url=url)],
    ])

async def resolver(app: Client, semaphore: asyncio.Semaphore, username: str) -> types.User:
    async with semaphore:
        return await app.resolve_peer(username)

async def pusher(message: Message, semaphore: asyncio.Semaphore, user: int, invite_link: str) -> Message:
    async with semaphore:
        return await message.bot.send_message(
            chat_id=user.user_id,
            text="Тебя зовут! Давай быстрее;)",
            reply_markup=push_kb(
                title=message.chat.title,
                url=invite_link,
            ),
        )

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def push(message: Message) -> None:
    pattern = r"@([A-Za-z0-9_]+)"
    usernames = re.findall(pattern, message.text)
    if usernames is None:
        return

    semaphore = asyncio.Semaphore(5)
    async with get_pyrogram_client(
        get_settings().tg.token, get_settings().tg.api_id, get_settings().tg.api_hash) as app:
        tasks = [resolver(app, semaphore, username) for username in usernames]
        users = await asyncio.gather(*tasks, return_exceptions=True)
    logger.debug(f"{usernames}\n\n{users}")
    link = await message.chat.create_invite_link()
    tasks = [pusher(message, semaphore, user, link.invite_link) for user in users]
    messages = await asyncio.gather(*tasks, return_exceptions=True)

    not_pushed = []
    for index, value in enumerate(messages):
        if isinstance(value, BaseException):
            not_pushed.append(users[index])
    await message.bot.send_message(
        message.from_user.id, 
        f"Вы упомянули пользователя/пользователей пушнул всех кого мог.\nНе смог позвать следующих:{','.join(not_pushed)}\nПерейти в чат можно по кнопке", # noqa E501
        reply_markup=push_kb(
            title=message.chat.title,
            url=link.invite_link,
        ),
    )
    