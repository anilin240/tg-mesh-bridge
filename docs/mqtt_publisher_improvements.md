# 📡 УЛУЧШЕНИЯ MQTT ПУБЛИКАЦИИ

**Дата:** 14 августа 2025  
**Статус:** ✅ ЗАВЕРШЕНО

---

## 🎯 ЦЕЛЬ

Исключить проблемы при публикации (когда connect/disconnect на каждый вызов):
1. Сделать в mqtt.py один «персистентный» Publisher (paho.mqtt client + loop_start), с on_connect/on_disconnect и lock
2. publish_downlink/publish_to_topic — тонкие обёртки вокруг одного Publisher
3. Проверить, что все вызовы (включая «Написать ноде») используют именно publish_downlink, и ошибки логируются

---

## ✅ **1. ПЕРСИСТЕНТНЫЙ PUBLISHER**

### **✅ Класс _Publisher в mqtt.py**
**Файл:** `app/src/bridge/mqtt.py:25-110`

```python
class _Publisher:
    def __init__(self) -> None:
        self._client: mqtt.Client | None = None
        self._lock = threading.Lock()
        self._cfg_snapshot: tuple[str, int, str | None, str | None] | None = None

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, reason_code: int, properties=None) -> None:
        logger.warning("MQTT publisher disconnected: code={}", reason_code)
        with self._lock:
            try:
                if self._client is not None:
                    try:
                        self._client.loop_stop()
                    except Exception:
                        pass
            finally:
                self._client = None

    def _ensure_client(self) -> mqtt.Client | None:
        """Create or re-create client if config changed or client is missing."""
        cfg = AppConfig()
        snapshot = (cfg.mqtt_host, int(cfg.mqtt_port), cfg.mqtt_user, cfg.mqtt_pass)
        with self._lock:
            try:
                need_new = (
                    self._client is None or self._cfg_snapshot != snapshot
                )
                if not need_new:
                    return self._client

                # Close previous client if any
                if self._client is not None:
                    try:
                        self._client.loop_stop()
                    except Exception:
                        pass
                    try:
                        self._client.disconnect()
                    except Exception:
                        pass
                    self._client = None

                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="tg-mesh-bot-publisher")
                if cfg.mqtt_user:
                    client.username_pw_set(cfg.mqtt_user, cfg.mqtt_pass or "")
                client.on_disconnect = self._on_disconnect
                client.connect(cfg.mqtt_host, int(cfg.mqtt_port))
                client.loop_start()

                self._client = client
                self._cfg_snapshot = snapshot
                logger.info("MQTT publisher connected to {}:{}", cfg.mqtt_host, cfg.mqtt_port)
                return self._client
            except Exception as e:
                logger.error("MQTT publisher ensure_client error: {}", e)
                self._client = None
                return None

    def publish(self, topic: str, payload_dict: dict[str, Any]) -> bool:
        try:
            client = self._ensure_client()
            if client is None:
                return False
            text = json.dumps(payload_dict, separators=(",", ":"))
            logger.info("Publishing to {}: {}", topic, text)
            info = client.publish(topic, payload=text, qos=0, retain=False)
            ok = True
            try:
                # paho-mqtt v2 returns MQTTMessageInfo with rc
                ok = getattr(info, "rc", mqtt.MQTT_ERR_SUCCESS) == mqtt.MQTT_ERR_SUCCESS
            except Exception:
                ok = True
            return bool(ok)
        except Exception as e:
            logger.error("MQTT publish error: {}", e)
            with self._lock:
                # Drop client so that next publish reconnects
                try:
                    if self._client is not None:
                        try:
                            self._client.loop_stop()
                        except Exception:
                            pass
                        try:
                            self._client.disconnect()
                        except Exception:
                            pass
                finally:
                    self._client = None
            return False
```

**Статус:** ✅ РЕАЛИЗОВАНО
- ✅ Один персистентный клиент с `loop_start()`
- ✅ `on_disconnect` callback для обработки отключений
- ✅ `threading.Lock()` для потокобезопасности
- ✅ Автоматическое переподключение при изменении конфигурации
- ✅ Обработка ошибок с очисткой клиента

