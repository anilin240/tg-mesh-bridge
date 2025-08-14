from __future__ import annotations

import asyncio
from typing import List

from aiogram import Router, types
from aiogram.filters import Command
from loguru import logger
from sqlalchemy import select, desc, func, text

from bridge.mqtt import publish_downlink
from common.db import SessionLocal
from common.models import HeardMap, Message
from common.i18n import get as _t
import os


send_nearby_router = Router()


def _select_recent_node_ids_for_gateway(gateway_node_id: int, limit: int = 100) -> List[int]:
    with SessionLocal() as session:
        fifteen_minutes_ago = func.now() - text("interval '15 minutes'")
        stmt = (
            select(HeardMap.node_id)
            .where(
                HeardMap.gateway_node_id == gateway_node_id,
                HeardMap.last_heard_at >= fifteen_minutes_ago,
            )
            .order_by(desc(HeardMap.last_heard_at))
            .limit(limit)
        )
        rows = session.execute(stmt).scalars().all()
        return [int(n) for n in rows]


@send_nearby_router.message(Command("send_nearby"))
async def handle_send_nearby(message: types.Message) -> None:
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "usage_send_nearby"))
            return

        try:
            gateway_node_id = int(parts[1])
        except ValueError:
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "invalid_gateway"))
            return

        text_to_send = parts[2].strip()
        if not text_to_send:
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "empty_text"))
            return

        node_ids = _select_recent_node_ids_for_gateway(gateway_node_id)
        if not node_ids:
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "no_active_nodes_nearby"))
            return

        # Limit recipients by env policy
        try:
            max_recipients = int(os.environ.get("NEARBY_MAX_RECIPIENTS", "50"))
        except Exception:
            max_recipients = 50
        to_send = node_ids[:max(0, max_recipients)]
        skipped = max(0, len(node_ids) - len(to_send))

        sent_count = 0
        for node_id in to_send:
            payload = {
                "from": gateway_node_id,
                "to": node_id,
                "type": "sendtext",
                "payload": f"[[TG]] {text_to_send}",
            }

            # Publish in thread to avoid blocking the event loop
            ok = await asyncio.to_thread(publish_downlink, payload)

            # Save message record regardless of publish result
            with SessionLocal() as session:
                m = Message(
                    direction="tg2mesh",
                    msg_id=None,
                    from_id=str(message.from_user.id),
                    to_id=str(node_id),
                    gateway_node_id=gateway_node_id,
                    payload=text_to_send,
                )
                session.add(m)
                session.commit()

            if ok:
                sent_count += 1

            # Small delay to avoid flooding
            await asyncio.sleep(0.08)

        with SessionLocal() as session:
            from common.models import User
            u = session.get(User, message.from_user.id)
            lang = (u.language if u else "en") or "en"
        if skipped > 0:
            await message.answer(_t(lang, "nearby_limited", delivered=sent_count, total=len(node_ids)))
        else:
            await message.answer(_t(lang, "sent_to_count", count=sent_count, gateway=gateway_node_id))
    except Exception as e:
        logger.error("/send_nearby handler error: {}", e)
        await message.answer("Failed to send to nearby nodes.")


