#!/usr/bin/env python3

import sys
import os

# Добавляем путь к модулям
sys.path.append('/home/shpil/tg-mesh-bridge/app/src')

from common.db import SessionLocal
from common.models import User

def update_user_code():
    """Обновляем код пользователя с реальным Telegram ID"""
    print("Введите ваш реальный Telegram ID (можно узнать у @userinfobot):")
    real_tg_id = input().strip()
    
    if not real_tg_id.isdigit():
        print("Ошибка: ID должен быть числом")
        return
    
    real_tg_id = int(real_tg_id)
    
    with SessionLocal() as session:
        # Находим пользователя с кодом ABCD1234
        user = session.execute(
            "SELECT * FROM users WHERE tg_code = 'ABCD1234'"
        ).fetchone()
        
        if not user:
            print("Пользователь с кодом ABCD1234 не найден")
            return
        
        print(f"Найден пользователь: {user}")
        
        # Обновляем ID пользователя
        session.execute(
            "UPDATE users SET tg_user_id = %s, tg_chat_id = %s WHERE tg_code = 'ABCD1234'",
            (real_tg_id, real_tg_id)
        )
        session.commit()
        
        print(f"Пользователь обновлен: tg_user_id = {real_tg_id}, tg_chat_id = {real_tg_id}")

if __name__ == "__main__":
    update_user_code()

