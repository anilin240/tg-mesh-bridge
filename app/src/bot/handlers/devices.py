from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.keyboards.menu import dev_menu, dev_actions_menu, top_menu
from common.i18n import t
from bot.services.users import get_or_create_user
from bridge.mqtt import publish_downlink
from bridge.repo import (
    get_user_devices,
    link_node_to_user_manual,
    rename_user_device,
    delete_user_device,
    get_device_by_id_for_user,
)

dev_router = Router()

# Удаляем дублирующие FSM состояния - всё обрабатывается в main.py через UserState.REGISTERING
# class DevFSM(StatesGroup):
#     wait_node_id_for_add = State()
#     wait_label_for_rename = State()
#     wait_text_for_write = State()

def lang_for(obj) -> str:
    try:
        u = get_or_create_user(obj.from_user.id, getattr(obj, "chat", getattr(obj.message, "chat", None)).id)
        return u.language or "ru"
    except Exception:
        return "ru"

# Удаляем дублирующие обработчики - теперь всё обрабатывается в main.py через UserState.REGISTERING
# @dev_router.message(DevFSM.wait_node_id_for_add)
# async def dev_add_value(m: Message, state: FSMContext):
#     ...

# @dev_router.message(DevFSM.wait_label_for_rename)
# async def dev_rename_value(m: Message, state: FSMContext):
#     ...

# @dev_router.message(DevFSM.wait_text_for_write)
# async def dev_write_value(m: Message, state: FSMContext):
#     ...
