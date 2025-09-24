from typing import List, Optional

from aiogram.fsm.state import State
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import DialogManager, ShowMode

from app.dialogs.common import CommonElements
from app.models import Task, Tag, TaskFilter
from app.services.repo import Repo
from app.states.task import TaskShowState, TaskCreateState

from .base import BaseListingWindow
from app.utils.get_pydantic_list import get_pydantic_list


class TasksWindow(BaseListingWindow):
    LISTING_MESSAGE = "{middleware_data[locales][tasks][listing]}"
    BUTTON_TEXT = "{item.completed} – {item.title} [{item.date_created}]"
    HEIGHT = 5

    def __init__(
            self,
            state: State,
            filter: Optional[TaskFilter] = None,
            switch_to: Optional[State] = None,
    ):
        self.filter = filter
        elements = [
            Button(
                Format("{middleware_data[locales][tasks][add_item_btn]}"),
                id="add_task",
                on_click=self.on_add_btn_click,
            ),
            self.get_filter_keyboard(),
        ]

        if self.filter:
            elements.append(
                SwitchTo(
                    Format("{middleware_data[locales][tasks][reset_filters]}"),
                    id="reset_filters",
                    state=TaskShowState.tasks,
                )
            )

        super().__init__(
            id="tasks",
            state=state,
            elements=elements,
            switch_to=switch_to,
        )

    @staticmethod
    def get_filter_keyboard():
        return SwitchTo(
            Const("🔖 Фильтр по тегам"),
            id="filter_menu",
            state=TaskShowState.tags,
        )

    @staticmethod
    async def on_add_btn_click(
            call_back,
            button,
            dialog_manager: DialogManager,
            **kwargs,
    ):
        await dialog_manager.start(TaskCreateState.set_title)

    async def get_filtered_items(
            self,
            dialog_manager: DialogManager,
    ) -> Optional[List[Task]]:
        items = []
        repo: Repo = dialog_manager.middleware_data["repo"]

        if self.filter.BY_TAG:
            items = await repo.task_dao.get_tasks(
                telegram_chat_id=dialog_manager.event.from_user.id,
                tags_ids=[
                    dialog_manager.dialog_data.get("tags_obj_id"),
                ],
            )

        return items

    async def get_items(self, dialog_manager: DialogManager) -> Optional[list[Task]]:
        if self.filter:
            return await self.get_filtered_items(dialog_manager)

        repo: Repo = dialog_manager.middleware_data["repo"]
        return await repo.task_dao.get_tasks(
            dialog_manager.event.from_user.id,
        )

    def data_getter(self, **kwargs):
        async def get_data(dialog_manager: DialogManager, **kwargs):
            items: List[Task] = get_pydantic_list(dialog_manager, "tasks", Task)

            print(f"TEST!!! filter: {self.filter}")

            if not items or self.filter:
                items = await self.get_items(dialog_manager)
                dialog_manager.dialog_data.update(
                    tasks=[item.model_dump_json() for item in items]
                )

            for item in items:
                item.completed = '✅' if item.completed else '❌'
                item.date_created = item.date_created.strftime("%d.%m.%Y %H:%M")

            return {"items": items, "count": len(items)}

        return get_data
