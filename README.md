# Meilisearch MCP Server

A Model Context Protocol (MCP) server for interacting with Meilisearch through LLM interfaces like Claude.

## Features

- Index and document management 
- Settings configuration with templates for common use cases (e-commerce, content search, SaaS)
- Task monitoring and API key management
- Built-in logging and monitoring tools
- Dynamic connection configuration to switch between Meilisearch instances

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
- Settings Management: configure search settings with templates
- API Key Management: create/update/delete API keys
- Task Monitoring: track and manage asynchronous tasks
- System Monitoring: health checks and metrics

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License

MIT