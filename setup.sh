#!/bin/bash

# Setup script for NotebookLM MCP

echo "🚀 Starting NotebookLM MCP Setup..."

# 1. Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# 2. Check if notebooklm-mcp is installed
if ! command -v notebooklm-mcp &> /dev/null && [ ! -f ~/.local/bin/notebooklm-mcp ]; then
    echo "❌ Error: notebooklm-mcp not found after installation."
    echo "Make sure ~/.local/bin is in your PATH or use the absolute path in your config."
else
    echo "✅ notebooklm-mcp is ready."
fi

# 3. Authentication
echo "🔐 Starting authentication process..."
if command -v notebooklm-mcp-auth &> /dev/null; then
    notebooklm-mcp-auth
elif [ -f ~/.local/bin/notebooklm-mcp-auth ]; then
    ~/.local/bin/notebooklm-mcp-auth
else
    echo "❌ Could not find notebooklm-mcp-auth."
    exit 1
fi

echo ""
echo "✨ Setup complete!"
echo "Next steps:"
echo "1. Copy the contents of mcp_config.json.example to your MCP client configuration."
echo "2. REPLACE the path in the 'command' field with the absolute path to your notebooklm-mcp binary."
echo "   (Usually: $(which notebooklm-mcp || echo '~/.local/bin/notebooklm-mcp'))"
echo "3. Run 'python3 example_usage.py' to test."
