"""
Utility for building optimized queries to notebook.

Principles:
- Using navigation map for precise positioning
- Query templates for standardization
- Token minimization through specific section references
"""

from typing import List, Optional, Dict
from notebook_template import NavigationMap, QueryTemplate, NotebookTemplate


class QueryBuilder:
    """
    Query builder for efficient navigation.
    
    Advantages:
    1. Automatic identification of relevant sections
    2. Using templates for standardization
    3. Query formulation optimization for token savings
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
        Builds query with specific section reference.
        
        Format: "In section [section] find [question]"
        
        Why this is efficient:
        - NotebookLM immediately knows where to look
        - No need to scan entire notebook
        - Token savings through precision
        """
        if section_hint:
            # Use explicit section hint
            section = self.navigation.section_index.get(section_hint)
            if section:
                return f"In section '{section.title}' find: {question}"
        
        # Automatically determine section by keywords
        optimized = self.template.generate_optimized_query(question, use_section_hint=True)
        return optimized
    
    def build_multi_section_query(
        self,
        question: str,
        section_ids: List[str]
    ) -> str:
        """
        Builds query for multiple sections.
        
        Used when information may be in different places.
        """
        section_titles = [
            self.navigation.section_index[sid].title
            for sid in section_ids
            if sid in self.navigation.section_index
        ]
        
        if not section_titles:
            return question
        
        sections_str = ", ".join([f"'{title}'" for title in section_titles])
        return f"In sections {sections_str} find: {question}"
    
    def build_comparison_query(
        self,
        topic1: str,
        topic2: str,
        section_id: Optional[str] = None
    ) -> str:
        """
        Builds query for comparing two topics.
        
        Optimized to get only relevant parts.
        """
        base_query = f"Compare {topic1} and {topic2}"
        
        if section_id:
            section = self.navigation.section_index.get(section_id)
            if section:
                return f"In section '{section.title}' {base_query}"
        
        return base_query
    
    def build_followup_query(
        self,
        previous_context: str,
        new_question: str
    ) -> str:
        """
        Builds follow-up query considering previous context.
        
        Important for maintaining dialog context without reloading data.
        """
        return f"Considering previous context about {previous_context}, {new_question}"


def create_query_templates() -> List[QueryTemplate]:
    """
    Creates standard query templates.
    
    Templates help:
    - Standardize query format
    - Teach system effective patterns
    - Simplify query generation
    """
    return [
        QueryTemplate(
            name="section_lookup",
            pattern="In section '{section}' find information about {topic}",
            example="In section 'API Reference' find information about authenticate method"
        ),
        QueryTemplate(
            name="comparison",
            pattern="Compare {topic1} and {topic2} in section '{section}'",
            example="Compare GET and POST methods in section 'HTTP Methods'"
        ),
        QueryTemplate(
            name="example_search",
            pattern="Find examples of {topic} usage",
            example="Find examples of OAuth authentication usage"
        ),
        QueryTemplate(
            name="definition",
            pattern="What is {term} in context of {section}?",
            example="What is middleware in context of Express.js?"
        )
    ]


# Usage example
if __name__ == "__main__":
    # TODO: Implement full example after notebook creation
    print("QueryBuilder ready to use")
    print("Template examples:")
    for template in create_query_templates():
        print(f"  - {template.name}: {template.example}")

