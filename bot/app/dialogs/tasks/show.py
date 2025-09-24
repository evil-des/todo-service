from aiogram_dialog import Dialog
from app.models import TaskFilter
from app.utils.get_settings import get_settings
from app.states.task import TaskShowState
from app.windows.create_tag_window import CreateTagWindow
from app.windows.listing import TasksWindow
from app.windows import TaskInfoWindow, DeleteTaskWindow
from app.windows.listing.tags_window import TagsWindow

settings = get_settings()


dialog = Dialog(
    TasksWindow(
        state=TaskShowState.tasks,
        switch_to=TaskShowState.task_info,
    ),
    TasksWindow(
        state=TaskShowState.filtered_tasks,
        switch_to=TaskShowState.task_info,
        filter=TaskFilter(BY_TAG=True),
    ),

    TagsWindow(
        state=TaskShowState.tags,
        switch_to=TaskShowState.filtered_tasks,
    ),
    CreateTagWindow(state=TaskShowState.add_tag),

    TaskInfoWindow(state=TaskShowState.task_info),
    DeleteTaskWindow(state=TaskShowState.delete_task),
)
