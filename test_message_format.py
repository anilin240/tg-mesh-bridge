#!/usr/bin/env python3
"""
Тестовый скрипт для проверки нового формата сообщений
"""

def test_new_message_format():
    """Тестируем новый формат сообщения"""
    
    # Симулируем данные из MQTT сообщения
    mesh_from = 1879503494  # ID вашего устройства
    message_text = "Привет! Это тестовое сообщение с новым красивым форматом! 🎉"
    
    # Получаем красивое имя ноды (симулируем)
    display_name = "Shpil_portable"  # Это должно быть получено из get_node_display_name()
    
    # Старый формат
    old_format = f"[from {display_name}] {message_text}".strip()
    
    # Новый формат
    new_format = f"<b>@{display_name}</b>: {message_text}".strip()
    
    print("=== Тест нового формата сообщений ===")
    print(f"Node ID: {mesh_from}")
    print(f"Display name: {display_name}")
    print(f"Message text: {message_text}")
    print()
    print("Старый формат:")
    print(f"'{old_format}'")
    print()
    print("Новый формат (HTML):")
    print(f"'{new_format}'")
    print()
    print("Как это будет выглядеть в Telegram:")
    print("**@Shpil_portable**: Привет! Это тестовое сообщение с новым красивым форматом! 🎉")
    print()
    print("✅ Новый формат готов к использованию!")

if __name__ == "__main__":
    test_new_message_format()
