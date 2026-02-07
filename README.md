# NotebookLM MCP Server

This repository provides a Model Context Protocol (MCP) server for [NotebookLM](https://notebooklm.google.com). It allows AI assistants (like Claude, Antigravity, or others supporting MCP) to interact with your NotebookLM notebooks, sources, and conversations.

## Features

- **List Notebooks**: View all your NotebookLM notebooks.
- **Create Notebooks**: Programmatically create new notebooks.
- **Manage Sources**: Add websites, Google Drive documents, or pasted text to your notebooks.
- **Query Notebooks**: Ask questions about your sources using the NotebookLM AI.
- **Conversation History**: Full support for follow-up questions and conversation context.

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
Run the provided setup script to install dependencies and authenticate:
```bash
chmod +x setup.sh
./setup.sh
```
Follow the prompts to authorize the application. This will create a local `auth.json` file in `~/.notebooklm-mcp/`.

### 3. Configure your MCP Client
Add the server to your `mcp_config.json`. **Use the absolute path** to the `notebooklm-mcp` binary (usually in your local bin after installation).

Example configuration:
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

## Usage Example

You can test your setup using the included `example_usage.py`:
```bash
python3 example_usage.py
```

## Security Note

> [!WARNING]
> Your authentication tokens are stored locally in `~/.notebooklm-mcp/auth.json`. **Never share this file** or commit it to a public repository. The `.gitignore` in this repo is already configured to ignore this folder.

## License

MIT
