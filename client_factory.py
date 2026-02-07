"""
Factory for creating NotebookLM clients.

Problem it solves:
- Duplication of client creation code in 4+ places
- No single point of authentication management
- Hard to test (no way to mock the client)

Solution:
- Singleton pattern for a single client instance
- Lazy initialization (created only on first request)
- Centralized authentication error handling
"""

from typing import Optional
from notebooklm_mcp.auth import load_cached_tokens
from notebooklm_mcp.api_client import NotebookLMClient


class ClientFactory:
    """
    Factory for creating and managing NotebookLM clients.
    
    Uses Singleton pattern to reuse a single client
    within the application session.
    
    Why Singleton is appropriate here:
    - Client contains state (cookies, session_id)
    - Reuse saves resources
    - Avoid multiple token checks
    """
    
    _instance: Optional['ClientFactory'] = None
    _client: Optional[NotebookLMClient] = None
    
    def __new__(cls):
        """Singleton: returns a single factory instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self, force_new: bool = False) -> Optional[NotebookLMClient]:
        """
        Gets or creates a NotebookLM client.
        
        Args:
            force_new: Force creation of a new client (for testing)
        
        Returns:
            NotebookLMClient or None if tokens not found
        
        Raises:
            RuntimeError: If tokens not found (can be changed to custom exception)
        """
        # If client already created and new one not required - return existing
        if self._client is not None and not force_new:
            return self._client
        
        # Load tokens
        tokens = load_cached_tokens()
        if not tokens:
            return None
        
        # Create new client
        self._client = NotebookLMClient(
            cookies=tokens.cookies,
            csrf_token=tokens.csrf_token,
            session_id=tokens.session_id
        )
        
        return self._client
    
    def reset(self):
        """
        Resets the cached client.
        
        Useful for:
        - Testing
        - Reconnecting after session expiration
        - Resetting state
        """
        self._client = None
    
    @classmethod
    def create_client(cls) -> Optional[NotebookLMClient]:
        """
        Convenient method for quick client creation.
        
        Usage:
            client = ClientFactory.create_client()
            if not client:
                print("Authentication error")
                return
        
        Returns:
            NotebookLMClient or None
        """
        factory = cls()
        return factory.get_client()


def get_notebooklm_client() -> Optional[NotebookLMClient]:
    """
    Convenient wrapper function for getting a client.
    
    Usage:
        client = get_notebooklm_client()
        if not client:
            print("❌ Error: Tokens not found. Run notebooklm-mcp-auth")
            return
    
    Returns:
        NotebookLMClient or None
    """
    return ClientFactory.create_client()

