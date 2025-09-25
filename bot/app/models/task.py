from datetime import datetime
from typing import List, Optional

from .base import BaseModel
from .user import TelegramUser
from enum import Enum, auto


class TaskNotifyStatusEnum(Enum):
    PENDING = "pending"
    ENQUEUED = "enqueued"
    SENT = "sent"
    FAILED = "failed"


class Tag(BaseModel):
    id: int
    name: str


class Task(BaseModel):
    id: int
    telegram_user: Optional[int] = None
    tags: Optional[List[int]] = []
    title: str
    description: str
    remind_time: datetime
    notify_status: TaskNotifyStatusEnum = TaskNotifyStatusEnum.PENDING
    notify_attempts: int = 0
    last_enqueued_at: Optional[datetime] = None
    notified_at: Optional[datetime] = None
    completed: bool
    date_created: datetime


class TaskFilter(BaseModel):
    BY_TAG: bool = False
