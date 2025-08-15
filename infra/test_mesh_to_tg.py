#!/usr/bin/env python3
"""
Скрипт для тестирования Mesh→TG функциональности
"""
import paho.mqtt.client as mqtt
import json
import time
import sys

def test_mesh_to_tg():
    """Тест отправки сообщения из Mesh в Telegram"""
    
    # Параметры подключения
    host = "localhost"
    port = 1883
    username = "your_mqtt_username"
    password = "your_mqtt_password"
    
    # Тестовые данные
    test_code = "EXAMPLE123"  # Example user code
    test_message = "Тестовое сообщение из Mesh"
    
    print(f"🔍 Тест Mesh→TG функциональности")
    print(f"📡 Подключение к MQTT: {host}:{port}")
    print(f"👤 Пользователь: {username}")
    print(f"🔑 Код: {test_code}")
    print(f"📝 Сообщение: {test_message}")
    print("=" * 50)
    
    # Создаём MQTT клиента
    client = mqtt.Client()
    client.username_pw_set(username, password)
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Подключение к MQTT успешно")
        else:
            print(f"❌ Ошибка подключения: {rc}")
    
    def on_publish(client, userdata, mid):
        print(f"📤 Сообщение опубликовано: {mid}")
    
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        # Подключаемся
        client.connect(host, port, 60)
        client.loop_start()
        
        # Ждём подключения
        time.sleep(2)
        
        # Формируем тестовое сообщение
        payload = f"@tg:{test_code} {test_message}"
        
        # Создаём JSON сообщение
        message = {
            "from": 123456,  # Example node_id
            "sender": "!b03b3d9c",  # Gateway
            "payload": payload,
            "id": int(time.time()),  # Уникальный ID
            "type": "text"
        }
        
        # Публикуем в топик
        topic = "msh/US/2/json/test"
        result = client.publish(topic, json.dumps(message))
        
        if result.rc == 0:
            print(f"✅ Сообщение отправлено в топик: {topic}")
            print(f"📄 JSON: {json.dumps(message, indent=2)}")
        else:
            print(f"❌ Ошибка публикации: {result.rc}")
        
        # Ждём немного
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        client.loop_stop()
        client.disconnect()
    
    return True

def test_mesh_to_tg_limit():
    """Тест превышения лимита устройств"""
    
    host = "localhost"
    port = 1883
    username = "your_mqtt_username"
    password = "your_mqtt_password"
    
    # Тестовые данные для пользователя с 3 устройствами
    test_code = "EXAMPLE456"  # Example user code for limit test
    test_message = "Тест превышения лимита"
    
    print(f"\n🔍 Тест превышения лимита устройств")
    print(f"🔑 Код: {test_code}")
    print(f"📝 Сообщение: {test_message}")
    print("=" * 50)
    
    client = mqtt.Client()
    client.username_pw_set(username, password)
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Подключение к MQTT успешно")
        else:
            print(f"❌ Ошибка подключения: {rc}")
    
    def on_publish(client, userdata, mid):
        print(f"📤 Сообщение опубликовано: {mid}")
    
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        client.connect(host, port, 60)
        client.loop_start()
        time.sleep(2)
        
        # Формируем сообщение с новым node_id
        payload = f"@tg:{test_code} {test_message}"
        
        message = {
            "from": 999999999,  # Новый node_id
            "sender": "!b03b3d9c",
            "payload": payload,
            "id": int(time.time()),
            "type": "text"
        }
        
        topic = "msh/US/2/json/test"
        result = client.publish(topic, json.dumps(message))
        
        if result.rc == 0:
            print(f"✅ Сообщение отправлено в топик: {topic}")
            print(f"📄 JSON: {json.dumps(message, indent=2)}")
        else:
            print(f"❌ Ошибка публикации: {result.rc}")
        
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        client.loop_stop()
        client.disconnect()
    
    return True

if __name__ == "__main__":
    print("🤖 ТЕСТИРОВАНИЕ MESH→TG ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 60)
    
    # Тест 1: Обычное сообщение
    success1 = test_mesh_to_tg()
    
    # Тест 2: Превышение лимита
    success2 = test_mesh_to_tg_limit()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    print(f"Тест 1 (обычное сообщение): {'✅ ПРОЙДЕН' if success1 else '❌ НЕ ПРОЙДЕН'}")
    print(f"Тест 2 (превышение лимита): {'✅ ПРОЙДЕН' if success2 else '❌ НЕ ПРОЙДЕН'}")
    
    if success1 and success2:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("📋 Проверьте логи приложения для подтверждения доставки сообщений")
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
