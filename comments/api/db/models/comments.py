import enum
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, String, Float, Text

from api.db.base import Base


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"))
    content: Mapped[str] = mapped_column(Text)
    posted_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
