from aiogram_dialog import Dialog, DialogManager, Window, ShowMode
from aiogram_dialog.widgets.text import Const, Jinja

from app.dialogs.common import CommonElements
from app.services.repo import Repo
from app.states.admin import MinWithdrawAmount, StatsMenu, Channels


async def get_stats(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.middleware_data["repo"]
    stats = await repo.admin_dao.get_stats()
    return {"stats": stats}


dialog = Dialog(
    Window(
        Jinja(
            "{% for key, value in stats.items() %}"
            "{{ key }}: <code>{{ value }}</code>\n"
            "{% endfor %}"
        ),
        getter=get_stats,
        state=StatsMenu.show
    )
)
