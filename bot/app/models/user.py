from datetime import datetime
from typing import List, Optional

from .base import BaseModel


class TelegramUser(BaseModel):
    id: int
    chat_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language: Optional[str] = None
