from aiogram import Router, types
from aiogram_dialog import DialogManager, StartMode
from aiogram import F

from app.keyboards import Menu
from app.services.repo import Repo
from app.states.user import TODOManage
from app.data.locales import locales

router = Router()


def get_button_name(name: str) -> list:
    return list(map(lambda v: v["menu_buttons"][name], locales.values()))


@router.message(F.text.in_(get_button_name("tasks")))
async def show_signals(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await dialog_manager.start(TODOManage.tasks, mode=StartMode.RESET_STACK)
