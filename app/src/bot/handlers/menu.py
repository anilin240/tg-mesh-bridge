from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.menu import top_menu, code_menu, dev_menu, nearby_menu, MenuCB, language_menu

from common.i18n import t
from bot.services.users import get_or_create_user

menu_router = Router()

def user_lang(msg_or_cb) -> str:
    try:
        from_user = msg_or_cb.from_user
        chat = msg_or_cb.chat if hasattr(msg_or_cb, "chat") else msg_or_cb.message.chat
        u = get_or_create_user(tg_user_id=from_user.id, tg_chat_id=chat.id)
        return u.language or "ru"
    except Exception:
        return "ru"

@menu_router.message(Command("start"))
async def start_cmd(m: Message):
    from loguru import logger
    logger.info("START: User {} sent /start command", m.from_user.id)
    logger.info("START: Message text: '{}'", m.text)
    logger.info("START: Chat ID: {}, User ID: {}", m.chat.id, m.from_user.id)
    
    try:
        # Показываем меню выбора языка
        await m.answer("Выберите язык / Choose language:", reply_markup=language_menu())
        logger.info("START: Successfully sent language menu to user {}", m.from_user.id)
    except Exception as e:
        logger.error("START: Error sending language menu to user {}: {}", m.from_user.id, e)
        # Fallback - отправляем простое сообщение
        await m.answer("Привет! / Hello!")

@menu_router.message(Command("help"))
async def help_cmd(m: Message):
    lang = user_lang(m)
    await m.answer(t(lang, "help.body"), reply_markup=top_menu(lang))