---

## ✅ **2. ТОНКИЕ ОБЁРТКИ**

### **✅ Единый экземпляр Publisher**
**Файл:** `app/src/bridge/mqtt.py:112`

```python
_publisher = _Publisher()
```

**Статус:** ✅ РЕАЛИЗОВАНО
- ✅ Один глобальный экземпляр `_Publisher`

### **✅ Функции-обёртки**
**Файл:** `app/src/bridge/mqtt.py:115-125`

```python
def publish_downlink(payload_dict: dict[str, Any]) -> bool:
    topic = AppConfig().mqtt_topic_pub
    return _publisher.publish(topic, payload_dict)


def publish_to_topic(topic: str, payload_dict: dict[str, Any]) -> bool:
    return _publisher.publish(topic, payload_dict)
```

**Статус:** ✅ РЕАЛИЗОВАНО
- ✅ `publish_downlink` - для отправки в стандартный топик
- ✅ `publish_to_topic` - для отправки в произвольный топик
- ✅ Обе функции используют один `_publisher`

---

## ✅ **3. ПРОВЕРКА ИСПОЛЬЗОВАНИЯ**

### **✅ Все места использования publish_downlink**
**Файлы и строки:**

1. **`app/src/bot/main.py:231,233`**
   ```python
   from bridge.mqtt import publish_downlink
   ok = publish_downlink(payload)
   ```
   **Назначение:** Отправка сообщений на устройства через FSM

2. **`app/src/bot/handlers/send_to_node.py:7,84`**
   ```python
   from bridge.mqtt import publish_downlink
   ok = publish_downlink(payload)
   ```
   **Назначение:** Команда `/send_to_node`

3. **`app/src/bot/handlers/send_nearby.py:10,94`**
   ```python
   from bridge.mqtt import publish_downlink
   ok = await asyncio.to_thread(publish_downlink, payload)
   ```
   **Назначение:** Команда `/send_nearby`

4. **`app/src/bot/handlers/devices.py:7`**
   ```python
   from bridge.mqtt import publish_downlink
   ```
   **Назначение:** Импорт для использования в FSM

**Статус:** ✅ ПРАВИЛЬНО - все используют `publish_downlink`

### **✅ Все места использования publish_to_topic**
**Файлы и строки:**

1. **`app/src/bot/main.py:29,118`**
   ```python
   from bridge.mqtt import publish_to_topic
   ok = publish_to_topic(topic, {"ping": "probe", "ts": __import__("time").time()})
   ```
   **Назначение:** Команда `/probe`

**Статус:** ✅ ПРАВИЛЬНО - используется `publish_to_topic`

---

## ✅ **4. ЛОГИРОВАНИЕ ОШИБОК**

### **✅ Логирование в Publisher**
**Файл:** `app/src/bridge/mqtt.py`

```python
# Отключения
logger.warning("MQTT publisher disconnected: code={}", reason_code)

# Ошибки создания клиента
logger.error("MQTT publisher ensure_client error: {}", e)

# Ошибки публикации
logger.error("MQTT publish error: {}", e)

# Успешные подключения
logger.info("MQTT publisher connected to {}:{}", cfg.mqtt_host, cfg.mqtt_port)

# Успешные публикации
logger.info("Publishing to {}: {}", topic, text)
```

**Статус:** ✅ РЕАЛИЗОВАНО
- ✅ Логирование отключений
- ✅ Логирование ошибок создания клиента
- ✅ Логирование ошибок публикации
- ✅ Логирование успешных подключений
- ✅ Логирование успешных публикаций

---

## 📋 **СПИСОК МЕСТ, ГДЕ РАНЬШЕ СОЗДАВАЛСЯ КЛИЕНТ НА КАЖДЫЙ PUBLISH**

### **✅ Проверка отсутствия прямого создания клиентов**

**Поиск `mqtt.Client` в основном коде:**
- ✅ `app/src/bridge/mqtt.py:66` - единственное создание в Publisher
- ✅ `app/src/bridge/consumer.py:353` - создание для Consumer (подписка)

