from aiogram.fsm.state import State, StatesGroup


class UserStart(StatesGroup):
    # menu = State()
    show = State()


class UserMainMenu(StatesGroup):
    signals = State()
    guide_games = State()
    guide = State()
    stats = State()
    deposit = State()


class ChooseLanguage(StatesGroup):
    show = State()
    command = State()
    language_changed = State()
