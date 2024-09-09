import abc

from aiocache import Cache
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.api import API


class DAO(abc.ABC):
    session: AsyncSession

    def __init__(self, api: API, cache: Cache | None = None):
        self.api = api
        self.cache = cache
