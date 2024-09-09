from typing import List, Optional
from sqlalchemy.future import select

from app.models import User, WithdrawRequest, Admin, ExchangeCurrency, TelegramChannel
from app.services.dao.base import DAO


class SettingsDAO(DAO):
    async def get_exchange_rate(self, currency: ExchangeCurrency, amount: float = None) -> float:
        return await self.api.get_exchange_rate(amount=amount, currency=currency)

    async def set_exchange_rate(self, amount: float, currency: ExchangeCurrency) -> bool:
        return await self.api.set_exchange_rate(amount, currency)

    async def get_channels(self) -> List[TelegramChannel]:
        return await self.api.get_channels()

    async def get_channel(self, id: int) -> TelegramChannel | None:
        channels = await self.api.get_channels()
        found = list(filter(lambda x: x.id == id, channels))
        if found:
            return found[0]
        return None

    async def set_channels(self, channels: List[TelegramChannel]) -> bool:
        return await self.api.set_channels(channels)

    async def get_min_withdraw_amount(self, currency: ExchangeCurrency) -> float:
        return await self.api.get_min_withdraw_amount(currency)

    async def set_min_withdraw_amount(self, amount: float, currency: ExchangeCurrency) -> bool:
        return await self.api.set_min_withdraw_amount(amount, currency)

    async def get_ref_basic_coin(self) -> int:
        return await self.api.get_ref_coin()

    async def get_ref_basic_energy(self) -> int:
        return await self.api.get_ref_energy()

    async def get_referral_deposit_status(self) -> bool:
        return await self.api.get_referral_deposit_status()

    async def get_first_withdraw_status(self) -> bool:
        return await self.api.get_first_withdraw_status()

    async def get_referral_deposit_bonus(self) -> int:
        return await self.api.get_referral_deposit_bonus()

    async def get_referral_deposit_bonus_status(self) -> bool:
        return await self.api.get_referral_deposit_bonus_status()

    async def set_ref_basic_coin(self, amount: int) -> bool:
        return await self.api.set_ref_coin(amount)

    async def set_ref_basic_energy(self, amount: int) -> bool:
        return await self.api.set_ref_energy(amount)

    async def set_referral_deposit_status(self, status: bool) -> bool:
        return await self.api.set_referral_deposit_status(status)

    async def set_first_withdraw_status(self, status: bool) -> bool:
        return await self.api.set_first_withdraw_status(status)

    async def set_referral_deposit_bonus(self, amount: int) -> bool:
        return await self.api.set_referral_deposit_bonus(amount)

    async def set_referral_deposit_bonus_status(self, status: bool) -> bool:
        return await self.api.set_referral_deposit_bonus_status(status)

    async def get_referral(self, referral_id: int = None, referrer_id: int = None, is_verified: bool = None):
        return await self.api.get_referral(referral_id, referrer_id, is_verified)

    async def delete_referral(self, referral_id: int = None, user_id: int = None) -> bool:
        return await self.api.delete_referral(referral_id, user_id)

    async def set_ban(self, user_id: int, status: bool) -> bool:
        return await self.api.set_ban(user_id, status)
