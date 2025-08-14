## Миграции БД (Alembic)

Зависимости установлены в `app/requirements.txt`: SQLAlchemy, Alembic, psycopg[binary].

### Переменные окружения
Используются переменные контейнера для подключения к Postgres:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

DSN формируется как: `postgresql+psycopg://<user>:<pass>@<host>:<port>/<db>`

### Основные команды

1) Поднять контейнеры
```
cd infra
docker compose up -d --build
```

2) Применить миграции
```
docker compose exec app alembic upgrade head
```

3) Проверить таблицы
```
docker compose exec postgres sh -lc "psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -c \"\\dt\""
```
Ожидаются таблицы: `users`, `nodes`, `gateways`, `heard_map`, `messages` (+ служебная `alembic_version`).

### Создание новой миграции (при изменении моделей)
После правок в `app/src/common/models.py`:
```
docker compose exec app alembic revision -m "your message" --autogenerate
docker compose exec app alembic upgrade head
```


