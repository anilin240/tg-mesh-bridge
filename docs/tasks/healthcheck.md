## Healthcheck для сервиса app

Скрипт: `python -m bot.healthcheck`

Проверки:
- Подключение к БД через SQLAlchemy (`SELECT 1`).
- Проверка наличия конфигурации MQTT (MQTT_HOST/MQTT_PORT).
- Опционально, при `REQUIRE_MQTT_SEEN=true` — проверяется, что `state.last_mqtt_message_at` был не старше 10 минут.

Результат:
- При успехе — exit(0)
- При ошибке — exit(1) и запись в логи причины

Настройка в docker compose (`infra/docker-compose.yml`):
```
healthcheck:
  test: ["CMD", "python", "-m", "bot.healthcheck"]
  interval: 20s
  timeout: 5s
  retries: 5
  start_period: 20s
```

Проверка:
- `docker compose up -d --build`
- `docker compose ps` — статус `app` должен стать `(healthy)`
- Включить строгую проверку MQTT: в `.env` добавить `REQUIRE_MQTT_SEEN=true`, затем перезапустить `app`
- Остановить брокер: `docker compose stop mosquitto`, подождать >10 минут — статус `app` станет `unhealthy`
- Запустить брокер: `docker compose start mosquitto` — после поступления сообщений статус вернётся к `healthy`


