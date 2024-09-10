from aiogram.fsm.state import State, StatesGroup


class UserStart(StatesGroup):
    # menu = State()
    show = State()


class TODOManage(StatesGroup):
    tasks = State()
    tags = State()
    task_info = State()
    delete_task = State()

    # add task
    add_task_set_title = State()
    add_task_set_desc = State()
    add_task_set_remind_time__calendar = State()
    add_task_set_remind_time__time = State()
    add_task_confirm = State()


class ChooseLanguage(StatesGroup):
    show = State()
    command = State()
    language_changed = State()
