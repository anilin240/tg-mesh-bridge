from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.keyboards.menu import dev_menu, dev_actions_menu, top_menu, MenuCB
from common.i18n import t
from bot.services.users import get_or_create_user
from bridge.mqtt import publish_downlink
from bridge.repo import (
    get_user_devices,
    link_node_to_user_manual,
    rename_user_device,
    delete_user_device,
    get_device_by_id_for_user,
)

dev_router = Router()

class DevFSM(StatesGroup):
    wait_node_id_for_add = State()
    wait_label_for_rename = State()
    wait_text_for_write = State()

def lang_for(obj) -> str:
    try:
        u = get_or_create_user(obj.from_user.id, getattr(obj, "chat", getattr(obj.message, "chat", None)).id)
        return u.language or "ru"
    except Exception:
        return "ru"

@dev_router.callback_query(MenuCB.filter(F.section == "dev"))
async def dev_root(cb: CallbackQuery, callback_data: MenuCB):
    if callback_data.action is not None:
        return
    lang = lang_for(cb)
    await cb.message.edit_text(t(lang, "dev.title"), reply_markup=dev_menu(lang))
    await cb.answer()

@dev_router.callback_query(MenuCB.filter())
async def dev_list(cb: CallbackQuery, callback_data: MenuCB):
    if callback_data.section != "dev" or callback_data.action != "list":
        return
    u = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    lang = u.language or "ru"
    items = get_user_devices(u.tg_user_id)
    if not items:
        await cb.message.edit_text(t(lang, "dev.none"), reply_markup=dev_menu(lang))
        return await cb.answer()
    lines = []
    for n in items:
        gw = n.last_gateway_node_id or "—"
        seen = n.last_seen_at.strftime("%Y-%m-%d %H:%M") if n.last_seen_at else "—"
        label = (getattr(n, "user_label", None) or n.alias or str(n.node_id))
        lines.append(t(lang, "dev.item", label=label, node_id=n.node_id, gw=gw, last_seen=seen))
    await cb.message.edit_text("\n".join(lines), reply_markup=dev_menu(lang))
    await cb.answer()

@dev_router.callback_query(MenuCB.filter())
async def dev_add(cb: CallbackQuery, callback_data: MenuCB, state: FSMContext):
    if callback_data.section != "dev" or callback_data.action != "add":
        return
    u = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    lang = u.language or "ru"
    items = get_user_devices(u.tg_user_id)
    if len(items) >= 3:
        await cb.message.edit_text(t(lang, "dev.limit"), reply_markup=dev_menu(lang))
        return await cb.answer()
    await state.set_state(DevFSM.wait_node_id_for_add)
    await cb.message.edit_text(t(lang, "dev.enter_node_id"))
    await cb.answer()

@dev_router.message(DevFSM.wait_node_id_for_add)
async def dev_add_value(m: Message, state: FSMContext):
    text = (m.text or "").strip()
    u = get_or_create_user(m.from_user.id, m.chat.id)
    lang = u.language or "ru"
    try:
        node_id = int(text, 0)  # поддержка '123456' и '0x1A2B'
    except Exception:
        return await m.answer(t(lang, "dev.enter_node_id"))
    res = link_node_to_user_manual(node_id=node_id, tg_user_id=u.tg_user_id)
    if res == "ok":
        await m.answer(t(lang, "dev.add_ok", node_id=node_id), reply_markup=top_menu(lang))
    elif res == "already":
        await m.answer(t(lang, "dev.add_already"), reply_markup=top_menu(lang))
    elif res == "owned_by_other":
        await m.answer(t(lang, "dev.add_owned_by_other"), reply_markup=top_menu(lang))
    else:  # 'limit'
        await m.answer(t(lang, "dev.limit"), reply_markup=top_menu(lang))
    await state.clear()

