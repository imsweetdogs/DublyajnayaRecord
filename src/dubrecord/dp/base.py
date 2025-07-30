from asyncio import gather

from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from dubrecord.settings import get_pyrogram_client, logger

router = Router()

def push_kb(title: str, url: str) -> None:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title,url=url)],
    ])

@router.message(F.chat.type.in_({"group", "supergroup"}), F.entities.mention)
async def push(message: Message) -> None:
    logger.debug(message.text)
    entities = [message.text[entity.offset:entity.offset + entity.length][1:] for entity in message.entities if entity.type == "mention"]
    async with get_pyrogram_client() as app:
        tasks = [app.resolve_peer(entity) for entity in entities]
        users = await gather(*tasks)
    link = await message.chat.create_invite_link()
    tasks = [
        message.bot.send_message(
            chat_id=user.user_id,
            text="Тебя зовут! Давай быстрее;)",
            reply_markup=push_kb(
                title=message.chat.title,
                url=link.invite_link,
            ),
        ) for user in users
    ]
    await gather(*tasks)
    await message.reply("Я позвал всех перечисленных")
