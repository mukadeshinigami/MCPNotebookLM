"""
Шаблон для создания структурированных блокнотов NotebookLM
с оптимизированной навигацией для экономии токенов.

Архитектура:
- Иерархическая структура источников с метаданными
- Навигационная карта для точного позиционирования
- Шаблоны запросов для эффективного поиска
"""

import sys
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from notebooklm_mcp.api_client import NotebookLMClient
from client_factory import get_notebooklm_client


class SourceType(Enum):
    """Типы источников для лучшей категоризации"""
    DOCUMENTATION = "documentation"
    CODE = "code"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    API_DOCS = "api_docs"
    EXAMPLES = "examples"


@dataclass
class SourceMetadata:
    """
    Метаданные источника для улучшения индексации и навигации.
    
    Почему это важно:
    - NotebookLM использует метаданные для лучшей релевантности
    - Теги позволяют делать точные запросы по категориям
    - Краткое описание помогает AI понять контекст без чтения всего источника
    """
    title: str
    category: str
    tags: List[str] = field(default_factory=list)
    description: str = ""
    source_type: SourceType = SourceType.DOCUMENTATION
    priority: int = 5  # 1-10, где 10 - самый важный
    related_sections: List[str] = field(default_factory=list)


@dataclass
class NavigationNode:
    """
    Узел навигационной карты. 
    
    Используется для создания иерархической структуры,
    которая помогает MCP делать точные запросы к конкретным разделам.
    """
    section_id: str
    title: str
    description: str
    keywords: List[str] = field(default_factory=list)
    children: List['NavigationNode'] = field(default_factory=list)
    source_metadata: Optional[SourceMetadata] = None


@dataclass
class QueryTemplate:
    """
    Шаблон запроса для точной навигации.
    
    Преимущества:
    - Предопределенные паттерны запросов
    - Указание конкретных разделов для экономии токенов
    - Стандартизация формата запросов
    """
    name: str
    pattern: str
    target_sections: List[str] = field(default_factory=list)
    example: str = ""


class NavigationMap:
    """
    Карта навигации блокнота.
    
    Позволяет:
    1. Быстро находить релевантные разделы по ключевым словам
    2. Строить иерархию для точных запросов
    3. Генерировать навигационные запросы автоматически
    """
    
    def __init__(self):
        self.root_nodes: List[NavigationNode] = []
        self.section_index: Dict[str, NavigationNode] = {}
        self.keyword_index: Dict[str, List[str]] = {}  # keyword -> [section_ids]
    
    def add_section(
        self,
        section_id: str,
        title: str,
        description: str,
        keywords: List[str],
        parent_id: Optional[str] = None,
        metadata: Optional[SourceMetadata] = None
    ) -> NavigationNode:
        """
        Добавляет раздел в навигационную карту.
        
        Args:
            section_id: Уникальный идентификатор раздела
            title: Название раздела
            description: Описание содержимого
            keywords: Ключевые слова для поиска
            parent_id: ID родительского раздела (для иерархии)
            metadata: Метаданные источника
        
        Returns:
            Созданный узел навигации
        """
        node = NavigationNode(
            section_id=section_id,
            title=title,
            description=description,
            keywords=keywords,
            source_metadata=metadata
        )
        
        # Индексируем по ключевым словам
        for keyword in keywords:
            if keyword.lower() not in self.keyword_index:
                self.keyword_index[keyword.lower()] = []
            self.keyword_index[keyword.lower()].append(section_id)
        
        # Добавляем в иерархию
        if parent_id:
            parent = self.section_index.get(parent_id)
            if parent:
                parent.children.append(node)
            else:
                # Если родитель не найден, добавляем как корневой
                self.root_nodes.append(node)
        else:
            self.root_nodes.append(node)
        
        self.section_index[section_id] = node
        return node
    
    def find_sections_by_keyword(self, keyword: str) -> List[NavigationNode]:
        """Находит разделы по ключевому слову"""
        keyword_lower = keyword.lower()
        section_ids = self.keyword_index.get(keyword_lower, [])
        return [self.section_index[sid] for sid in section_ids if sid in self.section_index]
    
    def generate_navigation_query(self, topic: str) -> str:
        """
        Генерирует оптимизированный запрос для навигации.
        
        Формат: "В разделе [section] найти информацию о [topic]"
        Это помогает NotebookLM точно определить релевантную секцию.
        """
        sections = self.find_sections_by_keyword(topic)
        if not sections:
            return f"Найти информацию о {topic}"
        
        # Используем первый найденный раздел для точности
        section_title = sections[0].title
        return f"В разделе '{section_title}' найти информацию о {topic}"


