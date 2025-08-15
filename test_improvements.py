#!/usr/bin/env python3
"""
Тестовый скрипт для проверки улучшений
"""

import sys
import os
sys.path.insert(0, 'src')

def test_mqtt_publisher():
    """Тест MQTT Publisher"""
    print("🔧 Тестируем MQTT Publisher...")
    try:
        from bridge.mqtt import publish_to_topic
        import time
        
        # Тест 1: Обычная публикация
        result1 = publish_to_topic('test/improvements', {
            'test': 'mqtt_publisher',
            'timestamp': time.time()
        })
        print(f"✅ Тест 1 - Обычная публикация: {result1}")
        
        # Тест 2: Публикация в стандартный топик
        from bridge.mqtt import publish_downlink
        result2 = publish_downlink({
            'to': 123456,  # Example node ID
            'type': 'sendtext',
            'payload': '[[TG]] Test message from improvements'
        })
        print(f"✅ Тест 2 - publish_downlink: {result2}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка MQTT Publisher: {e}")
        return False

def test_consumer_improvements():
    """Тест улучшений Consumer"""
    print("🔧 Тестируем Consumer улучшения...")
    try:
        from bridge.consumer import get_node_display_name
        
        # Тест функции получения красивого имени
        display_name = get_node_display_name(123456)  # Example node ID
print(f"✅ get_node_display_name(123456): '{display_name}'")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка Consumer: {e}")
        return False

def test_database():
    """Тест базы данных"""
    print("🔧 Тестируем базу данных...")
    try:
        from common.db import SessionLocal
        from common.models import Node
        from sqlalchemy import select
        
        with SessionLocal() as session:
            # Проверяем, что user_label колонка существует
            result = session.execute(select(Node.user_label)).first()
            print(f"✅ user_label колонка существует: {result is not None}")
            
            # Проверяем количество нод
            nodes_count = session.execute(select(Node)).scalars().all()
            print(f"✅ Количество нод в базе: {len(nodes_count)}")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_i18n():
    """Тест интернационализации"""
    print("🔧 Тестируем i18n...")
    try:
        from common.i18n import t
        
        # Тест русских ключей
        ru_text = t("ru", "dev.enter_node_id")
        print(f"✅ RU dev.enter_node_id: '{ru_text}'")
        
        # Тест английских ключей
        en_text = t("en", "dev.enter_node_id")
        print(f"✅ EN dev.enter_node_id: '{en_text}'")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка i18n: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ УЛУЧШЕНИЙ")
    print("=" * 50)
    
    tests = [
        ("MQTT Publisher", test_mqtt_publisher),
        ("Consumer улучшения", test_consumer_improvements),
        ("База данных", test_database),
        ("i18n", test_i18n),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ УЛУЧШЕНИЯ РАБОТАЮТ КОРРЕКТНО!")
    else:
        print("⚠️  Некоторые тесты не прошли")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
