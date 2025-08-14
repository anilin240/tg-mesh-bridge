import json
import os
import sys
import re
from typing import Any, Optional

from loguru import logger

try:
    if "/app/src" not in sys.path:
        sys.path.append("/app/src")
except Exception:
    pass

from common.config import AppConfig
from common.state import state
from bridge.repo import (
    get_user_tg_id_by_code,
    get_user_chat_id_by_code,
    upsert_node,
    upsert_gateway,
    upsert_heard_map,
    message_exists,
    save_message,
    link_node_to_user,
    update_node_alias,
    update_node_position,
)

from aiogram import Bot

import paho.mqtt.client as mqtt


SUBSCRIBE_TOPIC = None  # will be resolved from AppConfig at runtime


def _on_connect(client: mqtt.Client, userdata: Any, flags: dict, reason_code: int, properties=None) -> None:
    if reason_code == 0:
        topic = userdata.get("subscribe_topic") if isinstance(userdata, dict) else None
        if not topic:
            # Fallback to default from config
            try:
                topic = AppConfig().mqtt_topic_sub
            except Exception:
                topic = "msh/US/2/json/#"
        logger.info("MQTT connected successfully, subscribing to: {}", topic)
        client.subscribe(topic, qos=0)
        try:
            state.set_mqtt_connected(True)
        except Exception:
            pass
    else:
        logger.error("MQTT connection failed with code {}", reason_code)


CODE_RE = re.compile(r"@tg:([A-Z0-9]{4,8})(?:\s+|$)")


def _extract_code_and_message(payload: str) -> tuple[Optional[str], Optional[str]]:
    match = CODE_RE.search(payload)
    if not match:
        return None, None
    code = match.group(1)
    # Message is text after the matched token
    start = match.end()
    message = payload[start:].lstrip()
    return code, message


