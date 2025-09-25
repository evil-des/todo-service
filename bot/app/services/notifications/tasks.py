import datetime
from zoneinfo import ZoneInfo
from celery import shared_task
from aiogram import Bot
import asyncio

from app.services.internal import TODOCore, CommentsCRUD
from app.services.dao.task import TaskDAO
from app.utils.get_settings import get_settings


settings = get_settings()


@shared_task(name="send_telegram", bind=True, max_retries=5)
def send_telegram(self, chat_id: str, text: str, task_id: int):
    async def run():
        bot = Bot(token=settings.TOKEN)
        todo_core = TODOCore(settings.CORE_BASE_URL)
        comments_crud = CommentsCRUD(settings.COMMENTS_BASE_URL)
        task_dao = TaskDAO(todo_core, comments_crud)

        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"🗓️ Выполните задачу #{task_id} - {text}",
            )
            await task_dao.mark_notified(
                task_id,
                datetime.datetime.now(),
            )
        finally:
            await bot.session.close()

    try:
        asyncio.run(run())
    except Exception as e:
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
