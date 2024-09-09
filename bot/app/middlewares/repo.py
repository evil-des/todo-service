from typing import Any, Awaitable, Callable, Dict

from aiocache import Cache
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.repo import Repo


class RepoMiddleware(BaseMiddleware):
    def __init__(self, cache: Cache):
        super().__init__()
        self.cache = cache

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["repo"] = Repo(
            cache=self.cache,
            todo_core=data.get("todo_core"),
            comments=data.get("comments")
        )
        return await handler(event, data)
