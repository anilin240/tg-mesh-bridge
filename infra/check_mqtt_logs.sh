#!/bin/bash
# Скрипт для проверки логов MQTT брокера

echo "🔍 Проверка логов MQTT брокера"
echo "================================"

# Проверяем, запущен ли контейнер
if ! docker ps | grep -q tg-mesh-mosquitto; then
    echo "❌ Контейнер tg-mesh-mosquitto не запущен"
    exit 1
fi

echo "✅ Контейнер tg-mesh-mosquitto запущен"

# Проверяем логи контейнера
echo ""
echo "📋 Логи контейнера (последние 20 строк):"
echo "----------------------------------------"
docker logs --tail 20 tg-mesh-mosquitto

# Проверяем статус контейнера
echo ""
echo "📊 Статус контейнера:"
echo "--------------------"
docker inspect --format='{{.State.Status}}' tg-mesh-mosquitto

# Проверяем переменные окружения
echo ""
echo "🔧 Переменные окружения:"
echo "------------------------"
docker exec tg-mesh-mosquitto env | grep MQTT

# Проверяем файлы конфигурации
echo ""
echo "📁 Файлы конфигурации:"
echo "---------------------"
echo "mosquitto.conf:"
docker exec tg-mesh-mosquitto cat /mosquitto/config/mosquitto.conf

echo ""
echo "passwords:"
docker exec tg-mesh-mosquitto cat /mosquitto/config/passwords

echo ""
echo "acl:"
docker exec tg-mesh-mosquitto cat /mosquitto/config/acl

# Проверяем права доступа
echo ""
echo "🔐 Права доступа:"
echo "----------------"
docker exec tg-mesh-mosquitto ls -la /mosquitto/config/

echo ""
echo "✅ Проверка завершена"
