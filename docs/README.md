## tg-mesh-bridge — HOWTO

Запуск:
- Создайте `.env` в корне проекта (рядом с `infra/`), задайте `BOT_TOKEN`, `MQTT_*`, `POSTGRES_*` при необходимости.
- Поднимите стек:
```
make up
```

Миграции БД:
```
make db
```

Логи приложения:
```
make logs
```

Тесты:
```
make test
```

MQTT Проверка подписчика:
```
cd infra
docker compose exec mosquitto sh -lc "mosquitto_pub -h 192.168.50.81 -p 1883 -u bridge -P bridge -t 'msh/US/2/json/test/123' -m '{\"from\":111,\"sender\":9001,\"payload\":\"hello\"}'"
```

Команды бота:
- `/start` — выбор языка RU/EN
- `/help` — список команд и формат привязки
- `/link`, `/link new` — получить/обновить код привязки
- `/nearby [gateway_id]` — активные узлы рядом со шлюзом за 15 минут
- `/send_to_node <node_id> <text>` — отправить текст на узел
- `/send_nearby <gateway_id> <text>` — отправить на все узлы рядом со шлюзом (до 50 получателей)

Проверка привязки Meshtastic → Telegram:
1. Получите код через `/link`.
2. Опубликуйте JSON через MQTT, где payload содержит `@tg:<CODE> <text>`:
```
cd infra
docker compose exec mosquitto sh -lc "mosquitto_pub -h 192.168.50.81 -p 1883 -u bridge -P bridge -t 'msh/US/2/json/test/321' -m '{\"from\":1987123456,\"sender\":2130123456,\"payload\":\"@tg:YOURCODE hello from mesh\",\"id\":\"test-321\"}'"
```
3. Ожидается DM в Telegram и записи в таблицах `nodes`, `gateways`, `heard_map`, `messages`.


### Запуск на Pi

1) Скопируйте и настройте переменные окружения (файл лежит в корне):
```
cp .env.example .env && nano .env
```
2) Запустите сервисы:
```
cd infra && docker compose up -d --build
```
3) Проверьте здоровье приложения и логи:
```
docker compose ps && docker compose logs -f app
```

Примечание: контейнер Mosquitto при старте сам исправит права на файлы `passwords` и `acl`; `.env` читается из корня проекта (`../.env`).

### Скрипты

- `scripts/mqtt-selftest.sh` — проверяет, что подписка и публикация в MQTT работают локально (публикует тестовое сообщение и показывает, что подписчик его получил).
- `scripts/collect-logs.sh` — собирает логи стека и конфиги Mosquitto в zip-архив в домашней директории.


