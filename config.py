"""
Централизованная конфигурация приложения.

Проблема, которую решает:
- Хардкод значений (префиксы, лимиты) в разных местах
- Нет единого места для настроек
- Сложно менять поведение без правки кода

Решение:
- Класс Config с настройками по умолчанию
- Возможность переопределения через переменные окружения
- Типизированные значения для IDE-подсказок
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Config:
    """
    Конфигурация приложения.
    
    Использует dataclass для:
    - Автоматической генерации __init__, __repr__
    - Типизации полей
    - Удобного доступа к настройкам
    """
    
    # Настройки заметок
    note_prefix: str = "Заметка:"
    note_max_title_length: int = 50
    
    # Настройки запросов
    default_auto_save: bool = True
    default_use_optimization: bool = True
    query_timeout: Optional[int] = None  # None = без таймаута
    
    # Настройки вывода
    verbose: bool = True  # Показывать ли информационные сообщения
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Создает конфигурацию из переменных окружения.
        
        Переменные окружения:
        - NOTEBOOKLM_NOTE_PREFIX: префикс для заметок
        - NOTEBOOKLM_AUTO_SAVE: автоматическое сохранение (true/false)
        - NOTEBOOKLM_VERBOSE: подробный вывод (true/false)
        
        Returns:
            Config с настройками из окружения или значениями по умолчанию
        """
        return cls(
            note_prefix=os.getenv("NOTEBOOKLM_NOTE_PREFIX", "Заметка:"),
            note_max_title_length=int(os.getenv("NOTEBOOKLM_NOTE_MAX_TITLE", "50")),
            default_auto_save=os.getenv("NOTEBOOKLM_AUTO_SAVE", "true").lower() == "true",
            default_use_optimization=os.getenv("NOTEBOOKLM_USE_OPTIMIZATION", "true").lower() == "true",
            verbose=os.getenv("NOTEBOOKLM_VERBOSE", "true").lower() == "true",
        )
    
    def get_note_title(self, question: str) -> str:
        """
        Генерирует название заметки из вопроса.
        
        Args:
            question: Вопрос пользователя
        
        Returns:
            Название заметки с префиксом и обрезанным текстом
        """
        question_clean = question.strip()
        
        # Обрезаем до максимальной длины
        if len(question_clean) > self.note_max_title_length:
            question_title = question_clean[:self.note_max_title_length] + "..."
        else:
            question_title = question_clean
        
        return f"{self.note_prefix} {question_title}"


# Глобальный экземпляр конфигурации
# Можно переопределить через config.from_env() или создать свой экземпляр
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Получает глобальную конфигурацию.
    
    При первом вызове создает конфигурацию из переменных окружения.
    Последующие вызовы возвращают кэшированный экземпляр.
    
    Returns:
        Config: Экземпляр конфигурации
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config):
    """
    Устанавливает глобальную конфигурацию.
    
    Полезно для:
    - Тестирования (можно подставить mock-конфигурацию)
    - Программного изменения настроек
    
    Args:
        config: Экземпляр конфигурации
    """
    global _config
    _config = config

