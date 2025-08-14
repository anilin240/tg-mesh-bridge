from __future__ import annotations

from loguru import logger
from sqlalchemy import select

from common.db import SessionLocal
from common.models import User
from common.shortcode import generate_code


def get_or_create_user(tg_user_id: int, tg_chat_id: int | None = None) -> User:
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.tg_user_id == tg_user_id)).scalar_one_or_none()
        if user:
            logger.info("User exists: {} (chat_id: {})", tg_user_id, tg_chat_id)
            # backfill chat id if provided
            if tg_chat_id is not None and getattr(user, "tg_chat_id", None) != tg_chat_id:
                try:
                    user.tg_chat_id = tg_chat_id
                    session.commit()
                    logger.info("Updated chat_id for user {}: {}", tg_user_id, tg_chat_id)
                except Exception:
                    session.rollback()
            return user
        user = User(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id, language="en", tg_code=generate_code())
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info("User created: {}", tg_user_id)
        return user


def regenerate_code(tg_user_id: int) -> str:
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.tg_user_id == tg_user_id)).scalar_one_or_none()
        if not user:
            # Create if not exists
            user = User(tg_user_id=tg_user_id, language="en", tg_code=generate_code())
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info("User created during regenerate: {}", tg_user_id)
            return user.tg_code or ""
        user.tg_code = generate_code()
        session.commit()
        session.refresh(user)
        logger.info("User code regenerated: {}", tg_user_id)
        return user.tg_code or ""


def set_custom_code(tg_user_id: int, new_code: str, tg_chat_id: int | None = None) -> tuple[bool, str]:
    """Attempt to set a custom code for the user.

    Returns (ok, message_key) where message_key is i18n key for feedback.
    """
    new_code = (new_code or "").upper().strip()
    if not (4 <= len(new_code) <= 8):
        return False, "link_set_invalid"
    # Проверяем, что код содержит только буквы и цифры
    if not new_code.isalnum():
        return False, "link_set_invalid"

    with SessionLocal() as session:
        user = session.execute(select(User).where(User.tg_user_id == tg_user_id)).scalar_one_or_none()
        if not user:
            user = User(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id, language="en")
            session.add(user)
            session.flush()
        else:
            # Обновляем chat_id если он передан
            if tg_chat_id is not None:
                user.tg_chat_id = tg_chat_id
        # Ensure uniqueness by attempting commit; unique constraint on tg_code
        user.tg_code = new_code
        try:
            session.commit()
        except Exception:
            session.rollback()
            return False, "link_set_taken"
        return True, "link_set_ok"


def change_code_interactive(tg_user_id: int, new_code: str, tg_chat_id: int | None = None) -> tuple[bool, str]:
    """Интерактивная смена кода с обновлением ChatID.
    
    Returns (ok, message_key) where message_key is i18n key for feedback.
    """
    new_code = (new_code or "").upper().strip()
    
    # Проверка на 'auto' для автогенерации
    if new_code.lower() == 'auto':
        return change_code_auto(tg_user_id, tg_chat_id)
    
    # Валидация кода
    if not (4 <= len(new_code) <= 8):
        return False, "change_code_invalid"
    if not new_code.isalnum():
        return False, "change_code_invalid"

    with SessionLocal() as session:
        user = session.execute(select(User).where(User.tg_user_id == tg_user_id)).scalar_one_or_none()
        if not user:
            # Создаем пользователя если не существует
            user = User(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id, language="en", tg_code=new_code)
            session.add(user)
            try:
                session.commit()
                session.refresh(user)
                logger.info("User created with custom code: {} -> {}", tg_user_id, new_code)
                return True, "change_code_manual"
            except Exception:
                session.rollback()
                return False, "change_code_taken"
        else:
            # Обновляем chat_id если он передан
            if tg_chat_id is not None:
                user.tg_chat_id = tg_chat_id
                logger.info("Updated chat_id for user {}: {}", tg_user_id, tg_chat_id)
            
            # Сохраняем старый код для логирования
            old_code = user.tg_code
            
            # Устанавливаем новый код
            user.tg_code = new_code
            try:
                session.commit()
                session.refresh(user)
                logger.info("Code changed for user {}: {} -> {}", tg_user_id, old_code, new_code)
                return True, "change_code_manual"
            except Exception:
                session.rollback()
                return False, "change_code_taken"


def change_code_auto(tg_user_id: int, tg_chat_id: int | None = None) -> tuple[bool, str]:
    """Автоматическая смена кода с обновлением ChatID.
    
    Returns (ok, message_key) where message_key is i18n key for feedback.
    """
    new_code = generate_code()
    
    with SessionLocal() as session:
        user = session.execute(select(User).where(User.tg_user_id == tg_user_id)).scalar_one_or_none()
        if not user:
            # Создаем пользователя если не существует
            user = User(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id, language="en", tg_code=new_code)
            session.add(user)
            try:
                session.commit()
                session.refresh(user)
                logger.info("User created with auto-generated code: {} -> {}", tg_user_id, new_code)
                return True, "change_code_auto"
            except Exception:
                session.rollback()
                # Редкий случай - попробуем еще раз
                return change_code_auto(tg_user_id, tg_chat_id)
        else:
            # Обновляем chat_id если он передан
            if tg_chat_id is not None:
                user.tg_chat_id = tg_chat_id
                logger.info("Updated chat_id for user {}: {}", tg_user_id, tg_chat_id)
            
            # Сохраняем старый код для логирования
            old_code = user.tg_code
            
            # Устанавливаем новый код
            user.tg_code = new_code
            try:
                session.commit()
                session.refresh(user)
                logger.info("Code auto-changed for user {}: {} -> {}", tg_user_id, old_code, new_code)
                return True, "change_code_auto"
            except Exception:
                session.rollback()
                # Редкий случай - попробуем еще раз
                return change_code_auto(tg_user_id, tg_chat_id)


