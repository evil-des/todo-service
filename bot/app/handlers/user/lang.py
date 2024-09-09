from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode

from app.keyboards import Menu
from app.services.repo import Repo
from app.states.user import ChooseLanguage

router = Router()


@router.message(Command(
    types.BotCommand(
        command="lang",
        description="EN: Change language\nRU: Смена языка"
    )
))
async def change_language(
    message: types.Message, dialog_manager: DialogManager, repo: Repo
) -> None:
    await dialog_manager.start(
        ChooseLanguage.command,
        mode=StartMode.RESET_STACK,
    )

