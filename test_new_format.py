#!/usr/bin/env python3
"""
Скрипт для тестирования нового формата сообщений в Telegram
"""

import paho.mqtt.publish as publish
import json
import time

# Конфигурация MQTT (используем те же данные, что и в контейнере)
MQTT_HOST = "your_mqtt_host_ip"
MQTT_PORT = 1883
MQTT_USERNAME = "bridge"
MQTT_PASSWORD = "your_mqtt_password"
MQTT_TOPIC = "msh/US/2/json/mqtt/"

def send_test_message():
    """Отправить тестовое сообщение с новым форматом"""
    
    # Создаем тестовое сообщение
    test_message = {
        "to": 4294967295,  # Broadcast
        "type": "sendtext",  # Изменено на sendtext
        "payload": "[[TG]] @tg:SHPIL1 Привет! Это тестовое сообщение с новым красивым форматом! 🎉"
    }
    
    print(f"Отправляем тестовое сообщение...")
    print(f"Тема: {MQTT_TOPIC}")
    print(f"Сообщение: {json.dumps(test_message, indent=2)}")
    
    try:
        # Отправляем сообщение
        publish.single(
            topic=MQTT_TOPIC,
            payload=json.dumps(test_message),
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD}
        )
        print("✅ Сообщение отправлено успешно!")
        print("Проверьте Telegram - должно прийти сообщение в новом формате:")
        print("**@shpil_portable**: Привет! Это тестовое сообщение с новым красивым форматом! 🎉")
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

if __name__ == "__main__":
    send_test_message()
