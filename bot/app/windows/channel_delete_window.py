from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from app.dialogs.common import CommonElements
from app.services.repo import Repo
from app.states.admin import WithdrawListing, Channels
from app.models import TelegramChannel
from typing import List, Optional


class ChannelDeleteWindow(Window):
    def __init__(self, state: State) -> None:
        super().__init__(
            Const("Вы действительно хотите удалить этот канал?"),
            self.get_approve_keyboard(self.delete_channel, self.back),
            state=state,
        )

    @staticmethod
    def get_approve_keyboard(on_confirm_click, on_cancel_click):
        return CommonElements.confirm_n_cancel(on_confirm_click=on_confirm_click, on_cancel_click=on_cancel_click)

    @staticmethod
    async def delete_channel(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        repo: Repo = dialog_manager.middleware_data["repo"]
        dialog_data = dialog_manager.dialog_data

        channels: List[TelegramChannel] = dialog_data.get("channels")
        channel_id = dialog_data.get("channels_obj_id")

        for i, item in enumerate(channels):
            if item.id == channel_id:
                del channels[i]
                break

        await callback.answer("⏳ Ожидайте... Отправляем запрос к API")
        status = await repo.settings_dao.set_channels(channels)

        if status:
            await callback.answer("Канал успешно удален из БД 👍")
            dialog_data.update(channels=channels)

            await dialog_manager.start(
                state=Channels.all_channels, mode=StartMode.RESET_STACK
            )
            return

        await callback.answer("😵‍💫 Произошла ошибка при подтверждении заявки")

    @staticmethod
    async def back(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("Действие отменено!")
        await dialog_manager.done()
