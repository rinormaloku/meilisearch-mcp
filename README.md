# Meilisearch MCP Server

A Model Context Protocol (MCP) server for interacting with Meilisearch through LLM interfaces like Claude.

## Features

- Index and document management 
- Settings configuration and management
- Task monitoring and API key management
- Built-in logging and monitoring tools
- Dynamic connection configuration to switch between Meilisearch instances
- Smart search across single or multiple indices

## Installation

```bash
# Clone repository
git clone <repository_url>
cd meilisearch-mcp

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Requirements

- Python ≥ 3.9
- Running Meilisearch instance
- Node.js (for testing with MCP Inspector)

## Usage

### Environment Variables

```bash
MEILI_HTTP_ADDR=http://localhost:7700  # Default Meilisearch URL
MEILI_MASTER_KEY=your_master_key       # Optional: Default Meilisearch API key
```

### Dynamic Connection Configuration

The server provides tools to view and update connection settings at runtime:

- `get-connection-settings`: View current connection URL and API key status
- `update-connection-settings`: Update URL and/or API key to connect to a different Meilisearch instance

Example usage through MCP:
```json
// Get current settings
{
  "name": "get-connection-settings"
}

// Update connection settings
{
  "name": "update-connection-settings",
  "arguments": {
    "url": "http://new-host:7700",
    "api_key": "new-api-key"
  }
}
```

### Search Functionality

The server provides a flexible search tool that can search across one or all indices:

- `search`: Search through Meilisearch indices with optional parameters

Example usage through MCP:
```json
// Search in a specific index
{
  "name": "search",
  "arguments": {
    "query": "search term",
    "indexUid": "movies",
    "limit": 10
  }
}

// Search across all indices
{
  "name": "search",
  "arguments": {
    "query": "search term",
    "limit": 5,
    "sort": ["releaseDate:desc"]
  }
}
```

Available search parameters:
- `query`: The search query (required)
- `indexUid`: Specific index to search in (optional)
- `limit`: Maximum number of results per index (optional, default: 20)
- `offset`: Number of results to skip (optional, default: 0)
- `filter`: Filter expression (optional)
- `sort`: Sorting rules (optional)

### Running the Server

```bash
python -m src.meilisearch_mcp
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m src.meilisearch_mcp
```

## Available Tools

- Index Management: create/update/delete indexes
- Document Operations: add/update/delete documents
- Settings Management: configure search settings
- API Key Management: create/update/delete API keys
- Task Monitoring: track and manage asynchronous tasks
- System Monitoring: health checks and metrics
- Search: flexible search across single or multiple indices

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License

MIT