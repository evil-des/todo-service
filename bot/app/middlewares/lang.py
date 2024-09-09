from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, Update, CallbackQuery, base
from app.services.api import API
from app.services.repo import Repo


class LangMiddleware(BaseMiddleware):
    def __init__(self, locales: dict):
        super().__init__()
        self.locales = locales

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        try:
            # print(f"EVENT: {event}")
            chat_id = event.chat.id
        except AttributeError:
            if hasattr(event, "callback_query") and event.callback_query is not None:
                chat_id = event.callback_query.from_user.id
            elif hasattr(event, "message") and event.message is not None:
                chat_id = event.message.chat.id
            else:
                return await handler(event, data)

        repo: Repo = data["repo"]
        user = await repo.user_dao.get_user(chat_id)
        if user is None:
            return await handler(event, data)

        data["locales"] = self.locales.get(user.language)
        print(data["locales"])
        return await handler(event, data)
