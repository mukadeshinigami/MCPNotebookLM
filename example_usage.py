import sys
import os
import json
from notebooklm_mcp.auth import load_cached_tokens
from notebooklm_mcp.api_client import NotebookLMClient

def main():
    try:
        tokens = load_cached_tokens()
        if not tokens:
            print("Error: No cached tokens found. Run notebooklm-mcp-auth first.")
            sys.exit(1)
        
        print(f"Using cached tokens (extracted at: {tokens.extracted_at})")
        
        client = NotebookLMClient(
            cookies=tokens.cookies,
            csrf_token=tokens.csrf_token,
            session_id=tokens.session_id
        )
        
        title = "Antigravity Test Notebook"
        print(f"Creating test notebook: '{title}'...")
        notebook = client.create_notebook(title)
        
        if notebook:
            print(f"Successfully created notebook!")
            print(f"ID: {notebook.id}")
            print(f"Title: {notebook.title}")
            print(f"URL: {notebook.url}")
        else:
            print("Failed to create notebook.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
