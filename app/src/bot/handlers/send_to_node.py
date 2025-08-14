from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import Command
from loguru import logger
from sqlalchemy import select, desc, func, text

from bridge.mqtt import publish_downlink
from common.db import SessionLocal
from common.models import HeardMap, Gateway, Message
from common.i18n import get as _t


send_to_node_router = Router()


def _select_gateway_for_node(node_id: int) -> int | None:
    with SessionLocal() as session:
        fifteen_minutes_ago = func.now() - text("interval '15 minutes'")
        # Try the most recent gateway that heard this node within 15 minutes
        stmt = (
            select(HeardMap.gateway_node_id)
            .where(HeardMap.node_id == node_id, HeardMap.last_heard_at >= fifteen_minutes_ago)
            .order_by(desc(HeardMap.last_heard_at))
            .limit(1)
        )
        gw = session.execute(stmt).scalar_one_or_none()
        if gw is not None:
            return int(gw)

        # Fallback: most recent gateway overall
        stmt2 = select(Gateway.node_id).order_by(desc(Gateway.last_seen_at)).limit(1)
        gw2 = session.execute(stmt2).scalar_one_or_none()
        return int(gw2) if gw2 is not None else None


@send_to_node_router.message(Command("send_to_node"))
async def handle_send_to_node(message: types.Message) -> None:
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            # i18n
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "usage_send_to_node"))
            return

        try:
            node_id = int(parts[1])
        except ValueError:
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "invalid_node_id"))
            return

        text_to_send = parts[2].strip()
        if not text_to_send:
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "empty_text"))
            return

        gateway_node_id = _select_gateway_for_node(node_id)
        if gateway_node_id is None:
            with SessionLocal() as session:
                from common.models import User
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            await message.answer(_t(lang, "no_gateway"))
            return

        payload = {
            "from": gateway_node_id,
            "to": node_id,
            "type": "sendtext",
            "payload": f"[[TG]] {text_to_send}",
        }

        ok = publish_downlink(payload)

        # Save message record
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

        with SessionLocal() as session:
            from common.models import User
            u = session.get(User, message.from_user.id)
            lang = (u.language if u else "en") or "en"
        if ok:
            await message.answer(_t(lang, "sent_via_gateway", gateway=gateway_node_id))
        else:
            await message.answer(_t(lang, "mqtt_publish_failed"))
    except Exception as e:
        logger.error("/send_to_node handler error: {}", e)
        with SessionLocal() as session:
            from common.models import User
            u = session.get(User, message.from_user.id)
            lang = (u.language if u else "en") or "en"
        await message.answer(_t(lang, "send_error"))


