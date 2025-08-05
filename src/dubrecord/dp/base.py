import asyncio

from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from dubrecord.filters import MentionFilter
from dubrecord.settings import get_pyrogram_client, get_settings, logger

router = Router()

def push_kb(title: str, url: str) -> None:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title,url=url)],
    ])

async def resolver(entity: str, semaphore: asyncio.Semaphore) -> list:
    async with semaphore:
        logger.debug(f"resolver {entity}")
        async with get_pyrogram_client(
                get_settings().tg.token, 
                get_settings().tg.api_id,
                get_settings().tg.api_hash) as app:
            return await app.resolve_peer(entity)

async def pusher(user: int, message: Message, link: str, semaphore: asyncio.Semaphore) -> list:
    async with semaphore:
        return await message.bot.send_message(
            chat_id=user.user_id,
            text="Тебя зовут! Давай быстрее;)",
            reply_markup=push_kb(
                title=message.chat.title,
                url=link,
            ),
        )

@router.message(F.chat.type.in_({"group", "supergroup"}), MentionFilter())
async def push(message: Message) -> None:
    logger.debug(message.text)
    entities = [message.text[entity.offset:entity.offset + entity.length] for entity in message.entities if entity.type == "mention"]
    logger.debug(f"entities")
    semaphore = asyncio.Semaphore(5)
    tasks = [resolver(entity, semaphore) for entity in entities]
    users = await asyncio.gather(*tasks, return_exceptions=True)
    link = await message.chat.create_invite_link()
    tasks = [pusher(user, message, link.invite_link, semaphore) for user in users]
    messages = await asyncio.gather(*tasks, return_exceptions=True)
    not_pushed = []
    for index, value in enumerate(messages):
        if isinstance(value, BaseException):
            not_pushed.append(entities[index])
    await message.bot.send_message(
        message.from_user.id, 
        f"Вы упомянули пользователя/пользователей пушнул всех кого мог.\nНе смог позвать следующих:{','.join(not_pushed)}\nПерейти в чат можно по кнопке", 
        reply_markup=push_kb(
            title=message.chat.title,
            url=link.invite_link
        )
    )
    