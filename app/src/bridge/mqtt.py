from __future__ import annotations

import json
import threading
from typing import Any

import paho.mqtt.client as mqtt
from loguru import logger

from common.config import AppConfig


def _safe_join_topic(base: str, suffix: str) -> str:
    if not base:
        return suffix
    if not suffix:
        return base
    if base.endswith("/") and suffix.startswith("/"):
        return base.rstrip("/") + "/" + suffix.lstrip("/")
    if base.endswith("/") or suffix.startswith("/"):
        return base + suffix
    return base + "/" + suffix


class _Publisher:
    def __init__(self) -> None:
        self._client: mqtt.Client | None = None
        self._lock = threading.Lock()
        self._cfg_snapshot: tuple[str, int, str | None, str | None] | None = None

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, reason_code: int, properties=None) -> None:
        logger.warning("MQTT publisher disconnected: code={}", reason_code)
        with self._lock:
            try:
                if self._client is not None:
                    try:
                        self._client.loop_stop()
                    except Exception:
                        pass
            finally:
                self._client = None

    def _ensure_client(self) -> mqtt.Client | None:
        """Create or re-create client if config changed or client is missing."""
        cfg = AppConfig()
        snapshot = (cfg.mqtt_host, int(cfg.mqtt_port), cfg.mqtt_user, cfg.mqtt_pass)
        with self._lock:
            try:
                need_new = (
                    self._client is None or self._cfg_snapshot != snapshot
                )
                if not need_new:
                    return self._client

                # Close previous client if any
                if self._client is not None:
                    try:
                        self._client.loop_stop()
                    except Exception:
                        pass
                    try:
                        self._client.disconnect()
                    except Exception:
                        pass
                    self._client = None

                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="tg-mesh-bot-publisher")
                if cfg.mqtt_user:
                    client.username_pw_set(cfg.mqtt_user, cfg.mqtt_pass or "")
                client.on_disconnect = self._on_disconnect
                client.connect(cfg.mqtt_host, int(cfg.mqtt_port))
                client.loop_start()

                self._client = client
                self._cfg_snapshot = snapshot
                logger.info("MQTT publisher connected to {}:{}", cfg.mqtt_host, cfg.mqtt_port)
                return self._client
            except Exception as e:
                logger.error("MQTT publisher ensure_client error: {}", e)
                self._client = None
                return None

    def publish(self, topic: str, payload_dict: dict[str, Any]) -> bool:
        try:
            client = self._ensure_client()
            if client is None:
                return False
            text = json.dumps(payload_dict, separators=(",", ":"))
            logger.info("Publishing to {}: {}", topic, text)
            info = client.publish(topic, payload=text, qos=0, retain=False)
            ok = True
            try:
                # paho-mqtt v2 returns MQTTMessageInfo with rc
                ok = getattr(info, "rc", mqtt.MQTT_ERR_SUCCESS) == mqtt.MQTT_ERR_SUCCESS
            except Exception:
                ok = True
            return bool(ok)
        except Exception as e:
            logger.error("MQTT publish error: {}", e)
            with self._lock:
                # Drop client so that next publish reconnects
                try:
                    if self._client is not None:
                        try:
                            self._client.loop_stop()
                        except Exception:
                            pass
                        try:
                            self._client.disconnect()
                        except Exception:
                            pass
                finally:
                    self._client = None
            return False


_publisher = _Publisher()


def publish_downlink(payload_dict: dict[str, Any]) -> bool:
    topic = AppConfig().mqtt_topic_pub
    return _publisher.publish(topic, payload_dict)


def publish_to_topic(topic: str, payload_dict: dict[str, Any]) -> bool:
    return _publisher.publish(topic, payload_dict)


__all__ = ["publish_downlink", "publish_to_topic"]


