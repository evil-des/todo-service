from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.text import Format, Const, Jinja
from aiogram_dialog.widgets.kbd import WebApp, Button
from app.utils.get_settings import get_settings
from magic_filter import F

from app.states.user import UserStart

settings = get_settings()


def is_start(data: dict, widget: Whenable, manager: DialogManager):
    return not data["start_data"].get("is_verified")


def is_continue(data: dict, widget: Whenable, manager: DialogManager):
    return data["start_data"].get("is_verified")


def get_start_text(type_: str):
    locale_msg = f"middleware_data['locales']['{type_}']"

    return "{% if event.from_user.username %}" \
           "{{ " + locale_msg + ".format(username='@' + event.from_user.username) }}" \
           "{% else %}" \
           "{{ " + locale_msg + ".format(username=event.from_user.full_name) }}" \
           "{% endif %}"


dialog = Dialog(
    Window(
        Jinja(get_start_text("start_message"), when=is_start),
        WebApp(text=Format("{middleware_data[locales][start_game]}"), url=Const(settings.WEB_APP_START), when=is_start),

        Jinja(get_start_text("continue_message"), when=is_continue),
        state=UserStart.show
    )
)
