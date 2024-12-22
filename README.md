# Meilisearch MCP Server

This server allows you to interact with Meilisearch through the Model Context Protocol (MCP), enabling AI assistants like Claude to manage your Meilisearch instance.

## Prerequisites

- Python 3.9 or higher
- A running [Meilisearch](https://www.meilisearch.com/) instance
- [Claude Desktop](https://claude.ai/download) (latest version)

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd meilisearch-mcp-server
```

2. Create and activate a virtual environment:
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:
```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file with your Meilisearch connection details:
```env
MEILI_HOST=http://localhost:7700
MEILI_MASTER_KEY=your-master-key  # If you have authentication enabled
```

2. Configure Claude Desktop to use the server:

   a. Open Claude Desktop
   
   b. Open your Claude Desktop configuration:
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

   c. Add the following configuration:
   ```json
   {
     "mcpServers": {
       "meilisearch": {
         "command": "python",
         "args": [
           "/ABSOLUTE/PATH/TO/meilisearch_server.py"
         ],
         "env": {
           "MEILI_HOST": "http://localhost:7700",
           "MEILI_MASTER_KEY": "your-master-key"  // If authentication is enabled
         }
       }
     }
   }
   ```
   
   **Important**: Replace `/ABSOLUTE/PATH/TO/` with the actual path to your server file.

3. Restart Claude Desktop

## Available Resources

The server provides the following resources for each Meilisearch index:

### Index Statistics
- URI pattern: `meilisearch://index/{index_uid}/stats`
- Contains metadata and performance statistics for the index
- Updates automatically as the index changes

### Index Settings
- URI pattern: `meilisearch://index/{index_uid}/settings`
- Shows current configuration including ranking rules, synonyms, stop words, etc.
- Useful for understanding index behavior

### Task History
- URI pattern: `meilisearch://index/{index_uid}/tasks`
- Displays recent operations performed on the index
- Helps track index modifications and their status

## Available Tools

The server exposes the following tools:

### Index Management
- `list-indexes`: List all indexes in the Meilisearch instance
- `create-index`: Create a new index
- `delete-index`: Delete an existing index

### Document Operations
- `add-documents`: Add documents to an index
- `get-documents`: Get documents from an index
- `delete-documents`: Delete documents from an index

### Settings Management
- `get-settings`: Get settings of an index
- `update-settings`: Update settings of an index

### Task Management
- `get-task`: Get information about a specific task
- `list-tasks`: List all tasks

## Example Usage in Claude Desktop

Once configured, you can use natural language to interact with your Meilisearch instance. Here are some examples:

1. Creating an index:
```
Could you create a new index called "movies" with "id" as the primary key?
```

2. Adding documents:
```
Please add these movies to the index:
[
  {"id": 1, "title": "The Matrix", "year": 1999},
  {"id": 2, "title": "Inception", "year": 2010}
]
```

3. Optimizing settings:
```
Could you optimize the movies index for search-as-you-type behavior?
```

4. Getting documents:
```
Show me the first 5 documents in the movies index
```

## Optimized Settings Templates

The server includes pre-configured settings templates for common use cases:

### search-as-you-type
- Enables typo tolerance with standard thresholds
- Prioritizes word matching and proximity
- Best for instant search interfaces

### exact-search
- Disables typo tolerance
- Prioritizes exact word matches
- Best for technical or precision-critical searches

### fuzzy-search
- Enables aggressive typo tolerance
- Prioritizes typo handling over exact matches
- Best for user-friendly, forgiving search

## Troubleshooting

1. **Claude Desktop doesn't show the tools**
   - Verify your `claude_desktop_config.json` has the correct absolute path
   - Check that your Python environment has all dependencies installed
   - Look at Claude Desktop logs:
     - macOS: `~/Library/Logs/Claude/mcp*.log`
     - Windows: `%APPDATA%\Claude\logs\mcp*.log`

2. **Connection errors to Meilisearch**
   - Verify Meilisearch is running (`curl http://localhost:7700/health`)
   - Check your master key if authentication is enabled
   - Verify the host URL in your environment variables

3. **Permission errors**
   - Make sure the Python script has execute permissions
   - Verify Python has access to the directories it needs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.