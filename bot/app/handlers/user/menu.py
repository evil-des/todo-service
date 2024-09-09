from aiogram import Router, types
from aiogram_dialog import DialogManager, StartMode
from aiogram import F

from app.keyboards import Menu
from app.services.repo import Repo
from app.states.user import UserMainMenu, ChooseLanguage
from app.data.locales import locales
from app.filters import VerifiedFilter

router = Router()


def get_button_name(name: str) -> list:
    return list(map(lambda v: v["menu_buttons"][name], locales.values()))


@router.message(F.text.in_(get_button_name("signals")), VerifiedFilter())
async def show_signals(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await dialog_manager.start(UserMainMenu.signals, mode=StartMode.RESET_STACK)


@router.message(F.text.in_(get_button_name("guide")), VerifiedFilter())
async def show_guide(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await dialog_manager.start(UserMainMenu.guide_games, mode=StartMode.RESET_STACK)


@router.message(F.text.in_(get_button_name("stats")), VerifiedFilter())
async def show_support(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await dialog_manager.start(UserMainMenu.stats, mode=StartMode.RESET_STACK)


@router.message(F.text.in_(get_button_name("deposit")), VerifiedFilter())
async def show_deposit(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await dialog_manager.start(UserMainMenu.deposit, mode=StartMode.RESET_STACK)
