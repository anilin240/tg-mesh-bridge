#!/bin/bash
# Скрипт для проверки функций бота

echo "🤖 ПРОВЕРКА ФУНКЦИЙ БОТА"
echo "========================"
echo "Время: $(date)"
echo ""

# Проверяем статус контейнеров
echo "🔍 Проверка статуса контейнеров..."
if docker ps | grep -q tg-mesh-app; then
    echo "✅ Контейнер tg-mesh-app запущен"
else
    echo "❌ Контейнер tg-mesh-app не запущен"
    exit 1
fi

if docker ps | grep -q tg-mesh-postgres; then
    echo "✅ Контейнер tg-mesh-postgres запущен"
else
    echo "❌ Контейнер tg-mesh-postgres не запущен"
    exit 1
fi

echo ""

# 1. Проверка данных пользователей
echo "📊 1. ПРОВЕРКА ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ"
echo "-----------------------------------"
echo "Пользователи в базе:"
docker exec tg-mesh-postgres psql -U tgmesh -d tgmesh -c "SELECT tg_user_id, tg_code, language FROM users ORDER BY tg_user_id;"

echo ""

# 2. Проверка устройств
echo "📱 2. ПРОВЕРКА УСТРОЙСТВ"
echo "------------------------"
echo "Привязанные устройства:"
docker exec tg-mesh-postgres psql -U tgmesh -d tgmesh -c "SELECT node_id, owner_tg_user_id, user_label, alias FROM nodes WHERE owner_tg_user_id IS NOT NULL ORDER BY owner_tg_user_id, node_id;"

echo ""

# 3. Проверка лимита устройств
echo "🔢 3. ПРОВЕРКА ЛИМИТА УСТРОЙСТВ"
echo "-------------------------------"
echo "Количество устройств по пользователям:"
docker exec tg-mesh-postgres psql -U tgmesh -d tgmesh -c "SELECT owner_tg_user_id, COUNT(*) as device_count FROM nodes WHERE owner_tg_user_id IS NOT NULL GROUP BY owner_tg_user_id ORDER BY owner_tg_user_id;"

echo ""

# 4. Проверка MQTT сообщений
echo "📡 4. ПРОВЕРКА MQTT СООБЩЕНИЙ"
echo "-----------------------------"
echo "Последние 5 MQTT сообщений:"
docker logs --tail 10 tg-mesh-app | grep "MQTT message" | tail -5

echo ""

# 5. Проверка логов приложения
echo "📋 5. ПРОВЕРКА ЛОГОВ ПРИЛОЖЕНИЯ"
echo "-------------------------------"
echo "Последние 10 строк логов:"
docker logs --tail 10 tg-mesh-app

echo ""

# 6. Проверка функций через SQL
echo "🔧 6. ПРОВЕРКА ФУНКЦИЙ ЧЕРЕЗ SQL"
echo "--------------------------------"

# Проверка функции переименования
echo "Тест переименования устройства:"
docker exec tg-mesh-postgres psql -U tgmesh -d tgmesh -c "UPDATE nodes SET user_label = 'Тестовое устройство $(date +%s)' WHERE node_id = 123456;"

# Проверка результата
echo "Результат переименования:"
docker exec tg-mesh-postgres psql -U tgmesh -d tgmesh -c "SELECT node_id, user_label FROM nodes WHERE node_id = 123456;"

echo ""

# 7. Проверка MQTT брокера
echo "🔌 7. ПРОВЕРКА MQTT БРОКЕРА"
echo "---------------------------"
echo "Статус MQTT брокера:"
docker logs --tail 5 tg-mesh-mosquitto

echo ""

# 8. Проверка сетевых подключений
echo "🌐 8. ПРОВЕРКА СЕТЕВЫХ ПОДКЛЮЧЕНИЙ"
echo "---------------------------------"
echo "Порты:"
docker exec tg-mesh-app netstat -tlnp 2>/dev/null | grep -E "(1883|5432)" || echo "netstat недоступен"

echo ""

# 9. Проверка переменных окружения
echo "⚙️ 9. ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ"
echo "-----------------------------------"
echo "MQTT настройки:"
docker exec tg-mesh-app env | grep MQTT

echo ""

# 10. Итоговая проверка
echo "📊 10. ИТОГОВАЯ ПРОВЕРКА"
echo "------------------------"
echo "Статус всех сервисов:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep tg-mesh

echo ""
echo "✅ Проверка завершена"
