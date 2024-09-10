from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.text import Format, Const, Jinja
from app.utils.get_settings import get_settings
from magic_filter import F

from app.states.user import UserStart

settings = get_settings()


def get_start_text(type_: str):
    locale_msg = f"middleware_data['locales']['{type_}']"

    return "{% if event.from_user.username %}" \
           "{{ " + locale_msg + ".format(username='@' + event.from_user.username) }}" \
           "{% else %}" \
           "{{ " + locale_msg + ".format(username=event.from_user.full_name) }}" \
           "{% endif %}"


dialog = Dialog(
    Window(
        Jinja(get_start_text("start_message")),
        state=UserStart.show
    )
)
