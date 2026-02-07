"""
Template for creating structured NotebookLM notebooks
with optimized navigation for token savings.

Architecture:
- Hierarchical source structure with metadata
- Navigation map for precise positioning
- Query templates for efficient search
"""

import sys
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from notebooklm_mcp.api_client import NotebookLMClient
from client_factory import get_notebooklm_client


class SourceType(Enum):
    """Source types for better categorization"""
    DOCUMENTATION = "documentation"
    CODE = "code"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    API_DOCS = "api_docs"
    EXAMPLES = "examples"


@dataclass
class SourceMetadata:
    """
    Source metadata for improved indexing and navigation.
    
    Why this is important:
    - NotebookLM uses metadata for better relevance
    - Tags allow precise queries by category
    - Brief description helps AI understand context without reading entire source
    """
    title: str
    category: str
    tags: List[str] = field(default_factory=list)
    description: str = ""
    source_type: SourceType = SourceType.DOCUMENTATION
    priority: int = 5  # 1-10, where 10 is most important
    related_sections: List[str] = field(default_factory=list)


@dataclass
class NavigationNode:
    """
    Navigation map node.
    
    Used to create hierarchical structure
    that helps MCP make precise queries to specific sections.
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
    Query template for precise navigation.
    
    Advantages:
    - Predefined query patterns
    - Specifying specific sections to save tokens
    - Standardization of query format
    """
    name: str
    pattern: str
    target_sections: List[str] = field(default_factory=list)
    example: str = ""


class NavigationMap:
    """
    Notebook navigation map.
    
    Allows:
    1. Quickly find relevant sections by keywords
    2. Build hierarchy for precise queries
    3. Automatically generate navigation queries
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
        Adds a section to the navigation map.
        
        Args:
            section_id: Unique section identifier
            title: Section title
            description: Content description
            keywords: Search keywords
            parent_id: Parent section ID (for hierarchy)
            metadata: Source metadata
        
        Returns:
            Created navigation node
        """
        node = NavigationNode(
            section_id=section_id,
            title=title,
            description=description,
            keywords=keywords,
            source_metadata=metadata
        )
        
        # Index by keywords
        for keyword in keywords:
            if keyword.lower() not in self.keyword_index:
                self.keyword_index[keyword.lower()] = []
            self.keyword_index[keyword.lower()].append(section_id)
        
        # Add to hierarchy
        if parent_id:
            parent = self.section_index.get(parent_id)
            if parent:
                parent.children.append(node)
            else:
                # If parent not found, add as root
                self.root_nodes.append(node)
        else:
            self.root_nodes.append(node)
        
        self.section_index[section_id] = node
        return node
    
    def find_sections_by_keyword(self, keyword: str) -> List[NavigationNode]:
        """Finds sections by keyword"""
        keyword_lower = keyword.lower()
        section_ids = self.keyword_index.get(keyword_lower, [])
        return [self.section_index[sid] for sid in section_ids if sid in self.section_index]
    
    def generate_navigation_query(self, topic: str) -> str:
        """
        Generates optimized query for navigation.
        
        Format: "In section [section] find information about [topic]"
        This helps NotebookLM precisely identify the relevant section.
        """
        sections = self.find_sections_by_keyword(topic)
        if not sections:
            return f"Find information about {topic}"
        
        # Use first found section for precision
        section_title = sections[0].title
        return f"In section '{section_title}' find information about {topic}"


