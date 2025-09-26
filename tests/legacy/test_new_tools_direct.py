#!/usr/bin/env python3
"""
Direct test of new MCP tools (without Claude API)
Tests the tools directly to make sure they work
"""

import asyncio
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_new_tools_direct():
    """Test new tools directly"""
    print("🧪 TESTING NEW MCP TOOLS DIRECTLY")
    print("=" * 50)
    
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server_enhanced.py"],
        cwd="/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List all available tools
            tools = await session.list_tools()
            print(f"✅ Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"   🔧 {tool.name}: {tool.description}")
            print()
            
            # Test each new tool
            new_tools = [
                ("open_dashboard", {}, "🌐 Testing dashboard opening..."),
                ("get_system_status", {}, "🖥️  Testing system status check..."),
                ("generate_executive_report", {}, "📋 Testing executive report generation..."),
                ("export_data", {"format_type": "json"}, "💾 Testing data export...")
            ]
            
            for tool_name, args, description in new_tools:
                print(description)
                try:
                    result = await session.call_tool(tool_name, args)
                    
                    print("✅ SUCCESS!")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            # Show first 300 chars
                            text = content.text
                            if len(text) > 300:
                                text = text[:300] + "...[truncated]"
                            print(f"📝 Response: {text}")
                    print()
                    
                except Exception as e:
                    print(f"❌ ERROR: {e}")
                    print()

if __name__ == "__main__":
    asyncio.run(test_new_tools_direct())