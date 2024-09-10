from datetime import datetime
from typing import List, Optional

from .base import BaseModel
from .user import TelegramUser


class Tag(BaseModel):
    id: int
    title: str


class Task(BaseModel):
    id: int
    telegram_user: Optional[int] = None
    tags: Optional[List[int]] = []
    title: str
    description: str
    remind_time: datetime
    completed: bool
    date_created: datetime
