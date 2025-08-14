#!/usr/bin/env python3

import sys
import os

# Добавляем путь к модулям
sys.path.append('/home/shpil/tg-mesh-bridge/app/src')

from common.db import SessionLocal
from common.models import User

def create_test_user():
    with SessionLocal() as session:
        # Проверяем, существует ли пользователь
        existing_user = session.execute(
            "SELECT tg_user_id FROM users WHERE tg_code = 'ABCD1234'"
        ).scalar_one_or_none()
        
        if existing_user:
            print(f"Пользователь с кодом ABCD1234 уже существует: {existing_user}")
            return
        
        # Создаем нового пользователя
        user = User(
            tg_user_id=123456789,
            tg_chat_id=123456789,
            language='en',
            tg_code='ABCD1234'
        )
        
        session.add(user)
        session.commit()
        print("Тестовый пользователь создан успешно!")
        print(f"TG User ID: {user.tg_user_id}")
        print(f"TG Code: {user.tg_code}")

if __name__ == "__main__":
    create_test_user()

