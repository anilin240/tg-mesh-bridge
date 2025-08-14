from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import Command

from common.db import SessionLocal
from common.models import User
from common.i18n import t


help_router = Router()


@help_router.message(Command("help"))
async def handle_help(message: types.Message) -> None:
    with SessionLocal() as session:
        u = session.get(User, message.from_user.id)
        lang = (u.language if u else "en") or "en"
    await message.answer(t(lang, "help"))


