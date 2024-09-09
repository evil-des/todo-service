import abc

from aiocache import Cache
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.internal import CommentsCRUD, TODOCore


class DAO(abc.ABC):
    session: AsyncSession

    def __init__(self, todo_core: TODOCore, comments: CommentsCRUD, cache: Cache | None = None):
        self.todo_core = todo_core
        self.comments = comments
        self.cache = cache