class NotebookTemplate:
    """
    Шаблон для создания структурированного блокнота.
    
    Принципы работы:
    1. Структурирует источники с метаданными
    2. Создает навигационную карту
    3. Генерирует оптимизированные запросы
    4. Экономит токены через точную навигацию
    """
    
    def __init__(self, client: Optional[NotebookLMClient] = None):
        """
        Инициализирует шаблон блокнота.
        
        Args:
            client: Клиент NotebookLM. Если не указан, будет создан автоматически через ClientFactory
        """
        # Если клиент не передан, создаем через фабрику
        if client is None:
            client = get_notebooklm_client()
            if not client:
                raise RuntimeError("Не удалось создать клиент. Запустите notebooklm-mcp-auth")
        
        self.client = client
        self.navigation = NavigationMap()
        self.query_templates: List[QueryTemplate] = []
        self.notebook_id: Optional[str] = None
    
    def create_notebook(self, title: str, description: str = "") -> str:
        """
        Создает новый блокнот с указанным названием.
        
        Returns:
            ID созданного блокнота
        """
        notebook = self.client.create_notebook(title)
        if not notebook:
            raise RuntimeError("Не удалось создать блокнот")
        
        self.notebook_id = notebook.id
        
        # Добавляем описание как первый источник для контекста
        if description:
            self._add_index_source(description)
        
        return notebook.id
    
    def _add_index_source(self, content: str):
        """Добавляет индексный источник с описанием структуры"""
        if not self.notebook_id:
            return None
        
        try:
            result = self.client.add_text_source(
                notebook_id=self.notebook_id,
                text=content,
                title="Описание структуры блокнота"
            )
            return result
        except Exception as e:
            print(f"Предупреждение: Не удалось добавить индексный источник: {e}")
            return None
    
    def add_source_with_metadata(
        self,
        metadata: SourceMetadata,
        source_url: Optional[str] = None,
        source_text: Optional[str] = None,
        section_id: Optional[str] = None
    ) -> str:
        """
        Добавляет источник с метаданными для улучшенной индексации.
        
        Args:
            source_url: URL источника (веб-сайт или Google Drive)
            source_text: Текст для вставки
            metadata: Метаданные источника
            section_id: ID раздела для навигации
        
        Returns:
            ID добавленного источника
        """
        if not self.notebook_id:
            raise RuntimeError("Сначала создайте блокнот")
        
        # Формируем префикс с метаданными для лучшей индексации
        metadata_prefix = self._format_metadata_prefix(metadata)
        
        source_id = None
        
        # Добавляем источник
        if source_text:
            # Для текстовых источников добавляем метаданные в начало
            full_text = metadata_prefix + "\n\n" + source_text
            try:
                result = self.client.add_text_source(
                    notebook_id=self.notebook_id,
                    text=full_text,
                    title=metadata.title
                )
                if result:
                    source_id = result.get('sourceId') or result.get('id') or f"source_{metadata.title.lower().replace(' ', '_')}"
            except Exception as e:
                print(f"Ошибка при добавлении текстового источника: {e}")
                raise
        
        elif source_url:
            # Для URL источников метаданные только в навигации
            try:
                result = self.client.add_url_source(
                    notebook_id=self.notebook_id,
                    url=source_url,
                    title=metadata.title
                )
                if result:
                    source_id = result.get('sourceId') or result.get('id') or f"source_{metadata.title.lower().replace(' ', '_')}"
            except Exception as e:
                print(f"Ошибка при добавлении URL источника: {e}")
                raise
        else:
            raise ValueError("Необходимо указать либо source_text, либо source_url")
        
        # Добавляем в навигацию
        section_id = section_id or metadata.title.lower().replace(" ", "_")
        self.navigation.add_section(
            section_id=section_id,
            title=metadata.title,
            description=metadata.description,
            keywords=metadata.tags + [metadata.category],
            metadata=metadata
        )
        
        return source_id or f"source_{metadata.title.lower().replace(' ', '_')}"
    
    def _format_metadata_prefix(self, metadata: SourceMetadata) -> str:
        """
        Форматирует метаданные как префикс для источника.
        
        Это помогает NotebookLM лучше индексировать контент.
        """
        lines = [
            f"# {metadata.title}",
            f"**Категория:** {metadata.category}",
            f"**Тип:** {metadata.source_type.value}",
        ]
        
        if metadata.tags:
            lines.append(f"**Теги:** {', '.join(metadata.tags)}")
        
        if metadata.description:
            lines.append(f"**Описание:** {metadata.description}")
        
        if metadata.related_sections:
            lines.append(f"**Связанные разделы:** {', '.join(metadata.related_sections)}")
        
        lines.append("---\n")
        return "\n".join(lines)
    
    def add_query_template(self, template: QueryTemplate):
        """Добавляет шаблон запроса для стандартизации"""
        self.query_templates.append(template)
    
    def generate_optimized_query(
        self,
        question: str,
        use_section_hint: bool = True
    ) -> str:
        """
        Генерирует оптимизированный запрос с учетом навигации.
        
        Args:
            question: Вопрос пользователя
            use_section_hint: Использовать подсказки о разделе для точности
        
        Returns:
            Оптимизированный запрос для NotebookLM
        """
        if use_section_hint:
            # Пытаемся найти релевантный раздел
            query = self.navigation.generate_navigation_query(question)
            return query
        
        return question
    
    def get_navigation_summary(self) -> str:
        """
        Возвращает текстовое описание структуры блокнота.
        
        Используется для создания индексного источника.
        """
        lines = ["# Навигационная карта блокнота\n"]
        
        def format_node(node: NavigationNode, level: int = 0):
            indent = "  " * level
            lines.append(f"{indent}- **{node.title}** ({node.section_id})")
            if node.description:
                lines.append(f"{indent}  {node.description}")
            if node.keywords:
                lines.append(f"{indent}  Ключевые слова: {', '.join(node.keywords)}")
            lines.append("")
            
            for child in node.children:
                format_node(child, level + 1)
        
        for node in self.navigation.root_nodes:
            format_node(node)
        
        return "\n".join(lines)
