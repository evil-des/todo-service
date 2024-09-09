from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Any, Dict

from fastapi import Depends
from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.dependencies import get_db_session
from api.db.models.comments import CommentModel
from api.settings import settings
from api.services.todo_core.crud import TodoCoreCRUD
from api.services.todo_core.dependency import get_todo_core_crud
from redis.asyncio import ConnectionPool, Redis
from api.services.redis.dependency import get_redis_pool
import json


class CommentDAO:
    """Class for accessing comments table."""
    CACHE_EXPIRE = timedelta(hours=2)

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        todo_core: TodoCoreCRUD = Depends(get_todo_core_crud),
        redis_pool: ConnectionPool = Depends(get_redis_pool)
    ):
        self.session = session
        self.todo_core = todo_core
        self.redis_pool = redis_pool

    async def get_cached_data(self, key: str) -> Any | None:
        async with Redis(connection_pool=self.redis_pool) as redis:
            cached_data = await redis.get(key)

        return json.loads(cached_data) if cached_data else None

    async def set_cached_data(self, key: str, value: Any) -> None:
        async with Redis(connection_pool=self.redis_pool) as redis:
            await redis.set(key, json.dumps(value), ex=self.CACHE_EXPIRE)

    async def get_task(self, task_id: int) -> Dict | None:
        task = await self.get_cached_data(f"tasks:{task_id}")
        if not task:
            task = await self.todo_core.get("tasks", item_id=task_id)
            await self.set_cached_data(f"tasks:{task_id}", task)
        return task

    async def get_tasks(self, telegram_chat_id: Optional[int] = None) -> List[Any] | None:
        tasks = await self.get_cached_data(f"tasks_telegram_chat_id:{telegram_chat_id}")
        if not tasks:
            tasks = await self.todo_core.get(
                "tasks",
                params={"telegram_chat_id": telegram_chat_id}
            )
            if not tasks:
                return []

            await self.set_cached_data(f"tasks_telegram_chat_id:{telegram_chat_id}", tasks)
        return tasks

    async def create_comment(
        self,
        task_id: int,
        content: str,
    ) -> CommentModel | None:
        task = await self.get_task(task_id)
        if not task:
            return None

        comment = CommentModel(
            task_id=task_id,
            content=content
        )
        self.session.add(comment)

        try:
            await self.session.commit()
            return comment
        except IntegrityError:
            await self.session.rollback()
            return None

    async def get_comment(self, id: int = None) -> CommentModel | None:
        if id is None:
            return None

        query = select(CommentModel)
        if id:
            query = query.where(CommentModel.id == id)

        res = await self.session.execute(query)
        return res.scalars().first()

    async def get_all_comments(self, limit: int = None, offset: int = None) -> List[CommentModel]:
        """
        Get all comments with limit/offset pagination.
        """
        q = select(CommentModel).order_by(CommentModel.id)

        if limit and offset:
            q = select(CommentModel).limit(limit).offset(offset)

        raw_items = await self.session.execute(q)
        return list(raw_items.scalars().fetchall())

    async def filtered_comments(
        self,
        content: Optional[str] = None,
        posted_date: Optional[datetime] = None,
        telegram_chat_id: Optional[int] = None
    ) -> List[CommentModel]:
        query = select(CommentModel)

        if telegram_chat_id:
            tasks = await self.get_tasks(telegram_chat_id)
            if tasks:
                query = query.where(CommentModel.task_id.in_([item["id"] for item in tasks]))

        if content:
            key_word = content.lower()
            query = query.where(CommentModel.content.ilike("%" + key_word + "%+"))

        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
