from datetime import date
from typing import Callable

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button, Group, ScrollingGroup,
    Select, Back, SwitchTo, Calendar,
    ManagedCounter, Counter
)
from aiogram_dialog.widgets.text import Format

from app.dialogs.common import CommonElements
from app.models import TaskFilter
from app.utils.get_settings import get_settings
from magic_filter import F
from app.states.task import TODOManage, TaskCreateState
from app.windows.create_tag_window import CreateTagWindow
from app.windows.listing import TasksWindow
from app.windows import TaskInfoWindow, DeleteTaskWindow, CreateTaskWindow
from datetime import datetime

from app.windows.listing.tags_window import TagsWindow

settings = get_settings()


def time_format_checker(time_str):
    return datetime.strptime(str(time_str), "%H:%M")


def time_format_apply(time: datetime):
    return time.strftime("%H:%M")


def save_answer_to_dialog(
        key: str,
        type_factory: Callable = None,
):
    async def handler(
            tg_object: Message | CallbackQuery,
            widget: Widget,
            dialog_manager: DialogManager,
            *args,
    ):
        answer = args[0] if len(args) > 0 else None

        if tg_object is Message:
            answer = tg_object.text.strip()

        if type_factory:
            answer = type_factory(answer)

        print(f"ANSWER: {answer}")

        dialog_manager.dialog_data[key] = str(answer)
        await dialog_manager.next()

    return handler


def error_message(locale_name: str):
    async def handler(
            message: Message,
            widget: Widget,
            dialog_manager: DialogManager,
            *args,
    ):
        await message.answer(
            dialog_manager.middleware_data["locales"]
            ["tasks"]["add_task"][locale_name]
        )

    return handler


dialog = Dialog(
    CommonElements.input(
        id="title",
        text=Format("{middleware_data[locales][tasks][add_task][title]}"),
        on_success=save_answer_to_dialog(key="title"),
        cancel_only=True,
        state=TaskCreateState.set_title,
    ),

    CommonElements.input(
        id="desc",
        text=Format("{middleware_data[locales][tasks][add_task][description]}"),
        on_success=save_answer_to_dialog(key="description"),
        state=TaskCreateState.set_desc,
        skip=True,
    ),

    Window(
        Format("{middleware_data[locales][tasks][add_task][remind_time][date]}"),
        Calendar(
            id="calendar",
            on_click=save_answer_to_dialog(
                key="date",
            ),
        ),
        SwitchTo(
            Format("{middleware_data[locales][skip_btn]}"),
            id="skip_desc",
            state=TaskCreateState.confirm,
        ),
        state=TaskCreateState.set_remind_time__calendar,
    ),

    CommonElements.input(
        id="time",
        text=Format("{middleware_data[locales][tasks][add_task][remind_time][time]}"),
        on_success=save_answer_to_dialog(key="time", type_factory=time_format_apply),
        on_error=error_message("time_format"),
        type_factory=time_format_checker,
        state=TaskCreateState.set_remind_time__time,
    ),

    CreateTaskWindow(state=TaskCreateState.confirm),
)
