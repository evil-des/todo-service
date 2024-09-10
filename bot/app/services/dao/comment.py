from datetime import datetime
from typing import List, Optional
from aiogram import types
from app.models import Task, Tag, Comment
from app.services.dao.base import DAO


class CommentDAO(DAO):
    async def get_comment(self, id: int) -> Optional[Comment]:
        response = await self.todo_core.get("tags", item_id=id)
        if response:
            return Comment(**response)
        return None

    async def get_comments(self) -> Optional[List[Comment]]:
        response = await self.todo_core.get("tags")
        return [Comment(**item) for item in response if response]

    async def create_comment(self, task_id: int, content: str) -> Optional[Comment]:
        response = await self.comments.create(
            "comments",
            data={"task_id": task_id, "content": content}
        )

        if response:
            return Comment(**response)
        return None
