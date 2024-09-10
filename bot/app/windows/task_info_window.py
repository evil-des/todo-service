from typing import Dict, List

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Group, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja, Format

from app.dialogs.common import CommonElements
from app.models import Task
from app.services.repo import Repo
from app.states.user import TODOManage
import datetime


class TaskInfoWindow(Window):
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
            CommonElements.back_btn(on_click=self.on_back_click),
            getter=self.get_request_data(),
            state=state,
        )

    def get_keyboard(self):
        return Group(
            CommonElements.back_btn(on_click=self.on_back_click),
            SwitchTo(Const("❌ Удалить"), id="delete", state=TODOManage.delete_task),
            width=2,
        )

    @staticmethod
    async def on_back_click(call_back, button, dialog_manager: DialogManager, **kwargs):
        await dialog_manager.switch_to(TODOManage.tasks)

    def get_request_data(self):
        async def getter(dialog_manager: DialogManager, **kwargs) -> Dict:
            repo: Repo = dialog_manager.middleware_data["repo"]
            dialog_data = dialog_manager.dialog_data

            locale = dialog_manager.middleware_data["locales"]["tasks"]["task_info"]
            task = await repo.task_dao.get_task(dialog_data.get("tasks_obj_id"))

            return {
                "task_text": locale.format(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed='✅ выполнена' if task.completed else '❌ не выполнена',
                    date_created=task.date_created.strftime("%d.%m.%Y"),
                    remind_time=task.date_created.strftime("%d.%m.%Y %H:%M"),
                )
            }

        return getter

    @staticmethod
    def get_detailed_info() -> Format:
        return Format("{task_text}")
