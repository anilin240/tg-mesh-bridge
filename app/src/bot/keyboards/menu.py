from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from common.i18n import t

class MenuCB(CallbackData, prefix="m"):
    section: str
    action: str | None = None
    id: int | None = None

def top_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "menu.messages"), callback_data=MenuCB(section="messages").pack())],
        [InlineKeyboardButton(text=t(lang, "menu.devices"),  callback_data=MenuCB(section="dev").pack())],
        [InlineKeyboardButton(text=t(lang, "menu.network"),  callback_data=MenuCB(section="network").pack())],
        [InlineKeyboardButton(text=t(lang, "menu.help"),     callback_data=MenuCB(section="help").pack())],
    ])

def messages_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "messages.show"),   callback_data=MenuCB(section="messages", action="show").pack())],
        [InlineKeyboardButton(text=t(lang, "messages.change"), callback_data=MenuCB(section="messages", action="change").pack())],
        [InlineKeyboardButton(text=t(lang, "messages.set"),    callback_data=MenuCB(section="messages", action="set").pack())],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data=MenuCB(section="main").pack())],
    ])

def dev_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "dev.add"),    callback_data=MenuCB(section="dev", action="add").pack())],
        [InlineKeyboardButton(text=t(lang, "dev.list"),   callback_data=MenuCB(section="dev", action="list").pack())],
        [InlineKeyboardButton(text=t(lang, "dev.edit"),   callback_data=MenuCB(section="dev", action="edit").pack())],
        [InlineKeyboardButton(text=t(lang, "dev.delete"), callback_data=MenuCB(section="dev", action="delete").pack())],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data=MenuCB(section="main").pack())],
    ])

def dev_actions_menu(lang: str, node_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "dev.action.write"),   callback_data=MenuCB(section="dev", action="write",  id=node_id).pack())],
        [InlineKeyboardButton(text=t(lang, "dev.action.rename"),  callback_data=MenuCB(section="dev", action="rename", id=node_id).pack())],
        [InlineKeyboardButton(text=t(lang, "dev.action.delete"),  callback_data=MenuCB(section="dev", action="del_one", id=node_id).pack())],
    ])

def network_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "nearby.refresh"), callback_data=MenuCB(section="network", action="refresh").pack())],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data=MenuCB(section="main").pack())],
    ])
