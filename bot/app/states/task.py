from aiogram.fsm.state import State, StatesGroup


class TODOManage(StatesGroup):
    tasks = State()
    filtered_tasks = State()
    tags = State()
    task_info = State()
    delete_task = State()

    # add task
    add_task_set_title = State()
    add_task_set_desc = State()
    add_task_set_remind_time__calendar = State()
    add_task_set_remind_time__time = State()
    add_task_confirm = State()

    # add tag
    add_tag = State()


class TaskShowState(StatesGroup):
    tasks = State()
    filtered_tasks = State()
    tags = State()
    task_info = State()
    delete_task = State()

    # add tag
    add_tag = State()


class TaskCreateState(StatesGroup):
    set_title = State()
    set_desc = State()
    set_remind_time__calendar = State()
    set_remind_time__time = State()
    confirm = State()
