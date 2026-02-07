"""
Модуль для автоматического сохранения ответов NotebookLM в заметки.

Этот модуль предоставляет функцию для автоматического сохранения ответов
от NotebookLM как текстовых источников (заметок) в блокнот с префиксом "Заметка:".

Использование:
    from auto_save_notes import save_answer_as_note
    
    # Сохранение ответа
    source_id = save_answer_as_note(
        notebook_id="your-notebook-id",
        question="Ваш вопрос",
        answer="Ответ от NotebookLM",
        client=notebooklm_client
    )
"""

from typing import Optional, Tuple
from notebooklm_mcp.api_client import NotebookLMClient
from client_factory import get_notebooklm_client
from config import get_config


def save_answer_as_note(
    notebook_id: str,
    question: str,
    answer: str,
    client: Optional[NotebookLMClient] = None,
    note_prefix: Optional[str] = None
) -> Optional[str]:
    """
    Сохраняет ответ от NotebookLM как заметку (текстовый источник) в блокнот.
    
    Args:
        notebook_id: ID блокнота, в который нужно сохранить заметку
        question: Вопрос, на который был получен ответ
        answer: Ответ от NotebookLM
        client: Опциональный клиент NotebookLM. Если не указан, будет создан автоматически
        note_prefix: Префикс для названия заметки (по умолчанию из конфигурации)
    
    Returns:
        ID созданного источника или None в случае ошибки
    
    Example:
        >>> source_id = save_answer_as_note(
        ...     notebook_id="abc123",
        ...     question="Что такое Python?",
        ...     answer="Python - это язык программирования..."
        ... )
        >>> print(f"Заметка сохранена с ID: {source_id}")
    """
    # Получаем конфигурацию
    config = get_config()
    
    # Создаем клиент, если не передан
    if client is None:
        client = get_notebooklm_client()
        if not client:
            print("❌ Ошибка: Токены не найдены. Запустите notebooklm-mcp-auth")
            return None
    
    # Используем префикс из параметра или конфигурации
    prefix = note_prefix or config.note_prefix
    
    # Формируем название заметки через конфигурацию
    note_title = config.get_note_title(question)
    # Если передан кастомный префикс, заменяем его
    if note_prefix:
        note_title = f"{note_prefix} {note_title.split(' ', 1)[1] if ' ' in note_title else note_title}"
    
    # Формируем полный текст заметки
    # Включаем вопрос для контекста
    full_note_text = f"""Вопрос: {question}

{answer}"""
    
    try:
        # Добавляем текстовый источник
        result = client.add_text_source(
            notebook_id=notebook_id,
            text=full_note_text,
            title=note_title
        )
        
        if result:
            source_id = result.get('sourceId') or result.get('id') or result.get('source', {}).get('id')
            if source_id:
                print(f"✅ Заметка сохранена: {note_title}")
                print(f"   ID источника: {source_id}")
                return source_id
            else:
                print(f"⚠️  Заметка добавлена, но ID не получен: {note_title}")
                return None
        else:
            print(f"❌ Ошибка: Не удалось сохранить заметку: {note_title}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при сохранении заметки: {e}")
        import traceback
        traceback.print_exc()
        return None


def query_and_save(
    notebook_id: str,
    question: str,
    client: Optional[NotebookLMClient] = None,
    auto_save: Optional[bool] = None,
    note_prefix: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Выполняет запрос к блокноту и автоматически сохраняет ответ как заметку.
    
    Args:
        notebook_id: ID блокнота
        question: Вопрос для запроса
        client: Опциональный клиент NotebookLM
        auto_save: Автоматически сохранять ответ как заметку (по умолчанию из конфигурации)
        note_prefix: Префикс для названия заметки (по умолчанию из конфигурации)
    
    Returns:
        Кортеж (ответ, ID_источника) или (None, None) в случае ошибки
    
    Example:
        >>> answer, source_id = query_and_save(
        ...     notebook_id="abc123",
        ...     question="Что такое Python?",
        ...     auto_save=True
        ... )
        >>> print(f"Ответ: {answer}")
        >>> print(f"Заметка ID: {source_id}")
    """
    # Получаем конфигурацию
    config = get_config()
    
    # Создаем клиент, если не передан
    if client is None:
        client = get_notebooklm_client()
        if not client:
            print("❌ Ошибка: Токены не найдены. Запустите notebooklm-mcp-auth")
            return None, None
    
    # Используем значение из параметра или конфигурации
    should_save = auto_save if auto_save is not None else config.default_auto_save
    
    # Выполняем запрос
    try:
        response = client.query(notebook_id, question)
        
        # Извлекаем ответ, если это объект с полем answer
        if isinstance(response, dict):
            answer = response.get('answer') or response.get('response') or str(response)
        else:
            answer = response
        
        if not answer:
            print("❌ Не удалось получить ответ от NotebookLM")
            return None, None
        
        # Автоматически сохраняем как заметку, если включено
        source_id = None
        if should_save:
            source_id = save_answer_as_note(
                notebook_id=notebook_id,
                question=question,
                answer=answer,
                client=client,
                note_prefix=note_prefix
            )
        
        return answer, source_id
        
    except Exception as e:
        print(f"❌ Ошибка при запросе: {e}")
        import traceback
        traceback.print_exc()
        return None, None

