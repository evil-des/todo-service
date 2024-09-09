from aiogram import Router, types
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram_dialog import DialogManager, StartMode

from app.keyboards import Menu
from app.models import User
from app.services.repo import Repo
from app.states.user import UserStart, ChooseLanguage
from app.keyboards.menu import Menu

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_deep_link(
        message: types.Message, command: CommandObject,
        dialog_manager: DialogManager, repo: Repo
) -> None:
    # TODO referral
    args = command.args
    payload = decode_payload(args)
    referrer = None

    if payload and payload.isnumeric():
        referrer = await repo.user_dao.get_user(id=int(payload))

    await start_user(repo, dialog_manager, message, referrer=referrer)


@router.message(CommandStart())
async def start(message: types.Message, dialog_manager: DialogManager, repo: Repo) -> None:
    await start_user(repo, dialog_manager, message, referrer=None)


async def start_user(
    repo: Repo,
    dialog_manager: DialogManager,
    message: types.Message,
    referrer=None
) -> None:
    user = await repo.user_dao.get_user(chat_id=message.chat.id)

    if user is None:
        user = await repo.user_dao.create_user(
            chat_id=message.chat.id,
            first_name=message.chat.first_name,
            last_name=message.chat.last_name,
            username=message.chat.username,
            referrer=referrer
        )

    if user and not user.language:
        await dialog_manager.start(
            ChooseLanguage.show,
            mode=StartMode.RESET_STACK,
        )
        return

    await dialog_manager.start(
        UserStart.show,
        mode=StartMode.RESET_STACK,
        data={"is_verified": user.is_verified}
    )

    if user and user.is_verified:
        await show_user_menu(message, dialog_manager)


async def show_admin_dashboard(message: types.Message):
    await message.answer(
        "Внизу появилось Админ-меню\n\n"
        "*Вы видете это сообщение, потому что вас назначили Администратором*",
        reply_markup=Menu.admin()
    )


async def show_user_menu(message: types.Message, dialog_manager: DialogManager):
    await message.answer(
        dialog_manager.middleware_data["locales"]["show_menu"],
        reply_markup=Menu.user(dialog_manager.middleware_data["locales"])
    )


async def show_start_message(
        message: types.Message,
        manager: DialogManager,
        user: User,
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
