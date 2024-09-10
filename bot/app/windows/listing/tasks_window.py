from typing import List, Optional

from aiogram.fsm.state import State
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import DialogManager, ShowMode

from app.dialogs.common import CommonElements
from app.models import Task
from app.services.repo import Repo
from app.states.user import TODOManage

from .base import BaseListingWindow
from app.utils.get_pydantic_list import get_pydantic_list


class TasksWindow(BaseListingWindow):
    LISTING_MESSAGE = "{middleware_data[locales][tasks][listing]}"
    BUTTON_TEXT = "{item.completed} – {item.title} [{item.date_created}]"
    HEIGHT = 5

    def __init__(self, state: State, switch_to: Optional[State] = None):
        super().__init__(
            id="tasks",
            state=state,
            elements=[
                Button(
                    Format("{middleware_data[locales][tasks][add_item_btn]}"),
                    id="add_task", on_click=self.on_add_btn_click
                )
            ],
            switch_to=switch_to,
        )

    @staticmethod
    async def on_add_btn_click(call_back, button, dialog_manager: DialogManager, **kwargs):
        await dialog_manager.switch_to(TODOManage.add_task_set_title)

    def data_getter(self, **kwargs):
        async def get_data(dialog_manager: DialogManager, **kwargs):
            repo: Repo = dialog_manager.middleware_data["repo"]
            dialog_data = dialog_manager.dialog_data
            items: List[Task] = get_pydantic_list(dialog_manager, "tasks", Task)

            if not items:
                items: List[Task] = await repo.task_dao.get_tasks(dialog_manager.event.from_user.id)
                dialog_manager.dialog_data.update(tasks=[item.model_dump_json() for item in items])

            for item in items:
                item.completed = '✅' if item.completed else '❌'
                item.date_created = item.date_created.strftime("%d.%m.%Y %H:%M")

            return {"items": items, "count": len(items)}

        return get_data
