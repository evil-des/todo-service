from typing import List, Union, Optional, Dict, Any
from urllib.parse import urlparse

from aiogram import F
from aiogram.enums import ContentType
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, Window, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.common import ManagedScroll, Whenable
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput, TextInput, BaseInput
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Jinja, Format
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Group, StubScroll, NumberedPager, Url, Select, Back, \
    ScrollingGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from aiogram.utils.keyboard import InlineKeyboardBuilder, ButtonType

from app.dialogs.common import CommonElements
from app.services.repo import Repo
from app.models.user import User
from app.states.admin import Mailing
from app.data.locales import locales
from pydantic import BaseModel
from pydantic_core import from_json

ALLOWED_MEDIA = [ContentType.PHOTO, ContentType.VIDEO, ContentType.ANIMATION]


class MediaItem(BaseModel):
    file_id: str
    file_unique_id: str
    content_type: ContentType


class InputMedia(BaseModel):
    type: str
    media: str


class MarkupButton(BaseModel):
    id: int
    text: Optional[str] = "Не установлено"
    url: Optional[str] = "Не установлено"


def get_pydantic_list(dialog_manager: DialogManager, key: str, model: BaseModel) -> List[BaseModel | Any]:
    dialog_manager.dialog_data.setdefault(key, [])
    items: List[str] = dialog_manager.dialog_data.get(key, [])
    if not items:
        return []

    return [model.model_validate_json(item) for item in items]


async def on_timeout_error(message: Message, *args) -> None:
    await message.answer("<b>Ошибка:</b> при вводе значения тайм-аута разрешены только цифры")


def is_media_present(data: dict, widget: Whenable, manager: DialogManager):
    return not data["start_data"].get("is_verified")


