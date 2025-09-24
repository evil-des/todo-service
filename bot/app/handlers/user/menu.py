from aiogram import Router, types
from aiogram_dialog import DialogManager, StartMode
from aiogram import F

from app.keyboards import Menu
from app.services.repo import Repo
from app.states.task import TODOManage, TaskShowState
from app.data.locales import locales

router = Router()


def get_button_name(name: str) -> list:
    return list(map(lambda v: v["menu_buttons"][name], locales.values()))


@router.message(F.text.in_(get_button_name("tasks")))
async def show_tasks(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await dialog_manager.start(TaskShowState.tasks, mode=StartMode.RESET_STACK)
