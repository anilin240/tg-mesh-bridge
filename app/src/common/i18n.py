from __future__ import annotations

from typing import Any, Mapping


EN: dict[str, str] = {
    "start_welcome": "Welcome! Choose your language:",
    "lang_set_en": "Language set: English",
    "lang_set_ru": "Language set: Russian",

    "link_code": "Your link code: {code}. Send @tg:{code} from your Meshtastic node to link it.",

    "nearby_header": "Active near {gateway} (15m):",
    "nearby_none": "— none —",
    "invalid_gateway": "Invalid gateway_node_id. Use: /nearby [gateway_node_id]",
    "no_gateways": "No gateways seen yet.",
    "min_ago": "{minutes} min ago",

    "usage_send_to_node": "Usage: /send_to_node <node_id> <text>",
    "invalid_node_id": "Invalid node_id. Use integer.",
    "empty_text": "Text cannot be empty.",
    "no_gateway": "No gateway available to reach the node.",
    "sent_via_gateway": "Sent via gateway {gateway}.",
    "mqtt_publish_failed": "Failed to publish to MQTT.",
    "send_error": "Failed to send message to node.",

    "usage_send_nearby": "Usage: /send_nearby <gateway_node_id> <text>",
    "no_active_nodes_nearby": "No active nodes near this gateway in the last 15 minutes.",
    "sent_to_count": "Sent to {count} node(s) via gateway {gateway}.",
    "sent_to_count_truncated": "Sent to {count} node(s) via gateway {gateway}. Skipped {skipped}.",
    "rate_limited": "Too many requests. Try again later.",
    "nearby_limited": "Sent to {delivered}/{total} node(s). Limited by policy.",

    "help": (
        "Commands:\n"
        "/start — language selection\n"
        "/link — get your link code\n"
        "/send_to_node <node_id> <text> — send text to a node\n"
        "/send_nearby <gateway_id> <text> — send text to all nodes heard by the gateway (15m)\n"
        "/nearby [gateway_id] — list active nodes near the gateway (15m)\n\n"
        "Meshtastic format example: @tg:<CODE> <text>\n"
        "Get your <CODE> via /link"
    ),
    "link_new": "New link code: {code}",
    "link_set_prompt": "Send: /link set <CODE> (4-8 chars, A-Z and 2-9)",
    "link_set_ok": "Code set.",
    "link_set_invalid": "Invalid code. Use 4-8 chars from A-Z and 2-9.",
    "link_set_taken": "This code is already taken.",
    "change_code_prompt": (
        "🔄 **Change Code**\n\n"
        "Send your new code (4-8 characters, letters and numbers only).\n"
        "Or send 'auto' to generate a random code.\n\n"
        "**Current code:** {current_code}\n"
        "**Your Chat ID:** {chat_id}"
    ),
    "change_code_auto": "Auto-generated new code: {code}",
    "change_code_manual": "Code changed to: {code}",
    "change_code_invalid": "Invalid code. Use 4-8 characters, letters and numbers only.",
    "change_code_taken": "This code is already taken. Try another one.",
    
    # Новые ключи для улучшенного интерфейса
    "menu.top": "Выберите действие:",
    "menu.code": "📨 TG-код",
    "menu.devices": "📱 Мои устройства",
    "menu.nearby": "🌐 Рядом",
    "menu.help": "❓ Помощь",

    "messages.title": "📨 **Получение сообщений**\n\nНастройте получение сообщений из MeshTastic в ваш Telegram. Выберите действие:",
    "messages.show": "🔑 Показать код",
    "messages.change": "🔄 Сменить код",
    "messages.set": "⚙️ Настроить код",
    "messages.current": "Ваш код для получения сообщений: <b>{code}</b>",
    "messages.changed": "Новый код: <b>{code}</b>",
    "messages.enter_new": "Отправьте новый код (A–Z, 0–9, 4–12 символов):",
    "messages.set_ok": "Код установлен: <b>{code}</b>",
    "messages.set_fail": "Неверный код или уже занят. Попробуйте другой.",

    "dev.title": "📱 **Мои устройства**\n\nУправление подключенными MeshTastic-устройствами (до 3 на аккаунт). Выберите действие:",
    "dev.add": "➕ Добавить устройство",
    "dev.list": "📋 Список устройств",
    "dev.edit": "✏️ Редактировать",
    "dev.delete": "🗑️ Удалить",
    "dev.none": "У вас пока нет привязанных устройств.",
    "dev.limit": "Достигнут лимит: 3 устройства на аккаунт.",
    "dev.enter_node_id": "Отправьте <b>Node ID</b> устройства (число/hex):",
    "dev.add_ok": "Устройство добавлено: <b>{node_id}</b>",
    "dev.add_already": "Это устройство уже привязано к вам.",
    "dev.add_owned_by_other": "Устройство привязано к другому пользователю.",
    "dev.pick_for_edit": "Выберите устройство для редактирования:",
    "dev.pick_for_delete": "Выберите устройство для удаления:",
    "dev.pick_for_write": "Выберите устройство для отправки сообщения:",
    "dev.enter_label": "Введите новое имя (метка) для устройства <b>{node_id}</b>:",
    "dev.renamed": "Устройство <b>{node_id}</b> переименовано в: <b>{label}</b>",
    "dev.deleted": "Устройство удалено: <b>{node_id}</b>",
    "dev.item": "• <b>{label}</b> (ID: {node_id}) — последний шлюз: {gw} — виделись: {last_seen}",
    "dev.actions": "Устройство <b>{label}</b> (ID: {node_id}). Что сделать?",
    "dev.action.write": "✍️ Написать",
    "dev.action.rename": "✏️ Переименовать",
    "dev.action.delete": "🗑️ Удалить",
            "dev.enter_message": "Введите текст для <b>{label}</b> (ID: {node_id}):",
        "dev.sent": "Сообщение отправлено на устройство.",
                "dev.edit_device": "Устройство: <b>{label}</b> (ID: {node_id})",
        
        # Системные сообщения
        "system.node_linked": "Нода {node_id} привязана к вашему аккаунту.",
        
        # Обработчик неизвестных сообщений
        "unknown_message": "Используйте меню ниже для навигации:",

    "nearby.title": "Nodes heard at the selected gateway (15 min):",
    "nearby.refresh": "Refresh",
    "nearby.none": "No fresh data for the selected gateway.",

    "help.body": (
        "<b>How it works</b>\n"
        "1) TG Code: include @tg:YOUR_CODE in Mesh message to receive in TG.\n"
        "2) My Nodes: link up to 3 devices to write to them from the bot.\n"
        "3) Nearby: see who the internet gateway hears.\n"
    ),
    "register_prompt": (
        "📝 **Registration**\n\n"
        "You will register in the system. This will be linked to your Telegram account.\n"
        "You will be able to communicate with nodes through this.\n\n"
        "**Send your desired code in the next message.**\n"
        "Code must be 4-8 characters, letters and numbers only (e.g.: ABCD1234)"
    ),
    "welcome_long": (
        "Welcome to TG-Mesh Bridge!\n\n"
        "This bot links your Meshtastic device with Telegram.\n"
        "1) Get or set your personal code via buttons below (or /link).\n"
        "2) From your Meshtastic node send: @tg:<CODE> <text> to DM yourself here.\n"
        "3) You can register a node to your account with /register_node <node_id> [alias]."
    ),
    "register_ok": "You are registered. Your chat is saved and your code is {code}.",
    "register_node_usage": "Usage: /register_node <node_id> [alias]",
    "register_node_ok": "Node {node_id} registered to your account{alias_part}.",
    "register_node_taken": "Alias is already taken. Choose another one.",
    "register_node_invalid": "Invalid node_id. Use integer.",
    
    # Errors and system messages
    "error.unknown_command": "Unknown command",
    "error.menu_update": "Menu update error",
    "error.general": "Error",
    "error.mqtt": "MQTT error",
    "error.nearby_fetch": "Failed to fetch nearby nodes",
    "system.pong": "pong",
    "system.probe_sent": "probe sent",
    "system.probe_failed": "probe failed",
}


