import asyncio

import aiojobs
import orjson
import structlog
from aiocache import Cache
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram_dialog import setup_dialogs
from aiohttp import web
from redis.asyncio import Redis

from app import dialogs, handlers, utils, web_handlers
from app.middlewares import (  # UserObjectMiddleware,
    InternalServicesMiddleware,
    RepoMiddleware,
    StructLoggingMiddleware,
    LangMiddleware
)
from app.utils.get_settings import get_settings
from app.data.locales import locales

settings = get_settings()


async def create_db_connections(dp: Dispatcher) -> Cache:
    logger: structlog.typing.FilteringBoundLogger = dp["business_logger"]
    if settings.DEBUG:
        cache = Cache(cache_class=Cache.MEMORY)
    else:
        cache = Cache(
            cache_class=Cache.REDIS,
            endpoint=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_CACHE_DB,
        )

    dp["temp_bot_cloud_session"] = utils.smart_session.SmartAiogramAiohttpSession(
        json_loads=orjson.loads,
        logger=dp["aiogram_session_logger"],
    )

    return cache


async def close_db_connections(dp: Dispatcher) -> None:
    if "temp_bot_cloud_session" in dp.workflow_data:
        temp_bot_cloud_session: AiohttpSession = dp["temp_bot_cloud_session"]
        await temp_bot_cloud_session.close()
    if "temp_bot_local_session" in dp.workflow_data:
        temp_bot_local_session: AiohttpSession = dp["temp_bot_local_session"]
        await temp_bot_local_session.close()
    if "cache" in dp.workflow_data:
        cache: Cache = dp["cache"]  # type: ignore[type-arg]
        await cache.REDIS.close()


def register_dialogs(dp: Dispatcher):
    all_dialogs = [
        dialogs.user.start_message.dialog,
        dialogs.user.tasks.dialog,
        dialogs.user.choose_lang.dialog
    ]
    for dialog in all_dialogs:
        dp.include_router(dialog)

    setup_dialogs(dp)  # aiogram-dialog init


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.user.prepare_router())

    register_dialogs(dp)


def setup_middlewares(dp: Dispatcher, cache: Cache) -> None:
    dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))
    # dp.update.middleware(DBSessionMiddleware(session_pool=async_session))
    dp.update.middleware(
        InternalServicesMiddleware(
            comments_base=settings.COMMENTS_BASE_URL,
            todo_core_base=settings.CORE_BASE_URL
        )
    )
    dp.update.middleware(RepoMiddleware(cache=cache))
    # dp.update.middleware(BannedUserMiddleware())
    dp.update.middleware(LangMiddleware(locales))
    # dp.update.middleware(UserObjectMiddleware())


def setup_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(type="aiogram")
    dp["db_logger"] = utils.logging.setup_logger().bind(type="db")
    dp["cache_logger"] = utils.logging.setup_logger().bind(type="cache")
    dp["business_logger"] = utils.logging.setup_logger().bind(type="business")


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")

    cache = await create_db_connections(dp)
    setup_handlers(dp)
    setup_middlewares(dp, cache=cache)

    logger.info("Configured aiogram")


async def aiohttp_on_startup(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_startup(**workflow_data)


async def aiohttp_on_shutdown(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    for i in [app, *app._subapps]:  # dirty
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                dp["aiogram_logger"].info(
                    f"Waiting for {scheduler.pending_count} tasks to complete"
                )
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_shutdown(**workflow_data)


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)
    webhook_logger = dispatcher["aiogram_logger"].bind(
        webhook_url=settings.MAIN_WEBHOOK_ADDRESS
    )
    webhook_logger.debug("Configuring webhook")
    await bot.set_webhook(
        url=settings.MAIN_WEBHOOK_ADDRESS.format(
            token=settings.TOKEN, bot_id=settings.TOKEN.split(":")[0]
        ),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=settings.MAIN_WEBHOOK_SECRET_TOKEN,
    )
    webhook_logger.info("Configured webhook")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping webhook")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped webhook")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)
    dispatcher["aiogram_logger"].info("Started polling")


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


async def setup_aiohttp_app(bot: Bot, dp: Dispatcher) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        ("/tg/webhooks/", web_handlers.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dp"] = dp
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dp"] = dp
    app["scheduler"] = scheduler
    app.on_startup.append(aiohttp_on_startup)
    app.on_shutdown.append(aiohttp_on_shutdown)
    return app


def main() -> None:
    aiogram_session_logger = utils.logging.setup_logger().bind(type="aiogram_session")

    session = utils.smart_session.SmartAiogramAiohttpSession(
        json_loads=orjson.loads,
        logger=aiogram_session_logger,
    )
    bot = Bot(settings.TOKEN, parse_mode="HTML", session=session)

    if settings.DEBUG:
        storage = MemoryStorage()
    else:
        storage = RedisStorage(
            redis=Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_STORAGE_DB,
            ),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
        # await redis.flushdb()

    dp = Dispatcher(storage=storage)
    dp["aiogram_session_logger"] = aiogram_session_logger

    if settings.USE_WEBHOOK:
        dp.startup.register(aiogram_on_startup_webhook)
        dp.shutdown.register(aiogram_on_shutdown_webhook)
        web.run_app(
            asyncio.run(setup_aiohttp_app(bot, dp)),
            handle_signals=True,
            host=settings.MAIN_WEBHOOK_LISTENING_HOST,
            port=settings.MAIN_WEBHOOK_LISTENING_PORT,
        )
    else:
        dp.startup.register(aiogram_on_startup_polling)
        dp.shutdown.register(aiogram_on_shutdown_polling)
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
