from aiogram.filters import Filter
from aiogram.types import Message


class MentionFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    return True
        return False