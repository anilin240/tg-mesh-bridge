from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.menu import top_menu, MenuCB
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
    lang = user_lang(m)
    await m.answer(t(lang, "menu.top"), reply_markup=top_menu(lang))

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
        elif callback_data.section == "messages":
            if callback_data.action is None:
                from bot.keyboards.menu import messages_menu
                await cb.message.edit_text(t(lang, "messages.title"), reply_markup=messages_menu(lang))
            elif callback_data.action == "show":
                from bot.services.users import get_or_create_user
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                code = user.tg_code or "НЕТ"
                await cb.message.edit_text(t(lang, "messages.current", code=code), reply_markup=top_menu(lang), parse_mode="HTML")
            elif callback_data.action == "change":
                from bot.services.users import change_code_auto
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                ok, key = change_code_auto(cb.from_user.id, cb.message.chat.id)
                if ok:
                    new_code = user.tg_code or ""
                    await cb.message.edit_text(t(lang, key, code=new_code), reply_markup=top_menu(lang), parse_mode="HTML")
                else:
                    await cb.message.edit_text(t(lang, key), reply_markup=top_menu(lang), parse_mode="HTML")
            elif callback_data.action == "set":
                from bot.states import state_manager, UserState
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                current_code = user.tg_code or "НЕТ"
                state_manager.set_state(cb.from_user.id, UserState.CHANGING_CODE)
                await cb.message.edit_text(
                    t(lang, "change_code_prompt", current_code=current_code, chat_id=cb.message.chat.id),
                    reply_markup=top_menu(lang), parse_mode="HTML"
                )
            else:
                logger.warning("Unknown messages action: {}", callback_data.action)
                await cb.answer("Неизвестная команда")
                return
        elif callback_data.section == "dev":
            if callback_data.action is None:
                from bot.keyboards.menu import dev_menu
                await cb.message.edit_text(t(lang, "dev.title"), reply_markup=dev_menu(lang), parse_mode="HTML")
            elif callback_data.action == "add":
                from bot.states import state_manager, UserState
                state_manager.set_state(cb.from_user.id, UserState.REGISTERING)
                await cb.message.edit_text(t(lang, "dev.enter_node_id"), reply_markup=top_menu(lang), parse_mode="HTML")
            elif callback_data.action == "list":
                from bot.services.users import get_or_create_user
                from bridge.repo import get_user_devices
                user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
                items = get_user_devices(user.tg_user_id)
                if not items:
                    await cb.message.edit_text(t(lang, "dev.none"), reply_markup=top_menu(lang), parse_mode="HTML")
                else:
                    lines = []
                    for n in items:
                        gw = n.last_gateway_node_id or "—"
                        seen = n.last_seen_at.strftime("%Y-%m-%d %H:%M") if n.last_seen_at else "—"
                        label = (getattr(n, "user_label", None) or n.alias or str(n.node_id))
                        lines.append(t(lang, "dev.item", label=label, node_id=n.node_id, gw=gw, last_seen=seen))
                    await cb.message.edit_text("\n".join(lines), reply_markup=top_menu(lang), parse_mode="HTML")
            elif callback_data.action == "edit":
                await cb.message.edit_text(t(lang, "dev.pick_for_edit"), reply_markup=top_menu(lang), parse_mode="HTML")
            elif callback_data.action == "delete":
                await cb.message.edit_text(t(lang, "dev.pick_for_delete"), reply_markup=top_menu(lang), parse_mode="HTML")
            else:
                logger.warning("Unknown dev action: {}", callback_data.action)
                await cb.answer("Неизвестная команда")
                return
        elif callback_data.section == "network":
            if callback_data.action is None:
                from bot.keyboards.menu import network_menu
                await cb.message.edit_text(t(lang, "nearby.title"), reply_markup=network_menu(lang), parse_mode="HTML")
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
                logger.warning("Unknown network action: {}", callback_data.action)
                await cb.answer("Неизвестная команда")
                return
        else:
            logger.warning("Unknown callback: section={}, action={}", callback_data.section, callback_data.action)
            await cb.answer("Неизвестная команда")
            return
    except Exception as e:
        logger.error("Error handling callback: {}", e)
        await cb.answer("Ошибка обновления меню")
        return
    
    await cb.answer()

# Обработчики для подменю "messages"
@menu_router.callback_query(MenuCB.filter())
async def messages_show_cb(cb: CallbackQuery, callback_data: MenuCB):
    if callback_data.section != "messages" or callback_data.action != "show":
        return
    lang = user_lang(cb)
    from bot.services.users import get_or_create_user
    user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    code = user.tg_code or "НЕТ"
    await cb.message.edit_text(t(lang, "messages.current", code=code), reply_markup=top_menu(lang))
    await cb.answer()

@menu_router.callback_query(MenuCB.filter())
async def messages_change_cb(cb: CallbackQuery, callback_data: MenuCB):
    if callback_data.section != "messages" or callback_data.action != "change":
        return
    lang = user_lang(cb)
    from bot.services.users import change_code_auto
    from bot.states import state_manager, UserState
    
    user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    ok, key = change_code_auto(cb.from_user.id, cb.message.chat.id)
    if ok:
        new_code = user.tg_code or ""
        await cb.message.edit_text(t(lang, key, code=new_code), reply_markup=top_menu(lang))
    else:
        await cb.message.edit_text(t(lang, key), reply_markup=top_menu(lang))
    await cb.answer()

@menu_router.callback_query(MenuCB.filter())
async def messages_set_cb(cb: CallbackQuery, callback_data: MenuCB):
    if callback_data.section != "messages" or callback_data.action != "set":
        return
    lang = user_lang(cb)
    from bot.states import state_manager, UserState
    
    user = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    current_code = user.tg_code or "НЕТ"
    
    state_manager.set_state(cb.from_user.id, UserState.CHANGING_CODE)
    await cb.message.edit_text(
        t(lang, "change_code_prompt", current_code=current_code, chat_id=cb.message.chat.id),
        reply_markup=top_menu(lang)
    )
    await cb.answer()
