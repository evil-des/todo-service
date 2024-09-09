from typing import Any

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaId, MediaAttachment
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.media import StaticMedia, DynamicMedia
from aiogram_dialog.widgets.text import Format, Const, Jinja
from aiogram_dialog.widgets.kbd import WebApp, Button, Url, Group, ScrollingGroup, Select, Back
from app.utils.get_settings import get_settings
from magic_filter import F
from datetime import datetime, timedelta
from random import randint

from app.states.user import UserMainMenu


settings = get_settings()

# windows = {
#     "guide": UserMainMenu.guide,
#     "stats": UserMainMenu.stats
# }


def get_stats_text():
    return "{{ middleware_data[locales][stats].format(total_earned_RUB={total_earned}) }}"


async def get_stats(dialog_manager: DialogManager, **kwargs):
    k, x, z = 50, 34.2, 1.9
    initial_day = datetime(year=2024, month=1, day=1)

    stats = {
        "users_amount": int(100 * z * (datetime.today() - initial_day).days),
        "total_earned_RUB": int(600 * k * (datetime.today() - initial_day).days),
        "today_earned_RUB": int(100 * x * (datetime.today() - initial_day).days),
        "total_earned_USD": int(600 / 95.35 * k * (datetime.today() - initial_day).days),
        "today_earned_USD": int(100 / 95.35 * x * (datetime.today() - initial_day).days)
    }

    return {"stats": dialog_manager.middleware_data["locales"]["stats"].format(**stats)}


async def get_guide_games(dialog_manager: DialogManager, **kwargs):
    # return {"guide": dialog_manager.middleware_data["locales"]["guide"].format()}
    print(dialog_manager.middleware_data["locales"]["signals_menu"].values())
    return {
        "games": dialog_manager.middleware_data["locales"]["signals_menu"].values()
    }


async def on_game_selected(callback: CallbackQuery, widget: Any,
                           dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data.update(selected_game=item_id)
    await dialog_manager.switch_to(UserMainMenu.guide)


async def get_guide(dialog_manager: DialogManager, **kwargs):
    game: str = dialog_manager.dialog_data.get("selected_game")
    games = dialog_manager.middleware_data["locales"]["signals_menu"]
    video = None

    if game == games["mines"]:
        video = MediaAttachment(ContentType.VIDEO, url="https://i.imgur.com/JEIVyFW.mp4")
    elif game == games["lucky_jet"]:
        video = MediaAttachment(ContentType.VIDEO, url="https://i.imgur.com/g56AirX.mp4")

    return {
        "guide": dialog_manager.middleware_data["locales"]["guide"].format(game=game),
        "video": video
    }


dialog = Dialog(
    Window(
        Format("{middleware_data[locales][signals]}"),
        WebApp(Format("{middleware_data[locales][signals_menu][mines]}"), url=Const(settings.WEB_APP_MINES)),
        WebApp(Format("{middleware_data[locales][signals_menu][lucky_jet]}"), url=Const(settings.WEB_APP_LUCKY_JET)),
        state=UserMainMenu.signals
    ),
    Window(
        Format("<b>{middleware_data[locales][deposit]}</b>"),
        StaticMedia(url="https://i.imgur.com/HsxSNL7.jpeg"),
        Url(Format("{middleware_data[locales][deposit_btn]}"), url=Const("https://1woyz.com")),
        state=UserMainMenu.deposit
    ),
    Window(
        Format("{middleware_data[locales][guide_games]}"),
        ScrollingGroup(
            Select(
                id="select_game",
                item_id_getter=lambda x: x,
                items="games",
                text=Format("{item}"),
                on_click=on_game_selected
            ),
            height=2,
            hide_on_single_page=True,
            id="sg"
        ),
        getter=get_guide_games,
        state=UserMainMenu.guide_games
    ),
    Window(
        Format("{guide}"),
        DynamicMedia("video"),

        getter=get_guide,
        state=UserMainMenu.guide
    ),
    Window(
        Format("{stats}"),
        getter=get_stats,
        state=UserMainMenu.stats
    ),
    # *[
    #     Window(
    #         Format("{middleware_data[locales]" + f"[{key}]" + "}"),
    #         state=item
    #     )
    #     for key, item in windows.items()
    # ]
)
