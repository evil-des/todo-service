from datetime import datetime
from typing import List, Optional
from aiogram import types
from app.models import Task
from app.services.dao.base import DAO


class TaskDAO(DAO):
    async def get_task(self, id: int) -> Optional[Task]:
        response = await self.todo_core.get("tasks", item_id=id)
        if response:
            return Task(**response)
        return None

    async def get_tasks(
        self,
        telegram_chat_id: Optional[int] = None,
        completed: Optional[bool] = None,
        tags_ids: Optional[List[int]] = None
    ) -> Optional[List[Task]]:
        params = {}

        if telegram_chat_id:
            params["telegram_chat_id"] = telegram_chat_id
        if completed is not None:
            params["completed"] = completed
        if tags_ids:
            params["tags_ids"] = ",".join(map(str, tags_ids))

        response = await self.todo_core.get("tasks", params=params)
        return [Task(**item) for item in response if response]

    async def create_task(
        self,
        telegram_user_id: int,
        title: str,
        description: str,
        completed: bool,
        tags: Optional[List[int]] = None,
        remind_time: Optional[datetime] = None,
    ) -> Optional[Task]:
        if tags is None:
            tags = []

        response = await self.todo_core.create(
            "tasks",
            data={
                "telegram_user": telegram_user_id,
                "title": title,
                "description": description,
                "completed": completed,
                "tags": tags,
                "remind_time": str(remind_time)
            }
        )

        if response:
            return Task(**response)
        return None
