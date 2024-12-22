import asyncio
import os
import meilisearch
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
import mcp.server.stdio
from typing import Optional, List, Dict, Any

class MeilisearchMCPServer:
    def __init__(self, host: str = "http://localhost:7700", api_key: Optional[str] = None):
        # Initialize Meilisearch client
        self.client = meilisearch.Client(host, api_key)
        
        # Initialize MCP server
        self.server = Server("meilisearch-server")
        
        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        # Register resource handlers
        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            # Get all indexes for resource templates
            indexes = self.client.get_indexes()
            resources = []
            
            # Add resource templates for each index
            for index in indexes:
                resources.extend([
                    # Stats resource
                    types.Resource(
                        name=f"Stats for {index.uid}",
                        description=f"Statistics and metadata for the {index.uid} index",
                        uri=f"meilisearch://index/{index.uid}/stats"
                    ),
                    # Settings resource
                    types.Resource(
                        name=f"Settings for {index.uid}",
                        description=f"Current settings configuration for the {index.uid} index",
                        uri=f"meilisearch://index/{index.uid}/settings"
                    ),
                    # Tasks resource
                    types.Resource(
                        name=f"Tasks for {index.uid}",
                        description=f"Recent tasks history for the {index.uid} index",
                        uri=f"meilisearch://index/{index.uid}/tasks"
                    )
                ])
            
            return resources

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> List[types.Content]:
            # Parse URI to extract index and resource type
            try:
                _, _, index_uid, resource_type = uri.split('/')
            except ValueError:
                raise ValueError(f"Invalid resource URI: {uri}")
                
            index = self.client.get_index(index_uid)
            
            if resource_type == "stats":
                # Get index stats
                stats = index.get_stats()
                return [types.TextContent(
                    type="text",
                    text=f"Statistics for index {index_uid}:\n{str(stats)}"
                )]
                
            elif resource_type == "settings":
                # Get index settings
                settings = index.get_settings()
                return [types.TextContent(
                    type="text",
                    text=f"Settings for index {index_uid}:\n{str(settings)}"
                )]
                
            elif resource_type == "tasks":
                # Get index tasks
                tasks = self.client.get_tasks({"indexUids": [index_uid]})
                return [types.TextContent(
                    type="text",
                    text=f"Recent tasks for index {index_uid}:\n{str(tasks)}"
                )]
            
            else:
                raise ValueError(f"Unknown resource type: {resource_type}")

        # Tools for indexes
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            return [
                # Index Tools
                types.Tool(
                    name="list-indexes",
                    description="List all indexes in the Meilisearch instance",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    }
                ),
                types.Tool(
                    name="create-index",
                    description="Create a new index",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "uid": {"type": "string", "description": "Unique identifier for the index"},
                            "primaryKey": {"type": "string", "description": "Primary key field name"}
                        },
                        "required": ["uid"]
                    }
                ),
                types.Tool(
                    name="delete-index",
                    description="Delete an index",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "uid": {"type": "string", "description": "Index to delete"}
                        },
                        "required": ["uid"]
                    }
                ),
                
                # Document Tools
                types.Tool(
                    name="add-documents",
                    description="Add documents to an index",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "indexUid": {"type": "string", "description": "Index to add documents to"},
                            "documents": {"type": "array", "description": "Array of documents to add"},
                            "primaryKey": {"type": "string", "description": "Optional primary key field"}
                        },
                        "required": ["indexUid", "documents"]
                    }
                ),
                types.Tool(
                    name="get-documents",
                    description="Get documents from an index",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "indexUid": {"type": "string", "description": "Index to get documents from"},
                            "offset": {"type": "integer", "description": "Number of documents to skip"},
                            "limit": {"type": "integer", "description": "Max number of documents to return"}
                        },
                        "required": ["indexUid"]
                    }
                ),
                types.Tool(
                    name="delete-documents",
                    description="Delete documents from an index",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "indexUid": {"type": "string", "description": "Index to delete documents from"},
                            "documentIds": {"type": "array", "description": "Array of document IDs to delete"}
                        },
                        "required": ["indexUid", "documentIds"]
                    }
                ),
                
                # Settings Tools
                types.Tool(
                    name="get-settings",
                    description="Get settings of an index",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "indexUid": {"type": "string", "description": "Index to get settings from"}
                        },
                        "required": ["indexUid"]
                    }
                ),
                types.Tool(
                    name="update-settings",
                    description="Update settings of an index",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "indexUid": {"type": "string", "description": "Index to update settings for"},
                            "settings": {"type": "object", "description": "Settings object to update"}
                        },
                        "required": ["indexUid", "settings"]
                    }
                ),
                
                # Task Tools
                types.Tool(
                    name="get-task",
                    description="Get information about a specific task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "taskUid": {"type": "integer", "description": "Task ID to get info about"}
                        },
                        "required": ["taskUid"]
                    }
                ),
                types.Tool(
                    name="list-tasks",
                    description="List all tasks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Max number of tasks to return"},
                            "from": {"type": "integer", "description": "Task ID to start from"}
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            try:
                if name == "list-indexes":
                    indexes = self.client.get_indexes()
                    return [types.TextContent(type="text", text=str(indexes))]
                    
                elif name == "create-index":
                    index = self.client.create_index(
                        arguments["uid"],
                        arguments.get("primaryKey")
                    )
                    return [types.TextContent(type="text", text=f"Created index: {str(index)}")] 
                    
                elif name == "delete-index":
                    task = self.client.delete_index(arguments["uid"])
                    return [types.TextContent(type="text", text=f"Deletion task created: {str(task)}")]
                    
                elif name == "add-documents":
                    index = self.client.get_index(arguments["indexUid"])
                    task = index.add_documents(
                        arguments["documents"], 
                        arguments.get("primaryKey")
                    )
                    return [types.TextContent(type="text", text=f"Documents added. Task ID: {task['taskUid']}")] 
                    
                elif name == "get-documents":
                    index = self.client.get_index(arguments["indexUid"])
                    documents = index.get_documents(
                        offset=arguments.get("offset", 0),
                        limit=arguments.get("limit", 20)
                    )
                    return [types.TextContent(type="text", text=str(documents))]
                    
                elif name == "delete-documents":
                    index = self.client.get_index(arguments["indexUid"])
                    task = index.delete_documents(arguments["documentIds"])
                    return [types.TextContent(type="text", text=f"Document deletion task created: {str(task)}")]
                    
                elif name == "get-settings":
                    index = self.client.get_index(arguments["indexUid"])
                    settings = index.get_settings()
                    return [types.TextContent(type="text", text=str(settings))]
                    
                elif name == "update-settings":
                    index = self.client.get_index(arguments["indexUid"])
                    task = index.update_settings(arguments["settings"])
                    return [types.TextContent(type="text", text=f"Settings update task created: {str(task)}")]
                    
                elif name == "get-task":
                    task = self.client.get_task(arguments["taskUid"])
                    return [types.TextContent(type="text", text=str(task))]
                    
                elif name == "list-tasks":
                    tasks = self.client.get_tasks(
                        arguments.get("limit"),
                        arguments.get("from")
                    )
                    return [types.TextContent(type="text", text=str(tasks))]
                    
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

        # Register prompts
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[types.Prompt]:
            return [
                types.Prompt(
                    name="optimize-settings",
                    description="Configure optimal settings for common use cases",
                    arguments=[
                        types.PromptArgument(
                            name="useCase",
                            description="The use case to optimize for (e.g., 'search-as-you-type', 'exact-search', 'fuzzy-search')",
                            required=True
                        ),
                        types.PromptArgument(
                            name="indexUid",
                            description="Index to apply settings to",
                            required=True
                        )
                    ]
                )
            ]

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
            if name == "optimize-settings":
                if not arguments or "useCase" not in arguments or "indexUid" not in arguments:
                    raise ValueError("Missing required arguments")
                    
                use_case = arguments["useCase"].lower()
                index_uid = arguments["indexUid"]
                
                settings_templates = {
                    "search-as-you-type": {
                        "rankingRules": [
                            "words",
                            "typo",
                            "proximity",
                            "attribute",
                            "sort",
                            "exactness"
                        ],
                        "typoTolerance": {
                            "enabled": True,
                            "minWordSizeForTypos": {
                                "oneTypo": 5,
                                "twoTypos": 9
                            }
                        }
                    },
                    "exact-search": {
                        "rankingRules": [
                            "words",
                            "attribute",
                            "sort",
                            "exactness"
                        ],
                        "typoTolerance": {
                            "enabled": False
                        }
                    },
                    "fuzzy-search": {
                        "rankingRules": [
                            "typo",
                            "words",
                            "proximity",
                            "attribute",
                            "sort",
                            "exactness"
                        ],
                        "typoTolerance": {
                            "enabled": True,
                            "minWordSizeForTypos": {
                                "oneTypo": 3,
                                "twoTypos": 7
                            }
                        }
                    }
                }
                
                if use_case not in settings_templates:
                    return types.GetPromptResult(
                        messages=[
                            types.PromptMessage(
                                role="user",
                                content=types.TextContent(
                                    type="text",
                                    text=f"Unknown use case: {use_case}. Available use cases: {', '.join(settings_templates.keys())}"
                                )
                            )
                        ]
                    )
                
                settings = settings_templates[use_case]
                
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"Updating settings for index {index_uid} with {use_case} configuration:\n{str(settings)}"
                            )
                        )
                    ]
                )
            
            raise ValueError(f"Unknown prompt: {name}")

    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as streams:
            await self.server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="meilisearch-server",
                    server_version="0.1.0", 
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    # Get Meilisearch connection details from environment
    host = os.getenv("MEILI_HOST", "http://localhost:7700")
    api_key = os.getenv("MEILI_MASTER_KEY")
    
    # Create and run server
    server = MeilisearchMCPServer(host, api_key)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())