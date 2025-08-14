#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# MQTT настройки
MQTT_HOST = "192.168.50.81"
MQTT_PORT = 1883
MQTT_USER = "bridge"
MQTT_PASS = "bridge"
MQTT_TOPIC = "msh/US/2/json/#"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Подключение к MQTT брокеру {MQTT_HOST}:{MQTT_PORT} успешно!")
        print(f"👤 Пользователь: {MQTT_USER}")
        print(f"📡 Подписываемся на топик: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC, qos=0)
        print("🚀 Готов к приему сообщений от нод!")
        print("-" * 50)
    else:
        print(f"❌ Ошибка подключения: {rc}")

def on_message(client, userdata, msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n📨 [{timestamp}] Получено сообщение:")
    print(f"   Топик: {msg.topic}")
    
    try:
        # Пытаемся распарсить JSON
        payload = msg.payload.decode('utf-8', errors='replace')
        print(f"   Сырые данные: {payload}")
        
        data = json.loads(payload)
        print(f"   📋 JSON данные:")
        for key, value in data.items():
            print(f"      {key}: {value}")
        
        # Проверяем наличие кода @tg:
        if 'payload' in data and isinstance(data['payload'], str):
            payload_text = data['payload']
            if '@tg:' in payload_text:
                print(f"   🎯 Найден код @tg: в сообщении!")
                # Извлекаем код
                import re
                match = re.search(r'@tg:([A-Z0-9]{4,8})', payload_text)
                if match:
                    code = match.group(1)
                    print(f"   🔑 Извлеченный код: {code}")
                    # Извлекаем сообщение после кода
                    message_start = payload_text.find(code) + len(code)
                    message = payload_text[message_start:].strip()
                    if message:
                        print(f"   💬 Сообщение: {message}")
        
    except json.JSONDecodeError:
        print(f"   ⚠️  Не удалось распарсить JSON")
        print(f"   Сырые данные: {msg.payload.decode('utf-8', errors='replace')}")
    except Exception as e:
        print(f"   ❌ Ошибка обработки: {e}")
    
    print("-" * 50)

def on_disconnect(client, userdata, rc):
    print(f"🔌 Отключение от MQTT брокера: {rc}")

def main():
    print("🔍 Тестирование подключения к MQTT брокеру")
    print(f"🌐 Сервер: {MQTT_HOST}:{MQTT_PORT}")
    print(f"👤 Пользователь: {MQTT_USER}")
    print(f"📡 Топик: {MQTT_TOPIC}")
    print("=" * 50)
    
    # Создаем MQTT клиент
    client = mqtt.Client(client_id="test-mqtt-client")
    
    # Устанавливаем учетные данные
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    
    # Устанавливаем обработчики событий
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        # Подключаемся к брокеру
        print("🔗 Подключение к MQTT брокеру...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        
        # Запускаем цикл обработки сообщений
        print("⏳ Ожидание сообщений... (Ctrl+C для выхода)")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Остановка по запросу пользователя")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        client.disconnect()
        print("👋 Отключение завершено")

if __name__ == "__main__":
    main()
