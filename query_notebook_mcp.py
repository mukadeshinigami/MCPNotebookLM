"""
Утилита для тестирования запросов к блокноту через API.

Используется для:
1. Тестирования запросов перед использованием в Cursor
2. Отладки проблем с запросами
3. Демонстрации оптимизированных запросов
4. Автоматического сохранения ответов в заметки
"""

import sys
import json
from notebooklm_mcp.api_client import NotebookLMClient
from query_builder import QueryBuilder
from notebook_template import NotebookTemplate
from auto_save_notes import query_and_save, save_answer_as_note
from client_factory import get_notebooklm_client
from config import get_config


def list_notebooks():
    """Выводит список всех блокнотов"""
    client = get_notebooklm_client()
    if not client:
        print("❌ Ошибка: Токены не найдены. Запустите notebooklm-mcp-auth")
        return None
    
    notebooks = client.list_notebooks()
    return notebooks


def query_notebook_direct(
    notebook_id: str, 
    question: str, 
    use_optimization: Optional[bool] = None,
    auto_save: Optional[bool] = None
):
    """
    Прямой запрос к блокноту через API с автоматическим сохранением ответа.
    
    Args:
        notebook_id: ID блокнота
        question: Вопрос для запроса
        use_optimization: Использовать оптимизацию через навигацию (по умолчанию из конфигурации)
        auto_save: Автоматически сохранять ответ как заметку (по умолчанию из конфигурации)
    
    Returns:
        Ответ от NotebookLM (и ID источника, если auto_save=True)
    """
    config = get_config()
    client = get_notebooklm_client()
    
    if not client:
        print("❌ Ошибка: Токены не найдены")
        return None
    
    # Используем значения из параметров или конфигурации
    should_optimize = use_optimization if use_optimization is not None else config.default_use_optimization
    should_save = auto_save if auto_save is not None else config.default_auto_save
    
    # Если используем оптимизацию, пытаемся загрузить структуру
    if should_optimize:
        # TODO: Загрузить структуру блокнота из сохраненного файла
        # Пока просто используем вопрос как есть, но с подсказкой об оптимизации
        if config.verbose:
            print("💡 Совет: Используйте формат 'В разделе [название] найти [тема]' для экономии токенов")
    
    # Используем функцию с автосохранением, если включено
    if should_save:
        answer, source_id = query_and_save(
            notebook_id=notebook_id,
            question=question,
            client=client,
            auto_save=True
        )
        return answer
    else:
        # Выполняем запрос без автосохранения
        try:
            response = client.query(notebook_id, question)
            return response
        except Exception as e:
            print(f"❌ Ошибка при запросе: {e}")
            import traceback
            traceback.print_exc()
            return None


def interactive_query():
    """Интерактивный режим для запросов"""
    print("="*60)
    print("🔍 Интерактивный запрос к блокноту NotebookLM")
    print("="*60)
    
    # Список блокнотов
    print("\n📚 Загрузка списка блокнотов...")
    notebooks = list_notebooks()
    
    if not notebooks:
        print("❌ Не удалось загрузить блокноты")
        return
    
    print(f"\n✅ Найдено блокнотов: {len(notebooks)}")
    print("\nДоступные блокноты:")
    for i, notebook in enumerate(notebooks, 1):
        print(f"  {i}. {notebook.title} (ID: {notebook.id})")
    
    # Выбор блокнота
    try:
        choice = input("\nВыберите номер блокнота (или введите ID): ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(notebooks):
                selected_notebook = notebooks[idx]
            else:
                print("❌ Неверный номер")
                return
        else:
            # Поиск по ID
            selected_notebook = next((n for n in notebooks if n.id == choice), None)
            if not selected_notebook:
                print("❌ Блокнот не найден")
                return
        
        print(f"\n✅ Выбран блокнот: {selected_notebook.title}")
        print(f"   ID: {selected_notebook.id}")
        
        # Запрос
        print("\n" + "-"*60)
        print("💡 Совет: Используйте формат 'В разделе [название] найти [тема]'")
        print("   Пример: 'В разделе 'Основы Python' найти информацию о функциях'")
        print("-"*60)
        
        question = input("\nВведите ваш вопрос: ").strip()
        
        if not question:
            print("❌ Вопрос не может быть пустым")
            return
        
        # Спрашиваем, нужно ли автосохранение
        save_note = input("\n💾 Автоматически сохранить ответ как заметку? (Y/n): ").strip().lower()
        auto_save = save_note != 'n'
        
        print("\n⏳ Выполнение запроса...")
        response = query_notebook_direct(selected_notebook.id, question, auto_save=auto_save)
        
        if response:
            print("\n" + "="*60)
            print("📝 Ответ:")
            print("="*60)
            print(response)
            print("="*60)
            if auto_save:
                print("\n✅ Ответ автоматически сохранен как заметка в блокноте")
        else:
            print("\n❌ Не удалось получить ответ")
            
    except KeyboardInterrupt:
        print("\n\n👋 Выход...")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Главная функция"""
    if len(sys.argv) == 1:
        # Интерактивный режим
        interactive_query()
    elif len(sys.argv) == 3:
        # Режим с аргументами: notebook_id question
        notebook_id = sys.argv[1]
        question = sys.argv[2]
        
        print(f"📋 Блокнот ID: {notebook_id}")
        print(f"❓ Вопрос: {question}\n")
        
        # По умолчанию автосохранение включено
        response = query_notebook_direct(notebook_id, question, auto_save=True)
        
        if response:
            print("\n📝 Ответ:")
            print("-"*60)
            print(response)
            print("-"*60)
            print("\n✅ Ответ автоматически сохранен как заметка в блокноте")
        else:
            print("\n❌ Не удалось получить ответ")
            sys.exit(1)
    elif len(sys.argv) == 4 and sys.argv[3] in ['--no-save', '--no-auto-save']:
        # Режим с отключенным автосохранением
        notebook_id = sys.argv[1]
        question = sys.argv[2]
        
        print(f"📋 Блокнот ID: {notebook_id}")
        print(f"❓ Вопрос: {question}\n")
        
        response = query_notebook_direct(notebook_id, question, auto_save=False)
        
        if response:
            print("\n📝 Ответ:")
            print("-"*60)
            print(response)
            print("-"*60)
        else:
            print("\n❌ Не удалось получить ответ")
            sys.exit(1)
    else:
        print("Использование:")
        print("  python3 query_notebook_mcp.py                    # Интерактивный режим")
        print("  python3 query_notebook_mcp.py <notebook_id> <question>")
        print("  python3 query_notebook_mcp.py <notebook_id> <question> --no-save  # Без автосохранения")
        sys.exit(1)


if __name__ == "__main__":
    main()

