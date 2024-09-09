from typing import List, Optional

from aiogram.fsm.state import State
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager, ShowMode

from app.dialogs.common import CommonElements
from app.models import TelegramChannel
from app.services.repo import Repo
from app.states.admin import Channels, SettingsMenu

from .base import BaseListingWindow


class ChannelsWindow(BaseListingWindow):
    LISTING_MESSAGE = "Выберите канал для просмотра/редактирования, " \
                      "либо добавьте новый (всего {count} шт.):"
    BUTTON_TEXT = "{item.id} – {item.name}"
    HEIGHT = 5

    def __init__(self, state: State, switch_to: Optional[State] = None):
        super().__init__(
            id="channels",
            state=state,
            elements=[
                Button(Const("Как добавить?"), id="how_to_add", on_click=self.on_add_btn_click),
                CommonElements.back_btn(self.on_back_btn_click)
            ],
            switch_to=switch_to,
        )

    @staticmethod
    async def on_add_btn_click(call_back, button, dialog_manager: DialogManager, **kwargs):
        await dialog_manager.switch_to(Channels.add_new)

    @staticmethod
    async def on_back_btn_click(call_back, button, dialog_manager: DialogManager, **kwargs):
        await dialog_manager.start(SettingsMenu.show, show_mode=ShowMode.EDIT)

    def data_getter(self, **kwargs):
        async def get_data(dialog_manager: DialogManager, **kwargs):
            repo: Repo = dialog_manager.middleware_data["repo"]
            dialog_data = dialog_manager.dialog_data
            channels: List[TelegramChannel] = dialog_data.get("channels")

            if not channels:
                channels: List[TelegramChannel] = await repo.settings_dao.get_channels()
                dialog_manager.dialog_data.update(channels=channels)

            return {"items": channels, "count": len(channels)}

        return get_data
