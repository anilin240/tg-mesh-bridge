from __future__ import annotations

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class UserState(Enum):
    """Состояния пользователя в боте"""
    NORMAL = "normal"
    CHANGING_CODE = "changing_code"
    REGISTERING = "registering"


@dataclass
class UserSession:
    """Сессия пользователя"""
    state: UserState = UserState.NORMAL
    data: Optional[Dict] = None


class StateManager:
    """Менеджер состояний пользователей"""
    
    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
    
    def get_session(self, user_id: int) -> UserSession:
        """Получить сессию пользователя"""
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession()
        return self._sessions[user_id]
    
    def set_state(self, user_id: int, state: UserState, data: Optional[Dict] = None) -> None:
        """Установить состояние пользователя"""
        session = self.get_session(user_id)
        session.state = state
        session.data = data or {}
    
    def clear_state(self, user_id: int) -> None:
        """Очистить состояние пользователя"""
        if user_id in self._sessions:
            self._sessions[user_id] = UserSession()
    
    def is_in_state(self, user_id: int, state: UserState) -> bool:
        """Проверить, находится ли пользователь в определенном состоянии"""
        session = self.get_session(user_id)
        return session.state == state


# Глобальный экземпляр менеджера состояний
state_manager = StateManager()
