from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.common import CommonElements
from app.services.internal import TODOCore
from app.services.repo import Repo
from app.states.user import TODOManage


class DeleteTaskWindow(Window):
    def __init__(self, state: State) -> None:
        super().__init__(
            Format("{middleware_data[locales][tasks][delete_task][confirm]}"),
            self.get_approve_keyboard(self.delete_task, self.back),
            state=state,
        )

    @staticmethod
    def get_approve_keyboard(on_confirm_click, on_cancel_click):
        return CommonElements.confirm_n_cancel(on_confirm_click=on_confirm_click, on_cancel_click=on_cancel_click)

    @staticmethod
    async def delete_task(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        locales = dialog_manager.middleware_data["locales"]
        await callback.answer(locales["sending_request"])

        # repo: Repo = dialog_manager.middleware_data["repo"]
        todo_core: TODOCore = dialog_manager.middleware_data["todo_core"]
        task_id: int = dialog_manager.dialog_data.get("tasks_obj_id")

        status = await todo_core.delete("tasks", task_id)
        if status:
            await callback.answer(locales["tasks"]["delete_task"]["success"])
            await dialog_manager.start(
                state=TODOManage.tasks
            )
        else:
            await callback.answer(locales["tasks"]["delete_task"]["fail"])

    @staticmethod
    async def back(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("Действие отменено!")
        await dialog_manager.done()
        await callback.message.delete()
