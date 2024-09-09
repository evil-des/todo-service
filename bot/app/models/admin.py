from datetime import datetime
from typing import List, Optional
import enum
from .base import BaseModel


class Admin(BaseModel):
    id: int
    user_id: int


class WithdrawRequest(BaseModel):
    id: int
    user_id: int
    date_opened: datetime
    date_closed: None | datetime
    is_approved: bool
    wallet: str
    payment_system: str
    amount: float
    currency: str


class Referral(BaseModel):
    id: int
    user_id: int
    referrer_id: int


class TelegramChannel(BaseModel):
    id: int
    name: Optional[str] = None
    avatar: Optional[str] = None
    invite_link: Optional[str] = None
    subscribed: Optional[bool] = None


class ExchangeCurrency(enum.Enum):
    RUB = "RUB"
    USD = "USD"

    def __str__(self):
        return str(self.value)


class WithdrawRequestFilter(BaseModel):
    IS_DATE_OPENED_SORT_DESC: bool = False
    IS_DATE_OPENED_SORT: bool = False
    IS_CLOSED_REQUESTS: bool = False
    IS_CURRENCY_FILTER: bool = False
