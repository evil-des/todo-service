from typing import List, Any

from aiogram_dialog import DialogManager
from pydantic import BaseModel


def get_pydantic_list(dialog_manager: DialogManager, key: str, model: BaseModel) -> List[BaseModel | Any]:
    dialog_manager.dialog_data.setdefault(key, [])
    items: List[str] = dialog_manager.dialog_data.get(key, [])
    if not items:
        return []

    return [model.model_validate_json(item) for item in items]
