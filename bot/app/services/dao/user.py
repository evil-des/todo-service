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

        response: dict = await self.todo_core.get(
            "telegram_users",
            item_id=id,
            params=params
        )

        if response and all([not item for item in response.values()]):
            print("test")
            print(response)
            return None

        return TelegramUser(**response)

    async def get_users(self) -> Optional[List[TelegramUser]]:
        response = await self.todo_core.get("telegram_users")
        return [TelegramUser(**item) for item in response if response]

    async def create_user(
        self,
        chat_id: int,
        first_name: str,
        last_name: str,
        username: str
    ) -> TelegramUser:
        response = await self.todo_core.create(
            "telegram_users",
            {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "username": username}
        )
        return TelegramUser(**response)

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

    async def set_language(self, user_id: int, language: str) -> TelegramUser:
        response = await self.todo_core.patch(
            "telegram_users",
            item_id=user_id,
            data={"language": language}
        )
        return TelegramUser(**response)
