from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from app.services.internal.comments import CommentsCRUD
from app.services.internal.core import TODOCore


class InternalServicesMiddleware(BaseMiddleware):
    def __init__(self, todo_core_base: str, comments_base: str):
        super().__init__()
        self.todo_core_base = todo_core_base
        self.comments_base = comments_base

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["todo_core"] = TODOCore(self.todo_core_base)
        data["comments"] = CommentsCRUD(self.comments_base)
        return await handler(event, data)
