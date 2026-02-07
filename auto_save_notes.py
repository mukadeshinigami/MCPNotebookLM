"""
Module for automatically saving NotebookLM responses as notes.

This module provides functionality to automatically save responses
from NotebookLM as text sources (notes) in a notebook with "Note:" prefix.

Usage:
    from auto_save_notes import save_answer_as_note
    
    # Save response
    source_id = save_answer_as_note(
        notebook_id="your-notebook-id",
        question="Your question",
        answer="Response from NotebookLM",
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
    Saves NotebookLM response as a note (text source) in notebook.
    
    Args:
        notebook_id: Notebook ID where to save the note
        question: Question that received the answer
        answer: Response from NotebookLM
        client: Optional NotebookLM client. If not specified, will be created automatically
        note_prefix: Prefix for note title (default from configuration)
    
    Returns:
        ID of created source or None on error
    
    Example:
        >>> source_id = save_answer_as_note(
        ...     notebook_id="abc123",
        ...     question="What is Python?",
        ...     answer="Python is a programming language..."
        ... )
        >>> print(f"Note saved with ID: {source_id}")
    """
    # Get configuration
    config = get_config()
    
    # Create client if not provided
    if client is None:
        client = get_notebooklm_client()
        if not client:
            print("❌ Error: Tokens not found. Run notebooklm-mcp-auth")
            return None
    
    # Use prefix from parameter or configuration
    prefix = note_prefix or config.note_prefix
    
    # Generate note title via configuration
    note_title = config.get_note_title(question)
    # If custom prefix provided, replace it
    if note_prefix:
        note_title = f"{note_prefix} {note_title.split(' ', 1)[1] if ' ' in note_title else note_title}"
    
    # Format full note text
    # Include question for context
    full_note_text = f"""Question: {question}

{answer}"""
    
    try:
        # Add text source
        result = client.add_text_source(
            notebook_id=notebook_id,
            text=full_note_text,
            title=note_title
        )
        
        if result:
            source_id = result.get('sourceId') or result.get('id') or result.get('source', {}).get('id')
            if source_id:
                print(f"✅ Note saved: {note_title}")
                print(f"   Source ID: {source_id}")
                return source_id
            else:
                print(f"⚠️  Note added but ID not received: {note_title}")
                return None
        else:
            print(f"❌ Error: Failed to save note: {note_title}")
            return None
            
    except Exception as e:
        print(f"❌ Error saving note: {e}")
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
    Executes query to notebook and automatically saves response as note.
    
    Args:
        notebook_id: Notebook ID
        question: Question for query
        client: Optional NotebookLM client
        auto_save: Automatically save response as note (default from configuration)
        note_prefix: Prefix for note title (default from configuration)
    
    Returns:
        Tuple (answer, source_id) or (None, None) on error
    
    Example:
        >>> answer, source_id = query_and_save(
        ...     notebook_id="abc123",
        ...     question="What is Python?",
        ...     auto_save=True
        ... )
        >>> print(f"Answer: {answer}")
        >>> print(f"Note ID: {source_id}")
    """
    # Get configuration
    config = get_config()
    
    # Create client if not provided
    if client is None:
        client = get_notebooklm_client()
        if not client:
            print("❌ Error: Tokens not found. Run notebooklm-mcp-auth")
            return None, None
    
    # Use value from parameter or configuration
    should_save = auto_save if auto_save is not None else config.default_auto_save
    
    # Execute query
    try:
        response = client.query(notebook_id, question)
        
        # Extract answer if it's an object with answer field
        if isinstance(response, dict):
            answer = response.get('answer') or response.get('response') or str(response)
        else:
            answer = response
        
        if not answer:
            print("❌ Failed to get response from NotebookLM")
            return None, None
        
        # Automatically save as note if enabled
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
        print(f"❌ Error during query: {e}")
        import traceback
        traceback.print_exc()
        return None, None