@dev_router.callback_query(MenuCB.filter())
async def dev_edit(cb: CallbackQuery, callback_data: MenuCB):
    if callback_data.section != "dev" or callback_data.action != "edit":
        return
    u = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    lang = u.language or "ru"
    items = get_user_devices(u.tg_user_id)
    if not items:
        await cb.message.edit_text(t(lang, "dev.none"), reply_markup=dev_menu(lang))
        return await cb.answer()
    n = items[0]  # можно расширить до списка кнопок по всем устройствам
    label = (getattr(n, "user_label", None) or n.alias or str(n.node_id))
    await cb.message.edit_text(
        t(lang, "dev.actions", label=label, node_id=n.node_id),
        reply_markup=dev_actions_menu(lang, n.node_id),
    )
    await cb.answer()

@dev_router.callback_query(MenuCB.filter())
async def dev_rename(cb: CallbackQuery, callback_data: MenuCB, state: FSMContext):
    if callback_data.section != "dev" or callback_data.action != "rename":
        return
    u = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    lang = u.language or "ru"
    node_id = callback_data.id
    n = get_device_by_id_for_user(node_id, u.tg_user_id)
    if not n:
        return await cb.answer()
    await state.set_state(DevFSM.wait_label_for_rename)
    await state.update_data(node_id=node_id)
    await cb.message.edit_text(t(lang, "dev.enter_label", node_id=node_id))
    await cb.answer()

@dev_router.message(DevFSM.wait_label_for_rename)
async def dev_rename_value(m: Message, state: FSMContext):
    data = await state.get_data()
    node_id = data.get("node_id")
    u = get_or_create_user(m.from_user.id, m.chat.id)
    lang = u.language or "ru"
    label = (m.text or "").strip()[:64]
    if rename_user_device(node_id, u.tg_user_id, label):
        await m.answer(t(lang, "dev.renamed", node_id=node_id, label=label), reply_markup=top_menu(lang))
    else:
        await m.answer("Error", reply_markup=top_menu(lang))
    await state.clear()

@dev_router.callback_query(MenuCB.filter())
async def dev_del_one(cb: CallbackQuery, callback_data: MenuCB):
    if callback_data.section != "dev" or callback_data.action != "del_one":
        return
    u = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    lang = u.language or "ru"
    node_id = callback_data.id
    if delete_user_device(node_id, u.tg_user_id):
        await cb.message.edit_text(t(lang, "dev.deleted", node_id=node_id), reply_markup=dev_menu(lang))
    else:
        await cb.message.edit_text("Error", reply_markup=dev_menu(lang))
    await cb.answer()

@dev_router.callback_query(MenuCB.filter())
async def dev_write(cb: CallbackQuery, callback_data: MenuCB, state: FSMContext):
    if callback_data.section != "dev" or callback_data.action != "write":
        return
    u = get_or_create_user(cb.from_user.id, cb.message.chat.id)
    lang = u.language or "ru"
    node_id = callback_data.id
    n = get_device_by_id_for_user(node_id, u.tg_user_id)
    if not n:
        return await cb.answer()
    label = (getattr(n, "user_label", None) or n.alias or str(n.node_id))
    await state.set_state(DevFSM.wait_text_for_write)
    await state.update_data(node_id=node_id, label=label)
    await cb.message.edit_text(t(lang, "dev.enter_message", node_id=node_id, label=label))
    await cb.answer()

@dev_router.message(DevFSM.wait_text_for_write)
async def dev_write_value(m: Message, state: FSMContext):
    data = await state.get_data()
    node_id = int(data["node_id"])
    u = get_or_create_user(m.from_user.id, m.chat.id)
    lang = u.language or "ru"
    payload = {"to": node_id, "type": "sendtext", "payload": f"[[TG]] {m.text}"}
    ok = publish_downlink(payload)
    if ok:
        await m.answer(t(lang, "dev.sent"), reply_markup=top_menu(lang))
    else:
        await m.answer("MQTT error", reply_markup=top_menu(lang))
    await state.clear()
