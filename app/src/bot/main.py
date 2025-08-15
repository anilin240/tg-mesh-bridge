import asyncio
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.menu import top_menu, code_menu, dev_menu
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
# Удалён импорт help_router - файл удалён
from bot.handlers.menu import menu_router

from bot.handlers.fallback import fallback_router
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

    # Routers (в порядке приоритета)
    dp.include_router(nearby_router)
    dp.include_router(send_to_node_router)
    dp.include_router(send_nearby_router)
    dp.include_router(status_router)
    dp.include_router(menu_router)

    dp.include_router(fallback_router)  # Низкий приоритет - обработчик неизвестных сообщений
    # Удалена регистрация help_router - файл удалён

    def _main_menu(lang: str) -> InlineKeyboardMarkup:
        return top_menu(lang)

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
        await message.answer(_t("en", "system.pong"))

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
        await message.answer(_t("en", "system.probe_sent" if ok else "system.probe_failed"))

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
                lang = (u.language if u else "en") or "en"
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

    @dp.message(Command("start"))
    async def handle_start(message: types.Message) -> None:
        from loguru import logger
        logger.info("START: User {} sent /start command", message.from_user.id)
        logger.info("START: Message text: '{}'", message.text)
        logger.info("START: Chat ID: {}, User ID: {}", message.chat.id, message.from_user.id)
        
        try:
            # Показываем меню выбора языка
            from bot.keyboards.menu import language_menu
            await message.answer("Выберите язык / Choose language:", reply_markup=language_menu())
            logger.info("START: Successfully sent language menu to user {}", message.from_user.id)
        except Exception as e:
            logger.error("START: Error sending language menu to user {}: {}", message.from_user.id, e)
            # Fallback - отправляем простое сообщение
            await message.answer("Привет! / Hello!")


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
                await message.answer(_t(lang, key, code=new_code), reply_markup=code_menu(lang))
            else:
                await message.answer(_t(lang, key), reply_markup=code_menu(lang))
            
            # Очищаем состояние
            state_manager.clear_state(message.from_user.id)
            return
        
        elif state_manager.is_in_state(message.from_user.id, UserState.REGISTERING):
            # Пользователь в процессе работы с устройствами
            session = state_manager.get_session(message.from_user.id)
            data = session.data or {}
            action = data.get("action")
            node_id = data.get("node_id")
            
            if action == "add":
                # Обработка добавления устройства
                logger.info("DEV ADD: Parsing node_id input '{}' for user {}", txt, message.from_user.id)
                try:
                    node_id = int(txt, 0)  # поддержка '123456' и '0x1A2B'
                    logger.info("DEV ADD: Parse OK: node_id={} for user {}", node_id, message.from_user.id)
                except Exception as e:
                    logger.warning("DEV ADD: Parse ERROR: '{}' for user {} - {}", txt, message.from_user.id, str(e))
                    from bot.keyboards.menu import back_to_dev_menu
                    await message.answer(_t(lang, "dev.invalid_node_id"), reply_markup=back_to_dev_menu(lang))
                    return
                
                from bridge.repo import link_node_to_user_manual
                logger.info("DEV ADD: Calling link_node_to_user_manual(node_id={}, tg_user_id={})", node_id, message.from_user.id)
                res = link_node_to_user_manual(node_id=node_id, tg_user_id=message.from_user.id)
                logger.info("DEV ADD: link_node_to_user_manual result: '{}' for user {}", res, message.from_user.id)
                
                if res == "ok":
                    await message.answer(_t(lang, "dev.add_ok", node_id=node_id), reply_markup=dev_menu(lang))
                elif res == "already":
                    await message.answer(_t(lang, "dev.add_already"), reply_markup=dev_menu(lang))
                elif res == "owned_by_other":
                    await message.answer(_t(lang, "dev.add_owned_by_other"), reply_markup=dev_menu(lang))
                else:  # 'limit'
                    await message.answer(_t(lang, "dev.limit"), reply_markup=dev_menu(lang))
                
                logger.info("DEV ADD: Clearing state for user {}", message.from_user.id)
                state_manager.clear_state(message.from_user.id)
                return
            
            elif action == "write" and node_id:
                # Обработка ввода текста для отправки на устройство
                from bridge.mqtt import publish_downlink
                payload = {"to": node_id, "type": "sendtext", "payload": f"[[TG]] {txt}"}
                ok = publish_downlink(payload)
                if ok:
                    await message.answer(_t(lang, "dev.sent"), reply_markup=dev_menu(lang))
                else:
                    await message.answer(_t(lang, "error.mqtt"), reply_markup=dev_menu(lang))
                state_manager.clear_state(message.from_user.id)
                return
            
            elif action == "rename" and node_id:
                # Обработка ввода метки для переименования устройства
                from bridge.repo import rename_user_device
                label = txt.strip()[:64]
                if rename_user_device(node_id, message.from_user.id, label):
                    await message.answer(_t(lang, "dev.renamed", node_id=node_id, label=label), reply_markup=dev_menu(lang))
                else:
                    await message.answer(_t(lang, "error.general"), reply_markup=dev_menu(lang))
                state_manager.clear_state(message.from_user.id)
                return
            
            else:
                # Неизвестное действие - очищаем состояние
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

    # Обработчик неизвестных сообщений перенесён в fallback_router

    # Run MQTT consumer in a parallel task
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, run_consumer)

    logger.info("Starting bot polling")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())