class NotebookTemplate:
    """
    Template for creating structured notebooks.
    
    Working principles:
    1. Structures sources with metadata
    2. Creates navigation map
    3. Generates optimized queries
    4. Saves tokens through precise navigation
    """
    
    def __init__(self, client: Optional[NotebookLMClient] = None):
        """
        Initializes notebook template.
        
        Args:
            client: NotebookLM client. If not specified, will be created automatically via ClientFactory
        """
        # If client not provided, create via factory
        if client is None:
            client = get_notebooklm_client()
            if not client:
                raise RuntimeError("Failed to create client. Run notebooklm-mcp-auth")
        
        self.client = client
        self.navigation = NavigationMap()
        self.query_templates: List[QueryTemplate] = []
        self.notebook_id: Optional[str] = None
    
    def create_notebook(self, title: str, description: str = "") -> str:
        """
        Creates a new notebook with specified title.
        
        Returns:
            ID of created notebook
        """
        notebook = self.client.create_notebook(title)
        if not notebook:
            raise RuntimeError("Failed to create notebook")
        
        self.notebook_id = notebook.id
        
        # Add description as first source for context
        if description:
            self._add_index_source(description)
        
        return notebook.id
    
    def _add_index_source(self, content: str):
        """Adds index source with structure description"""
        if not self.notebook_id:
            return None
        
        try:
            result = self.client.add_text_source(
                notebook_id=self.notebook_id,
                text=content,
                title="Notebook structure description"
            )
            return result
        except Exception as e:
            print(f"Warning: Failed to add index source: {e}")
            return None
    
    def add_source_with_metadata(
        self,
        metadata: SourceMetadata,
        source_url: Optional[str] = None,
        source_text: Optional[str] = None,
        section_id: Optional[str] = None
    ) -> str:
        """
        Adds source with metadata for improved indexing.
        
        Args:
            source_url: Source URL (website or Google Drive)
            source_text: Text to insert
            metadata: Source metadata
            section_id: Section ID for navigation
        
        Returns:
            ID of added source
        """
        if not self.notebook_id:
            raise RuntimeError("Create notebook first")
        
        # Format metadata prefix for better indexing
        metadata_prefix = self._format_metadata_prefix(metadata)
        
        source_id = None
        
        # Add source
        if source_text:
            # For text sources, add metadata at the beginning
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
                print(f"Error adding text source: {e}")
                raise
        
        elif source_url:
            # For URL sources, metadata only in navigation
            try:
                result = self.client.add_url_source(
                    notebook_id=self.notebook_id,
                    url=source_url,
                    title=metadata.title
                )
                if result:
                    source_id = result.get('sourceId') or result.get('id') or f"source_{metadata.title.lower().replace(' ', '_')}"
            except Exception as e:
                print(f"Error adding URL source: {e}")
                raise
        else:
            raise ValueError("Must specify either source_text or source_url")
        
        # Add to navigation
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
        Formats metadata as prefix for source.
        
        This helps NotebookLM better index content.
        """
        lines = [
            f"# {metadata.title}",
            f"**Category:** {metadata.category}",
            f"**Type:** {metadata.source_type.value}",
        ]
        
        if metadata.tags:
            lines.append(f"**Tags:** {', '.join(metadata.tags)}")
        
        if metadata.description:
            lines.append(f"**Description:** {metadata.description}")
        
        if metadata.related_sections:
            lines.append(f"**Related sections:** {', '.join(metadata.related_sections)}")
        
        lines.append("---\n")
        return "\n".join(lines)
    
    def add_query_template(self, template: QueryTemplate):
        """Adds query template for standardization"""
        self.query_templates.append(template)
    
    def generate_optimized_query(
        self,
        question: str,
        use_section_hint: bool = True
    ) -> str:
        """
        Generates optimized query considering navigation.
        
        Args:
            question: User question
            use_section_hint: Use section hints for precision
        
        Returns:
            Optimized query for NotebookLM
        """
        if use_section_hint:
            # Try to find relevant section
            query = self.navigation.generate_navigation_query(question)
            return query
        
        return question
    
    def get_navigation_summary(self) -> str:
        """
        Returns text description of notebook structure.
        
        Used for creating index source.
        """
        lines = ["# Notebook navigation map\n"]
        
        def format_node(node: NavigationNode, level: int = 0):
            indent = "  " * level
            lines.append(f"{indent}- **{node.title}** ({node.section_id})")
            if node.description:
                lines.append(f"{indent}  {node.description}")
            if node.keywords:
                lines.append(f"{indent}  Keywords: {', '.join(node.keywords)}")
            lines.append("")
            
            for child in node.children:
                format_node(child, level + 1)
        
        for node in self.navigation.root_nodes:
            format_node(node)
        
        return "\n".join(lines)
