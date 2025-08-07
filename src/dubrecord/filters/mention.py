import re

from aiogram.filters import Filter
from aiogram.types import Message


class MentionFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        pattern = r"@([A-Za-z0-9_.]+)(?=\s|$)"
        if res := re.findall(pattern, message.text):
            return {"mentions": res}
        return False