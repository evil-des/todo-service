import typing

from aiogram.filters import Filter
from aiogram.types import Message
from app.services.repo import Repo


class AdminFilter(Filter):
    async def __call__(self, message: Message, repo: Repo) -> bool:
        user = await repo.user_dao.get_user(chat_id=message.chat.id)
        is_admin = await repo.admin_dao.get_admin(user_id=user.id)

        if is_admin:
            return True

        return False
