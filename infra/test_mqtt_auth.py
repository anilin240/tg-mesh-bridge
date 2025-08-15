#!/usr/bin/env python3
"""
Тестовый скрипт для проверки MQTT аутентификации и ACL
"""
import paho.mqtt.client as mqtt
import time
import sys

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        print("✅ Успешное подключение к MQTT брокеру")
    elif rc == 5:
        print("❌ Ошибка аутентификации - неверный логин/пароль")
    else:
        print(f"❌ Ошибка подключения: {rc}")

def on_message(client, userdata, msg):
    print(f"📨 Получено сообщение: {msg.topic} -> {msg.payload.decode()}")

def on_publish(client, userdata, mid):
    print(f"📤 Сообщение опубликовано: {mid}")

def test_mqtt_connection():
    # Параметры подключения
    host = "localhost"
    port = 1883
    username = "your_mqtt_username"
password = "your_mqtt_password"
    
    print(f"🔌 Тестирование подключения к MQTT брокеру {host}:{port}")
    print(f"👤 Пользователь: {username}")
    
    # Создаём клиента
    client = mqtt.Client()
    client.username_pw_set(username, password)
    
    # Устанавливаем callback'и
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    
    try:
        # Подключаемся
        client.connect(host, port, 60)
        client.loop_start()
        
        # Ждём подключения
        time.sleep(2)
        
        # Тестируем подписку на топик для чтения
        print("\n📖 Тестирование подписки на msh/US/2/json/#")
        result = client.subscribe("msh/US/2/json/#")
        if result[0] == 0:
            print("✅ Подписка успешна")
        else:
            print(f"❌ Ошибка подписки: {result[0]}")
        
        # Тестируем публикацию в топик для записи
        print("\n📝 Тестирование публикации в msh/US/2/json/mqtt/")
        result = client.publish("msh/US/2/json/mqtt/test", "test message")
        if result[0] == 0:
            print("✅ Публикация успешна")
        else:
            print(f"❌ Ошибка публикации: {result[0]}")
        
        # Тестируем публикацию в запрещённый топик
        print("\n🚫 Тестирование публикации в запрещённый топик msh/forbidden/")
        result = client.publish("msh/forbidden/test", "forbidden message")
        if result[0] == 0:
            print("❌ Публикация в запрещённый топик прошла (ACL не работает)")
        else:
            print("✅ Публикация в запрещённый топик заблокирована")
        
        # Ждём немного для получения сообщений
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        client.loop_stop()
        client.disconnect()
    
    return True

if __name__ == "__main__":
    success = test_mqtt_connection()
    sys.exit(0 if success else 1)
