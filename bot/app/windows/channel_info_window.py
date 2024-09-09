from typing import Dict, List

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Group, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from app.dialogs.common import CommonElements
from app.models import TelegramChannel
from app.services.repo import Repo
from app.states.admin import Channels


class ChannelInfoWindow(Window):
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
            SwitchTo(Const("❌ Удалить"), id="delete", state=Channels.delete),
            width=2,
        )

    def get_request_data(self):
        async def book_getter(dialog_manager: DialogManager, **kwargs) -> Dict:
            repo: Repo = dialog_manager.middleware_data["repo"]
            dialog_data = dialog_manager.dialog_data
            channels: List[TelegramChannel] = dialog_data.get("channels")

            if channels:
                request: TelegramChannel = list(filter(
                    lambda x: x.id == dialog_data.get("channels_obj_id"), channels)
                )[0]
            else:
                request: TelegramChannel = await repo.settings_dao.get_channel(
                    id=dialog_manager.dialog_data.get("channels_obj_id")
                )

            return {
                "id": request.id,
                "name": request.name,
                "invite_link": request.invite_link,
            }

        return book_getter

    @staticmethod
    def get_detailed_info() -> Jinja:
        return Jinja(
            "Телеграмм канал/группа <code>ID: {{ id }}</code>\n\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
            "Название: <b>{{ name }}</b>\n"
            "Ссылка на вступление: {{ invite_link }}\n"
            "➖➖➖➖➖➖➖➖➖➖"
        )
