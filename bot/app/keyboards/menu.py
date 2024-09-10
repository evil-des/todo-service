import aiogram
from app.utils.get_settings import get_settings

from .default.consts import DefaultConstructor


class Menu(DefaultConstructor):
    settings = get_settings()

    @staticmethod
    def user(locales: dict) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        buttons = locales["menu_buttons"].values()
        return Menu._create_kb(buttons, schema)
