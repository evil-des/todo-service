from typing import Dict

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window, ShowMode
from aiogram_dialog.widgets.kbd import Group, SwitchTo, Button
from aiogram_dialog.widgets.text import Const, Jinja, Format

from app.dialogs.common import CommonElements
from app.models import User
from app.services.repo import Repo
from app.states.admin import UsersListing


class UserInfoWindow(Window):
    def __init__(
        self,
        state: State,
        is_referral: bool = False,
        delete_referral_state: State = None,
        back_to: State = None
    ) -> None:
        self.this_state = state
        self.is_referral: bool = is_referral
        self.delete_referral_state = delete_referral_state
        self.back_to = back_to

        super().__init__(
            self.get_detailed_info(),
            self.get_keyboard(),
            getter=self.get_data(),
            state=state,
        )

    def get_keyboard(self):
        buttons = [
            CommonElements.back_btn(on_click=self.on_back_click()),
            SwitchTo(Const("🔄 Обновить"), id="update", state=self.this_state)
        ]

        if not self.is_referral:
            buttons += [
                Button(Format("Бан {emoji_ban}"), id="ban_user", on_click=self.on_ban_click()),
                SwitchTo(Const("Рефералы"), id="show_referrals", state=UsersListing.user_referrals),
            ]

        if self.delete_referral_state:
            buttons.append(
                SwitchTo(Const("Отвязать реферала"), id="delete_referral", state=self.delete_referral_state)
            )

        return Group(*buttons, width=2)

    def get_data(self):
        async def getter(dialog_manager: DialogManager, **kwargs) -> Dict:
            repo: Repo = dialog_manager.middleware_data["repo"]
            origin = "referrals" if self.is_referral else "users"

            if not dialog_manager.dialog_data.get("user_info"):
                user: User = await repo.user_dao.get_user(
                    id=dialog_manager.dialog_data.get(f"{origin}_obj_id")
                )

                data = user.__dict__
            else:
                data = dialog_manager.dialog_data["user_info"]
                dialog_manager.dialog_data.update(user_info=None)

            if self.is_referral:
                data["is_referral"] = self.is_referral

            if not self.is_referral:
                data["emoji_ban"] = "✅" if data.get("is_banned") else "❌"
                dialog_manager.dialog_data.update(is_banned=data.get("is_banned"))

            if not data.get("last_name"):
                data["last_name"] = ""

            return data

        return getter

    def on_ban_click(self):
        async def handler(
                callback: CallbackQuery,
                button: Button,
                manager: DialogManager
        ):
            repo: Repo = manager.middleware_data["repo"]
            dialog_data = manager.dialog_data

            await repo.settings_dao.set_ban(dialog_data.get("users_obj_id"), not dialog_data.get("is_banned"))
            await manager.switch_to(self.this_state)

        return handler

    def on_back_click(self):
        async def handler(
                callback: CallbackQuery,
                button: Button,
                manager: DialogManager
        ):
            if self.back_to:
                await manager.switch_to(self.back_to)
                return

            if self.is_referral:
                await manager.switch_to(UsersListing.user_referrals)
                return

            if not self.is_referral:
                await manager.switch_to(UsersListing.all_users)
                return

        return handler

    @staticmethod
    def get_detailed_info() -> Jinja:
        return Jinja(
            "Пользователь <code>#{{ id }}</code>:\n\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
            "TG_ID: <code>{{ chat_id }}</code>\n"
            "Имя: <code>{{ first_name }} {{ last_name }}</code>\n"
            "Username: @{{ username }}\n"
            "Верифицирован: <code>{% if is_verified %}Да{% else %}Нет{% endif %}</code>\n"
            "Кол-во коинов: <code>{{ coin_amount }}</code>\n"
            "Кол-во энергии: <code>{{ energy_amount }}</code>\n"
            "Кол-во макс. энергии: <code>{{ max_energy_amount }} / 3000</code>\n"
            "Язык: <b>{{ language }}</b>\n\n"
            "Дата создания: <b>{{ date_started }}</b>\n"
            "Дата верификации: <b>{{ date_verified }}</b>\n\n"
            "Заблокирован: {% if is_banned %}Да{% else %}Нет{% endif %}\n\n"
            "➖➖➖➖➖➖➖➖➖➖\n\n"
            "{% if not is_referral %}"
            "Чтобы посмотреть рефералов пользователя, нажмите на кнопку ниже"
            "{% endif %}"
        )
