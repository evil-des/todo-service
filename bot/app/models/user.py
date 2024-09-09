from datetime import datetime
from typing import List, Optional

from .base import BaseModel


class TelegramUser(BaseModel):
    id: int
    chat_id: int
    first_name: str
    last_name: str
    username: str
    language: Optional[str] = None
