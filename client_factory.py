"""
Фабрика для создания клиентов NotebookLM.

Проблема, которую решает:
- Дублирование кода создания клиента в 4+ местах
- Нет единой точки управления аутентификацией
- Сложно тестировать (нет возможности подменить клиент)

Решение:
- Singleton-паттерн для единого экземпляра клиента
- Ленивая инициализация (создается только при первом запросе)
- Централизованная обработка ошибок аутентификации
"""

from typing import Optional
from notebooklm_mcp.auth import load_cached_tokens
from notebooklm_mcp.api_client import NotebookLMClient


class ClientFactory:
    """
    Фабрика для создания и управления клиентами NotebookLM.
    
    Использует Singleton-паттерн для переиспользования одного клиента
    в рамках сессии приложения.
    
    Почему Singleton здесь уместен:
    - Клиент содержит состояние (cookies, session_id)
    - Переиспользование экономит ресурсы
    - Избегаем множественных проверок токенов
    """
    
    _instance: Optional['ClientFactory'] = None
    _client: Optional[NotebookLMClient] = None
    
    def __new__(cls):
        """Singleton: возвращает один экземпляр фабрики."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self, force_new: bool = False) -> Optional[NotebookLMClient]:
        """
        Получает или создает клиент NotebookLM.
        
        Args:
            force_new: Принудительно создать новый клиент (для тестирования)
        
        Returns:
            NotebookLMClient или None, если токены не найдены
        
        Raises:
            RuntimeError: Если токены не найдены (можно изменить на кастомное исключение)
        """
        # Если клиент уже создан и не требуется новый - возвращаем существующий
        if self._client is not None and not force_new:
            return self._client
        
        # Загружаем токены
        tokens = load_cached_tokens()
        if not tokens:
            return None
        
        # Создаем новый клиент
        self._client = NotebookLMClient(
            cookies=tokens.cookies,
            csrf_token=tokens.csrf_token,
            session_id=tokens.session_id
        )
        
        return self._client
    
    def reset(self):
        """
        Сбрасывает кэшированный клиент.
        
        Полезно для:
        - Тестирования
        - Переподключения после истечения сессии
        - Сброса состояния
        """
        self._client = None
    
    @classmethod
    def create_client(cls) -> Optional[NotebookLMClient]:
        """
        Удобный метод для быстрого создания клиента.
        
        Использование:
            client = ClientFactory.create_client()
            if not client:
                print("Ошибка аутентификации")
                return
        
        Returns:
            NotebookLMClient или None
        """
        factory = cls()
        return factory.get_client()


def get_notebooklm_client() -> Optional[NotebookLMClient]:
    """
    Удобная функция-обертка для получения клиента.
    
    Использование:
        client = get_notebooklm_client()
        if not client:
            print("❌ Ошибка: Токены не найдены. Запустите notebooklm-mcp-auth")
            return
    
    Returns:
        NotebookLMClient или None
    """
    return ClientFactory.create_client()

