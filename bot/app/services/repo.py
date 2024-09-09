from aiocache import Cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.dao import TelegramUserDAO
from app.services.internal.comments import CommentsCRUD
from app.services.internal.core import TODOCore


class Repo:
    def __init__(self, todo_core: TODOCore, comments: CommentsCRUD, cache: Cache = None):
        self.user_dao = TelegramUserDAO(todo_core=todo_core, comments=comments)
