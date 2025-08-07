import asyncio

from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import Client
from pyrogram.raw.types import InputPeerUser

from dubrecord.filters import MentionFilter
from dubrecord.settings import get_pyrogram_client, get_settings

router = Router()

def push_kb(title: str, url: str) -> None:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title,url=url)],
    ])

async def resolver(app: Client, semaphore: asyncio.Semaphore, username: str) -> InputPeerUser:
    async with semaphore:
        user = await app.resolve_peer(username)
        return user.user_id

async def pusher(message: Message, semaphore: asyncio.Semaphore, user_id: int, invite_link: str) -> Message:
    async with semaphore:
        return await message.bot.send_message(
            chat_id=user_id,
            text="Тебя зовут! Давай быстрее;)",
            reply_markup=push_kb(
                title=message.chat.title,
                url=invite_link,
            ),
        )

@router.message(F.chat.type.in_({"group", "supergroup"}), MentionFilter())
async def push(message: Message, mentions: list) -> None:
    semaphore = asyncio.Semaphore(5)
    async with get_pyrogram_client(
        get_settings().tg.token, get_settings().tg.api_id, get_settings().tg.api_hash) as app:
        tasks = [resolver(app, semaphore, username) for username in mentions]
        users_ids = await asyncio.gather(*tasks, return_exceptions=True)
    users = [[user_id, username] for user_id, username in zip(users_ids, mentions) if user_id != message.from_user.id]

    link = await message.chat.create_invite_link()
    tasks = [pusher(message, semaphore, user[0], link.invite_link) for user in users]
    messages = await asyncio.gather(*tasks, return_exceptions=True)

    not_pushed = []
    for index, value in enumerate(messages):
        if isinstance(value, BaseException):
            not_pushed.append(users[index][1])
    if not_pushed:
        await message.bot.send_message(
            message.from_user.id, 
            f"Вы упомянули пользователя/пользователей пушнул всех кого мог.\nНе смог позвать следующих:{','.join(not_pushed)}\nПерейти в чат можно по кнопке", # noqa E501
            reply_markup=push_kb(
                title=message.chat.title,
                url=link.invite_link,
            ),
        )
    