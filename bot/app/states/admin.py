from aiogram.fsm.state import State, StatesGroup


class SettingsMenu(StatesGroup):
    show = State()


class StatsMenu(StatesGroup):
    show = State()


class ExchangeRate(StatesGroup):
    info = State()
    set_rub = State()


class MinWithdrawAmount(StatesGroup):
    info = State()
    set_rub = State()


class Channels(StatesGroup):
    all_channels = State()
    add_new = State()
    delete = State()
    info = State()


# REF SYSTEM SETTINGS

class RefSystem(StatesGroup):
    all_settings = State()


class RefBasics(StatesGroup):
    coin = State()
    energy = State()

    set_coin = State()
    set_energy = State()


class RefStatuses(StatesGroup):
    first_withdraw = State()
    referral_deposit = State()
    referral_deposit_bonus = State()


class RefReferralDepositStatus(StatesGroup):
    show = State()
    set = State()


class RefFirstWithdrawStatus(StatesGroup):
    show = State()
    set = State()


class RefReferralDepositBonus(StatesGroup):
    show = State()
    set = State()


class RefReferralDepositBonusStatus(StatesGroup):
    show = State()
    set = State()

# REF SYSTEM END


class WithdrawListing(StatesGroup):
    choose_mode = State()

    all_requests = State()
    closed_requests = State()
    date_opened_desc = State()

    request_info = State()
    closed_request_info = State()

    cancel_request = State()
    approve_request = State()

    user_referrals = State()
    referral_info = State()


class UsersListing(StatesGroup):
    all_users = State()

    user_info = State()
    ban_user = State()

    user_referrals = State()
    referral_info = State()
    delete_referral = State()

    search = State()


class Mailing(StatesGroup):
    show_types = State()
    set_lang = State()

    set_media = State()

    set_message_text = State()
    markup = State()
    markup_button = State()

    button_name = State()
    button_link = State()

    mailing_preview = State()
    confirm = State()
