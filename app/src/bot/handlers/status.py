from __future__ import annotations

from datetime import datetime, timezone

from aiogram import Router, types
from aiogram.filters import Command
from loguru import logger
from sqlalchemy import text, select, func

from common.db import SessionLocal
from common.models import HeardMap, Gateway
from common.state import state
from common.config import AppConfig


status_router = Router()


def _format_timedelta(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


@status_router.message(Command("status"))
async def handle_status(message: types.Message) -> None:
    db_ok = False
    active_nodes = 0
    total_gateways = 0
    fresh_gateways = 0
    try:
        with SessionLocal() as session:
            session.execute(text("select 1"))
            db_ok = True

            fifteen = func.now() - text("interval '15 minutes'")
            active_nodes = session.execute(
                select(func.count()).select_from(HeardMap).where(HeardMap.last_heard_at >= fifteen)
            ).scalar_one()

            total_gateways = session.execute(select(func.count()).select_from(Gateway)).scalar_one()
            fresh_gateways = session.execute(
                select(func.count()).select_from(Gateway).where(Gateway.last_seen_at >= fifteen)
            ).scalar_one()
    except Exception as e:
        logger.error("/status DB error: {}", e)

    now = datetime.now(timezone.utc)
    last_msg = state.last_mqtt_message_at
    if last_msg is None:
        last_msg_text = "never"
    else:
        diff_minutes = int((now - last_msg).total_seconds() // 60)
        last_msg_text = f"{diff_minutes} min ago"

    uptime_secs = int((now - state.started_at).total_seconds())

    config = AppConfig()
    # Shorten topic for display if too long
    topic_sub_disp = config.mqtt_topic_sub
    if len(topic_sub_disp) > 48:
        topic_sub_disp = topic_sub_disp[:45] + "..."

    text_resp = (
        "Status:\n"
        f" - DB: {'OK' if db_ok else 'ERROR'}\n"
        f" - MQTT: {'connected' if state.mqtt_connected else 'disconnected'}\n"
        f" - MQTT_TOPIC_SUB: {topic_sub_disp}\n"
        f" - Last MQTT msg: {last_msg_text}\n"
        f" - Active nodes (15m): {active_nodes}\n"
        f" - Gateways: {total_gateways} (fresh: {fresh_gateways})\n"
        f" - Uptime: {_format_timedelta(uptime_secs)}"
    )

    await message.answer(text_resp)


