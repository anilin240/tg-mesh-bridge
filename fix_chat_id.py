#!/usr/bin/env python3

import sys
import os

# Добавляем путь к модулям
sys.path.append('/home/shpil/tg-mesh-bridge/app/src')

from common.db import SessionLocal

def fix_chat_id():
    """Исправляем chat_id для пользователя SHPIL"""
    print("Введите ваш chat_id (ID чата с ботом):")
    print("Чтобы получить chat_id, отправьте любое сообщение боту и посмотрите в логах")
    chat_id = input().strip()
    
    if not chat_id.isdigit():
        print("Ошибка: chat_id должен быть числом")
        return
    
    chat_id = int(chat_id)
    
    with SessionLocal() as session:
        # Обновляем chat_id для пользователя SHPIL
        result = session.execute(
            "UPDATE users SET tg_chat_id = %s WHERE tg_code = 'SHPIL'",
            (chat_id,)
        )
        session.commit()
        
        if result.rowcount > 0:
            print(f"Chat ID обновлен: {chat_id}")
            
            # Проверяем результат
            user = session.execute(
                "SELECT tg_user_id, tg_chat_id, tg_code FROM users WHERE tg_code = 'SHPIL'"
            ).fetchone()
            
            print(f"Пользователь: {user}")
        else:
            print("Пользователь с кодом SHPIL не найден")

if __name__ == "__main__":
    fix_chat_id()

