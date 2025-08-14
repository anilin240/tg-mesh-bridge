from __future__ import annotations

import os
import sys
from datetime import datetime, timezone, timedelta

from loguru import logger
from sqlalchemy import text

try:
    if "/app/src" not in sys.path:
        sys.path.append("/app/src")
except Exception:
    pass

from common.db import SessionLocal
from common.config import AppConfig
from common.state import state


def main() -> int:
    try:
        # DB check via SessionLocal
        with SessionLocal() as session:
            session.execute(text("select 1"))

        # MQTT basic config presence
        cfg = AppConfig()
        if not cfg.mqtt_host or not cfg.mqtt_port:
            logger.error("MQTT config missing")
            return 1

        # Optional: REQUIRE_MQTT_SEEN=true enforces last message within 10 minutes
        require_seen = os.environ.get("REQUIRE_MQTT_SEEN", "false").lower() == "true"
        if require_seen:
            last = state.last_mqtt_message_at
            if last is None:
                logger.error("Healthcheck: MQTT message has not been seen yet")
                return 1
            age = datetime.now(timezone.utc) - last
            if age > timedelta(minutes=10):
                logger.error("Healthcheck: last MQTT message too old: {} seconds", int(age.total_seconds()))
                return 1
        return 0
    except Exception as e:
        logger.error("Healthcheck failed: {}", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())


