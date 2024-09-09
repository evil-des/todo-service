from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from app.dialogs.common import CommonElements
from app.services.repo import Repo
from app.states.admin import UsersListing


class DeleteReferralWindow(Window):
    def __init__(self, state: State) -> None:
        super().__init__(
            Const("Вы действительно хотите отвязать данного реферала от пользователя?"),
            self.get_approve_keyboard(self.delete_referral, self.back),
            state=state,
        )

    @staticmethod
    def get_approve_keyboard(on_confirm_click, on_cancel_click):
        return CommonElements.confirm_n_cancel(on_confirm_click=on_confirm_click, on_cancel_click=on_cancel_click)

    @staticmethod
    async def delete_referral(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("⏳ Ожидайте... Отправляем запрос к API")
        repo: Repo = dialog_manager.middleware_data["repo"]
        user_id: int = dialog_manager.dialog_data.get("users_obj_id")

        status = await repo.settings_dao.delete_referral(user_id=user_id)
        if status:
            await callback.answer("Реферал успешно отвязан 👍")
            await dialog_manager.start(
                state=UsersListing.user_referrals
            )
        else:
            await callback.answer("😵‍💫 Произошла ошибка при удалении реферала")

    @staticmethod
    async def back(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("Действие отменено!")
        await dialog_manager.done()
        await callback.message.delete()
