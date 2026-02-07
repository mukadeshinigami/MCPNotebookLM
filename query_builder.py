"""
Утилита для построения оптимизированных запросов к блокноту.

Принципы:
- Использование навигационной карты для точного позиционирования
- Шаблоны запросов для стандартизации
- Минимизация токенов через конкретные указания разделов
"""

from typing import List, Optional, Dict
from notebook_template import NavigationMap, QueryTemplate, NotebookTemplate


class QueryBuilder:
    """
    Построитель запросов для эффективной навигации.
    
    Преимущества:
    1. Автоматическое определение релевантных разделов
    2. Использование шаблонов для стандартизации
    3. Оптимизация формулировок для экономии токенов
    """
    
    def __init__(self, template: NotebookTemplate):
        self.template = template
        self.navigation = template.navigation
    
    def build_section_query(
        self,
        question: str,
        section_hint: Optional[str] = None
    ) -> str:
        """
        Строит запрос с указанием конкретного раздела.
        
        Формат: "В разделе [section] найти [question]"
        
        Почему это эффективно:
        - NotebookLM сразу знает, где искать
        - Не нужно сканировать весь блокнот
        - Экономия токенов за счет точности
        """
        if section_hint:
            # Используем явную подсказку о разделе
            section = self.navigation.section_index.get(section_hint)
            if section:
                return f"В разделе '{section.title}' найти: {question}"
        
        # Автоматически определяем раздел по ключевым словам
        optimized = self.template.generate_optimized_query(question, use_section_hint=True)
        return optimized
    
    def build_multi_section_query(
        self,
        question: str,
        section_ids: List[str]
    ) -> str:
        """
        Строит запрос для нескольких разделов.
        
        Используется когда информация может быть в разных местах.
        """
        section_titles = [
            self.navigation.section_index[sid].title
            for sid in section_ids
            if sid in self.navigation.section_index
        ]
        
        if not section_titles:
            return question
        
        sections_str = ", ".join([f"'{title}'" for title in section_titles])
        return f"В разделах {sections_str} найти: {question}"
    
    def build_comparison_query(
        self,
        topic1: str,
        topic2: str,
        section_id: Optional[str] = None
    ) -> str:
        """
        Строит запрос для сравнения двух тем.
        
        Оптимизирован для получения только релевантных частей.
        """
        base_query = f"Сравнить {topic1} и {topic2}"
        
        if section_id:
            section = self.navigation.section_index.get(section_id)
            if section:
                return f"В разделе '{section.title}' {base_query}"
        
        return base_query
    
    def build_followup_query(
        self,
        previous_context: str,
        new_question: str
    ) -> str:
        """
        Строит уточняющий запрос с учетом предыдущего контекста.
        
        Важно для поддержания контекста диалога без повторной загрузки данных.
        """
        return f"Учитывая предыдущий контекст о {previous_context}, {new_question}"


def create_query_templates() -> List[QueryTemplate]:
    """
    Создает стандартные шаблоны запросов.
    
    Шаблоны помогают:
    - Стандартизировать формат запросов
    - Обучить систему эффективным паттернам
    - Упростить генерацию запросов
    """
    return [
        QueryTemplate(
            name="section_lookup",
            pattern="В разделе '{section}' найти информацию о {topic}",
            example="В разделе 'API Reference' найти информацию о методе authenticate"
        ),
        QueryTemplate(
            name="comparison",
            pattern="Сравнить {topic1} и {topic2} в разделе '{section}'",
            example="Сравнить GET и POST методы в разделе 'HTTP Methods'"
        ),
        QueryTemplate(
            name="example_search",
            pattern="Найти примеры использования {topic}",
            example="Найти примеры использования OAuth authentication"
        ),
        QueryTemplate(
            name="definition",
            pattern="Что такое {term} в контексте {section}?",
            example="Что такое middleware в контексте Express.js?"
        )
    ]


# Пример использования
if __name__ == "__main__":
    # TODO: Реализовать полный пример после создания блокнота
    print("QueryBuilder готов к использованию")
    print("Примеры шаблонов:")
    for template in create_query_templates():
        print(f"  - {template.name}: {template.example}")

