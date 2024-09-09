from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, ShowMode
from aiogram_dialog.widgets.text import Format, Const, Text
from aiogram_dialog.widgets.kbd import Group, Button, SwitchTo
from app.dialogs.common import CommonElements
from app.models import WithdrawRequest
from app.services.repo import Repo
from app.states.admin import WithdrawListing
from typing import Dict, List, Optional, Callable


class DataChanger(Window):
    def __init__(self, name: str, desc: str, data_type: str, state, dao_attribute_name: str, on_change_click=None, on_back_click=None) -> None:
        self.name = name
        self.desc = desc
        # self.setting_name = setting_name
        self.data_type = data_type
        self.state = state
        self.dao_attribute_name = dao_attribute_name
        self.on_back_click = on_back_click
        self.custom_change_click = on_change_click

        super().__init__(
            self.get_detailed_info(),
            self.get_keyboard(),
            getter=self.get_data(),
            state=self.state,
        )

    def get_data(self):
        async def getter(dialog_manager: DialogManager, **kwargs) -> Dict:
            repo: Repo = dialog_manager.middleware_data["repo"]
            get_settings = getattr(repo.settings_dao, "get_" + self.dao_attribute_name)
            value = await get_settings()
            data = {
                "name": self.name,
                "desc": self.desc,
                "value": value,
                "emoji": "✅" if value else "❌"
            }
            dialog_manager.dialog_data.update(**data)

            return data

        return getter

    def get_detailed_info(self) -> Text:
        return Format(
            "Название: <code>{name}</code>\n"
            "Текущее значение: <code>{value}</code>\n\n"
            "Описание:\n<i>{desc}</i>\n\n"
            "Чтобы изменить значение, нажмите на кнопку ниже"
        )

    def on_change_click(self):
        if self.custom_change_click is not None:
            return self.custom_change_click

        async def handler(
            callback: CallbackQuery,
            button: Button,
            manager: DialogManager
        ):
            repo: Repo = manager.middleware_data["repo"]

            if self.data_type == "bool":
                set_settings = getattr(repo.settings_dao, "set_" + self.dao_attribute_name)
                new_value = not manager.dialog_data["value"]
                await set_settings(new_value)

            await manager.start(self.state, show_mode=ShowMode.EDIT)

        return handler

    def get_keyboard(self) -> Group:
        if self.data_type == "bool":
            return Group(
                Button(Format("Статус - {emoji}"), id="change", on_click=self.on_change_click()),
                CommonElements.back_btn(self.on_back_click)
            )

        return Group(
            Button(Const("Изменить"), id="change", on_click=self.on_change_click()),
            CommonElements.back_btn(self.on_back_click)
        )
