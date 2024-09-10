from datetime import datetime

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.common import CommonElements
from app.models import TelegramUser
from app.services.internal import TODOCore
from app.services.repo import Repo
from app.states.user import TODOManage


class CreateTaskWindow(Window):
    def __init__(self, state: State) -> None:
        super().__init__(
            Format("{middleware_data[locales][tasks][add_task][confirm]}"),
            self.get_approve_keyboard(self.create_task, self.back),
            state=state,
        )

    @staticmethod
    def get_approve_keyboard(on_confirm_click, on_cancel_click):
        return CommonElements.confirm_n_cancel(on_confirm_click=on_confirm_click, on_cancel_click=on_cancel_click)

    @staticmethod
    async def create_task(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        locales = dialog_manager.middleware_data["locales"]
        await callback.answer(locales["sending_request"])

        repo: Repo = dialog_manager.middleware_data["repo"]
        user: TelegramUser = await repo.user_dao.get_user(dialog_manager.event.from_user.id)

        data = dialog_manager.dialog_data

        date_obj = datetime.strptime(data.get("date"), "%Y-%m-%d").date()
        time_obj = datetime.strptime(data.get("time"), "%H:%M").time()
        remind_time = datetime.combine(date_obj, time_obj)

        status = await repo.task_dao.create_task(
            telegram_user_id=user.id,
            title=data.get("title"),
            description=data.get("description"),
            completed=False,
            remind_time=remind_time
        )
        if status:
            await callback.answer(locales["tasks"]["add_task"]["success"])
            await dialog_manager.start(
                state=TODOManage.tasks
            )
        else:
            await callback.answer(locales["tasks"]["add_task"]["fail"])

    @staticmethod
    async def back(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("Действие отменено!")
        await dialog_manager.done()
        await callback.message.delete()
