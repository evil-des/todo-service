from aiogram import F, Router, types
from typing import Union, Dict, Any
from aiogram.filters import Filter
from aiogram.types import Message
from aiogram_dialog import DialogManager

from app.handlers.user.start import show_user_menu

router = Router()


class WebAppDataFilter(Filter):
    async def __call__(self, message: Message, **kwargs) -> Union[bool, Dict[str, Any]]:
        return dict(web_app_data=message.web_app_data) if message.web_app_data else False


@router.message(WebAppDataFilter())
async def handle_web_app_data(
        message: types.Message,
        web_app_data: types.WebAppData,
        dialog_manager: DialogManager
):
    if web_app_data.data == "start:success":
        await show_user_menu(message, dialog_manager)