RU: dict[str, str] = {
    "start_welcome": "Добро пожаловать! Выберите язык:",
    "lang_set_en": "Язык установлен: Английский",
    "lang_set_ru": "Язык установлен: Русский",

    "link_code": "Ваш код привязки: {code}. Отправьте @tg:{code} с вашего Meshtastic-узла, чтобы привязать его.",

    "nearby_header": "Активные рядом с шлюзом {gateway} (15 мин):",
    "nearby_none": "— нет —",
    "invalid_gateway": "Некорректный gateway_node_id. Используйте: /nearby [gateway_node_id]",
    "no_gateways": "Шлюзы ещё не обнаружены.",
    "min_ago": "{minutes} мин назад",

    "usage_send_to_node": "Использование: /send_to_node <node_id> <text>",
    "invalid_node_id": "Некорректный node_id. Нужен целое число.",
    "empty_text": "Текст не может быть пустым.",
    "no_gateway": "Нет доступного шлюза для доставки узлу.",
    "sent_via_gateway": "Отправлено через шлюз {gateway}.",
    "mqtt_publish_failed": "Не удалось опубликовать в MQTT.",
    "send_error": "Не удалось отправить сообщение узлу.",

    "usage_send_nearby": "Использование: /send_nearby <gateway_node_id> <text>",
    "no_active_nodes_nearby": "Нет активных узлов рядом с этим шлюзом за последние 15 минут.",
    "sent_to_count": "Отправлено {count} узлам через шлюз {gateway}.",
    "sent_to_count_truncated": "Отправлено {count} узлам через шлюз {gateway}. Пропущено {skipped}.",
    "rate_limited": "Слишком много запросов. Попробуйте позже.",
    "nearby_limited": "Отправлено {delivered} из {total} узлов. Ограничено политикой.",

    "help": (
        "Команды:\n"
        "/start — выбор языка\n"
        "/link — получить код привязки\n"
        "/send_to_node <node_id> <text> — отправить текст на узел\n"
        "/send_nearby <gateway_id> <text> — отправить всем узлам рядом со шлюзом (15 мин)\n"
        "/nearby [gateway_id] — список активных узлов рядом со шлюзом (15 мин)\n\n"
        "Пример для Mesh: @tg:<CODE> <текст>\n"
        "Получить <CODE> можно через /link"
    ),
    "link_new": "Новый код: {code}",
    "link_set_prompt": "Отправьте: /link set <КОД> (4–8 символов, A-Z и 2–9)",
    "link_set_ok": "Код установлен.",
    "link_set_invalid": "Некорректный код. Используйте 4–8 символов из A-Z и 2–9.",
    "link_set_taken": "Такой код уже занят.",
    "change_code_prompt": (
        "🔄 **Смена кода**\n\n"
        "Отправьте новый код (4-8 символов, только буквы и цифры).\n"
        "Или отправьте 'auto' для автогенерации.\n\n"
        "**Текущий код:** {current_code}\n"
        "**Ваш Chat ID:** {chat_id}"
    ),
    "change_code_auto": "Автогенерированный код: {code}",
    "change_code_manual": "Код изменён на: {code}",
    "change_code_invalid": "Некорректный код. Используйте 4-8 символов, только буквы и цифры.",
    "change_code_taken": "Этот код уже занят. Попробуйте другой.",
    "register_prompt": (
        "📝 **Регистрация**\n\n"
        "Вы зарегистрируетесь в системе. Это привяжется к вашему Telegram-аккаунту.\n"
        "Вы сможете через это общаться с нодами.\n\n"
        "**Отправьте следующим сообщением свой код, который хотите использовать.**\n"
        "Код должен быть 4-8 символов, только буквы и цифры (например: ABCD1234)"
    ),
    "welcome_long": (
        "Добро пожаловать в TG-Mesh Bridge!\n\n"
        "Этот бот связывает ваш Meshtastic с Telegram.\n"
        "1) Получите или задайте личный код через кнопки ниже (или /link).\n"
        "2) С узла Meshtastic отправьте: @tg:<КОД> <текст>, чтобы получить сообщение здесь.\n"
        "3) Зарегистрируйте ноду на себя: /register_node <node_id> [alias]."
    ),
    "register_ok": "Регистрация выполнена. Чат сохранён, ваш код: {code}.",
    "register_node_usage": "Использование: /register_node <node_id> [alias]",
    "register_node_ok": "Нода {node_id} привязана к вашему аккаунту{alias_part}.",
    "register_node_taken": "Имя (alias) уже занято. Выберите другое.",
    "register_node_invalid": "Некорректный node_id. Нужен целое число.",
    
    # Ошибки и системные сообщения
    "error.unknown_command": "Неизвестная команда",
    "error.menu_update": "Ошибка обновления меню",
    "error.general": "Ошибка",
    "error.mqtt": "Ошибка MQTT",
    "error.nearby_fetch": "Не удалось получить список нод",
    "system.pong": "pong",
    "system.probe_sent": "probe sent",
    "system.probe_failed": "probe failed",
    
    # Новые ключи для улучшенного интерфейса
    "menu.top": "Выберите действие:",
    "menu.code": "TG‑код",
    "menu.devices": "Мои ноды",
    "menu.nearby": "Рядом",
    "menu.help": "Помощь",
    "menu.back": "🔙 Назад",

    "code.title": "TG‑код — это метка для доставки сообщений из MeshTastic в ваш Telegram.\nВыберите действие:",
    "code.show": "Показать код",
    "code.change": "Сменить код",
    "code.set": "Задать код",
    "code.current": "Ваш текущий TG‑код: <b>{code}</b>",
    "code.changed": "Сгенерирован новый TG‑код: <b>{code}</b>",
    "code.enter_new": "Отправьте новый TG‑код (латинские буквы/цифры, 4–12 символов):",
    "code.set_ok": "TG‑код сохранён: <b>{code}</b>",
    "code.set_fail": "Неверный формат или код занят. Попробуйте другой.",

    "dev.title": "Мои ноды (до 3 на аккаунт). Что сделать?",
    "dev.add": "Добавить",
    "dev.list": "Список",
    "dev.edit": "Редактировать",
    "dev.delete": "Удалить",
    "dev.none": "У вас пока нет привязанных устройств.",
    "dev.limit": "Достигнут лимит: 3 устройства на аккаунт.",
    "dev.enter_node_id": "Отправьте <b>Node ID</b> устройства (число/hex):",
    "dev.add_ok": "Устройство добавлено: <b>{node_id}</b>",
    "dev.add_already": "Это устройство уже привязано к вам.",
    "dev.add_owned_by_other": "Устройство привязано к другому пользователю.",
    "dev.pick_for_edit": "Выберите устройство для редактирования:",
    "dev.pick_for_delete": "Выберите устройство для удаления:",
    "dev.pick_for_write": "Выберите устройство для отправки сообщения:",
    "dev.enter_label": "Введите новое имя (метка) для устройства <b>{node_id}</b>:",
    "dev.renamed": "Устройство <b>{node_id}</b> переименовано в: <b>{label}</b>",
    "dev.deleted": "Устройство удалено: <b>{node_id}</b>",
    "dev.item": "• <b>{label}</b> (ID: {node_id}) — последний шлюз: {gw} — виделись: {last_seen}",
    "dev.actions": "Устройство <b>{label}</b> (ID: {node_id}). Что сделать?",
    "dev.action.write": "Написать",
    "dev.action.rename": "Переименовать",
    "dev.action.delete": "Удалить",
    "dev.enter_message": "Введите текст для <b>{label}</b> (ID: {node_id}):",
    "dev.sent": "Сообщение отправлено в MeshTastic.",
    "dev.invalid_node_id": "❌ Неверный формат Node ID. Используйте число (например: 123456) или hex (например: 0x1A2B).",
    
    # Обработчик неизвестных сообщений
    "unknown_message": "Используйте меню ниже для навигации:",

    "nearby.title": "Узлы, слышимые у выбранного шлюза за 15 минут:",
    "nearby.refresh": "Обновить",
    "nearby.none": "Нет свежих данных по выбранному шлюзу.",

    "help.body": (
        "<b>Как это работает</b>\n"
        "1) TG‑код: вставляйте в сообщение из Mesh: @tg:ВАШ_КОД — и оно придёт вам в TG.\n"
        "2) Мои ноды: привяжите до 3 устройств, чтобы писать на них из бота.\n"
        "3) Рядом: смотрите кого слышит интернет‑шлюз.\n"
    ),
}


