from aiogram_dialog import Dialog, DialogManager, Window, ShowMode
from aiogram_dialog.widgets.text import Const, Jinja, Format
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Group
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup

from app.services.repo import Repo
from app.models.user import TelegramUser
from app.states.user import ChooseLanguage, UserStart, TODOManage
from app.data.locales import locales
from app.handlers.user.start import show_start_message, show_user_menu
from app.keyboards.menu import Menu


async def on_lang_click(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    repo: Repo = manager.middleware_data["repo"]
    # user: TelegramUser = await repo.user_dao.get_user(chat_id=callback.from_user.id)

    await change_language(manager, button, callback)
    await manager.start(UserStart.show, show_mode=ShowMode.EDIT)


async def on_lang_command(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    repo: Repo = manager.middleware_data["repo"]
    # user: TelegramUser = await repo.user_dao.get_user(chat_id=callback.from_user.id)

    await change_language(manager, button, callback)
    await manager.switch_to(ChooseLanguage.language_changed)

    await show_user_menu(message=callback.message, dialog_manager=manager)


async def change_language(manager, button, callback):
    repo: Repo = manager.middleware_data["repo"]
    user: TelegramUser = await repo.user_dao.get_user(chat_id=callback.from_user.id)
    language: str = " ".join(button.widget_id.split("_")[1:]).replace("  ", "-")

    status = await repo.user_dao.set_language(user.id, language)
    if status:
        manager.middleware_data.update(locales=locales.get(language))


def get_language_buttons(on_click):
    return [Button(Const(locales[item].get('lang_name')), id=f"lang_{item.replace('-', '__')}", on_click=on_click)
            for item in locales.keys()]


def get_language_text() -> Const:
    return Const("\n".join(
        [locales[item].get('choose_lang_short') for item in locales.keys()]
    ))


dialog = Dialog(
    Window(
        get_language_text(),
        Group(*get_language_buttons(on_lang_click)),
        state=ChooseLanguage.show
    ),
    Window(
        get_language_text(),
        Group(*get_language_buttons(on_lang_command)),
        state=ChooseLanguage.command
    ),
    Window(
        Format("{middleware_data[locales][change_language]}"),
        state=ChooseLanguage.language_changed
    )
)
