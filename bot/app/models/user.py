from datetime import datetime
from typing import List, Optional

from .base import BaseModel


class User(BaseModel):
    id: int
    chat_id: int
    first_name: str
    last_name: str
    username: str
    language: Optional[str] = None
    is_pp_registered: bool
    is_verified: bool
    signals_amount: int
    date_started: datetime
    date_verified: Optional[datetime] = None
