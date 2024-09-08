from typing import Optional

from pydantic import BaseModel


class RedisValueDTO(BaseModel):
    """DTO for redis values."""

    key: str
    value: Optional[str] = None  # noqa: WPS110
    store_time: Optional[int] = None
