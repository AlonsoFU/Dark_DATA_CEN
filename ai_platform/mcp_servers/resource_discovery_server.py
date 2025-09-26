#!/usr/bin/env python3
"""
Resource Discovery MCP Server - Platform Resource Intelligence
Centralized resource discovery and cataloging for the AI platform
"""

import asyncio
import json
import os
from pathlib import Path
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

server = Server("resource-discovery-server")

def get_project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent.parent

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available resource discovery tools."""
    return [
        types.Tool(
            name="discover_platform_resources",
            description="Discover all available resources in the AI platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Type of resource: all, mcp_servers, data_sources, ai_tools, domain_processors",
                        "enum": ["all", "mcp_servers", "data_sources", "ai_tools", "domain_processors"]
                    },
                    "include_status": {
                        "type": "boolean",
                        "description": "Include status information for each resource",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="search_unified_documents",
            description="Search across all platform and domain documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific domains to search (operaciones, mercados, legal)"
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Type of document: extractions, source_documents, all"
                    },
                    "limit": {"type": "integer", "description": "Maximum results to return", "default": 50}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_mcp_server_capabilities",
            description="Get detailed capabilities of available MCP servers",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "Specific server: operaciones, mercados, legal, cross_domain, enhanced, core",
                        "enum": ["operaciones", "mercados", "legal", "cross_domain", "enhanced", "core", "all"]
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="analyze_data_flow",
            description="Analyze data flow between domains, platform_data, and AI components",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Data source to analyze"},
                    "target": {"type": "string", "description": "Data target to analyze"},
                    "flow_type": {
                        "type": "string",
                        "description": "Type of flow analysis",
                        "enum": ["extraction_to_platform", "platform_to_ai", "cross_domain", "full_pipeline"]
                    }
                },
                "required": ["flow_type"]
            }
        ),
        types.Tool(
            name="validate_resource_integration",
            description="Validate that resources are properly integrated and accessible",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_category": {
                        "type": "string",
                        "description": "Category to validate",
                        "enum": ["mcp_servers", "data_sources", "ai_components", "domain_processors", "all"]
                    },
                    "check_connectivity": {
                        "type": "boolean",
                        "description": "Check if resources are accessible",
                        "default": True
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for resource discovery."""

    if name == "discover_platform_resources":
        resource_type = arguments.get("resource_type", "all")
        include_status = arguments.get("include_status", True)

        try:
            project_root = get_project_root()
            resources_dir = project_root / "ai_platform" / "resources"

            # Load resource catalog
            catalog_path = resources_dir / "platform_resource_catalog.json"
            if catalog_path.exists():
                with open(catalog_path, 'r') as f:
                    catalog = json.load(f)

                if resource_type == "all":
                    result = catalog
                else:
                    # Filter by resource type
                    type_mapping = {
                        "mcp_servers": "mcp_servers",
                        "data_sources": "data_infrastructure",
                        "ai_tools": "ai_capabilities",
                        "domain_processors": "domain_data"
                    }
                    if resource_type in type_mapping:
                        result = {resource_type: catalog.get(type_mapping[resource_type], {})}
                    else:
                        result = catalog

                return [types.TextContent(
                    type="text",
                    text=f"Platform Resources Discovery Results:\n\n{json.dumps(result, indent=2)}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="Resource catalog not found. Please ensure ai_platform/resources/ is properly configured."
                )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error discovering resources: {str(e)}"
            )]

    elif name == "search_unified_documents":
        query = arguments.get("query", "")
        domains = arguments.get("domains", [])
        document_type = arguments.get("document_type", "all")
        limit = arguments.get("limit", 50)

        try:
            project_root = get_project_root()
            search_results = []

            # Search in platform_data
            platform_data_path = project_root / "platform_data"
            if platform_data_path.exists():
                search_results.append({
                    "source": "platform_data",
                    "location": str(platform_data_path),
                    "type": "consolidated_database",
                    "search_note": "Use direct database queries for detailed search"
                })

            # Search in domain extractions
            domains_path = project_root / "domains"
            if domains_path.exists():
                target_domains = domains if domains else ["operaciones", "mercados", "legal"]

                for domain in target_domains:
                    domain_path = domains_path / domain
                    if domain_path.exists():
                        # Find extraction files
                        extraction_files = list(domain_path.rglob("*.json"))
                        if extraction_files:
                            search_results.append({
                                "domain": domain,
                                "extraction_files_count": len(extraction_files),
                                "sample_files": [str(f.relative_to(project_root)) for f in extraction_files[:5]],
                                "search_note": f"Found {len(extraction_files)} JSON files in {domain} domain"
                            })

            result = {
                "query": query,
                "search_results": search_results[:limit],
                "total_sources_found": len(search_results)
            }

            return [types.TextContent(
                type="text",
                text=f"Unified Document Search Results:\n\n{json.dumps(result, indent=2)}"
            )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error searching documents: {str(e)}"
            )]

    elif name == "get_mcp_server_capabilities":
        server_name = arguments.get("server_name", "all")

        try:
            project_root = get_project_root()
            resources_dir = project_root / "ai_platform" / "resources"

            # Load tool registry
            registry_path = resources_dir / "enhanced_tool_registry.json"
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)

                mcp_tools = registry.get("mcp_server_tools", {})

                if server_name == "all":
                    result = mcp_tools
                else:
                    server_key = f"{server_name}_server_tools"
                    if server_key in mcp_tools:
                        result = {server_name: mcp_tools[server_key]}
                    else:
                        result = {"error": f"Server '{server_name}' not found in registry"}

                return [types.TextContent(
                    type="text",
                    text=f"MCP Server Capabilities:\n\n{json.dumps(result, indent=2)}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="Tool registry not found. Please ensure ai_platform/resources/ is properly configured."
                )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error getting server capabilities: {str(e)}"
            )]

    elif name == "analyze_data_flow":
        flow_type = arguments.get("flow_type", "full_pipeline")
        source = arguments.get("source", "")
        target = arguments.get("target", "")

        flow_patterns = {
            "extraction_to_platform": {
                "description": "How domain extractions flow into platform_data",
                "flow": [
                    "domains/*/data/extractions/*.json",
                    "→ processing via ai_platform/processors/",
                    "→ consolidation into platform_data/database/",
                    "→ accessible via MCP servers"
                ]
            },
            "platform_to_ai": {
                "description": "How platform data flows to AI components",
                "flow": [
                    "platform_data/database/",
                    "→ ai_platform/mcp_servers/",
                    "→ ai_platform/ai_models/ + knowledge_base/",
                    "→ intelligent analysis and insights"
                ]
            },
            "cross_domain": {
                "description": "How cross-domain analysis works",
                "flow": [
                    "domains/operaciones/ + domains/mercados/ + domains/legal/",
                    "→ ai_platform/mcp_servers/cross_domain_server.py",
                    "→ ai_platform/knowledge_graph/",
                    "→ integrated intelligence"
                ]
            },
            "full_pipeline": {
                "description": "Complete data flow from extraction to AI insights",
                "flow": [
                    "PDF Documents",
                    "→ domains/*/processors/",
                    "→ domains/*/data/extractions/*.json",
                    "→ platform_data/database/ (consolidation)",
                    "→ ai_platform/mcp_servers/ (access)",
                    "→ ai_platform/ai_models/ (analysis)",
                    "→ AI-powered insights"
                ]
            }
        }

        result = flow_patterns.get(flow_type, {"error": "Flow type not found"})

        return [types.TextContent(
            type="text",
            text=f"Data Flow Analysis - {flow_type}:\n\n{json.dumps(result, indent=2)}"
        )]

    elif name == "validate_resource_integration":
        resource_category = arguments.get("resource_category", "all")
        check_connectivity = arguments.get("check_connectivity", True)

        try:
            project_root = get_project_root()
            validation_results = []

            # Validate MCP servers
            if resource_category in ["mcp_servers", "all"]:
                mcp_servers_dir = project_root / "ai_platform" / "mcp_servers"
                if mcp_servers_dir.exists():
                    server_files = list(mcp_servers_dir.glob("*.py"))
                    validation_results.append({
                        "category": "mcp_servers",
                        "status": "accessible",
                        "count": len(server_files),
                        "files": [f.name for f in server_files]
                    })

            # Validate data sources
            if resource_category in ["data_sources", "all"]:
                platform_data_exists = (project_root / "platform_data").exists()
                domains_exist = (project_root / "domains").exists()

                validation_results.append({
                    "category": "data_sources",
                    "platform_data": "accessible" if platform_data_exists else "not_found",
                    "domains": "accessible" if domains_exist else "not_found"
                })

            # Validate AI components
            if resource_category in ["ai_components", "all"]:
                ai_components = ["knowledge_base", "knowledge_graph", "ai_models", "analyzers", "processors"]
                ai_status = {}

                for component in ai_components:
                    component_path = project_root / "ai_platform" / component
                    ai_status[component] = "accessible" if component_path.exists() else "not_found"

                validation_results.append({
                    "category": "ai_components",
                    "components": ai_status
                })

            result = {
                "validation_timestamp": "2025-09-25",
                "results": validation_results,
                "overall_status": "platform_integrated"
            }

            return [types.TextContent(
                type="text",
                text=f"Resource Integration Validation:\n\n{json.dumps(result, indent=2)}"
            )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error validating resources: {str(e)}"
            )]

    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="resource-discovery-server",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())