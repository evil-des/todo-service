import enum
from typing import Any, Optional, List
from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    task_id: int
    content: str


class Comment(CommentCreate):
    id: int

    class Config:
        from_attributes = True
