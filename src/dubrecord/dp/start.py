from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(F.chat.type.in_({"private"}), Command("start"))
async def start(message: Message) -> None:
    await message.reply("Теперь я буду тебя звать на записи:)")