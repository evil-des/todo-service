from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Window, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from app.dialogs.common import CommonElements
from app.services.repo import Repo
from app.states.admin import WithdrawListing


class WithdrawCancelWindow(Window):
    def __init__(self, state: State) -> None:
        super().__init__(
            Const("Вы действительно хотите отклонить эту заявку?"),
            self.get_cancel_keyboard(self.cancel_request, self.back),
            state=state,
        )

    @staticmethod
    def get_cancel_keyboard(on_confirm_click, on_cancel_click):
        return CommonElements.confirm_n_cancel(on_confirm_click=on_confirm_click, on_cancel_click=on_cancel_click)

    @staticmethod
    async def cancel_request(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("⏳ Ожидайте... Отправляем запрос к API")
        repo: Repo = dialog_manager.middleware_data["repo"]
        request_id: int = dialog_manager.dialog_data.get("withdraw_obj_id")

        status = await repo.admin_dao.cancel_withdraw_request(request_id)

        if status:
            await callback.answer("Заявка успешно отклонена 👍")
            await dialog_manager.start(
                state=WithdrawListing.all_requests, mode=StartMode.RESET_STACK
            )
        else:
            await callback.answer("😵‍💫 Произошла ошибка при отклонении заявки")

    @staticmethod
    async def back(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("Действие отменено!")
        await dialog_manager.start(
            state=WithdrawListing.all_requests, mode=StartMode.NEW_STACK
        )
