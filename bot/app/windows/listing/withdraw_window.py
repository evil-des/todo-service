from typing import List, Optional

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from app.models import WithdrawRequest, WithdrawRequestFilter
from app.services.repo import Repo
from app.states.admin import WithdrawListing

from .base import BaseListingWindow


class WithdrawWindow(BaseListingWindow):
    LISTING_MESSAGE = "Выберите заявку на вывод из списка (всего {count} шт.):"
    BUTTON_TEXT = "#{item.id} – {item.amount} {item.currency}"

    def __init__(
        self, state: State, filter: WithdrawRequestFilter = None, switch_to: State = None
    ):
        elements = None
        if not filter.IS_CLOSED_REQUESTS:
            elements = [self.get_filter_keyboard(filter)]

        super().__init__(
            id="withdraw",
            state=state,
            elements=elements,
            data_getter_kwargs={"filter": filter},
            switch_to=switch_to,
        )

    @staticmethod
    def get_filter_keyboard(filter: WithdrawRequestFilter = None):
        sort_icon = "↓"
        btn_switch_to = WithdrawListing.all_requests

        if not filter or not filter.IS_DATE_OPENED_SORT_DESC:
            sort_icon = "⬆"
            btn_switch_to = WithdrawListing.date_opened_desc

        return SwitchTo(
            Const(f"🔖 Сортировка по дате {sort_icon}"), id="filter_menu", state=btn_switch_to
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
            withdraw_requests: Optional[List[WithdrawRequest]] = []

            if filter is None:
                withdraw_requests = await repo.admin_dao.get_withdraw_requests()

            if filter is not None:
                withdraw_requests = await self.get_filtered_items(
                    dialog_manager, filter
                )

            return {"items": withdraw_requests, "count": len(withdraw_requests)}

        return get_data
