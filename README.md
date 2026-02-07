# NotebookLM MCP Server

This repository provides a Model Context Protocol (MCP) server for [NotebookLM](https://notebooklm.google.com). It allows AI assistants (like Claude, Antigravity, or others supporting MCP) to interact with your NotebookLM notebooks, sources, and conversations.

## Features

- **List Notebooks**: View all your NotebookLM notebooks.
- **Create Notebooks**: Programmatically create new notebooks.
- **Manage Sources**: Add websites, Google Drive documents, or pasted text to your notebooks.
- **Query Notebooks**: Ask questions about your sources using the NotebookLM AI.
- **Conversation History**: Full support for follow-up questions and conversation context.
- **Auto-Save Notes**: Automatically save AI responses as notes in your notebooks.

## Prerequisites

- Python 3.10 or higher.
- A Google Account with access to NotebookLM.
- An MCP-compatible client (e.g., Cursor, Claude Desktop).

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/MCPNotebookLM.git
cd MCPNotebookLM
```

### 2. Set up the environment

Install dependencies:
```bash
pip install -r requirements.txt
```

Authenticate with NotebookLM:
```bash
notebooklm-mcp-auth
```
Follow the prompts to authorize the application. This will create a local `auth.json` file in `~/.notebooklm-mcp/`.

### 3. Configure your MCP Client

**For Cursor:**
1. Copy `mcp_config.json.example` to your Cursor config directory:
   - Linux: `~/.config/cursor/mcp.json`
   - macOS: `~/Library/Application Support/Cursor/mcp.json`
   - Windows: `%APPDATA%\Cursor\mcp.json`

2. Edit the `command` field with the absolute path to `notebooklm-mcp`:
   ```json
   {
     "mcpServers": {
       "notebooklm": {
         "command": "/home/YOUR_USER/.local/bin/notebooklm-mcp",
         "args": [],
         "env": {}
       }
     }
   }
   ```

3. Find the binary path:
   ```bash
   which notebooklm-mcp
   # or
   ls ~/.local/bin/notebooklm-mcp
   ```

4. Restart Cursor to apply the configuration.

## Usage Examples

### Basic Usage

Test your setup by listing notebooks:
```bash
python3 query_notebook_mcp.py
```

Or query a notebook directly:
```bash
python3 query_notebook_mcp.py <notebook_id> "Your question"
```

### Auto-Save Notes Feature

The repository includes an automatic note-saving feature that saves all AI responses as notes in your notebooks. This is especially useful when working through MCP API, as responses aren't automatically saved in the web interface history.

**Quick start:**
```python
from auto_save_notes import query_and_save

answer, source_id = query_and_save(
    notebook_id="your-notebook-id",
    question="What is Python?",
    auto_save=True
)
```

See `docs/AUTO_SAVE_NOTES.md` for detailed documentation (if available locally).

## Security Note

> [!WARNING]
> Your authentication tokens are stored locally in `~/.notebooklm-mcp/auth.json`. **Never share this file** or commit it to a public repository. The `.gitignore` in this repo is already configured to ignore this folder.

## License

MIT
