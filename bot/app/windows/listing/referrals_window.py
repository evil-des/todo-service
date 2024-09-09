from typing import List, Optional

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from app.models import WithdrawRequest, WithdrawRequestFilter, User
from app.services.repo import Repo
from app.states.admin import WithdrawListing
from app.dialogs.common import CommonElements

from .base import BaseListingWindow


class ReferralsWindow(BaseListingWindow):
    LISTING_MESSAGE = "Выберите реферала для просмотра информации (всего {count} шт.):"
    BUTTON_TEXT = "#{item.id} - USER_ID: {item.user_id}"

    def __init__(self, state: State, switch_to: State = None):
        elements = [CommonElements.back_btn()]

        super().__init__(
            id="referrals",
            state=state,
            elements=elements,
            data_getter_kwargs={"filter": None},
            switch_to=switch_to,
        )

    def data_getter(self, filter=None):
        async def get_data(dialog_manager: DialogManager, **kwargs):
            repo: Repo = dialog_manager.middleware_data["repo"]
            referrals = await repo.settings_dao.get_referral(referrer_id=dialog_manager.dialog_data.get("users_obj_id"))
            return {"items": referrals, "count": len(referrals)}

        return get_data
