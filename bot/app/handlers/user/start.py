from aiogram import Router, types
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram_dialog import DialogManager, StartMode

from app.keyboards import Menu
from app.models import TelegramUser
from app.services.repo import Repo
from app.states.user import UserStart, ChooseLanguage
from app.keyboards.menu import Menu

router = Router()


@router.message(CommandStart())
async def start(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await start_user(repo, dialog_manager, message)


async def start_user(
    repo: Repo,
    dialog_manager: DialogManager,
    message: types.Message,
) -> None:
    user = await repo.user_dao.get_user(chat_id=message.chat.id)
    print(message.chat.id)
    print(user)

    if user is None:
        user = await repo.user_dao.create_user(
            chat_id=message.chat.id,
            first_name=message.chat.first_name,
            last_name=message.chat.last_name,
            username=message.chat.username
        )

    if user and not user.language:
        await dialog_manager.start(
            ChooseLanguage.show,
            mode=StartMode.RESET_STACK,
        )
        return

    await dialog_manager.start(
        UserStart.show,
        mode=StartMode.RESET_STACK
    )

    await show_user_menu(message, dialog_manager)


async def show_user_menu(message: types.Message, dialog_manager: DialogManager):
    await message.answer(
        dialog_manager.middleware_data["locales"]["show_menu"],
        reply_markup=Menu.user(dialog_manager.middleware_data["locales"])
    )


async def show_start_message(
    message: types.Message,
    manager: DialogManager,
    user: TelegramUser,
    delete_message: bool = False
):
    if delete_message:
        await message.delete()
        await manager.done()

    markup = types.ReplyKeyboardMarkup(
        keyboard=[[Menu.start_page(manager.middleware_data["locales"])]],
        resize_keyboard=True
    )

    await message.answer(
        manager.middleware_data["locales"]["start_message"].format(username=f"@{user.username}"),
        reply_markup=markup
    )
