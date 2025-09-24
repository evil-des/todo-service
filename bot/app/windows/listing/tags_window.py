from typing import List, Optional

from aiogram.fsm.state import State
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import DialogManager, ShowMode

from app.dialogs.common import CommonElements
from app.models import Task, Tag
from app.services.repo import Repo
from ...states.task import TODOManage

from .base import BaseListingWindow
from app.utils.get_pydantic_list import get_pydantic_list


class TagsWindow(BaseListingWindow):
    LISTING_MESSAGE = "{middleware_data[locales][tasks][listing_choose_tag]}"
    BUTTON_TEXT = "{item.name}"
    HEIGHT = 5
    WIDTH = 2

    def __init__(self, state: State, switch_to: Optional[State] = None):
        super().__init__(
            id="tags",
            state=state,
            elements=[
                Button(
                    Format("{middleware_data[locales][tasks][add_item_btn]}"),
                    id="add_tag",
                    on_click=self.on_add_btn_click,
                ),
            ],
            switch_to=switch_to,
        )

    @staticmethod
    async def on_add_btn_click(
            call_back,
            button,
            dialog_manager: DialogManager,
            **kwargs,
    ):
        await dialog_manager.switch_to(TODOManage.add_tag)

    def data_getter(self, **kwargs):
        async def get_data(dialog_manager: DialogManager, **kwargs):
            repo: Repo = dialog_manager.middleware_data["repo"]
            dialog_data = dialog_manager.dialog_data
            items: List[Tag] = get_pydantic_list(dialog_manager, "tags", Tag)

            if not items:
                items: List[Task] = await repo.tag_dao.get_tags()
                dialog_manager.dialog_data.update(
                    tags=[item.model_dump_json() for item in items]
                )

            return {"items": items, "count": len(items)}

        return get_data
