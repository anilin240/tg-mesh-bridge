from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any
import asyncio


@dataclass
class RuntimeState:
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mqtt_connected: bool = False
    last_mqtt_message_at: Optional[datetime] = None
    bot: Optional[Any] = None
    loop: Optional[asyncio.AbstractEventLoop] = None

    def set_mqtt_connected(self, value: bool) -> None:
        self.mqtt_connected = bool(value)

    def touch_mqtt_message(self) -> None:
        self.last_mqtt_message_at = datetime.now(timezone.utc)

    def set_bot(self, bot: Any) -> None:
        self.bot = bot

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop


state = RuntimeState()

__all__ = ["RuntimeState", "state"]


