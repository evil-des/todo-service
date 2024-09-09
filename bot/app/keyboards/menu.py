import aiogram
from app.utils.get_settings import get_settings

from .default.consts import DefaultConstructor


class Menu(DefaultConstructor):
    settings = get_settings()

    @staticmethod
    def admin() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [2, 2, 1]
        buttons = ["💰 Заявки на вывод", "📌 Статистика", "⚙️ Настройки", "Пользователи", "Рассылка"]
        return Menu._create_kb(buttons, schema)

    @staticmethod
    def user(locales: dict) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1, 2, 1]
        buttons = locales["menu_buttons"].values()
        return Menu._create_kb(buttons, schema)

    @staticmethod
    def start_page(locales: dict) -> aiogram.types.KeyboardButton:
        return aiogram.types.KeyboardButton(
            text=locales["start_game"],
            web_app=aiogram.types.WebAppInfo(url=Menu.settings.WEB_APP_START)
        )
