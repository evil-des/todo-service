from datetime import datetime
from typing import List, Optional
from aiogram import types
from app.models import Task, Tag
from app.services.dao.base import DAO


class TagDAO(DAO):
    async def get_tag(self, id: int) -> Optional[Tag]:
        response = await self.todo_core.get("tags", item_id=id)
        if response:
            return Tag(**response)
        return None

    async def get_tags(self) -> Optional[List[Tag]]:
        response = await self.todo_core.get("tags")
        return [Tag(**item) for item in response if response]

    async def create_tag(self, name: str) -> Optional[Tag]:
        response = await self.todo_core.create(
            "tags",
            data={"name": name}
        )

        if response:
            return Tag(**response)
        return None
