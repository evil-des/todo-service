from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode

from app.keyboards import Menu
from app.services.repo import Repo
from app.states.admin import Mailing
from app.filters import AdminFilter

router = Router()


@router.message(Command(
    types.BotCommand(
        command="mailing",
        description="Начать рассылку для пользователей"
    )
), AdminFilter())
async def start_mailing(
    message: types.Message, dialog_manager: DialogManager, repo: Repo
) -> None:
    await dialog_manager.start(
        Mailing.show_types,
        mode=StartMode.RESET_STACK,
    )

