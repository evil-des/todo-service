from typing import List, Optional

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import SwitchTo, Button
from aiogram_dialog.widgets.text import Const

from app.models import WithdrawRequest, WithdrawRequestFilter, User
from app.services.repo import Repo
from app.states.admin import WithdrawListing
from app.dialogs.common import CommonElements

from .base import BaseListingWindow


class UsersWindow(BaseListingWindow):
    LISTING_MESSAGE = "Выберите пользователя для просмотра информации (всего {count} шт.):"
    BUTTON_TEXT = "#{item.id} – @{item.username} [{item.chat_id}]"

    def __init__(
        self, state: State, filter: WithdrawRequestFilter = None, switch_to: State = None,
        is_referrals: bool = False, search_state: State = None
    ):
        self.is_referrals = is_referrals
        elements = []
        window_id = "users"

        if not self.is_referrals:
            elements.append(
                SwitchTo(Const("🔍 Поиск"), id="search", state=search_state)
            )

        if self.is_referrals:
            elements.append(CommonElements.back_btn())
            window_id = "referrals"

        super().__init__(
            id=window_id,
            state=state,
            elements=elements,
            data_getter_kwargs={"filter": filter},
            switch_to=switch_to,
        )

    @staticmethod
    def get_btn_keyboard(referrals_state: State):
        return SwitchTo(
            Const(f"Показать рефералов"), id="show_referrals", state=referrals_state
        )

    @staticmethod
    async def get_filtered_items(
        dialog_manager: DialogManager,
        filter: WithdrawRequestFilter
    ) -> Optional[List[WithdrawRequest]]:
        repo: Repo = dialog_manager.middleware_data["repo"]
        is_shown = True

        if filter.IS_CLOSED_REQUESTS:
            is_shown = False

        withdraw_requests: List[WithdrawRequest] = await repo.admin_dao.get_withdraw_requests(
            order_by="date_opened",
            is_desc=filter.IS_DATE_OPENED_SORT_DESC,
            is_shown=is_shown
        )

        return withdraw_requests

    def data_getter(self, filter: WithdrawRequestFilter = None):
        async def get_data(dialog_manager: DialogManager, **kwargs):
            repo: Repo = dialog_manager.middleware_data["repo"]
            users: Optional[List[User]] = []

            if self.is_referrals:
                referrals = await repo.settings_dao.get_referral(
                    referrer_id=dialog_manager.dialog_data.get("users_obj_id"),
                    is_verified=True
                )
                for item in referrals:
                    user = await repo.user_dao.get_user(id=item.user_id)
                    users.append(user)

            if not self.is_referrals:
                users = await repo.user_dao.get_users()

            # if filter is not None:
            #     users = await self.get_filtered_items(
            #         dialog_manager, filter
            #     )

            return {"items": users, "count": len(users)}

        return get_data
