from aiogram import Router

from . import start, lang, menu


def prepare_router() -> Router:
    user_router = Router(name=__name__)
    user_router.include_router(start.router)
    user_router.include_router(lang.router)
    user_router.include_router(menu.router)
    return user_router
