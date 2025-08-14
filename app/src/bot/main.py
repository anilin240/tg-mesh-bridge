import asyncio
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.menu import top_menu, messages_menu, dev_menu, network_menu
from loguru import logger

try:
    # When executed as a module, ensure '/app/src' is importable in case PYTHONPATH is not set
    if "/app/src" not in sys.path:
        sys.path.append("/app/src")
except Exception:
    pass

from common.config import AppConfig
from bridge.consumer import run_consumer
from bot.services.users import get_or_create_user, regenerate_code, change_code_interactive
from bot.states import state_manager, UserState
from bot.handlers.nearby import nearby_router
from bot.handlers.send_to_node import send_to_node_router
from bot.handlers.send_nearby import send_nearby_router
from bot.handlers.status import status_router
from bot.handlers.help import help_router
from bot.handlers.menu import menu_router
from bot.handlers.devices import dev_router
from common.i18n import get as _t
from bridge.mqtt import publish_to_topic


async def main() -> None:
    config = AppConfig()
    from datetime import datetime, timezone
    started_at = datetime.now(timezone.utc)
    logger.info(
        "Starting bot version={} | MQTT_HOST={} | MQTT_PORT={} | MQTT_TOPIC_SUB={} | MQTT_TOPIC_PUB={} | POSTGRES_HOST={} | POSTGRES_DB={} | started_at={}Z",
        "0.1.0",
        config.mqtt_host,
        config.mqtt_port,
        config.mqtt_topic_sub,
        config.mqtt_topic_pub,
        config.postgres_host,
        config.postgres_db,
        started_at.strftime("%Y-%m-%dT%H:%M:%S"),
    )
    # Initialize runtime state start time
    try:
        from common.state import state
        state.started_at = started_at
    except Exception:
        pass
    if not config.bot_token:
        logger.warning("BOT_TOKEN is not set; running MQTT consumer only")
        # Run only the MQTT consumer so that logs are visible in the app container
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, run_consumer)
        return

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    from common.state import state
    state.set_bot(bot)
    state.set_loop(asyncio.get_running_loop())
    # подключаем middleware ДО роутеров
    from bot.middlewares.ratelimit import RateLimitMiddleware as RL2
    dp.message.middleware(RL2())
    dp.callback_query.middleware(RL2())

    # Routers
    dp.include_router(nearby_router)
    dp.include_router(send_to_node_router)
    dp.include_router(send_nearby_router)
    dp.include_router(status_router)
    dp.include_router(menu_router)
    dp.include_router(dev_router)
    # help is handled locally below with menu

    def _main_menu(lang: str) -> InlineKeyboardMarkup:
        return top_menu(lang)

    @dp.message(Command("start"))
    async def handle_start(message: types.Message) -> None:
        from bot.services.users import get_or_create_user
        # Save chat id immediately
        get_or_create_user(message.from_user.id, message.chat.id)
        kb_lang = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="RU", callback_data="setlang:ru"), InlineKeyboardButton(text="EN", callback_data="setlang:en")]
        ])
        await message.answer(_t("en", "start_welcome"), reply_markup=kb_lang)

    @dp.callback_query(lambda c: c.data and c.data.startswith("setlang:"))
    async def handle_set_language(callback: types.CallbackQuery) -> None:
        lang = callback.data.split(":", 1)[1]
        from bot.services.users import get_or_create_user
        user = get_or_create_user(callback.from_user.id)
        # update language
        from common.db import SessionLocal
        from sqlalchemy import select
        from common.models import User
        with SessionLocal() as session:
            u = session.get(User, user.tg_user_id)
            if u:
                u.language = lang
                session.commit()
        text = _t(lang, "lang_set_ru") if lang == "ru" else _t(lang, "lang_set_en")
        await callback.message.edit_text(text)
        # show main menu
        await callback.message.answer(_t(lang, "menu.top"), reply_markup=_main_menu(lang))
        await callback.answer()

    @dp.message(Command("ping"))
    async def handle_ping(message: types.Message) -> None:
        await message.answer("pong")

    @dp.message(Command("probe"))
    async def handle_probe(message: types.Message) -> None:
        # Публикуем тестовый JSON в общий топик, который слушают ноды (или шлюз)
        # Можно указать другой топик: /probe <topic>
        parts = message.text.split(maxsplit=1)
        topic = None
        if len(parts) > 1:
            topic = parts[1].strip()
        if not topic:
            from common.config import AppConfig
            topic = AppConfig().mqtt_topic_pub
        ok = publish_to_topic(topic, {"ping": "probe", "ts": __import__("time").time()})
        await message.answer("probe sent" if ok else "probe failed")

    @dp.message(Command("help"))
    async def handle_help(message: types.Message) -> None:
        # detect language
        from common.db import SessionLocal
        from common.models import User
        with SessionLocal() as session:
            u = session.get(User, message.from_user.id)
            lang = (u.language if u else "en") or "en"
        await message.answer(_t(lang, "help.body"), reply_markup=_main_menu(lang))

    @dp.message(Command("link"))
    async def handle_link(message: types.Message) -> None:
        args = message.text.split(maxsplit=1)
        if len(args) > 1 and args[1].lower() == "new":
            new_code = regenerate_code(message.from_user.id)
            lang = "en"
            from common.db import SessionLocal
            from common.models import User
            from sqlalchemy import select
            with SessionLocal() as session:
                u = session.get(User, message.from_user.id)
                if u and u.language:
                    lang = u.language
            text = _t(lang, "link_new", code=new_code)
            await message.answer(text)
            return
        if len(args) > 1 and args[1].lower().startswith("set"):
            parts = args[1].split(maxsplit=1)
            lang = "en"
            from common.db import SessionLocal
            from common.models import User
            with SessionLocal() as session:
                u = session.get(User, message.from_user.id)
                lang = (u.language if u else "en") or "en"
            if len(parts) < 2:
                await message.answer(_t(lang, "link_set_prompt"))
                return
            from bot.services.users import set_custom_code
            ok, key = set_custom_code(message.from_user.id, parts[1])
            if ok:
                await message.answer(_t(lang, key))
            else:
                await message.answer(_t(lang, key))
            return
        user = get_or_create_user(message.from_user.id, message.chat.id)
        lang = user.language or "en"
        code_value = user.tg_code or ""
        text = _t(lang, "link_code", code=code_value)
        await message.answer(text, reply_markup=_main_menu(lang))

    async def handle_nearby_button(message: types.Message) -> None:
        """Обработка кнопки 'Показать окружение'"""
        from common.db import SessionLocal
        from common.models import User
        with SessionLocal() as session:
            u = session.get(User, message.from_user.id)
            lang = (u.language if u else "en") or "en"
        
        # Получаем последний активный шлюз
        from bot.handlers.nearby import _get_latest_gateway_node_id, _get_recent_nodes_for_gateway
        import math
        from datetime import datetime, timezone
        
        gateway_node_id = _get_latest_gateway_node_id()
        if gateway_node_id is None:
            await message.answer(_t(lang, "no_gateways"), reply_markup=_main_menu(lang))
            return

        rows = _get_recent_nodes_for_gateway(gateway_node_id)
        if not rows:
            header = _t(lang, "nearby_header", gateway=gateway_node_id)
            await message.answer(f"{header}\n{_t(lang, 'nearby_none')}", reply_markup=_main_menu(lang))
            return

        now_utc = datetime.now(timezone.utc)
        lines: list[str] = [_t(lang, "nearby_header", gateway=gateway_node_id)]
        for node_id, alias, last_heard_at in rows:
            # Compute minutes ago, clamp to >=0
            diff_minutes = max(0, int(math.floor((now_utc - last_heard_at).total_seconds() / 60)))
            alias_text = f" {alias}" if alias else ""
            lines.append(f"• {node_id}{alias_text} ({_t(lang, 'min_ago', minutes=diff_minutes)})")

        await message.answer("\n".join(lines), reply_markup=_main_menu(lang))

    # Text message handler for code registration and state management
    @dp.message()
    async def handle_text_messages(message: types.Message) -> None:
        txt = (message.text or "").strip()
        if txt.startswith("/"):
            return
            
        from common.db import SessionLocal
        from common.models import User
        with SessionLocal() as session:
            u = session.get(User, message.from_user.id)
            lang = (u.language if u else "en") or "en"
        
        # Проверяем состояние пользователя
        if state_manager.is_in_state(message.from_user.id, UserState.CHANGING_CODE):
            # Пользователь в процессе смены кода
            ok, key = change_code_interactive(message.from_user.id, txt, message.chat.id)
            if ok:
                # Получаем новый код для отображения
                user = get_or_create_user(message.from_user.id, message.chat.id)
                new_code = user.tg_code or ""
                await message.answer(_t(lang, key, code=new_code), reply_markup=_main_menu(lang))
            else:
                await message.answer(_t(lang, key), reply_markup=_main_menu(lang))
            
            # Очищаем состояние
            state_manager.clear_state(message.from_user.id)
            return
        
        # Проверяем, не является ли сообщение кодом для регистрации
        # Код должен быть 4-8 символов, только буквы и цифры
        if len(txt) >= 4 and len(txt) <= 8 and txt.isalnum() and txt.isupper():
            # Это может быть код для регистрации
            from bot.services.users import set_custom_code
            ok, key = set_custom_code(message.from_user.id, txt, message.chat.id)
            if ok:
                await message.answer(_t(lang, key), reply_markup=_main_menu(lang))
            else:
                await message.answer(_t(lang, key), reply_markup=_main_menu(lang))
            return

    # Run MQTT consumer in a parallel task
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, run_consumer)

    logger.info("Starting bot polling")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())


