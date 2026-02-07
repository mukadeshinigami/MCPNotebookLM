"""
Utility for testing notebook queries via API.

Used for:
1. Testing queries before using in Cursor
2. Debugging query issues
3. Demonstrating optimized queries
4. Automatically saving responses as notes
"""

import sys
import json
from typing import Optional
from notebooklm_mcp.api_client import NotebookLMClient
from query_builder import QueryBuilder
from notebook_template import NotebookTemplate
from auto_save_notes import query_and_save, save_answer_as_note
from client_factory import get_notebooklm_client
from config import get_config


def list_notebooks():
    """Lists all notebooks"""
    client = get_notebooklm_client()
    if not client:
        print("❌ Error: Tokens not found. Run notebooklm-mcp-auth")
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
    Direct query to notebook via API with automatic response saving.
    
    Args:
        notebook_id: Notebook ID
        question: Question for query
        use_optimization: Use optimization via navigation (default from configuration)
        auto_save: Automatically save response as note (default from configuration)
    
    Returns:
        Response from NotebookLM (and source ID if auto_save=True)
    """
    config = get_config()
    client = get_notebooklm_client()
    
    if not client:
        print("❌ Error: Tokens not found")
        return None
    
    # Use values from parameters or configuration
    should_optimize = use_optimization if use_optimization is not None else config.default_use_optimization
    should_save = auto_save if auto_save is not None else config.default_auto_save
    
    # If using optimization, try to load structure
    if should_optimize:
        # TODO: Load notebook structure from saved file
        # For now just use question as is, but with optimization hint
        if config.verbose:
            print("💡 Tip: Use format 'In section [name] find [topic]' to save tokens")
    
    # Use function with auto-save if enabled
    if should_save:
        answer, source_id = query_and_save(
            notebook_id=notebook_id,
            question=question,
            client=client,
            auto_save=True
        )
        return answer
    else:
        # Execute query without auto-save
        try:
            response = client.query(notebook_id, question)
            return response
        except Exception as e:
            print(f"❌ Error during query: {e}")
            import traceback
            traceback.print_exc()
            return None


def interactive_query():
    """Interactive mode for queries"""
    print("="*60)
    print("🔍 Interactive NotebookLM notebook query")
    print("="*60)
    
    # List notebooks
    print("\n📚 Loading notebook list...")
    notebooks = list_notebooks()
    
    if not notebooks:
        print("❌ Failed to load notebooks")
        return
    
    print(f"\n✅ Found notebooks: {len(notebooks)}")
    print("\nAvailable notebooks:")
    for i, notebook in enumerate(notebooks, 1):
        print(f"  {i}. {notebook.title} (ID: {notebook.id})")
    
    # Select notebook
    try:
        choice = input("\nSelect notebook number (or enter ID): ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(notebooks):
                selected_notebook = notebooks[idx]
            else:
                print("❌ Invalid number")
                return
        else:
            # Search by ID
            selected_notebook = next((n for n in notebooks if n.id == choice), None)
            if not selected_notebook:
                print("❌ Notebook not found")
                return
        
        print(f"\n✅ Selected notebook: {selected_notebook.title}")
        print(f"   ID: {selected_notebook.id}")
        
        # Query
        print("\n" + "-"*60)
        print("💡 Tip: Use format 'In section [name] find [topic]'")
        print("   Example: 'In section 'Python Basics' find information about functions'")
        print("-"*60)
        
        question = input("\nEnter your question: ").strip()
        
        if not question:
            print("❌ Question cannot be empty")
            return
        
        # Ask about auto-save
        save_note = input("\n💾 Automatically save response as note? (Y/n): ").strip().lower()
        auto_save = save_note != 'n'
        
        print("\n⏳ Executing query...")
        response = query_notebook_direct(selected_notebook.id, question, auto_save=auto_save)
        
        if response:
            print("\n" + "="*60)
            print("📝 Answer:")
            print("="*60)
            print(response)
            print("="*60)
            if auto_save:
                print("\n✅ Response automatically saved as note in notebook")
        else:
            print("\n❌ Failed to get response")
            
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_query()
    elif len(sys.argv) == 3:
        # Mode with arguments: notebook_id question
        notebook_id = sys.argv[1]
        question = sys.argv[2]
        
        print(f"📋 Notebook ID: {notebook_id}")
        print(f"❓ Question: {question}\n")
        
        # Auto-save enabled by default
        response = query_notebook_direct(notebook_id, question, auto_save=True)
        
        if response:
            print("\n📝 Answer:")
            print("-"*60)
            print(response)
            print("-"*60)
            print("\n✅ Response automatically saved as note in notebook")
        else:
            print("\n❌ Failed to get response")
            sys.exit(1)
    elif len(sys.argv) == 4 and sys.argv[3] in ['--no-save', '--no-auto-save']:
        # Mode with auto-save disabled
        notebook_id = sys.argv[1]
        question = sys.argv[2]
        
        print(f"📋 Notebook ID: {notebook_id}")
        print(f"❓ Question: {question}\n")
        
        response = query_notebook_direct(notebook_id, question, auto_save=False)
        
        if response:
            print("\n📝 Answer:")
            print("-"*60)
            print(response)
            print("-"*60)
        else:
            print("\n❌ Failed to get response")
            sys.exit(1)
    else:
        print("Usage:")
        print("  python3 query_notebook_mcp.py                    # Interactive mode")
        print("  python3 query_notebook_mcp.py <notebook_id> <question>")
        print("  python3 query_notebook_mcp.py <notebook_id> <question> --no-save  # Without auto-save")
        sys.exit(1)


if __name__ == "__main__":
    main()