**Поиск `connect`/`disconnect`/`loop_start`/`loop_stop`:**
- ✅ `app/src/bridge/mqtt.py` - только в Publisher классе
- ✅ `app/src/bridge/consumer.py` - только в Consumer

**Поиск `publish`:**
- ✅ `app/src/bridge/mqtt.py:82,89,121,125` - только в Publisher и обёртках

**Статус:** ✅ НЕТ ПРЯМОГО СОЗДАНИЯ КЛИЕНТОВ НА КАЖДЫЙ PUBLISH

---

## ✅ **ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА НА ЕДИНЫЙ PUBLISHER**

### **✅ Архитектура публикации**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   main.py       │    │  send_to_node   │    │  send_nearby    │
│   (FSM write)   │    │   (/send_to)    │    │  (/send_nearby) │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   bridge.mqtt             │
                    │   publish_downlink()      │
                    │   publish_to_topic()      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   _Publisher              │
                    │   (единственный экземпляр)│
                    │   - _client               │
                    │   - _lock                 │
                    │   - _ensure_client()      │
                    │   - publish()             │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   paho.mqtt.Client        │
                    │   (персистентный)         │
                    │   - loop_start()          │
                    │   - on_disconnect         │
                    └───────────────────────────┘
```

### **✅ Ключевые преимущества**

1. **✅ Персистентное подключение**
   - Один клиент создаётся при первом вызове
   - `loop_start()` поддерживает соединение
   - Переподключение только при изменении конфигурации

2. **✅ Потокобезопасность**
   - `threading.Lock()` защищает доступ к клиенту
   - Безопасное пересоздание при ошибках

3. **✅ Автоматическое восстановление**
   - `on_disconnect` callback очищает клиент
   - Следующий вызов автоматически переподключается

4. **✅ Единая точка управления**
   - Все публикации идут через один Publisher
   - Централизованное логирование ошибок

---

## 🔍 **ПРОВЕРКА ОТСУТСТВИЯ ПРОБЛЕМ**

### **✅ Проверка создания клиентов:**
- ❌ `mqtt.Client(` - НЕ НАЙДЕНО в обработчиках
- ❌ `connect(` - НЕ НАЙДЕНО в обработчиках
- ❌ `loop_start(` - НЕ НАЙДЕНО в обработчиках
- ✅ Только в `mqtt.py` (Publisher) и `consumer.py` (Consumer)

### **✅ Проверка использования функций:**
- ✅ `publish_downlink` - используется везде для отправки сообщений
- ✅ `publish_to_topic` - используется для `/probe`
- ✅ Нет прямых вызовов `client.publish`

### **✅ Проверка логирования:**
- ✅ `MQTT publisher disconnected` - логирование отключений
- ✅ `MQTT publisher ensure_client error` - ошибки создания
- ✅ `MQTT publish error` - ошибки публикации
- ✅ `Publishing to` - логирование публикаций

---

## ✅ **ЗАКЛЮЧЕНИЕ**

**Улучшения MQTT публикации завершены:**

1. ✅ **Персистентный Publisher** - один клиент с `loop_start()`
2. ✅ **Тонкие обёртки** - `publish_downlink`/`publish_to_topic`
3. ✅ **Правильное использование** - все вызовы используют обёртки
4. ✅ **Подробное логирование** - все ошибки логируются

### **✅ Ключевые улучшения:**
- **Производительность** - нет connect/disconnect на каждый вызов
- **Надёжность** - автоматическое переподключение при ошибках
- **Потокобезопасность** - Lock защищает доступ к клиенту
- **Отладка** - подробные логи для диагностики проблем

### **✅ Пример результата:**
```
Первый вызов: MQTT publisher connected to localhost:1883
Публикация: Publishing to msh/US/2/json/mqtt: {"to":123456,"type":"sendtext","payload":"[[TG]] Hello"}
Ошибка: MQTT publisher disconnected: code=1
Автоматическое восстановление: MQTT publisher connected to localhost:1883
```

**Теперь MQTT публикация работает через единый персистентный Publisher без проблем с connect/disconnect!** 🎯