@menu_router.callback_query(MenuCB.filter())
async def universal_callback_handler(cb: CallbackQuery, callback_data: MenuCB):
    from loguru import logger
    logger.info("Universal callback received: section={}, action={}", callback_data.section, callback_data.action)
    
    lang = user_lang(cb)
    
    try:
        if callback_data.section == "main":
            await cb.message.edit_text(t(lang, "menu.top"), reply_markup=top_menu(lang), parse_mode="HTML")
        elif callback_data.section == "help":
            await cb.message.edit_text(t(lang, "help.body"), reply_markup=top_menu(lang), parse_mode="HTML")
        elif callback_data.section == "code":
            if callback_data.action is None:
                await cb.message.edit_text(t(lang, "code.title"), reply_markup=code_menu(lang))
            elif callback_data.action == "show":
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                code = user.tg_code or "НЕТ"
                await cb.message.edit_text(t(lang, "code.current", code=code), reply_markup=code_menu(lang), parse_mode="HTML")
            elif callback_data.action == "change":
                from bot.services.users import change_code_auto
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                ok, key = change_code_auto(cb.from_user.id, cb.message.chat.id)
                if ok:
                    new_code = user.tg_code or ""
                    await cb.message.edit_text(t(lang, key, code=new_code), reply_markup=code_menu(lang), parse_mode="HTML")
                else:
                    await cb.message.edit_text(t(lang, key), reply_markup=code_menu(lang), parse_mode="HTML")
            elif callback_data.action == "set":
                from bot.states import state_manager, UserState
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                current_code = user.tg_code or "НЕТ"
                state_manager.set_state(cb.from_user.id, UserState.CHANGING_CODE)
                await cb.message.edit_text(
                    t(lang, "change_code_prompt", current_code=current_code, chat_id=cb.message.chat.id),
                    reply_markup=code_menu(lang), parse_mode="HTML"
                )
            else:
                logger.warning("Unknown code action: {}", callback_data.action)
                await cb.answer(t(lang, "error.unknown_command"))
                return
        elif callback_data.section == "dev":
            if callback_data.action is None:
                await cb.message.edit_text(t(lang, "dev.title"), reply_markup=dev_menu(lang), parse_mode="HTML")
            elif callback_data.action == "add":
                from bot.states import state_manager, UserState
                from bot.keyboards.menu import back_to_dev_menu
                logger.info("DEV ADD: User {} clicked 'Add device' button", cb.from_user.id)
                state_manager.set_state(cb.from_user.id, UserState.REGISTERING, {"action": "add"})
                logger.info("DEV ADD: Set UserState.REGISTERING with action=add for user {}", cb.from_user.id)
                await cb.message.edit_text(t(lang, "dev.enter_node_id"), reply_markup=back_to_dev_menu(lang), parse_mode="HTML")
            elif callback_data.action == "list":
                from bridge.repo import get_user_devices
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                items = get_user_devices(user.tg_user_id)
                if not items:
                    await cb.message.edit_text(t(lang, "dev.none"), reply_markup=dev_menu(lang), parse_mode="HTML")
                else:
                    lines = []
                    for n in items:
                        gw = n.last_gateway_node_id or "—"
                        seen = n.last_seen_at.strftime("%Y-%m-%d %H:%M") if n.last_seen_at else "—"
                        label = (getattr(n, "user_label", None) or n.alias or str(n.node_id))
                        lines.append(t(lang, "dev.item", label=label, node_id=n.node_id, gw=gw, last_seen=seen))
                    await cb.message.edit_text("\n".join(lines), reply_markup=dev_menu(lang), parse_mode="HTML")
            elif callback_data.action == "edit":
                # Показываем список устройств для редактирования
                from bridge.repo import get_user_devices
                from bot.keyboards.menu import dev_actions_menu
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                items = get_user_devices(user.tg_user_id)
                if not items:
                    await cb.message.edit_text(t(lang, "dev.none"), reply_markup=dev_menu(lang), parse_mode="HTML")
                else:
                    lines = [t(lang, "dev.pick_for_edit")]
                    for n in items:
                        label = (getattr(n, "user_label", None) or n.alias or str(n.node_id))
                        lines.append(f"• <b>{label}</b> (ID: {n.node_id})")
                    text = "\n".join(lines)
                    # Создаём клавиатуру с кнопками для каждого устройства
                    keyboard = []
                    for n in items:
                        keyboard.append([InlineKeyboardButton(
                            text=f"✏️ {getattr(n, 'user_label', None) or n.alias or str(n.node_id)}",
                            callback_data=MenuCB(section="dev", action="edit_device", id=n.node_id).pack()
                        )])
                    keyboard.append([InlineKeyboardButton(text=t(lang, "menu.back"), callback_data=MenuCB(section="dev").pack())])
                    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                    await cb.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
            elif callback_data.action == "delete":
                # Показываем список устройств для удаления
                from bridge.repo import get_user_devices
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                items = get_user_devices(user.tg_user_id)
                if not items:
                    await cb.message.edit_text(t(lang, "dev.none"), reply_markup=dev_menu(lang), parse_mode="HTML")
                else:
                    lines = [t(lang, "dev.pick_for_delete")]
                    for n in items:
                        label = (getattr(n, "user_label", None) or n.alias or str(n.node_id))
                        lines.append(f"• <b>{label}</b> (ID: {n.node_id})")
                    text = "\n".join(lines)
                    # Создаём клавиатуру с кнопками для каждого устройства
                    keyboard = []
                    for n in items:
                        keyboard.append([InlineKeyboardButton(
                            text=f"🗑️ {getattr(n, 'user_label', None) or n.alias or str(n.node_id)}",
                            callback_data=MenuCB(section="dev", action="del_one", id=n.node_id).pack()
                        )])
                    keyboard.append([InlineKeyboardButton(text=t(lang, "menu.back"), callback_data=MenuCB(section="dev").pack())])
                    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                    await cb.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
            elif callback_data.action == "edit_device":
                # Показываем меню действий для конкретного устройства
                if not callback_data.id:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
                from bridge.repo import get_device_by_id_for_user
                from bot.keyboards.menu import dev_actions_menu
                device = get_device_by_id_for_user(callback_data.id, cb.from_user.id)
                if device:
                    label = (getattr(device, "user_label", None) or device.alias or str(device.node_id))
                    text = t(lang, "dev.edit_device", label=label, node_id=device.node_id)
                    markup = dev_actions_menu(lang, device.node_id)
                    # Добавляем кнопку "Назад"
                    markup.inline_keyboard.append([InlineKeyboardButton(text=t(lang, "menu.back"), callback_data=MenuCB(section="dev", action="edit").pack())])
                    await cb.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
                else:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
            elif callback_data.action == "write":
                # Обработка действия "Написать" для конкретного устройства
                if not callback_data.id:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
                
                # Получаем информацию об устройстве для отображения
                from bridge.repo import get_device_by_id_for_user
                from bot.keyboards.menu import back_to_dev_menu
                device = get_device_by_id_for_user(callback_data.id, cb.from_user.id)
                if device:
                    label = (getattr(device, "user_label", None) or device.alias or str(device.node_id))
                    await cb.message.edit_text(
                        t(lang, "dev.enter_message", label=label, node_id=device.node_id),
                        reply_markup=back_to_dev_menu(lang), parse_mode="HTML"
                    )
                    # Устанавливаем FSM состояние через state_manager
                    from bot.states import state_manager, UserState
                    state_manager.set_state(cb.from_user.id, UserState.REGISTERING, {"action": "write", "node_id": callback_data.id})
                else:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
            elif callback_data.action == "rename":
                # Обработка действия "Переименовать" для конкретного устройства
                if not callback_data.id:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
                
                # Получаем информацию об устройстве для отображения
                from bridge.repo import get_device_by_id_for_user
                from bot.keyboards.menu import back_to_dev_menu
                device = get_device_by_id_for_user(callback_data.id, cb.from_user.id)
                if device:
                    current_label = (getattr(device, "user_label", None) or device.alias or str(device.node_id))
                    await cb.message.edit_text(
                        t(lang, "dev.enter_label", node_id=device.node_id),
                        reply_markup=back_to_dev_menu(lang), parse_mode="HTML"
                    )
                    # Устанавливаем FSM состояние через state_manager
                    from bot.states import state_manager, UserState
                    state_manager.set_state(cb.from_user.id, UserState.REGISTERING, {"action": "rename", "node_id": callback_data.id})
                else:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
            elif callback_data.action == "back":
                # Обработка кнопки "Назад" - возврат к меню устройств
                from bot.states import state_manager
                logger.info("DEV BACK: User {} clicked 'Back' button", cb.from_user.id)
                # Очищаем состояние пользователя
                state_manager.clear_state(cb.from_user.id)
                logger.info("DEV BACK: Cleared state for user {}", cb.from_user.id)
                # Возвращаемся к меню устройств
                await cb.message.edit_text(t(lang, "dev.title"), reply_markup=dev_menu(lang), parse_mode="HTML")
                return
            elif callback_data.action == "del_one":
                # Обработка действия "Удалить" для конкретного устройства
                if not callback_data.id:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
                from bridge.repo import delete_user_device
                
                # Получаем информацию об устройстве для отображения
                from bridge.repo import get_device_by_id_for_user
                device = get_device_by_id_for_user(callback_data.id, cb.from_user.id)
                if device:
                    label = (getattr(device, "user_label", None) or device.alias or str(device.node_id))
                    if delete_user_device(callback_data.id, cb.from_user.id):
                        await cb.message.edit_text(
                            t(lang, "dev.deleted", node_id=device.node_id),
                            reply_markup=dev_menu(lang), parse_mode="HTML"
                        )
                    else:
                        await cb.answer(t(lang, "error.general"))
                        return
                else:
                    await cb.answer(t(lang, "error.unknown_command"))
                    return
            else:
                logger.warning("Unknown dev action: {}", callback_data.action)
                await cb.answer(t(lang, "error.unknown_command"))
                return
        elif callback_data.section == "nearby":
            if callback_data.action is None:
                await cb.message.edit_text(t(lang, "nearby.title"), reply_markup=nearby_menu(lang), parse_mode="HTML")
            elif callback_data.action == "refresh":
                from bot.handlers.nearby import _get_latest_gateway_node_id, _get_recent_nodes_for_gateway
                import math
                from datetime import datetime, timezone
                
                gateway_node_id = _get_latest_gateway_node_id()
                if gateway_node_id is None:
                    await cb.message.edit_text(t(lang, "no_gateways"), reply_markup=top_menu(lang), parse_mode="HTML")
                else:
                    rows = _get_recent_nodes_for_gateway(gateway_node_id)
                    if not rows:
                        header = t(lang, "nearby_header", gateway=gateway_node_id)
                        await cb.message.edit_text(f"{header}\n{t(lang, 'nearby_none')}", reply_markup=top_menu(lang), parse_mode="HTML")
                    else:
                        now_utc = datetime.now(timezone.utc)
                        lines: list[str] = [t(lang, "nearby_header", gateway=gateway_node_id)]
                        for node_id, alias, last_heard_at in rows:
                            diff_minutes = max(0, int(math.floor((now_utc - last_heard_at).total_seconds() / 60)))
                            alias_text = f" {alias}" if alias else ""
                            lines.append(f"• {node_id}{alias_text} ({t(lang, 'min_ago', minutes=diff_minutes)})")
                        await cb.message.edit_text("\n".join(lines), reply_markup=top_menu(lang), parse_mode="HTML")
            else:
                logger.warning("Unknown nearby action: {}", callback_data.action)
                await cb.answer(t(lang, "error.unknown_command"))
                return
        else:
            logger.warning("Unknown callback: section={}, action={}", callback_data.section, callback_data.action)
            await cb.answer(t(lang, "error.unknown_command"))
            return
    except Exception as e:
        logger.error("Error handling callback: {}", e)
        await cb.answer(t(lang, "error.menu_update"))
        return
    
    await cb.answer()
