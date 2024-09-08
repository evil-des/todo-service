from api.services.todo_core.crud import TodoCoreCRUD
from api.settings import settings


def get_todo_core_crud() -> TodoCoreCRUD:
    return TodoCoreCRUD(base_url=settings.todo_core.base_url)