async def on_mailing_type_click(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    dialog_manager.dialog_data.update(mailing_type=button.widget_id)
    await dialog_manager.switch_to(Mailing.set_lang)


async def on_users_lang_click(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    dialog_manager.dialog_data.update(language=button.widget_id)
    await dialog_manager.switch_to(Mailing.set_media)


async def on_new_message_success(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, *args
) -> None:
    msg_type: str = widget.widget.widget_id.split("_")[-1]
    is_verified = True if msg_type == "verified" else False

    dialog_manager.dialog_data.update(message=message.text, is_verified=is_verified)
    await dialog_manager.switch_to(Mailing.confirm, show_mode=ShowMode.SEND)


async def on_media_input(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager,
):
    dialog_manager.dialog_data.setdefault("media_list", [])
    media_list: List[MediaItem | str] = get_pydantic_list(dialog_manager, "media_list", MediaItem)

    # (message.photo[-1].file_id, message.photo[-1].file_unique_id)
    media, content_type = None, None

    if message.photo:
        media = message.photo[-1]
        content_type = ContentType.PHOTO
    elif message.video:
        media = message.video
        content_type = ContentType.VIDEO
    elif message.animation:
        media = message.animation
        content_type = ContentType.ANIMATION

    media_list.append(
        MediaItem(
            file_id=media.file_id,
            file_unique_id=media.file_unique_id,
            content_type=content_type,
        ).model_dump_json()
    )

    dialog_manager.dialog_data.update(media_list=media_list)


async def on_media_delete(
        callback: CallbackQuery, widget: Button, dialog_manager: DialogManager,
):
    scroll: ManagedScroll = dialog_manager.find("pages")
    page_number = await scroll.get_page()
    media_list = dialog_manager.dialog_data.get("media_list", [])
    del media_list[page_number]
    if page_number > 0:
        await scroll.set_page(page_number - 1)


async def media_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    scroll: ManagedScroll = dialog_manager.find("pages")
    page_number = await scroll.get_page()
    media_list = get_pydantic_list(dialog_manager, "media_list", MediaItem)
    if media_list:
        media_item: MediaItem = media_list[page_number]
        media = MediaAttachment(
            file_id=MediaId(media_item.file_id, media_item.file_unique_id),
            type=media_item.content_type,
        )
    else:
        media = MediaAttachment(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Image_not_available.png/800px-Image_not_available.png?20210219185637",
            # noqa: E501
            type=ContentType.PHOTO,
        )
    return {
        "media_count": len(media_list),
        "page_number": page_number + 1,
        "media": media,
    }


async def on_message_input(
        message: Message, m_input: MessageInput, dialog_manager: DialogManager, *args
) -> None:
    media_list: List[MediaItem] = get_pydantic_list(dialog_manager, "media_list", MediaItem)
    dialog_manager.dialog_data.update(
        text=message.html_text.strip(),
        caption=message.text.strip(),
        caption_entities=[item.model_dump_json() for item in message.entities]
    )

    if not media_list:
        await dialog_manager.switch_to(Mailing.markup)
    else:
        await send_message_preview(message, dialog_manager, media_list=media_list)


async def on_skip_text(
        callback: CallbackQuery, widget: Button, dialog_manager: DialogManager,
):
    await send_message_preview(callback.message, dialog_manager, skip_text=True)


async def send_message_preview(
        message: Message,
        dialog_manager: DialogManager,
        skip_text: bool = False,
        media_list: List[MediaItem] = None
):
    text, caption, caption_entities = None, None, None
    markup = None

    if not skip_text:
        text = dialog_manager.dialog_data.get("text")

        caption = dialog_manager.dialog_data.get("caption")
        caption_entities = get_pydantic_list(dialog_manager, "caption_entities", MessageEntity)

        markup = get_markup(dialog_manager)

    if media_list is None:
        media_list: List[MediaItem] = get_pydantic_list(dialog_manager, "media_list", MediaItem)

    await message.answer("Так будет выглядеть сообщение, которое увидят пользователи:")

    if media_list:
        media_group = get_media_group_builder(media_list, text=caption, caption_entities=caption_entities)
        await message.answer_media_group(media_group.build())
    else:
        await message.answer(text, parse_mode="html", reply_markup=markup)

    await dialog_manager.switch_to(Mailing.confirm, show_mode=ShowMode.SEND)


def get_markup(dialog_manager: DialogManager) -> InlineKeyboardMarkup | None:
    markup_builder = InlineKeyboardBuilder()
    buttons: List[MarkupButton] = get_pydantic_list(dialog_manager, "buttons", MarkupButton)

    if not buttons:
        return None

    markup_builder.row(*[
        InlineKeyboardButton(text=item.text, url=item.url)
        for item in buttons
    ], width=1)

    return markup_builder.as_markup()


def get_media_group_builder(media_list: List[MediaItem], text: str = None, caption_entities=None) -> MediaGroupBuilder:
    media_group = MediaGroupBuilder()

    if text:
        media_group.caption = text
        media_group.caption_entities = caption_entities

    for item in media_list:
        media_group.add(type=item.content_type, media=item.file_id)

    return media_group


async def on_confirm_click(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    repo: Repo = manager.middleware_data["repo"]
    mailing_type: str = manager.dialog_data.get("mailing_type")

    media_list: List[MediaItem] | None = get_pydantic_list(manager, "media_list", MediaItem)
    buttons: List[MarkupButton] | list | None = get_pydantic_list(manager, "buttons", MarkupButton)

    input_media = None
    if media_list:
        input_media = [{"type": item.content_type, "media": item.file_id} for item in media_list]

    if buttons:
        buttons = [{"text": item.text, "url": item.url} for item in buttons]

    is_verified, all_users = True, False
    if mailing_type == "not_verified":
        is_verified = False
    elif mailing_type == "all_users":
        all_users = True

    status = await repo.admin_dao.start_mailing(
        text=manager.dialog_data.get("text"),
        media=input_media,
        buttons=buttons,
        language=manager.dialog_data.get("language"),
        is_verified=is_verified,
        timeout=0.3,
        all_users=all_users,
        admin_chat_id=callback.from_user.id
    )

    if status:
        await callback.message.edit_text("Рассылка успешно запущена!")
        await manager.done()
    else:
        await callback.message.edit_text("При запуске рассылки произошла ошибка!")
        await manager.done()


async def media_count_getter(dialog_manager: DialogManager, **kwargs):
    media_list: List[MediaItem] = dialog_manager.dialog_data.get("media_list")
    if not media_list:
        return {"media_count": 0}
    return {"media_count": len(media_list)}


async def markup_getter(dialog_manager: DialogManager, **kwargs):
    buttons: List[MarkupButton] = get_pydantic_list(dialog_manager, "buttons", MarkupButton)
    return {
        "buttons": buttons,
        "buttons_count": len(buttons)
    }


async def button_info_getter(dialog_manager: DialogManager, **kwargs):
    buttons: List[MarkupButton | str] = get_pydantic_list(dialog_manager, "buttons", MarkupButton)
    buttons_id: int = dialog_manager.dialog_data.get("buttons_id")

    if not buttons_id:
        buttons_id = len(buttons) + 1

        button = MarkupButton(id=buttons_id)
        buttons.append(button.model_dump_json())

        dialog_manager.dialog_data.update(buttons=buttons, buttons_id=buttons_id)
    else:
        button: MarkupButton = list(filter(lambda x: x.id == buttons_id, buttons))[0]

    return {
        "id": button.id,
        "name": button.text,
        "link": button.url.lstrip("https://").lstrip("http://"),
        "buttons_count": len(buttons)
    }


async def on_markup_button_click(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
        item_id: str
):
    manager.dialog_data.update(buttons_id=int(item_id))
    await manager.switch_to(Mailing.markup_button)


async def on_markup_skip_click(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    manager.dialog_data.update(buttons=None, buttons_id=None)
    await manager.switch_to(Mailing.confirm)


async def on_button_name_input(
        message: Message, m_input: MessageInput, dialog_manager: DialogManager, *args
) -> None:
    buttons: List[MarkupButton] = get_pydantic_list(dialog_manager, "buttons", MarkupButton)
    buttons_id: int = dialog_manager.dialog_data.get("buttons_id")

    button: MarkupButton = list(filter(lambda x: x.id == buttons_id, buttons))[0]

    button.text = message.text.strip()
    dialog_manager.dialog_data.update(buttons=[item.model_dump_json() for item in buttons])

    await dialog_manager.switch_to(Mailing.markup_button)


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


async def on_button_link_input(
        message: Message, m_input: MessageInput, dialog_manager: DialogManager, *args
) -> None:
    if not uri_validator(message.text.strip()):
        await message.answer("Вы отправили не ссылку!")
        return

    buttons: List[MarkupButton] = get_pydantic_list(dialog_manager, "buttons", MarkupButton)
    buttons_id: int = dialog_manager.dialog_data.get("buttons_id")

    button: MarkupButton = list(filter(lambda x: x.id == buttons_id, buttons))[0]

    button.url = message.text.strip()
    dialog_manager.dialog_data.update(buttons=[item.model_dump_json() for item in buttons])

    await dialog_manager.switch_to(Mailing.markup_button)


async def on_button_delete(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    buttons: List[MarkupButton] = get_pydantic_list(dialog_manager, "buttons", MarkupButton)
    buttons_id: int = dialog_manager.dialog_data.get("buttons_id")

    for i, item in enumerate(buttons):
        if item.id == buttons_id:
            del buttons[i]
            break

    await dialog_manager.switch_to(Mailing.markup)


async def switch_to_button_info(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    if button.widget_id == "add":
        dialog_manager.dialog_data.update(buttons_id=None)

    await dialog_manager.switch_to(Mailing.markup_button)


async def on_markup_done(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    await send_message_preview(callback.message, dialog_manager)


dialog = Dialog(
    Window(
        Const("Выберите тип пользователей, которые получат рассылку:"),
        Group(*[
            Button(Const(name), id=users_type, on_click=on_mailing_type_click)
            for name, users_type in [
                ["Прошли рег-ю", "verified"],
                ["Не прошли рег-ю", "not_verified"],
                ["Всем", "all_users"],
            ]
        ]),
        state=Mailing.show_types
    ),
    Window(
        Const("Выберите язык пользователей:"),
        Group(*[
            Button(Const(name), id=users_type, on_click=on_users_lang_click)
            for name, users_type in [
                ["Русский 🇷🇺", "ru"],
                ["Английский 🇺🇸", "en"],
                ["Испанский 🇪🇸", "es"],
                ["Французский 🇫🇷", "fr"],
            ]
        ]),
        state=Mailing.set_lang
    ),
    Window(
        Const("Отправьте фото или другие медиа:"),
        Group(
            SwitchTo(Const("Пропустить"), state=Mailing.set_message_text, id="skip_media"),
            SwitchTo(Const("Готово ✅"), state=Mailing.set_message_text, id="done", when=F["media_count"] >= 1),
            width=2
        ),

        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Button(
            Format("🗑️ Удалить фото #{page_number}"),
            id="del",
            on_click=on_media_delete,
            when="media_count",
            # Alternative F['media_count']
        ),
        MessageInput(
            content_types=ALLOWED_MEDIA,
            func=on_media_input
        ),
        getter=media_getter,
        state=Mailing.set_media
    ),
    Window(
        Const("Отправьте текст, который увидят пользователи:"),
        Button(Const("Пропустить"), id="skip_text", on_click=on_skip_text, when=F["media_count"] >= 1),

        MessageInput(
            content_types=ContentType.TEXT,
            func=on_message_input
        ),
        getter=media_count_getter,
        state=Mailing.set_message_text
    ),
    Window(
        Const("Настройте кнопки, которые увидят пользователи:"),
        ScrollingGroup(
            Select(
                id="buttons",
                item_id_getter=lambda x: x.id,
                items="buttons",
                text=Format("{item.text}"),
                on_click=on_markup_button_click,
                when=F["buttons_count"] >= 1,
            ),
            id="sg",
            height=5,
            width=1,
            hide_on_single_page=True
        ),
        Button(Const("Добавить +"), id="add", on_click=switch_to_button_info),
        Group(
            Button(Const("Пропустить"), on_click=on_markup_skip_click, id="skip_markup"),
            Button(Const("Готово ✅"), on_click=on_markup_done, id="done", when=F["buttons_count"] >= 1),
            width=2
        ),
        getter=markup_getter,
        state=Mailing.markup,
    ),
    Window(
        Const("Настройки кнопки:"),
        Group(
            SwitchTo(Format("Название - {name}"), id="name", state=Mailing.button_name),
            SwitchTo(Format("Ссылка - {link}"), id="link", state=Mailing.button_link),
        ),
        Group(
            Button(Const("Удалить"), id="delete", on_click=on_button_delete),
            SwitchTo(
                Const("Готово ✅"),
                id="done",
                state=Mailing.markup,
                when=F["name"] != "Не установлено" and
                     F["link"] != "Не установлено"
            ),
            width=2
        ),
        getter=button_info_getter,
        state=Mailing.markup_button
    ),
    Window(
        Const("Введите название для кнопки:"),
        MessageInput(content_types=ContentType.TEXT, func=on_button_name_input),
        state=Mailing.button_name
    ),
    Window(
        Const("Отправьте ссылку для кнопки:"),
        MessageInput(content_types=ContentType.TEXT, func=on_button_link_input),
        state=Mailing.button_link
    ),
    Window(
        Const("Запустить рассылку?"),
        CommonElements.confirm_n_cancel(on_confirm_click, CommonElements.on_cancel_click),
        state=Mailing.confirm
    )
)
