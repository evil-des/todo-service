import typing

from aiogram.filters import Filter
from aiogram.types import Message
from app.services.repo import Repo


class VerifiedFilter(Filter):
    async def __call__(self, message: Message, repo: Repo) -> bool:
        user = await repo.user_dao.get_user(chat_id=message.chat.id)

        return user.is_verified
