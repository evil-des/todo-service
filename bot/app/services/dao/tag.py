from datetime import datetime
from typing import List, Optional
from aiogram import types
from app.models import Task, Tag
from app.services.dao.base import DAO


class TagDAO(DAO):
    async def get_tag(self, id: int) -> Optional[Tag]:
        return await self.todo_core.get("tags", item_id=id)

    async def get_tags(self) -> Optional[List[Tag]]:
        return await self.todo_core.get("tasks")

    async def create_tag(self, name: str) -> Tag:
        tag = await self.todo_core.create(
            "tags",
            data={"name": name}
        )
        return tag
