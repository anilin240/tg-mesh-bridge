from __future__ import annotations

import math
from datetime import datetime, timezone

from aiogram import Router, types
from aiogram.filters import Command
from loguru import logger
from sqlalchemy import select, desc, text, func
from sqlalchemy.orm import aliased

from common.db import SessionLocal
from common.models import Gateway, HeardMap, Node
from common.i18n import get as _t


nearby_router = Router()


def _get_latest_gateway_node_id() -> int | None:
    with SessionLocal() as session:
        stmt = (
            select(Gateway.node_id)
            .order_by(desc(Gateway.last_seen_at))
            .limit(1)
        )
        result = session.execute(stmt).scalar_one_or_none()
        return int(result) if result is not None else None


def _get_recent_nodes_for_gateway(gateway_node_id: int, limit: int = 20) -> list[tuple[int, str | None, datetime]]:
    with SessionLocal() as session:
        n = aliased(Node)
        fifteen_minutes_ago = func.now() - text("interval '15 minutes'")
        stmt = (
            select(HeardMap.node_id, n.alias, HeardMap.last_heard_at)
            .join(n, n.node_id == HeardMap.node_id, isouter=True)
            .where(
                HeardMap.gateway_node_id == gateway_node_id,
                HeardMap.last_heard_at >= fifteen_minutes_ago,
            )
            .order_by(desc(HeardMap.last_heard_at))
            .limit(limit)
        )
        rows = session.execute(stmt).all()
        return [(int(node_id), alias, last_heard_at) for node_id, alias, last_heard_at in rows]


@nearby_router.message(Command("nearby"))
async def handle_nearby(message: types.Message) -> None:
    try:
        parts = message.text.split(maxsplit=1)
        gateway_node_id: int | None = None
        if len(parts) > 1:
            arg = parts[1].strip()
            try:
                gateway_node_id = int(arg)
            except ValueError:
                # language lookup
                from common.db import SessionLocal
                from common.models import User
                with SessionLocal() as session:
                    u = session.get(User, message.from_user.id)
                    lang = (u.language if u else "en") or "en"
                await message.answer(_t(lang, "invalid_gateway"))
                return

        if gateway_node_id is None:
            gateway_node_id = _get_latest_gateway_node_id()
            if gateway_node_id is None:
                from common.db import SessionLocal
                from common.models import User
                with SessionLocal() as session:
                    u = session.get(User, message.from_user.id)
                    lang = (u.language if u else "en") or "en"
                await message.answer(_t(lang, "no_gateways"))
                return

        rows = _get_recent_nodes_for_gateway(gateway_node_id)
        if not rows:
            from common.db import SessionLocal
            from common.models import User
            with SessionLocal() as session:
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            header = _t(lang, "nearby_header", gateway=gateway_node_id)
            await message.answer(f"{header}\n{_t(lang, 'nearby_none')}")
            return

        now_utc = datetime.now(timezone.utc)
        from common.db import SessionLocal
        from common.models import User
        with SessionLocal() as session:
            u = session.get(User, message.from_user.id)
            lang = (u.language if u else "en") or "en"
        lines: list[str] = [_t(lang, "nearby_header", gateway=gateway_node_id)]
        for node_id, alias, last_heard_at in rows:
            # Compute minutes ago, clamp to >=0
            diff_minutes = max(0, int(math.floor((now_utc - last_heard_at).total_seconds() / 60)))
            alias_text = f" {alias}" if alias else ""
            lines.append(f" • {node_id}{alias_text} — {_t(lang, 'min_ago', minutes=diff_minutes)}")

        await message.answer("\n".join(lines))
    except Exception as e:
        logger.error("/nearby handler error: {}", e)
        await message.answer("Failed to fetch nearby nodes.")


