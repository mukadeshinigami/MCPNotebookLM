"""
Centralized application configuration.

Problem it solves:
- Hardcoded values (prefixes, limits) in different places
- No single place for settings
- Hard to change behavior without code changes

Solution:
- Config class with default settings
- Ability to override via environment variables
- Typed values for IDE hints
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Config:
    """
    Application configuration.
    
    Uses dataclass for:
    - Automatic generation of __init__, __repr__
    - Field typing
    - Convenient access to settings
    """
    
    # Note settings
    note_prefix: str = "Note:"
    note_max_title_length: int = 50
    
    # Query settings
    default_auto_save: bool = True
    default_use_optimization: bool = True
    query_timeout: Optional[int] = None  # None = no timeout
    
    # Output settings
    verbose: bool = True  # Show informational messages
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Creates configuration from environment variables.
        
        Environment variables:
        - NOTEBOOKLM_NOTE_PREFIX: prefix for notes
        - NOTEBOOKLM_AUTO_SAVE: automatic saving (true/false)
        - NOTEBOOKLM_VERBOSE: verbose output (true/false)
        
        Returns:
            Config with settings from environment or default values
        """
        return cls(
            note_prefix=os.getenv("NOTEBOOKLM_NOTE_PREFIX", "Note:"),
            note_max_title_length=int(os.getenv("NOTEBOOKLM_NOTE_MAX_TITLE", "50")),
            default_auto_save=os.getenv("NOTEBOOKLM_AUTO_SAVE", "true").lower() == "true",
            default_use_optimization=os.getenv("NOTEBOOKLM_USE_OPTIMIZATION", "true").lower() == "true",
            verbose=os.getenv("NOTEBOOKLM_VERBOSE", "true").lower() == "true",
        )
    
    def get_note_title(self, question: str) -> str:
        """
        Generates note title from question.
        
        Args:
            question: User question
        
        Returns:
            Note title with prefix and truncated text
        """
        question_clean = question.strip()
        
        # Truncate to max length
        if len(question_clean) > self.note_max_title_length:
            question_title = question_clean[:self.note_max_title_length] + "..."
        else:
            question_title = question_clean
        
        return f"{self.note_prefix} {question_title}"


# Global configuration instance
# Can be overridden via config.from_env() or create your own instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Gets global configuration.
    
    On first call creates configuration from environment variables.
    Subsequent calls return cached instance.
    
    Returns:
        Config: Configuration instance
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config):
    """
    Sets global configuration.
    
    Useful for:
    - Testing (can substitute mock configuration)
    - Programmatic setting changes
    
    Args:
        config: Configuration instance
    """
    global _config
    _config = config

