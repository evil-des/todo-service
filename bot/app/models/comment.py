from datetime import datetime
from typing import List, Optional

from .base import BaseModel
from .user import TelegramUser


class Comment(BaseModel):
    id: int
    task_id: int
    content: str
    posted_date: datetime
