from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from bot.states import state_manager, UserState
from common.i18n import t
from bot.keyboards.menu import top_menu

fallback_router = Router()

def user_lang(obj) -> str:
    """Получить язык пользователя"""
    from common.db import SessionLocal
    from common.models import User
    with SessionLocal() as session:
        u = session.get(User, obj.from_user.id)
        return (u.language if u else "en") or "en"

@fallback_router.message()
async def handle_unknown_messages(message: Message) -> None:
    """Обработчик для всех неизвестных текстовых сообщений (низкий приоритет)"""
    txt = (message.text or "").strip()
    
    # Пропускаем команды
    if txt.startswith("/"):
        return
        
    # Проверяем UserState состояния (state_manager)
    if state_manager.is_in_state(message.from_user.id, UserState.CHANGING_CODE) or \
       state_manager.is_in_state(message.from_user.id, UserState.REGISTERING):
        return
        
    # Проверяем FSM состояния (dev_router обрабатывает их с высоким приоритетом)
    # Если пользователь в FSM состоянии, не обрабатываем
    # УДАЛЕНО: DevFSM состояния больше не используются, всё через UserState.REGISTERING
        
    # Получаем язык пользователя
    lang = user_lang(message)
    
    # Отвечаем подсказкой с главным меню
    await message.answer(t(lang, "unknown_message"), reply_markup=top_menu(lang))