messages: dict[str, Mapping[str, str]] = {
    "en": {
        "help": (
            "Commands:\n"
            "/start – choose language\n"
            "/link – get your code\n"
            "/link new – regenerate code\n"
            "/nearby [gateway] – nodes active near gateway (15m)\n"
            "/send_to_node <node_id> <text>\n"
            "/send_nearby <gateway_id> <text>\n"
            "/status – service status\n\n"
            "From Meshtastic: @tg:<CODE> <text>"
        ),
        "rate_limit": "Too many requests. Please slow down.",
        "nearby_limited": "Sent to {delivered}/{total} node(s). Limited by policy.",
        "status_header": "Status:",
        "status_db_ok": "- DB: OK",
        "status_db_err": "- DB: ERROR",
        "status_mqtt_connected": "- MQTT: connected",
        "status_mqtt_disconnected": "- MQTT: disconnected",
        "status_last_mqtt": "- Last MQTT msg: {ago}",
        "status_active_nodes": "- Active nodes (15m): {count}",
        "status_gateways": "- Gateways: {total} (fresh: {fresh})",
        "status_uptime": "- Uptime: {uptime}",
        "nearby_header": "Active near {gateway} (15m):",
        "sent_via_gateway": "Sent via gateway {gateway}.",
        "no_gateway": "No gateway available.",
        "link_code": "Your link code: {code}. Send @tg:{code} from your Meshtastic node to link it.",
        "link_new": "New link code: {code}",
        "node_linked": "Node {node_id} has been linked to your account.",
        "min_ago": "{minutes} min ago",
        "no_gateways": "No gateways seen yet.",
        "invalid_gateway": "Invalid gateway_node_id. Use: /nearby [gateway_node_id]",
        
        # Новые ключи для улучшенного интерфейса
        "menu.top": "Choose an action:",
        "menu.code": "TG Code",
        "menu.devices": "My Nodes",
        "menu.nearby": "Nearby",
        "menu.help": "Help",
        "menu.back": "🔙 Back",
        "code.title": "TG Code routes MeshTastic messages to your Telegram. Choose:",
        "code.show": "Show code",
        "code.change": "New random",
        "code.set": "Set code",
        "code.current": "Your TG Code: <b>{code}</b>",
        "code.changed": "New TG Code: <b>{code}</b>",
        "code.enter_new": "Send a new TG Code (A–Z, 0–9, 4–12 chars):",
        "code.set_ok": "TG Code set: <b>{code}</b>",
        "code.set_fail": "Invalid or taken. Try another.",
        "dev.title": "My nodes (up to 3 per account). Choose:",
        "dev.add": "Add",
        "dev.list": "List",
        "dev.edit": "Edit",
        "dev.delete": "Delete",
        "dev.none": "No devices yet.",
        "dev.limit": "Limit reached: 3 devices per account.",
        "dev.enter_node_id": "Send device <b>Node ID</b> (int/hex):",
        "dev.invalid_node_id": "❌ Invalid Node ID format. Use number (e.g., 123456) or hex (e.g., 0x1A2B).",
        "dev.add_ok": "Device added: <b>{node_id}</b>",
        "dev.add_already": "This device is already linked to you.",
        "dev.add_owned_by_other": "This device is linked to another user.",
        "dev.pick_for_edit": "Pick a device to edit:",
        "dev.pick_for_delete": "Pick a device to delete:",
        "dev.pick_for_write": "Pick a device to write:",
        "dev.enter_label": "Send new label for device <b>{node_id}</b>:",
        "dev.renamed": "Device <b>{node_id}</b> renamed to: <b>{label}</b>",
        "dev.deleted": "Device deleted: <b>{node_id}</b>",
        "dev.item": "• <b>{label}</b> (ID: {node_id}) — last GW: {gw} — seen: {last_seen}",
        "dev.actions": "Device <b>{label}</b> (ID: {node_id}). Choose:",
        "dev.action.write": "Write",
        "dev.action.rename": "Rename",
        "dev.action.delete": "Delete",
        "dev.enter_message": "Enter text for <b>{label}</b> (ID: {node_id}):",
        "dev.sent": "Message sent to MeshTastic.",
        "dev.edit_device": "Device: <b>{label}</b> (ID: {node_id})",
        
        # System messages
        "system.node_linked": "Node {node_id} has been linked to your account.",
        
        # Unknown message handler
        "unknown_message": "Use the menu below for navigation:",
        "nearby.title": "Nodes heard at the selected gateway (15 min):",
        "nearby.refresh": "Refresh",
        "nearby.none": "No fresh data for the selected gateway.",
        "help.body": (
            "<b>How it works</b>\n"
            "1) TG Code: include @tg:YOUR_CODE in Mesh message to receive in TG.\n"
            "2) My Nodes: link up to 3 devices to write to them from the bot.\n"
            "3) Nearby: see who the internet gateway hears.\n"
        ),
    },
    "ru": {
        "help": (
            "Команды:\n"
            "/start – выбор языка\n"
            "/link – получить код\n"
            "/link new – сгенерировать новый код\n"
            "/nearby [gateway] – активные ноды у шлюза (15 мин)\n"
            "/send_to_node <node_id> <текст>\n"
            "/send_nearby <gateway_id> <текст>\n"
            "/status – статус сервиса\n\n"
            "С меш-устройства: @tg:<КОД> <текст>"
        ),
        "rate_limit": "Слишком часто. Пожалуйста, замедлитесь.",
        "nearby_limited": "Отправлено {delivered} из {total}. Ограничено политикой.",
        "status_header": "Статус:",
        "status_db_ok": "- БД: OK",
        "status_db_err": "- БД: ОШИБКА",
        "status_mqtt_connected": "- MQTT: подключено",
        "status_mqtt_disconnected": "- MQTT: нет подключения",
        "status_last_mqtt": "- Последнее MQTT-сообщение: {ago}",
        "status_active_nodes": "- Активные ноды (15 мин): {count}",
        "status_gateways": "- Шлюзы: {total} (свежие: {fresh})",
        "status_uptime": "- Аптайм: {uptime}",
        "nearby_header": "Активные рядом со шлюзом {gateway} (15 мин):",
        "sent_via_gateway": "Отправлено через шлюз {gateway}.",
        "no_gateway": "Нет доступного шлюза.",
        "link_code": "Ваш код: {code}. Отправьте @tg:{code} с Meshtastic-устройства для привязки.",
        "link_new": "Новый код: {code}",
        "node_linked": "Нода {node_id} привязана к вашему аккаунту.",
        "min_ago": "{minutes} мин назад",
        "no_gateways": "Шлюзы ещё не обнаружены.",
        "invalid_gateway": "Некорректный gateway_node_id. Используйте: /nearby [gateway_node_id]",
        
        # Новые ключи для улучшенного интерфейса
        "menu.top": "Выберите действие:",
        "menu.code": "📨 TG-код",
        "menu.devices": "📱 Мои устройства",
        "menu.nearby": "🌐 Рядом",
        "menu.help": "❓ Помощь",
        "menu.back": "🔙 Назад",
        "messages.title": "📨 **Получение сообщений**\n\nНастройте получение сообщений из MeshTastic в ваш Telegram. Выберите действие:",
        "messages.show": "🔑 Показать код",
        "messages.change": "🔄 Сменить код",
        "messages.set": "⚙️ Настроить код",
        "messages.current": "Ваш код для получения сообщений: <b>{code}</b>",
        "messages.changed": "Новый код: <b>{code}</b>",
        "messages.enter_new": "Отправьте новый код (A–Z, 0–9, 4–12 символов):",
        "messages.set_ok": "Код установлен: <b>{code}</b>",
        "messages.set_fail": "Неверный код или уже занят. Попробуйте другой.",
        "dev.title": "📱 **Мои устройства**\n\nУправление подключенными MeshTastic-устройствами (до 3 на аккаунт). Выберите действие:",
        "dev.add": "➕ Добавить устройство",
        "dev.list": "📋 Список устройств",
        "dev.edit": "✏️ Редактировать",
        "dev.delete": "🗑️ Удалить",
        "dev.none": "У вас пока нет привязанных устройств.",
        "dev.limit": "Достигнут лимит: 3 устройства на аккаунт.",
        "dev.enter_node_id": "Отправьте <b>Node ID</b> устройства (число/hex):",
        "dev.invalid_node_id": "❌ Неверный формат Node ID. Используйте число (например: 123456) или hex (например: 0x1A2B).",
        "dev.add_ok": "Устройство добавлено: <b>{node_id}</b>",
        "dev.add_already": "Это устройство уже привязано к вам.",
        "dev.add_owned_by_other": "Устройство привязано к другому пользователю.",
        "dev.pick_for_edit": "Выберите устройство для редактирования:",
        "dev.pick_for_delete": "Выберите устройство для удаления:",
        "dev.pick_for_write": "Выберите устройство для отправки сообщения:",
        "dev.enter_label": "Введите новое имя (метка) для устройства <b>{node_id}</b>:",
        "dev.renamed": "Устройство <b>{node_id}</b> переименовано в: <b>{label}</b>",
        "dev.deleted": "Устройство удалено: <b>{node_id}</b>",
        "dev.item": "• <b>{label}</b> (ID: {node_id}) — последний шлюз: {gw} — виделись: {last_seen}",
        "dev.actions": "Устройство <b>{label}</b> (ID: {node_id}). Что сделать?",
        "dev.action.write": "✍️ Написать",
        "dev.action.rename": "✏️ Переименовать",
        "dev.action.delete": "🗑️ Удалить",
        "dev.enter_message": "Введите текст для <b>{label}</b> (ID: {node_id}):",
        "dev.sent": "Сообщение отправлено в MeshTastic.",
        "dev.edit_device": "Устройство: <b>{label}</b> (ID: {node_id})",
        
        # Системные сообщения
        "system.node_linked": "Node {node_id} has been linked to your account.",
        
        # Обработчик неизвестных сообщений
        "unknown_message": "Используйте меню ниже для навигации:",
        "nearby.title": "Узлы, слышимые у выбранного шлюза за 15 минут:",
        "nearby.refresh": "Обновить",
        "nearby.none": "Нет свежих данных по выбранному шлюзу.",
        "help.body": (
            "<b>Как это работает</b>\n"
            "1) TG‑код: вставляйте в сообщение из Mesh: @tg:ВАШ_КОД — и оно придёт вам в TG.\n"
            "2) Мои ноды: привяжите до 3 устройств, чтобы писать на них из бота.\n"
            "3) Рядом: смотрите кого слышит интернет‑шлюз.\n"
        ),
    },
}

LANGS: dict[str, Mapping[str, str]] = {"en": {**EN, **messages["en"]}, "ru": {**RU, **messages["ru"]}}


def get(lang: str, key: str, /, **kwargs: Any) -> str:
    lang = (lang or "en").lower()
    dct = LANGS.get(lang) or EN
    template = dct.get(key) or EN.get(key) or key
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def t(lang: str, key: str, /, **kwargs: Any) -> str:
    return get(lang, key, **kwargs)


__all__ = ["get", "t", "messages"]


