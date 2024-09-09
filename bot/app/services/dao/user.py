from typing import List, Optional
from aiogram import types
from app.models import User
from app.services.dao.base import DAO


class UserDAO(DAO):
    async def get_user(self, chat_id: int = None, id: int = None, username: str = None) -> Optional[User]:
        return await self.api.get_users(id=id, chat_id=chat_id, username=username)

    async def get_users(self, ids: List[int] | None = None, limit: int = None, offset: int = None) -> Optional[List[User]]:
        return await self.api.get_users(limit=limit, offset=offset)

    async def create_user(
        self,
        chat_id: int,
        first_name: str,
        last_name: str,
        username: str,
        referrer: User = None
    ) -> User:
        referrer_id = referrer.id if referrer is not None else None
        user = await self.api.create_user(chat_id, first_name, last_name, username, referrer_id)
        return user

    async def create_user_if_not_exist(
        self,
        chat_id: int,
        first_name: str,
        last_name: str,
        username: str,
        referrer: User = None
    ) -> User:
        user = await self.get_user(chat_id=chat_id)

        if user is None:
            user = await self.create_user(
                chat_id=chat_id, first_name=first_name,
                last_name=last_name, username=username,
                referrer=referrer
            )
        return user

    async def set_language(self, user_id: int, language: str) -> bool:
        return await self.api.set_language(user_id, language)