def _on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
    payload_text: str
    try:
        payload_text = msg.payload.decode("utf-8", errors="replace")
        data = json.loads(payload_text)
        logger.info("MQTT message on {}: {}", msg.topic, data)
        try:
            state.touch_mqtt_message()
        except Exception:
            pass

        # Expected fields
        mesh_from = data.get("from")
        mesh_sender = data.get("sender")
        payload_str = data.get("payload")
        msg_id = data.get("id")
        
        # Try to convert mesh_sender to int, but handle non-numeric values
        gateway_node_id = None
        if mesh_sender is not None:
            try:
                gateway_node_id = int(mesh_sender)
            except (ValueError, TypeError):
                # If mesh_sender is not a number (e.g., "!b03b3d9c"), skip it
                pass

        # Extract text from payload (can be string or dict with 'text' field)
        text_payload = None
        if isinstance(payload_str, str):
            text_payload = payload_str
        elif isinstance(payload_str, dict) and 'text' in payload_str:
            text_payload = payload_str['text']
        
        if text_payload:
            # upserts for presence data
            try:
                if mesh_from:
                    upsert_node(int(mesh_from), gateway_node_id)
                if gateway_node_id:
                    upsert_gateway(gateway_node_id)
                if mesh_from and gateway_node_id:
                    upsert_heard_map(int(mesh_from), gateway_node_id)
            except Exception as e:
                logger.error("DB upsert error: {}", e)

            # Deduplication by (direction, msg_id)
            if message_exists("mesh2tg", str(msg_id)):
                logger.info("Duplicate message skipped: {}", msg_id)
                return

            # Anti-loop: ignore messages originating from this bot prefix
            if text_payload.startswith("[[TG]] "):
                return

            code, message_text = _extract_code_and_message(text_payload)
            logger.info("Extracted code: {}, message: {}", code, message_text)
            if not code:
                logger.info("No code found in payload, skipping message")
                return

            tg_user_id = None
            tg_chat_id = None
            try:
                tg_user_id = get_user_tg_id_by_code(code)
                tg_chat_id = get_user_chat_id_by_code(code)
            except Exception as e:
                logger.error("DB query error (get user by code): {}", e)
                return

            if not tg_user_id:
                logger.warning("CODE not found: {}", code)
                # anyway save message record for audit
                try:
                    save_message(
                        direction="mesh2tg",
                        msg_id=str(msg_id),
                        from_id=str(mesh_from) if mesh_from is not None else None,
                        to_id=None,
                        gateway_node_id=gateway_node_id,
                        payload=text_payload,
                    )
                except Exception as e:
                    logger.error("Save message error: {}", e)
                return

            # Attempt to link node to user if not linked yet
            link_performed = False
            try:
                if mesh_from is not None and tg_user_id is not None:
                    link_performed = link_node_to_user(int(mesh_from), int(tg_user_id))
            except Exception as e:
                logger.error("Link node to user error: {}", e)

            text_to_send = f"[from {mesh_from}] {message_text or ''}".strip()

            # Send DM via Telegram Bot
            try:
                config = AppConfig()
                from common.state import state
                bot = state.bot
                loop = state.loop
                if bot and loop:
                    import asyncio
                    async def _send():
                        logger.info("Attempting to send message to chat_id: {}", tg_chat_id or tg_user_id)
                        if link_performed:
                            try:
                                await bot.send_message(
                                    chat_id=int(tg_chat_id or tg_user_id),
                                    text=f"Node {mesh_from} has been linked to your account.",
                                )
                                logger.info("Link confirmation sent successfully")
                                try:
                                    save_message(
                                        direction="system",
                                        msg_id=None,
                                        from_id=str(mesh_from) if mesh_from is not None else None,
                                        to_id=str(tg_user_id),
                                        gateway_node_id=gateway_node_id,
                                        payload="link_ok",
                                    )
                                except Exception:
                                    pass
                            except Exception:
                                logger.warning("Failed to send link confirmation DM")
                        try:
                            await bot.send_message(chat_id=int(tg_chat_id or tg_user_id), text=text_to_send)
                            logger.info("Message sent successfully to Telegram")
                        except Exception as e:
                            logger.error("Failed to send message to Telegram: {}", e)
                    asyncio.run_coroutine_threadsafe(_send(), loop)
                else:
                    logger.error("Bot/loop not initialized")
            except Exception as e:
                logger.error("Failed to send DM: {}", e)

            # Save message after sending (or attempting to)
            try:
                save_message(
                    direction="mesh2tg",
                    msg_id=msg_id,
                    from_id=str(mesh_from) if mesh_from is not None else None,
                    to_id=str(tg_user_id) if tg_user_id is not None else None,
                    gateway_node_id=gateway_node_id,
                    payload=payload_str,
                )
            except Exception as e:
                logger.error("Save message error: {}", e)
            return

        # Non-text JSON handling (NodeInfo / Position or others)
        # Upserts still apply
        try:
            if mesh_from:
                upsert_node(int(mesh_from), gateway_node_id)
            if gateway_node_id:
                upsert_gateway(gateway_node_id)
            if mesh_from and gateway_node_id:
                upsert_heard_map(int(mesh_from), gateway_node_id)
        except Exception as e:
            logger.error("DB upsert error: {}", e)

        try:
            # Heuristics for NodeInfo
            alias_value = None
            if isinstance(data, dict):
                # meshtastic often provides 'type' or 'msgtype'
                msg_type = data.get("type") or data.get("msgtype")
                user_obj = data.get("user") or {}
                possible_alias = user_obj.get("longname") or user_obj.get("shortname") or user_obj.get("alias")
                if msg_type and str(msg_type).lower().startswith("node"):
                    alias_value = possible_alias
                elif possible_alias:
                    alias_value = possible_alias

                if alias_value and mesh_from is not None:
                    update_node_alias(int(mesh_from), str(alias_value)[:64])

                # Heuristics for Position
                lat = data.get("lat")
                lon = data.get("lon")
                alt = data.get("alt")
                # Some payloads may wrap position
                pos = data.get("position") or {}
                if lat is None and lon is None and isinstance(pos, dict):
                    lat = pos.get("lat")
                    lon = pos.get("lon")
                    alt = pos.get("alt") if alt is None else alt

                if lat is not None and lon is not None and mesh_from is not None:
                    from datetime import datetime, timezone

                    update_node_position(
                        int(mesh_from), float(lat), float(lon), float(alt) if alt is not None else None, datetime.now(timezone.utc)
                    )
        except Exception as e:
            logger.error("Non-text JSON handling error: {}", e)

        # upserts for presence data
        try:
            if mesh_from:
                upsert_node(int(mesh_from), gateway_node_id)
            if gateway_node_id:
                upsert_gateway(gateway_node_id)
            if mesh_from and gateway_node_id:
                upsert_heard_map(int(mesh_from), gateway_node_id)
        except Exception as e:
            logger.error("DB upsert error: {}", e)

        # Deduplication by (direction, msg_id)
        if message_exists("mesh2tg", msg_id):
            logger.info("Duplicate message skipped: {}", msg_id)
            return

        # Anti-loop: ignore messages originating from this bot prefix
        if isinstance(payload_str, str) and payload_str.startswith("[[TG]] "):
            return

        # Only process text payloads
        if not isinstance(payload_str, str):
            return

        code, message_text = _extract_code_and_message(payload_str)
        if not code:
            return

        tg_user_id = None
        try:
            tg_user_id = get_user_tg_id_by_code(code)
        except Exception as e:
            logger.error("DB query error (get user by code): {}", e)
            return

        if not tg_user_id:
            logger.warning("CODE not found: {}", code)
            # anyway save message record for audit
            try:
                save_message(
                    direction="mesh2tg",
                    msg_id=msg_id,
                    from_id=str(mesh_from) if mesh_from is not None else None,
                    to_id=None,
                    gateway_node_id=int(mesh_sender) if mesh_sender is not None else None,
                    payload=payload_str,
                )
            except Exception as e:
                logger.error("Save message error: {}", e)
            return

        # Attempt to link node to user if not linked yet
        link_performed = False
        try:
            if mesh_from is not None and tg_user_id is not None:
                link_performed = link_node_to_user(int(mesh_from), int(tg_user_id))
        except Exception as e:
            logger.error("Link node to user error: {}", e)

        text_to_send = f"[from {mesh_from}] {message_text or ''}".strip()

        # Send DM via Telegram Bot
        try:
            config = AppConfig()
            from common.state import state
            bot = state.bot
            loop = state.loop
            if bot and loop:
                import asyncio
                async def _send():
                    if link_performed:
                        try:
                            await bot.send_message(
                                chat_id=int(tg_chat_id or tg_user_id),
                                text=f"Node {mesh_from} has been linked to your account.",
                            )
                            try:
                                save_message(
                                    direction="system",
                                    msg_id=None,
                                    from_id=str(mesh_from) if mesh_from is not None else None,
                                    to_id=str(tg_user_id),
                                    gateway_node_id=gateway_node_id,
                                    payload="link_ok",
                                )
                            except Exception:
                                pass
                        except Exception:
                            logger.warning("Failed to send link confirmation DM")
                    await bot.send_message(chat_id=int(tg_chat_id or tg_user_id), text=text_to_send)
                asyncio.run_coroutine_threadsafe(_send(), loop)
            else:
                logger.error("Bot/loop not initialized")
        except Exception as e:
            logger.error("Failed to send DM: {}", e)

        # Save message after sending (or attempting to)
        try:
            save_message(
                direction="mesh2tg",
                msg_id=str(msg_id),
                from_id=str(mesh_from) if mesh_from is not None else None,
                to_id=str(tg_user_id) if tg_user_id is not None else None,
                gateway_node_id=gateway_node_id,
                payload=payload_str,
            )
        except Exception as e:
            logger.error("Save message error: {}", e)
    except json.JSONDecodeError:
        logger.warning("MQTT non-JSON payload on {}: {}", msg.topic, payload_text)


def _on_disconnect(client: mqtt.Client, userdata: Any, reason_code: int, properties=None) -> None:
    try:
        state.set_mqtt_connected(False)
    except Exception:
        pass


def run_consumer() -> None:
    config = AppConfig()

    # Create MQTT client
    client = mqtt.Client(client_id="tg-mesh-bridge-consumer", userdata={"subscribe_topic": config.mqtt_topic_sub})

    if config.mqtt_user:
        client.username_pw_set(config.mqtt_user, config.mqtt_pass or "")

    client.on_connect = _on_connect
    client.on_message = _on_message
    client.on_disconnect = _on_disconnect

    logger.info(
        "Connecting to MQTT broker {}:{} as {} | topic_sub={}",
        config.mqtt_host,
        config.mqtt_port,
        config.mqtt_user or "anonymous",
        config.mqtt_topic_sub,
    )

    client.connect(config.mqtt_host, int(config.mqtt_port))
    client.loop_forever()


if __name__ == "__main__":
    run_consumer()




