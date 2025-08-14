from __future__ import annotations

from datetime import datetime, timezone

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from common.ratelimit import limiter
from common.i18n import get as _t
from common.db import SessionLocal
from common.models import User


WHITELIST = {"/status", "/help"}


class RateLimitMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        text = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            text = (event.text or "").strip()
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        # Skip non-command messages and whitelisted commands
        if isinstance(event, Message):
            if not text.startswith("/") or text.split(maxsplit=1)[0] in WHITELIST:
                return await handler(event, data)

        if user_id is None:
            return await handler(event, data)

        now = datetime.now(timezone.utc)
        allowed = limiter.allow(user_id, now)
        if not allowed:
            # detect language
            with SessionLocal() as session:
                u = session.get(User, user_id)
                lang = (u.language if u else "en") or "en"
            await event.answer(_t(lang, "rate_limited"))
            return

        return await handler(event, data)


