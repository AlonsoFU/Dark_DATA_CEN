#!/usr/bin/env python3
"""
Test script for MCP Server
Demonstrates how AI tools can access dark data
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🔌 Testing Dark Data MCP Server...")
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server.py"],
        cwd="/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                print("✅ MCP Server connected successfully!")
                
                # List available tools
                print("\n📋 Available Tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"   🔧 {tool.name}: {tool.description}")
                
                # List available resources
                print("\n📚 Available Resources:")
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"   📄 {resource.name}: {resource.description}")
                
                # Test search_incidents tool
                print("\n🔍 Testing search_incidents tool...")
                search_result = await session.call_tool(
                    "search_incidents",
                    {"query": "Siemens protection", "limit": 2}
                )
                print("Search Results:")
                for content in search_result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
                
                # Test compliance report
                print("\n📊 Testing compliance report...")
                compliance_result = await session.call_tool(
                    "get_compliance_report",
                    {}
                )
                print("Compliance Report:")
                for content in compliance_result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
                
                # Test equipment analysis
                print("\n⚙️ Testing equipment analysis...")
                equipment_result = await session.call_tool(
                    "analyze_equipment_failures",
                    {}
                )
                print("Equipment Analysis:")
                for content in equipment_result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
                
                # Test incident timeline
                print("\n🕐 Testing incident timeline...")
                timeline_result = await session.call_tool(
                    "get_incident_timeline",
                    {}
                )
                print("Incident Timeline:")
                for content in timeline_result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
                
                print("\n✅ All MCP tests completed successfully!")
                print("\n🎉 Your Dark Data is now MCP-ready!")
                print("🔗 AI tools can now access your power system failure data directly!")
                
    except Exception as e:
        print(f"❌ MCP Test failed: {e}")
        print("Please check that the MCP server is properly configured.")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())