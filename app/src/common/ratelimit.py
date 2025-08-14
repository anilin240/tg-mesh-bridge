from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple


@dataclass
class RateLimiter:
    limit_per_minute: int
    # key: (user_id, minute_key) -> count
    _counts: Dict[Tuple[int, int], int] = field(default_factory=dict)

    def allow(self, user_id: int, now: datetime) -> bool:
        if self.limit_per_minute <= 0:
            return True
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        minute_key = int(now.timestamp() // 60)
        # cleanup old counters (keep only current and previous minute)
        old_keys = [k for k in self._counts if k[1] < minute_key - 1]
        for k in old_keys:
            self._counts.pop(k, None)
        key = (int(user_id), minute_key)
        cnt = self._counts.get(key, 0)
        if cnt < self.limit_per_minute:
            self._counts[key] = cnt + 1
            return True
        return False


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except Exception:
        return default


limiter = RateLimiter(limit_per_minute=_env_int("RATE_LIMIT_PER_MIN", 10))

__all__ = ["RateLimiter", "limiter"]


