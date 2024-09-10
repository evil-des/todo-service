from datetime import date

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button, Group, ScrollingGroup,
    Select, Back, SwitchTo, Calendar,
    ManagedCounter, Counter
)
from aiogram_dialog.widgets.text import Format

from app.utils.get_settings import get_settings
from magic_filter import F
from app.states.user import TODOManage
from app.windows.listing import TasksWindow
from app.windows import TaskInfoWindow, DeleteTaskWindow, CreateTaskWindow
from datetime import datetime

settings = get_settings()


def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


async def on_task_title_input(
        message: Message, m_input: MessageInput, dialog_manager: DialogManager, *args
) -> None:
    dialog_manager.dialog_data.update(title=message.text.strip())
    await dialog_manager.next()


async def on_task_description_input(
        message: Message, m_input: MessageInput, dialog_manager: DialogManager, *args
) -> None:
    dialog_manager.dialog_data.update(description=message.text.strip())
    await dialog_manager.next()


async def on_date_selected(callback: CallbackQuery, widget,
                           dialog_manager: DialogManager, selected_date: date):
    print(str(selected_date))
    dialog_manager.dialog_data.update(date=str(selected_date))
    await dialog_manager.next()


async def on_task_time_input(
        message: Message, m_input: MessageInput, dialog_manager: DialogManager, *args
) -> None:
    if is_valid_time(message.text.strip()):
        dialog_manager.dialog_data.update(time=message.text.strip())
        await dialog_manager.next()
    else:
        await message.answer(
            dialog_manager.middleware_data["locales"]
            ["tasks"]["add_task"]["time_format"]
        )


dialog = Dialog(
    TasksWindow(state=TODOManage.tasks, switch_to=TODOManage.task_info),
    Window(
        Format("{middleware_data[locales][tasks][add_task][title]}"),
        MessageInput(
            content_types=ContentType.TEXT,
            func=on_task_title_input
        ),
        state=TODOManage.add_task_set_title
    ),
    Window(
        Format("{middleware_data[locales][tasks][add_task][description]}"),
        SwitchTo(
            Format("{middleware_data[locales][skip_btn]}"),
            id="skip_desc", state=TODOManage.add_task_set_desc
        ),

        MessageInput(
            content_types=ContentType.TEXT,
            func=on_task_description_input
        ),

        state=TODOManage.add_task_set_desc
    ),
    Window(
        Format("{middleware_data[locales][tasks][add_task][remind_time][date]}"),
        Calendar(id="calendar", on_click=on_date_selected),
        SwitchTo(
            Format("{middleware_data[locales][skip_btn]}"),
            id="skip_desc", state=TODOManage.add_task_confirm
        ),

        state=TODOManage.add_task_set_remind_time__calendar
    ),

    Window(
        Format("{middleware_data[locales][tasks][add_task][remind_time][time]}"),
        MessageInput(
            content_types=ContentType.TEXT,
            func=on_task_time_input
        ),

        state=TODOManage.add_task_set_remind_time__time
    ),

    CreateTaskWindow(state=TODOManage.add_task_confirm),

    TaskInfoWindow(state=TODOManage.task_info),
    DeleteTaskWindow(state=TODOManage.delete_task)
)
