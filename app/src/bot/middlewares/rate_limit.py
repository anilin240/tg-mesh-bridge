from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from common.i18n import get as _t
from common.db import SessionLocal
from common.models import User


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit_per_minute: int = 10) -> None:
        super().__init__()
        self.limit = limit_per_minute
        self.user_hits: Dict[int, Deque[float]] = defaultdict(deque)

    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id is None:
            return await handler(event, data)

        now = time.time()
        window_start = now - 60
        dq = self.user_hits[user_id]

        # purge old timestamps
        while dq and dq[0] < window_start:
            dq.popleft()

        if len(dq) >= self.limit:
            # detect language
            with SessionLocal() as session:
                u = session.get(User, user_id)
                lang = (u.language if u else "en") or "en"
            if isinstance(event, Message):
                await event.answer(_t(lang, "rate_limited"))
            elif isinstance(event, CallbackQuery):
                await event.answer(_t(lang, "rate_limited"), show_alert=True)
            return

        dq.append(now)
        return await handler(event, data)


