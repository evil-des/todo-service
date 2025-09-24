from aiogram.fsm.state import State, StatesGroup


class UserStart(StatesGroup):
    # menu = State()
    show = State()


class ChooseLanguage(StatesGroup):
    show = State()
    command = State()
    language_changed = State()
