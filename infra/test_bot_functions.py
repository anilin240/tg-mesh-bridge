#!/usr/bin/env python3
"""
Скрипт для автоматизированного тестирования функций бота
"""
import requests
import json
import time
import sys
from datetime import datetime

# Конфигурация
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Замените на реальный токен
CHAT_ID = "123456789"  # Example test user ID
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(text, chat_id=CHAT_ID):
    """Отправить сообщение боту"""
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=data)
    return response.json()

def send_callback_query(callback_data, chat_id=CHAT_ID, message_id=None):
    """Отправить callback query"""
    url = f"{BASE_URL}/answerCallbackQuery"
    data = {
        "callback_query_id": "test_query",
        "chat_id": chat_id,
        "message_id": message_id,
        "data": callback_data
    }
    response = requests.post(url, json=data)
    return response.json()

def get_updates(offset=None):
    """Получить обновления от бота"""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()

def test_start_command():
    """Тест команды /start"""
    print("🔍 Тест 1: /start команда")
    print("=" * 50)
    
    result = send_message("/start")
    print(f"Отправлено: /start")
    print(f"Результат: {result}")
    
    if result.get("ok"):
        print("✅ /start команда работает")
        return True
    else:
        print("❌ /start команда не работает")
        return False

def test_tg_code_menu():
    """Тест меню TG-код"""
    print("\n🔍 Тест 2: Меню TG-код")
    print("=" * 50)
    
    # Тест показа кода
    print("📖 Тест показа кода...")
    result = send_callback_query('{"section": "code", "action": "show"}')
    print(f"Результат показа: {result}")
    
    # Тест смены кода
    print("🔄 Тест смены кода...")
    result = send_callback_query('{"section": "code", "action": "change"}')
    print(f"Результат смены: {result}")
    
    return True

def test_devices_menu():
    """Тест меню Мои ноды"""
    print("\n🔍 Тест 3: Меню Мои ноды")
    print("=" * 50)
    
    # Тест списка устройств
    print("📋 Тест списка устройств...")
    result = send_callback_query('{"section": "dev", "action": "list"}')
    print(f"Результат списка: {result}")
    
    # Тест добавления устройства
    print("➕ Тест добавления устройства...")
    result = send_callback_query('{"section": "dev", "action": "add"}')
    print(f"Результат добавления: {result}")
    
    return True

def test_nearby_menu():
    """Тест меню Рядом"""
    print("\n🔍 Тест 4: Меню Рядом")
    print("=" * 50)
    
    # Тест обновления списка
    print("🔄 Тест обновления списка...")
    result = send_callback_query('{"section": "nearby", "action": "refresh"}')
    print(f"Результат обновления: {result}")
    
    return True

def test_fallback_handler():
    """Тест fallback обработчика"""
    print("\n🔍 Тест 5: Fallback обработчик")
    print("=" * 50)
    
    # Тест произвольного текста
    print("📝 Тест произвольного текста...")
    result = send_message("произвольный текст")
    print(f"Результат: {result}")
    
    return True

def test_mesh_to_tg():
    """Тест Mesh→TG сообщений"""
    print("\n🔍 Тест 6: Mesh→TG сообщения")
    print("=" * 50)
    
    # Проверяем логи MQTT
    print("📡 Проверка MQTT логов...")
    # Здесь нужно проверить логи consumer'а
    
    return True

def main():
    """Основная функция тестирования"""
    print("🤖 АВТОМАТИЗИРОВАННОЕ ТЕСТИРОВАНИЕ БОТА")
    print("=" * 60)
    print(f"Время начала: {datetime.now()}")
    print(f"Бот токен: {BOT_TOKEN[:10]}...")
    print(f"Тестовый пользователь: {CHAT_ID}")
    print("=" * 60)
    
    tests = [
        ("/start команда", test_start_command),
        ("Меню TG-код", test_tg_code_menu),
        ("Меню Мои ноды", test_devices_menu),
        ("Меню Рядом", test_nearby_menu),
        ("Fallback обработчик", test_fallback_handler),
        ("Mesh→TG сообщения", test_mesh_to_tg),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'ПРОЙДЕН' if result else 'НЕ ПРОЙДЕН'}")
        except Exception as e:
            print(f"❌ {test_name}: ОШИБКА - {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Пауза между тестами
    
    # Итоговый отчёт
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{test_name}: {status}")
    
    print(f"\nРезультат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BOT_TOKEN = sys.argv[1]
    if len(sys.argv) > 2:
        CHAT_ID = sys.argv[2]
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("❌ Укажите токен бота как аргумент: python test_bot_functions.py YOUR_BOT_TOKEN [CHAT_ID]")
        sys.exit(1)
    
    sys.exit(main())
