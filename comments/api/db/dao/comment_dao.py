from datetime import datetime
from typing import List, Optional, Tuple

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


class CommentDAO:
    """Class for accessing comments table."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        todo_core: TodoCoreCRUD = Depends(get_todo_core_crud)
    ):
        self.session = session
        self.todo_core = todo_core

    async def create_comment(
        self,
        task_id: int,
        content: str,
    ) -> CommentModel | None:
        task = await self.todo_core.get("tasks", item_id=task_id)
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
            tasks = await self.todo_core.get(
                "tasks",
                params={"telegram_chat_id": telegram_chat_id}
            )
            query = query.where(CommentModel.task_id.in_([item["id"] for item in tasks]))

        if content:
            key_word = content.lower()
            query = query.where(CommentModel.content.ilike("%" + key_word + "%+"))

        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
