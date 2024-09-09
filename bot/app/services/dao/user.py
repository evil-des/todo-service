from typing import List, Optional
from aiogram import types
from app.models import TelegramUser
from app.services.dao.base import DAO


class TelegramUserDAO(DAO):
    async def get_user(self, chat_id: int = None, id: int = None, username: str = None) -> Optional[TelegramUser]:
        params = {}

        if chat_id:
            params["chat_id"] = chat_id
        if username:
            params["username"] = username

        return await self.todo_core.get(
            "telegram_users",
            item_id=id,
            params=params
        )

    async def get_users(self) -> Optional[List[TelegramUser]]:
        return await self.todo_core.get("telegram_users")

    async def create_user(
        self,
        chat_id: int,
        first_name: str,
        last_name: str,
        username: str
    ) -> TelegramUser:
        user = await self.todo_core.create(
            "telegram_users",
            {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "username": username}
        )
        return user

    async def create_user_if_not_exist(
        self,
        chat_id: int,
        first_name: str,
        last_name: str,
        username: str
    ) -> TelegramUser:
        user = await self.get_user(chat_id=chat_id)

        if user is None:
            user = await self.create_user(
                chat_id=chat_id, first_name=first_name,
                last_name=last_name, username=username,
            )
        return user

    async def set_language(self, user_id: int, language: str) -> bool:
        return await self.todo_core.update(
            "telegram_users",
            item_id=user_id,
            data={"language": language}
        )
