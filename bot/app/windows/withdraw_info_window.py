from typing import Dict

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Group, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from app.dialogs.common import CommonElements
from app.models import WithdrawRequest
from app.services.repo import Repo
from app.states.admin import WithdrawListing


class WithdrawInfoWindow(Window):
    def __init__(self, state: State, show_keyboard: bool = True) -> None:
        if show_keyboard:
            super().__init__(
                self.get_detailed_info(),
                self.get_keyboard(),
                getter=self.get_request_data(),
                state=state,
            )
            return

        super().__init__(
            self.get_detailed_info(),
            CommonElements.back_btn(),
            getter=self.get_request_data(),
            state=state,
        )

    @staticmethod
    def get_keyboard():
        return Group(
            CommonElements.back_btn(),
            SwitchTo(Const("Рефералы"), id="show_referrals", state=WithdrawListing.user_referrals),
            SwitchTo(
                Const("✅ Подтвердить"), id="approve_request", state=WithdrawListing.approve_request
            ),
            SwitchTo(
                Const("❌ Отклонить"), id="delete_request", state=WithdrawListing.cancel_request
            ),
            width=2,
        )

    def get_request_data(self):
        async def book_getter(dialog_manager: DialogManager, **kwargs) -> Dict:
            repo: Repo = dialog_manager.middleware_data["repo"]
            request = await repo.admin_dao.get_withdraw_request(
                id=dialog_manager.dialog_data.get("withdraw_obj_id")
            )

            user = await repo.user_dao.get_user(id=request.user_id)
            dialog_manager.dialog_data.update(users_obj_id=request.user_id)

            return {
                "id": request.id,
                "user_id": request.user_id,
                "username": f"{'@' + user.username if user.username else 'Отсутствует'}",
                "full_name": f"{user.first_name if user.first_name else ''}"
                             f"{' ' + user.last_name if user.last_name else ''}",
                "coins": user.coin_amount,
                "energy": user.energy_amount,

                "amount": request.amount,
                "currency": request.currency,
                "wallet": request.wallet,
                "payment_system": request.payment_system,
                "date_opened": request.date_opened,
                "date_closed": request.date_closed
            }

        return book_getter

    @staticmethod
    def get_detailed_info() -> Jinja:
        return Jinja(
            "📌 Заявка на вывод <code>#{{ id }}</code>:\n\n"
            "<i>Информация о пользователе:</i>\n\n"
            "ID: <code>{{ user_id }}</code>\n"
            "Имя: <code>{{ full_name }}</code>\n"
            "Username: {{ username }}\n"
            "Баланс (коины): {{ coins }}\n"
            "Баланс (энергия): {{ energy }}\n\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
            "Сумма: <code>{{ amount }}</code>\n"
            "Валюта: <code>{{ currency }}</code>\n"
            "Кошелек: <code>{{ wallet }}</code>\n"
            "Платежная система: <code>{{ payment_system }}</code>\n\n"
            "Дата создания: <b>{{ date_opened }}</b>\n"
            "Дата закрытия: <b>{{ date_closed }}</b>\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
