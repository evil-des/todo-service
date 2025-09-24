from datetime import datetime

from aiogram.enums import ContentType
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.common import CommonElements
from app.models import TelegramUser
from app.services.internal import TODOCore
from app.services.repo import Repo
from app.states.task import TODOManage


class CreateTagWindow(Window):
    def __init__(self, state: State) -> None:
        super().__init__(
            Format("{middleware_data[locales][tasks][add_tag][title]}"),
            MessageInput(
                content_types=ContentType.TEXT,
                func=self.on_title_input(),
            ),
            state=state,
        )

    def on_title_input(self):
        async def on_tag_title_input(
                message: Message, m_input: MessageInput, dialog_manager: DialogManager, *args
        ) -> None:
            await self.create_tag(message, dialog_manager)

        return on_tag_title_input

    @staticmethod
    async def create_tag(
        message: Message,
        dialog_manager: DialogManager,
    ) -> None:
        locales = dialog_manager.middleware_data["locales"]
        repo: Repo = dialog_manager.middleware_data["repo"]
        user: TelegramUser = await repo.user_dao.get_user(
            dialog_manager.event.from_user.id
        )

        status = await repo.tag_dao.create_tag(message.text.strip())
        if status:
            await message.answer(locales["tasks"]["add_tag"]["success"])
            await dialog_manager.start(state=TODOManage.filtered_tasks)
        else:
            await message.answer(locales["tasks"]["add_tag"]["fail"])

    @staticmethod
    async def back(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await callback.answer("Действие отменено!")
        await dialog_manager.done()
        await callback.message.delete()
